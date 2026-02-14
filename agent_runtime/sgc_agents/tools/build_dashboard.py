from __future__ import annotations

import argparse
import html
import re
from collections import Counter
from pathlib import Path
from string import Template
from typing import Any

import yaml

from ..config import repo_root


LMD_PATH = Path("docs/_control/lmd.yml")
MATRIX_PATH = Path("docs/_control/matriz_registros.yml")
QA_REPORT_PATH = Path("docs/_control/reporte_qa_compliance.md")
DASHBOARD_PATH = Path("docs/_control/dashboard_sgc.html")

QA_SECTION_RE = re.compile(r"##\s+\d+\.\s+([^\n]+)\n```yaml\n(.*?)\n```", re.DOTALL)
QA_DATE_RE = re.compile(r"-\s+Fecha:\s+([^\n]+)")
QA_TOTAL_RE = re.compile(r"-\s+Hallazgos totales:\s+([0-9]+)")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    parsed = yaml.safe_load(_read_text(path)) or {}
    return parsed if isinstance(parsed, dict) else {}


def _esc(value: Any) -> str:
    return html.escape(str(value))


def _is_pending(value: Any) -> bool:
    text = str(value or "").strip().upper()
    if not text:
        return True
    return "TODO" in text or "TBD" in text or "<DEFINIR>" in text


def _parse_qa_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "fecha": "N/A",
            "hallazgos_totales": 0,
            "checks": [],
            "raw": "",
        }

    content = _read_text(path)
    date_match = QA_DATE_RE.search(content)
    total_match = QA_TOTAL_RE.search(content)

    checks: list[dict[str, Any]] = []
    for title, yaml_block in QA_SECTION_RE.findall(content):
        parsed = yaml.safe_load(yaml_block) or {}
        findings = parsed.get("hallazgos", [])
        findings_count = len(findings) if isinstance(findings, list) else 0
        checks.append(
            {
                "titulo": title.strip(),
                "valido": bool(parsed.get("valido", False)),
                "hallazgos": findings_count,
                "detalle": parsed,
            }
        )

    return {
        "fecha": date_match.group(1).strip() if date_match else "N/A",
        "hallazgos_totales": int(total_match.group(1)) if total_match else 0,
        "checks": checks,
        "raw": content,
    }


def _metric_cards(
    lmd_docs: list[dict[str, Any]],
    matrix_rows: list[dict[str, Any]],
    qa: dict[str, Any],
) -> list[dict[str, Any]]:
    total_docs = len(lmd_docs)
    by_status = Counter(str(row.get("estado", "")).strip() for row in lmd_docs)
    vigentes = by_status.get("VIGENTE", 0)

    pending_matrix = 0
    for row in matrix_rows:
        if (
            _is_pending(row.get("responsable"))
            or _is_pending(row.get("retencion"))
            or _is_pending(row.get("disposicion_final"))
            or _is_pending(row.get("acceso"))
        ):
            pending_matrix += 1

    return [
        {
            "label": "Documentos controlados",
            "value": total_docs,
            "tone": "ok",
        },
        {
            "label": "Documentos vigentes",
            "value": vigentes,
            "tone": "ok" if vigentes else "warn",
        },
        {
            "label": "Registros en matriz",
            "value": len(matrix_rows),
            "tone": "ok",
        },
        {
            "label": "Hallazgos QA",
            "value": qa.get("hallazgos_totales", 0),
            "tone": "ok" if qa.get("hallazgos_totales", 0) == 0 else "bad",
        },
        {
            "label": "Pendientes matriz",
            "value": pending_matrix,
            "tone": "ok" if pending_matrix == 0 else "warn",
        },
    ]


def _render_distribution(title: str, counts: Counter[str], total: int) -> str:
    rows: list[str] = []
    for key, count in counts.most_common():
        pct = (count / total * 100.0) if total else 0.0
        rows.append(
            """
            <div class="dist-row">
              <div class="dist-label">{label}</div>
              <div class="dist-track"><span style="width:{pct:.2f}%"></span></div>
              <div class="dist-value">{count}</div>
            </div>
            """.format(label=_esc(key or "N/A"), pct=pct, count=count)
        )

    if not rows:
        rows.append('<div class="muted">Sin datos disponibles.</div>')

    return """
    <section class="panel stagger-2">
      <h3>{title}</h3>
      <div class="dist-grid">{rows}</div>
    </section>
    """.format(title=_esc(title), rows="".join(rows))


def _render_checks_table(checks: list[dict[str, Any]]) -> str:
    if not checks:
        return "<p class=\"muted\">No se encontro informacion QA.</p>"

    rows: list[str] = []
    for check in checks:
        status = "OK" if check.get("valido") else "Falla"
        cls = "ok" if check.get("valido") else "bad"
        rows.append(
            """
            <tr>
              <td>{titulo}</td>
              <td><span class="badge {cls}">{status}</span></td>
              <td>{hallazgos}</td>
            </tr>
            """.format(
                titulo=_esc(check.get("titulo", "N/A")),
                cls=cls,
                status=status,
                hallazgos=_esc(check.get("hallazgos", 0)),
            )
        )

    return """
    <table>
      <thead>
        <tr>
          <th>Chequeo</th>
          <th>Estado</th>
          <th>Hallazgos</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    """.format(rows="".join(rows))


def _render_records_table(matrix_rows: list[dict[str, Any]]) -> str:
    if not matrix_rows:
        return "<p class=\"muted\">No hay filas en matriz_registros.yml.</p>"

    rows: list[str] = []
    for row in matrix_rows:
        pending = (
            _is_pending(row.get("responsable"))
            or _is_pending(row.get("retencion"))
            or _is_pending(row.get("disposicion_final"))
            or _is_pending(row.get("acceso"))
        )
        rows.append(
            """
            <tr>
              <td>{codigo}</td>
              <td>{formato}</td>
              <td>{responsable}</td>
              <td>{retencion}</td>
              <td><span class="badge {cls}">{estado}</span></td>
            </tr>
            """.format(
                codigo=_esc(row.get("codigo", "N/A")),
                formato=_esc(row.get("codigo_formato", "N/A")),
                responsable=_esc(row.get("responsable", "N/A")),
                retencion=_esc(row.get("retencion", "N/A")),
                cls="warn" if pending else "ok",
                estado="Pendiente" if pending else "Completo",
            )
        )

    return """
    <table>
      <thead>
        <tr>
          <th>Codigo registro</th>
          <th>Formato origen</th>
          <th>Responsable</th>
          <th>Retencion</th>
          <th>Calidad de dato</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    """.format(rows="".join(rows))


def render_dashboard_html(data: dict[str, Any]) -> str:
    cards = data["cards"]
    docs = data["docs"]
    matrix_rows = data["matrix_rows"]
    qa = data["qa"]
    generated_at = str(qa.get("fecha", "N/A"))

    status_counts = Counter(str(row.get("estado", "")).strip() for row in docs)
    type_counts = Counter(str(row.get("tipo", "")).strip() for row in docs)

    card_html = "".join(
        """
        <article class="card {tone} stagger-1">
          <p>{label}</p>
          <strong>{value}</strong>
        </article>
        """.format(label=_esc(card["label"]), value=_esc(card["value"]), tone=_esc(card["tone"]))
        for card in cards
    )

    overall_ok = qa.get("hallazgos_totales", 0) == 0
    overall_text = "Cumplimiento estable" if overall_ok else "Requiere atencion"
    overall_class = "ok" if overall_ok else "bad"

    template = Template(
        """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dashboard SGC</title>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap");

    :root {
      --bg: #f6f3ea;
      --panel: #fffef8;
      --ink: #102a3a;
      --muted: #5a6771;
      --line: #d8ddd2;
      --ok: #0f766e;
      --warn: #b45309;
      --bad: #b42318;
      --accent: #005f73;
      --accent-soft: #d9f0ec;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Space Grotesk", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at 12% 8%, #d9f0ec 0, rgba(217,240,236,0) 46%),
                  radial-gradient(circle at 88% 3%, #ffe3c3 0, rgba(255,227,195,0) 42%),
                  var(--bg);
      line-height: 1.4;
    }

    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 18px 44px;
    }

    .hero {
      background: linear-gradient(120deg, #fffef8 0%, #eef7f5 100%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 22px;
      box-shadow: 0 18px 38px rgba(16, 42, 58, 0.08);
      animation: fadeUp .45s ease both;
    }

    h1 { margin: 0; font-size: clamp(1.5rem, 2.4vw, 2.25rem); }
    h2 { margin: 3px 0 0; color: var(--muted); font-size: 1rem; font-weight: 500; }
    h3 { margin: 0 0 14px; font-size: 1.02rem; }

    .meta {
      margin-top: 14px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      font-family: "IBM Plex Mono", monospace;
      font-size: .85rem;
      color: var(--muted);
    }

    .cards {
      margin-top: 16px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      min-height: 102px;
      display: grid;
      align-content: space-between;
    }

    .card p { margin: 0; color: var(--muted); font-size: .88rem; }
    .card strong { font-size: 2rem; line-height: 1; }
    .card.ok strong { color: var(--ok); }
    .card.warn strong { color: var(--warn); }
    .card.bad strong { color: var(--bad); }

    .grid {
      margin-top: 16px;
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 12px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      box-shadow: 0 10px 24px rgba(16, 42, 58, 0.06);
    }

    .col-6 { grid-column: span 6; }
    .col-12 { grid-column: span 12; }

    .dist-row {
      display: grid;
      grid-template-columns: 130px 1fr 36px;
      gap: 10px;
      align-items: center;
      margin-bottom: 9px;
      font-size: .88rem;
    }

    .dist-label { color: var(--muted); }
    .dist-track {
      height: 12px;
      background: #e9ece3;
      border-radius: 999px;
      overflow: hidden;
    }

    .dist-track span {
      display: block;
      height: 100%;
      background: linear-gradient(90deg, var(--accent) 0%, #22a39f 100%);
      border-radius: 999px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: .88rem;
    }

    th, td {
      border-bottom: 1px solid var(--line);
      text-align: left;
      padding: 9px 7px;
      vertical-align: top;
    }

    th {
      color: #334155;
      background: #f3f7f3;
      font-weight: 600;
      position: sticky;
      top: 0;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: .76rem;
      font-weight: 700;
      letter-spacing: .02em;
      border: 1px solid transparent;
    }

    .badge.ok { color: var(--ok); border-color: #97d6cb; background: #edf9f6; }
    .badge.warn { color: var(--warn); border-color: #f4cf9f; background: #fff6e8; }
    .badge.bad { color: var(--bad); border-color: #f0b4ad; background: #fff0ee; }

    .muted { color: var(--muted); }

    .footer {
      margin-top: 15px;
      font-family: "IBM Plex Mono", monospace;
      font-size: .8rem;
      color: var(--muted);
    }

    .stagger-1 { animation: fadeUp .55s ease both; }
    .stagger-2 { animation: fadeUp .65s ease both; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 900px) {
      .col-6 { grid-column: span 12; }
      .dist-row { grid-template-columns: 1fr; gap: 4px; }
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>Dashboard SGC</h1>
      <h2>Control documental + trazabilidad + cumplimiento QA</h2>
      <div class="meta">
        <span>QA corte: $qa_date</span>
        <span>Corte dashboard: $generated_at</span>
        <span class="badge $overall_class">$overall_text</span>
      </div>
      <div class="cards">$cards</div>
    </section>

    <section class="grid">
      <div class="col-6">$status_dist</div>
      <div class="col-6">$type_dist</div>

      <section class="panel col-6 stagger-2">
        <h3>Pipeline QA deterministico</h3>
        $checks_table
      </section>

      <section class="panel col-6 stagger-2">
        <h3>Resumen operativo</h3>
        <p class="muted">Documentos en LMD: <strong>$docs_total</strong></p>
        <p class="muted">Filas en matriz de registros: <strong>$matrix_total</strong></p>
        <p class="muted">Hallazgos QA: <strong>$qa_findings</strong></p>
        <p class="muted">Este tablero se autogenera. No editar manualmente.</p>
      </section>

      <section class="panel col-12 stagger-2">
        <h3>Matriz de registros (calidad de dato)</h3>
        $records_table
      </section>
    </section>

    <p class="footer">Fuente: lmd.yml + matriz_registros.yml + reporte_qa_compliance.md</p>
  </main>
</body>
</html>
"""
    )

    return template.safe_substitute(
        qa_date=_esc(qa.get("fecha", "N/A")),
        generated_at=_esc(generated_at),
        overall_class=_esc(overall_class),
        overall_text=_esc(overall_text),
        cards=card_html,
        status_dist=_render_distribution("Distribucion por estado", status_counts, len(docs)),
        type_dist=_render_distribution("Distribucion por tipo documental", type_counts, len(docs)),
        checks_table=_render_checks_table(qa.get("checks", [])),
        docs_total=_esc(len(docs)),
        matrix_total=_esc(len(matrix_rows)),
        qa_findings=_esc(qa.get("hallazgos_totales", 0)),
        records_table=_render_records_table(matrix_rows),
    )


def build_dashboard(root: Path | None = None, output: Path | None = None) -> Path:
    resolved_root = root.resolve() if root else repo_root().resolve()
    output_path = output or (resolved_root / DASHBOARD_PATH)

    lmd = _load_yaml(resolved_root / LMD_PATH)
    matrix = _load_yaml(resolved_root / MATRIX_PATH)
    qa = _parse_qa_report(resolved_root / QA_REPORT_PATH)

    docs = lmd.get("documentos", [])
    matrix_rows = matrix.get("registros", [])
    docs = docs if isinstance(docs, list) else []
    matrix_rows = matrix_rows if isinstance(matrix_rows, list) else []

    dashboard_data = {
        "docs": docs,
        "matrix_rows": matrix_rows,
        "qa": qa,
        "cards": _metric_cards(docs, matrix_rows, qa),
    }

    html_content = render_dashboard_html(dashboard_data)
    _write_text(output_path, html_content)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera dashboard HTML del SGC desde artefactos de control"
    )
    parser.add_argument(
        "--repo-root",
        help="Ruta raiz del repo SGC. Si no se indica, usa SGC_REPO_ROOT o auto-deteccion.",
    )
    parser.add_argument(
        "--output",
        help="Ruta de salida del dashboard (default: docs/_control/dashboard_sgc.html)",
    )
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else None
    output = Path(args.output).resolve() if args.output else None

    path = build_dashboard(root, output)
    print(f"OK: dashboard generado en {path}")


if __name__ == "__main__":
    main()
