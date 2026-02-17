from __future__ import annotations

from pathlib import Path

import yaml

from sgc_agents.tools.compliance_tools import _validate_traceability_for_path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _format_doc(estado: str = "VIGENTE") -> str:
    return f"""---
codigo: "FOR-SGC-02"
titulo: "Registro de No Conformidad"
tipo: "FOR"
version: "1.0"
estado: "{estado}"
fecha_emision: "2026-02-09"
proceso: "SGC / Mejora"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# FOR-SGC-02 Registro de No Conformidad

## 1. Objetivo
Controlar no conformidades.
"""


def _record_doc(
    formato: str,
    include_frontmatter: bool = True,
    include_location_pointer: bool = True,
) -> str:
    frontmatter = ""
    if include_frontmatter:
        location_line = (
            'ubicacion_externa_url: "s3://sgc-registros/tests/REG-SGC-NC-2026-001.json"\n'
            if include_location_pointer
            else ""
        )
        frontmatter = (
            f"""---
formato_origen: "{formato}"
codigo_registro: "REG-SGC-NC-2026-001"
fecha_registro: "2026-02-09"
{location_line}---

"""
        )

    return (
        frontmatter
        + "# REG-SGC-NC-2026-001 (Wrapper de metadatos)\n\n"
        + "Este archivo referencia un sistema externo de registros.\n"
    )


def _write_matrix(repo: Path, include_mapping: bool = True) -> None:
    matrix_path = repo / "docs/_control/matriz_registros.yml"
    if include_mapping:
        payload = {
            "registros": [
                {
                    "codigo": "REG-SGC-NC",
                    "codigo_formato": "FOR-SGC-02",
                    "nombre": "Registro NC",
                    "responsable": "Calidad",
                    "retencion": "5 anos",
                    "disposicion_final": "Archivo historico",
                    "acceso": "Calidad",
                    "ubicacion": "docs/06_registros/no_conformidades/",
                    "ubicacion_externa_url": "s3://sgc-registros/catalogo/REG-SGC-NC.json",
                }
            ]
        }
    else:
        payload = {"registros": []}

    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _setup_repo(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv("SGC_REPO_ROOT", str(tmp_path))
    _write_matrix(tmp_path, include_mapping=True)
    return tmp_path


def test_p1_fails_when_formato_origen_is_missing(tmp_path, monkeypatch) -> None:
    repo = _setup_repo(tmp_path, monkeypatch)

    _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
    record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
    _write(record_path, _record_doc("FOR-SGC-02", include_frontmatter=False))

    result = _validate_traceability_for_path(record_path)

    assert result["valido"] is False
    assert result["axiomas"]["P1_procedencia"] is False
    assert "[P1]" in result["hallazgos"][0]


def test_p2_fails_when_format_does_not_exist(tmp_path, monkeypatch) -> None:
    repo = _setup_repo(tmp_path, monkeypatch)

    record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
    _write(record_path, _record_doc("FOR-SGC-99"))

    result = _validate_traceability_for_path(record_path)

    assert result["valido"] is False
    assert result["axiomas"]["P1_procedencia"] is True
    assert result["axiomas"]["P2_existencia_canonica"] is False
    assert "[P2]" in result["hallazgos"][0]


def test_p3_fails_when_origin_format_is_not_vigente(tmp_path, monkeypatch) -> None:
    repo = _setup_repo(tmp_path, monkeypatch)

    _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc(estado="BORRADOR"))
    record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
    _write(record_path, _record_doc("FOR-SGC-02"))

    result = _validate_traceability_for_path(record_path)

    assert result["valido"] is False
    assert result["axiomas"]["P1_procedencia"] is True
    assert result["axiomas"]["P2_existencia_canonica"] is True
    assert result["axiomas"]["P3_vigencia_legal"] is False
    assert any("[P3]" in item for item in result["hallazgos"])


def test_p4_fails_when_format_is_not_in_matrix(tmp_path, monkeypatch) -> None:
    repo = _setup_repo(tmp_path, monkeypatch)
    _write_matrix(repo, include_mapping=False)

    _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
    record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
    _write(record_path, _record_doc("FOR-SGC-02"))

    result = _validate_traceability_for_path(record_path)

    assert result["valido"] is False
    assert result["axiomas"]["P1_procedencia"] is True
    assert result["axiomas"]["P2_existencia_canonica"] is True
    assert result["axiomas"]["P3_vigencia_legal"] is True
    assert result["axiomas"]["P4_sincronizacion_ssot"] is False
    assert any("[P4]" in item for item in result["hallazgos"])


def test_p5_fails_when_wrapper_has_no_external_or_physical_pointer(tmp_path, monkeypatch) -> None:
    repo = _setup_repo(tmp_path, monkeypatch)

    _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
    record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
    _write(
        record_path,
        _record_doc("FOR-SGC-02", include_frontmatter=True, include_location_pointer=False),
    )

    result = _validate_traceability_for_path(record_path)

    assert result["valido"] is False
    assert result["axiomas"]["P1_procedencia"] is True
    assert result["axiomas"]["P5_isomorfismo_estructural"] is False
    assert any("[P5]" in item for item in result["hallazgos"])


def test_all_axioms_pass_for_valid_traceability(tmp_path, monkeypatch) -> None:
    repo = _setup_repo(tmp_path, monkeypatch)

    _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
    record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
    _write(record_path, _record_doc("FOR-SGC-02"))

    result = _validate_traceability_for_path(record_path)

    assert result["valido"] is True
    assert all(result["axiomas"].values())
