from __future__ import annotations

from pathlib import Path

from sgc_agents.tools.build_dashboard import _parse_qa_report, build_dashboard


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_parse_qa_report_extracts_checks_and_totals(tmp_path) -> None:
    report = """# Reporte QA/Compliance (Neuro-Simbolico)

- Fecha: 2026-02-14
- Hallazgos totales: 2

## 1. auditar_invariantes_de_estado
```yaml
skill: auditar_invariantes_de_estado
valido: true
hallazgos: []
```

## 2. validar_trazabilidad
```yaml
skill: auditar_trazabilidad
valido: false
hallazgos:
- P3
- P5
```
"""
    path = tmp_path / "docs/_control/reporte_qa_compliance.md"
    _write(path, report)

    payload = _parse_qa_report(path)

    assert payload["fecha"] == "2026-02-14"
    assert payload["hallazgos_totales"] == 2
    assert len(payload["checks"]) == 2
    assert payload["checks"][0]["valido"] is True
    assert payload["checks"][1]["hallazgos"] == 2


def test_build_dashboard_renders_html_from_control_artifacts(tmp_path) -> None:
    lmd = """documentos:
- codigo: FOR-SGC-01
  titulo: Solicitud
  tipo: FOR
  estado: VIGENTE
  proceso: SGC
- codigo: PR-SGC-01
  titulo: Control documental
  tipo: PR
  estado: BORRADOR
  proceso: SGC
"""
    matrix = """registros:
- codigo: REG-SGC-NC
  codigo_formato: FOR-SGC-02
  responsable: <DEFINIR>
  retencion: 'TODO: Definir'
  disposicion_final: 'TODO: Definir'
  acceso: Calidad
"""
    report = """# Reporte QA/Compliance (Neuro-Simbolico)

- Fecha: 2026-02-14
- Hallazgos totales: 0

## 1. auditar_invariantes_de_estado
```yaml
skill: auditar_invariantes_de_estado
valido: true
hallazgos: []
```
"""

    _write(tmp_path / "docs/_control/lmd.yml", lmd)
    _write(tmp_path / "docs/_control/matriz_registros.yml", matrix)
    _write(tmp_path / "docs/_control/reporte_qa_compliance.md", report)

    output = build_dashboard(tmp_path)
    html = output.read_text(encoding="utf-8")

    assert output.name == "dashboard_sgc.html"
    assert "Dashboard SGC" in html
    assert "QA corte: 2026-02-14" in html
    assert "Documentos controlados" in html
    assert "Matriz de registros (calidad de dato)" in html
    assert "REG-SGC-NC" in html
    assert "$qa_date" not in html
