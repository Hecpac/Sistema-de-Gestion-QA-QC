from __future__ import annotations

import argparse
import html
import re
from collections import Counter
from pathlib import Path
from string import Template
from typing import Any

import yaml

from ..config import (
    LMD_PATH,
    MATRIX_PATH,
    QA_REPORT_PATH,
    QA_HISTORY_PATH,
    DASHBOARD_PATH,
    repo_root,
)
from ..utils import read, write, is_pending_value

# Relative control artifact paths (resolved against --repo-root at runtime)
LMD_REL_PATH = Path(LMD_PATH)
MATRIX_REL_PATH = Path(MATRIX_PATH)
QA_REPORT_REL_PATH = Path(QA_REPORT_PATH)
QA_HISTORY_REL_PATH = Path(QA_HISTORY_PATH)
DASHBOARD_REL_PATH = Path(DASHBOARD_PATH)

QA_SECTION_RE = re.compile(r"##\s+\d+\.\s+([^\n]+)\n```yaml\n(.*?)\n```", re.DOTALL)
QA_DATE_RE = re.compile(r"-\s+Fecha:\s+([^\n]+)")
QA_TOTAL_RE = re.compile(r"-\s+Hallazgos totales:\s+([0-9]+)")


# _read_text and _write_text are now imported from utils as read and write

def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    parsed = yaml.safe_load(read(path)) or {}
    return parsed if isinstance(parsed, dict) else {}


def _esc(value: Any) -> str:
    return html.escape(str(value))


def _parse_qa_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "fecha": "N/A",
            "hallazgos_totales": 0,
            "checks": [],
            "raw": "",
        }

    content = read(path)
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


def _parse_qa_history(path: Path, limit: int = 12) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    payload = _load_yaml(path)
    runs = payload.get("runs", [])
    if not isinstance(runs, list):
        return []

    normalized: list[dict[str, Any]] = []
    for row in runs:
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "timestamp": str(row.get("timestamp", "")).strip(),
                "date": str(row.get("date", "")).strip(),
                "hallazgos": int(row.get("hallazgos", 0) or 0),
                "source": str(row.get("source", "desconocido")).strip() or "desconocido",
            }
        )

    normalized.sort(key=lambda r: (r["timestamp"], r["date"]))
    return normalized[-limit:]


def _qa_ok_streak(history_runs: list[dict[str, Any]]) -> int:
    streak = 0
    for row in reversed(history_runs):
        if int(row.get("hallazgos", 0) or 0) == 0:
            streak += 1
            continue
        break
    return streak


def _metric_cards(
    lmd_docs: list[dict[str, Any]],
    matrix_rows: list[dict[str, Any]],
    qa: dict[str, Any],
    qa_history: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    total_docs = len(lmd_docs)
    by_status = Counter(str(row.get("estado", "")).strip() for row in lmd_docs)
    vigentes = by_status.get("VIGENTE", 0)

    pending_matrix = 0
    for row in matrix_rows:
        if (
            is_pending_value(row.get("responsable"))
            or is_pending_value(row.get("retencion"))
            or is_pending_value(row.get("disposicion_final"))
            or is_pending_value(row.get("acceso"))
        ):
            pending_matrix += 1

    qa_streak = _qa_ok_streak(qa_history)

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
            "label": "Racha QA OK",
            "value": qa_streak,
            "tone": "ok" if qa_streak >= 4 else "warn" if qa_streak else "bad",
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


def _render_history_table(history_runs: list[dict[str, Any]]) -> str:
    if not history_runs:
        return '<p class="muted">Sin corridas historicas de monitor QA.</p>'

    rows: list[str] = []
    for run in reversed(history_runs):
        hallazgos = int(run.get("hallazgos", 0) or 0)
        cls = "ok" if hallazgos == 0 else "bad"
        status = "OK" if hallazgos == 0 else "Falla"
        rows.append(
            """
            <tr>
              <td>{date}</td>
              <td>{source}</td>
              <td><span class=\"badge {cls}\">{status}</span></td>
              <td>{hallazgos}</td>
            </tr>
            """.format(
                date=_esc(run.get("date") or run.get("timestamp") or "N/A"),
                source=_esc(run.get("source", "desconocido")),
                cls=cls,
                status=status,
                hallazgos=hallazgos,
            )
        )

    return """
    <table>
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Origen</th>
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
            is_pending_value(row.get("responsable"))
            or is_pending_value(row.get("retencion"))
            or is_pending_value(row.get("disposicion_final"))
            or is_pending_value(row.get("acceso"))
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
    qa_history = data.get("qa_history", [])
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

    _template_dir = Path(__file__).resolve().parent.parent / "templates"
    template = Template((_template_dir / "dashboard.html").read_text(encoding="utf-8"))

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
        qa_streak=_esc(_qa_ok_streak(qa_history)),
        history_table=_render_history_table(qa_history),
        records_table=_render_records_table(matrix_rows),
    )


def build_dashboard(root: Path | None = None, output: Path | None = None) -> Path:
    resolved_root = root.resolve() if root else repo_root().resolve()
    output_path = output or (resolved_root / DASHBOARD_REL_PATH)

    lmd = _load_yaml(resolved_root / LMD_REL_PATH)
    matrix = _load_yaml(resolved_root / MATRIX_REL_PATH)
    qa = _parse_qa_report(resolved_root / QA_REPORT_REL_PATH)
    qa_history = _parse_qa_history(resolved_root / QA_HISTORY_REL_PATH)

    docs = lmd.get("documentos", [])
    matrix_rows = matrix.get("registros", [])
    docs = docs if isinstance(docs, list) else []
    matrix_rows = matrix_rows if isinstance(matrix_rows, list) else []

    dashboard_data = {
        "docs": docs,
        "matrix_rows": matrix_rows,
        "qa": qa,
        "qa_history": qa_history,
        "cards": _metric_cards(docs, matrix_rows, qa, qa_history),
    }

    html_content = render_dashboard_html(dashboard_data)
    write(output_path, html_content)
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
