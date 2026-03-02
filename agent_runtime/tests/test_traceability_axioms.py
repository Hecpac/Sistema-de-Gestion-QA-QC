from __future__ import annotations

from pathlib import Path

import yaml

from sgc_agents.tools.compliance_tools import (
    _validate_header_isomorphism,
    _validate_pointer_schema,
    _validate_traceability_for_path,
)


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


# ===================================================================
# P5b — Pointer schema validation (_validate_pointer_schema)
# ===================================================================


class TestValidatePointerSchema:
    def test_valid_s3_url(self):
        meta = {"ubicacion_externa_url": "s3://bucket/path/file.json"}
        assert _validate_pointer_schema(meta) == []

    def test_valid_https_url(self):
        meta = {"ubicacion_externa_url": "https://example.com/record.json"}
        assert _validate_pointer_schema(meta) == []

    def test_valid_gs_url(self):
        meta = {"ubicacion_externa_url": "gs://bucket/path/file.json"}
        assert _validate_pointer_schema(meta) == []

    def test_valid_jira_url(self):
        meta = {"ubicacion_externa_url": "jira://PROJECT-123"}
        assert _validate_pointer_schema(meta) == []

    def test_valid_sap_url(self):
        meta = {"ubicacion_externa_url": "sap://MM/4500001234"}
        assert _validate_pointer_schema(meta) == []

    def test_invalid_scheme(self):
        meta = {"ubicacion_externa_url": "ftp://server/file.pdf"}
        findings = _validate_pointer_schema(meta)
        assert len(findings) == 1
        assert "ftp" in findings[0]
        assert "[P5]" in findings[0]

    def test_no_scheme(self):
        meta = {"ubicacion_externa_url": "just-a-string"}
        findings = _validate_pointer_schema(meta)
        assert len(findings) == 1
        assert "esquema" in findings[0]

    def test_https_without_host(self):
        meta = {"ubicacion_externa_url": "https://"}
        findings = _validate_pointer_schema(meta)
        assert len(findings) == 1
        assert "host" in findings[0]

    def test_s3_without_bucket(self):
        meta = {"ubicacion_externa_url": "s3://"}
        findings = _validate_pointer_schema(meta)
        assert len(findings) == 1
        assert "bucket" in findings[0]

    def test_physical_location_valid(self):
        meta = {"ubicacion_fisica": "Archivo Central, Caja 42"}
        assert _validate_pointer_schema(meta) == []

    def test_physical_location_tbd(self):
        meta = {"ubicacion_fisica": "TBD"}
        findings = _validate_pointer_schema(meta)
        assert len(findings) == 1
        assert "pendiente" in findings[0]

    def test_physical_location_todo(self):
        meta = {"ubicacion_fisica": "TODO"}
        findings = _validate_pointer_schema(meta)
        assert len(findings) == 1

    def test_physical_location_too_short(self):
        meta = {"ubicacion_fisica": "AB"}
        findings = _validate_pointer_schema(meta)
        assert len(findings) == 1
        assert "corta" in findings[0]

    def test_physical_skipped_when_external_present(self):
        """When external URL is present, physical location is not validated for placeholders."""
        meta = {
            "ubicacion_externa_url": "s3://bucket/file.json",
            "ubicacion_fisica": "TBD",
        }
        assert _validate_pointer_schema(meta) == []

    def test_empty_meta(self):
        assert _validate_pointer_schema({}) == []

    def test_none_values(self):
        meta = {"ubicacion_externa_url": None, "ubicacion_fisica": None}
        assert _validate_pointer_schema(meta) == []


# ===================================================================
# P5c — Header isomorphism (_validate_header_isomorphism)
# ===================================================================


_FORMAT_WITH_FILL_SECTION = """---
codigo: "FOR-SGC-99"
titulo: "Test Format"
tipo: "FOR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-01-01"
proceso: "SGC"
elaboro: "Test"
reviso: "Test"
aprobo: "Test"
---

# FOR-SGC-99 Test Format

## 1. Objetivo
Testing.

## 9. Formato de llenado

### Campo A
Instrucciones A.

### Campo B
Instrucciones B.

### Campo C
Instrucciones C.
"""

_FORMAT_WITHOUT_FILL_SECTION = """---
codigo: "FOR-SGC-99"
titulo: "Simple Format"
tipo: "FOR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-01-01"
proceso: "SGC"
elaboro: "Test"
reviso: "Test"
aprobo: "Test"
---

# FOR-SGC-99 Simple Format

## 1. Objetivo
Testing.

## 2. Alcance
All.
"""


class TestValidateHeaderIsomorphism:
    def test_all_headers_present(self):
        record = """# REG Wrapper

## 9. Formato de llenado

### Campo A
Data.

### Campo B
Data.

### Campo C
Data.
"""
        assert _validate_header_isomorphism(_FORMAT_WITH_FILL_SECTION, record) == []

    def test_missing_headers_detected(self):
        record = """# REG Wrapper

## 9. Formato de llenado

### Campo A
Data.
"""
        findings = _validate_header_isomorphism(_FORMAT_WITH_FILL_SECTION, record)
        assert len(findings) == 1
        assert "[P5]" in findings[0]
        assert "2 header(s)" in findings[0]

    def test_all_missing(self):
        record = """# REG Wrapper

## Some unrelated section
Content.
"""
        findings = _validate_header_isomorphism(_FORMAT_WITH_FILL_SECTION, record)
        assert len(findings) == 1
        # 4 headers: "9. formato de llenado" + Campo A/B/C
        assert "4 header(s)" in findings[0]

    def test_format_without_fill_section_uses_all_headers(self):
        """When no 'Formato de llenado' section, falls back to all headers."""
        record = """# Simple Record

## 1. Objetivo
Done.

## 2. Alcance
Done.
"""
        assert _validate_header_isomorphism(_FORMAT_WITHOUT_FILL_SECTION, record) == []

    def test_format_without_fill_section_missing_headers(self):
        record = """# Simple Record

## 1. Objetivo
Done.
"""
        findings = _validate_header_isomorphism(_FORMAT_WITHOUT_FILL_SECTION, record)
        assert len(findings) == 1
        assert "[P5]" in findings[0]

    def test_empty_format_returns_no_findings(self):
        """A format with no extractable headers produces no findings."""
        assert _validate_header_isomorphism("# Just a title\n", "# Record\n") == []

    def test_normalized_heading_comparison(self):
        """Numbered headings like '### 1. Campo A' should match '### Campo A'."""
        record = """# REG Wrapper

## 9. Formato de llenado

### 1. Campo A
Data.

### 2. Campo B
Data.

### 3. Campo C
Data.
"""
        assert _validate_header_isomorphism(_FORMAT_WITH_FILL_SECTION, record) == []


# ===================================================================
# P5 integration in _validate_traceability_for_path
# ===================================================================


def _record_with_url(formato: str, url: str) -> str:
    return f"""---
formato_origen: "{formato}"
codigo_registro: "REG-SGC-NC-2026-001"
fecha_registro: "2026-02-09"
ubicacion_externa_url: "{url}"
---

# REG-SGC-NC-2026-001 (Wrapper)

## 1. Naturaleza
Wrapper de metadatos.
"""


def _record_with_physical(formato: str, ubicacion: str) -> str:
    return f"""---
formato_origen: "{formato}"
codigo_registro: "REG-SGC-NC-2026-001"
fecha_registro: "2026-02-09"
ubicacion_fisica: "{ubicacion}"
---

# REG-SGC-NC-2026-001 (Wrapper)

## 1. Objetivo
Inline record.
"""


class TestP5Integration:
    def test_p5_passes_with_valid_s3_url(self, tmp_path, monkeypatch):
        repo = _setup_repo(tmp_path, monkeypatch)
        _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
        record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
        _write(record_path, _record_with_url("FOR-SGC-02", "s3://bucket/file.json"))

        result = _validate_traceability_for_path(record_path)

        assert result["axiomas"]["P5_isomorfismo_estructural"] is True
        assert not any("[P5]" in f for f in result["hallazgos"])

    def test_p5_fails_with_invalid_scheme(self, tmp_path, monkeypatch):
        repo = _setup_repo(tmp_path, monkeypatch)
        _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
        record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
        _write(record_path, _record_with_url("FOR-SGC-02", "ftp://server/file.pdf"))

        result = _validate_traceability_for_path(record_path)

        assert result["axiomas"]["P5_isomorfismo_estructural"] is False
        assert any("[P5]" in f and "ftp" in f for f in result["hallazgos"])

    def test_p5_passes_with_valid_physical_location(self, tmp_path, monkeypatch):
        repo = _setup_repo(tmp_path, monkeypatch)
        fmt = _format_doc()
        _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", fmt)
        record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
        # Physical record with all format headers present
        record = f"""---
formato_origen: "FOR-SGC-02"
codigo_registro: "REG-SGC-NC-2026-001"
fecha_registro: "2026-02-09"
ubicacion_fisica: "Archivo Central, Caja 42, Gaveta 3"
---

# REG-SGC-NC-2026-001

## 1. Objetivo
Controlar no conformidades.
"""
        _write(record_path, record)

        result = _validate_traceability_for_path(record_path)

        assert result["axiomas"]["P5_isomorfismo_estructural"] is True

    def test_p5_fails_physical_record_missing_headers(self, tmp_path, monkeypatch):
        """Inline record (physical only) must have format headers."""
        repo = _setup_repo(tmp_path, monkeypatch)
        _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
        record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
        record = """---
formato_origen: "FOR-SGC-02"
codigo_registro: "REG-SGC-NC-2026-001"
fecha_registro: "2026-02-09"
ubicacion_fisica: "Archivo Central, Caja 42"
---

# REG-SGC-NC-2026-001

## Seccion completamente diferente
Nada que ver con el formato.
"""
        _write(record_path, record)

        result = _validate_traceability_for_path(record_path)

        assert result["axiomas"]["P5_isomorfismo_estructural"] is False
        assert any("[P5]" in f and "Isomorfismo" in f for f in result["hallazgos"])

    def test_p5_skips_isomorphism_for_external_records(self, tmp_path, monkeypatch):
        """External records (with URL) skip header isomorphism check."""
        repo = _setup_repo(tmp_path, monkeypatch)
        _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
        record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
        # Has external URL but NO matching headers — should still pass
        record = """---
formato_origen: "FOR-SGC-02"
codigo_registro: "REG-SGC-NC-2026-001"
fecha_registro: "2026-02-09"
ubicacion_externa_url: "s3://bucket/record.json"
---

# REG Wrapper

## Naturaleza
Solo metadata.
"""
        _write(record_path, record)

        result = _validate_traceability_for_path(record_path)

        assert result["axiomas"]["P5_isomorfismo_estructural"] is True

    def test_p5_fails_with_no_pointer_at_all(self, tmp_path, monkeypatch):
        repo = _setup_repo(tmp_path, monkeypatch)
        _write(repo / "docs/05_formatos/FOR-SGC-02_Registro.md", _format_doc())
        record_path = repo / "docs/06_registros/no_conformidades/REG-SGC-NC-2026-001.md"
        _write(
            record_path,
            _record_doc("FOR-SGC-02", include_frontmatter=True, include_location_pointer=False),
        )

        result = _validate_traceability_for_path(record_path)

        assert result["axiomas"]["P5_isomorfismo_estructural"] is False
        assert any("[P5]" in f and "no declara" in f for f in result["hallazgos"])
