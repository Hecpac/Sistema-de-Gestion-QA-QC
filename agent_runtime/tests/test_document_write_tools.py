"""Tests para tools de escritura de documentos (create, update, from_template)."""
from __future__ import annotations

from pathlib import Path

import yaml
import pytest

from sgc_agents.tools.document_tools import (
    AUDIT_LOG_REL,
    TIPO_DIRECTORY_MAP,
    _bump_minor_version,
    _create_document_from_template_impl,
    _create_document_impl,
    _obsolete_document_impl,
    _promote_document_impl,
    _sanitize_filename,
    _update_document_impl,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_repo(tmp_path: Path) -> Path:
    """Crea estructura minima de repo SGC para tests."""
    root = tmp_path / "repo"
    (root / "docs" / "_control").mkdir(parents=True)
    (root / "docs" / "03_procedimientos").mkdir(parents=True)
    (root / "docs" / "04_instructivos").mkdir(parents=True)
    (root / "docs" / "05_formatos").mkdir(parents=True)
    (root / "docs" / "01_politica_objetivos").mkdir(parents=True)
    (root / "docs" / "02_mapa_procesos").mkdir(parents=True)
    (root / "templates").mkdir(parents=True)

    # Template de procedimiento
    _write(
        root / "templates" / "TEMPLATE_Procedimiento.md",
        """---
codigo: "PR-XXX-00"
titulo: "TITULO"
tipo: "PR"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "YYYY-MM-DD"
proceso: "SGC"
elaboro: "<NOMBRE>"
reviso: "<NOMBRE>"
aprobo: "<NOMBRE>"
---

# TITULO

## 1. Objetivo
TODO: Describir objetivo.

## 2. Alcance
TODO: Definir alcance.

## 3. Referencias
- N/A

## 4. Definiciones
- N/A

## 5. Responsabilidades
TODO: Definir responsables.

## 6. Desarrollo
TODO: Describir metodologia.

## 7. Registros asociados
- N/A

## 8. Control de cambios
| Version | Fecha | Descripcion |
|---------|-------|-------------|
| 1.0 | YYYY-MM-DD | Emision inicial |
""",
    )

    # Template generico (para POL, PLAN, MAN)
    _write(
        root / "templates" / "TEMPLATE_Documento_SGC.md",
        """---
codigo: "XXX-XXX-00"
titulo: "TITULO"
tipo: "POL"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "YYYY-MM-DD"
proceso: "SGC"
elaboro: "<NOMBRE>"
reviso: "<NOMBRE>"
aprobo: "<NOMBRE>"
---

# TITULO

## 1. Objetivo
TODO: Describir objetivo.

## 2. Alcance
TODO: Definir alcance.

## 3. Responsabilidades
TODO: Definir responsables.

## 4. Desarrollo
TODO: Describir contenido.

## 5. Registros asociados
- N/A

## 6. Control de cambios
| Version | Fecha | Descripcion |
|---------|-------|-------------|
| 1.0 | YYYY-MM-DD | Emision inicial |
""",
    )

    return root


def _existing_doc(codigo: str = "PR-SGC-01") -> str:
    return f"""---
codigo: "{codigo}"
titulo: "Control de Documentos"
tipo: "PR"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "2026-02-09"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# {codigo} Control de Documentos

## 1. Objetivo
Controlar documentos del SGC.

## 2. Alcance
Todo el SGC.

## 3. Responsabilidades
Coordinacion de Calidad.

## 4. Desarrollo
Procedimiento base.

## 5. Registros asociados
- N/A

## 6. Control de cambios
| Version | Fecha | Descripcion |
|---------|-------|-------------|
| 1.0 | 2026-02-09 | Emision inicial |
"""


# ---------------------------------------------------------------------------
# Tests unitarios de helpers
# ---------------------------------------------------------------------------


class TestSanitizeFilename:
    def test_strips_accents(self):
        assert _sanitize_filename("Gestión de Nóminas") == "Gestion_de_Nominas"

    def test_replaces_spaces_with_underscores(self):
        assert _sanitize_filename("Control de Documentos") == "Control_de_Documentos"

    def test_removes_special_chars(self):
        result = _sanitize_filename("Plan (v2) — Final!")
        assert "(" not in result
        assert "!" not in result

    def test_empty_string(self):
        assert _sanitize_filename("") == ""


class TestBumpMinorVersion:
    def test_bump_1_0(self):
        assert _bump_minor_version("1.0") == "1.1"

    def test_bump_2_3(self):
        assert _bump_minor_version("2.3") == "2.4"

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            _bump_minor_version("abc")


# ---------------------------------------------------------------------------
# Tests de create_document
# ---------------------------------------------------------------------------


class TestCreateDocument:
    def test_happy_path(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _create_document_impl(
            codigo="PR-SGC-99",
            titulo="Procedimiento de Prueba",
            tipo="PR",
            proceso="SGC / Pruebas",
            elaboro="Tester",
            reviso="Revisor",
            aprobo="Aprobador",
            content_body="# PR-SGC-99\n\n## 1. Objetivo\nProbar creacion.\n",
        )

        assert result.startswith("OK:")
        assert "PR-SGC-99" in result

        # Verify file exists
        expected = root / "docs/03_procedimientos/PR-SGC-99_Procedimiento_de_Prueba.md"
        assert expected.exists()

        # Verify frontmatter
        content = expected.read_text(encoding="utf-8")
        assert "BORRADOR" in content
        assert 'version: "1.0"' in content or "version: '1.0'" in content

        # Verify LMD updated
        lmd = root / "docs/_control/lmd.yml"
        assert lmd.exists()
        lmd_data = yaml.safe_load(lmd.read_text(encoding="utf-8"))
        codigos = [d["codigo"] for d in lmd_data["documentos"]]
        assert "PR-SGC-99" in codigos

    def test_rejects_duplicate_codigo(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        # Pre-create a document
        _write(
            root / "docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md",
            _existing_doc("PR-SGC-01"),
        )

        result = _create_document_impl(
            codigo="PR-SGC-01",
            titulo="Otro Documento",
            tipo="PR",
            proceso="SGC",
            elaboro="Test",
            reviso="Test",
            aprobo="Test",
            content_body="Contenido.",
        )

        assert "ERROR" in result
        assert "duplicado" in result.lower() or "Codigo duplicado" in result

    def test_rejects_invalid_codigo_pattern(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _create_document_impl(
            codigo="bad-code",
            titulo="Test",
            tipo="PR",
            proceso="SGC",
            elaboro="Test",
            reviso="Test",
            aprobo="Test",
            content_body="Test.",
        )

        assert "ERROR" in result

    def test_rejects_tipo_prefix_mismatch(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _create_document_impl(
            codigo="PR-SGC-01",
            titulo="Test",
            tipo="IT",  # mismatch: codigo starts with PR but tipo is IT
            proceso="SGC",
            elaboro="Test",
            reviso="Test",
            aprobo="Test",
            content_body="Test.",
        )

        assert "ERROR" in result

    def test_resolves_correct_directory_per_tipo(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        for tipo, expected_dir in TIPO_DIRECTORY_MAP.items():
            codigo = f"{tipo}-TEST-01"
            result = _create_document_impl(
                codigo=codigo,
                titulo=f"Test {tipo}",
                tipo=tipo,
                proceso="SGC",
                elaboro="Test",
                reviso="Test",
                aprobo="Test",
                content_body=f"Test {tipo}.",
            )
            assert result.startswith("OK:"), f"Fallo para tipo {tipo}: {result}"
            assert expected_dir in result

    def test_filename_strips_accents(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _create_document_impl(
            codigo="PR-SGC-50",
            titulo="Gestión de Nóminas",
            tipo="PR",
            proceso="SGC",
            elaboro="Test",
            reviso="Test",
            aprobo="Test",
            content_body="Test.",
        )

        assert "OK:" in result
        expected = root / "docs/03_procedimientos/PR-SGC-50_Gestion_de_Nominas.md"
        assert expected.exists()


# ---------------------------------------------------------------------------
# Tests de update_document
# ---------------------------------------------------------------------------


class TestUpdateDocument:
    def test_changes_titulo_preserves_rest(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md"
        _write(doc_path, _existing_doc("PR-SGC-01"))

        result = _update_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md",
            titulo="Nuevo Titulo",
        )

        assert "OK:" in result
        content = doc_path.read_text(encoding="utf-8")
        assert "Nuevo Titulo" in content
        assert "PR-SGC-01" in content  # codigo preserved
        assert "Calidad" in content  # elaboro preserved

    def test_body_change_auto_bumps_version(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md"
        _write(doc_path, _existing_doc("PR-SGC-01"))

        result = _update_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md",
            content_body="# Contenido completamente nuevo\n\n## 1. Objetivo\nNuevo.\n",
        )

        assert "OK:" in result
        assert "v1.1" in result  # auto-bumped from 1.0

    def test_explicit_version_overrides_auto_bump(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md"
        _write(doc_path, _existing_doc("PR-SGC-01"))

        result = _update_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md",
            content_body="Nuevo contenido.",
            version="2.0",
        )

        assert "OK:" in result
        assert "v2.0" in result

    def test_rejects_invalid_state(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md"
        _write(doc_path, _existing_doc("PR-SGC-01"))

        result = _update_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md",
            estado="INVALIDO",
        )

        assert "ERROR" in result

    def test_nonexistent_file(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _update_document_impl(
            path="docs/03_procedimientos/NO_EXISTE.md",
            titulo="Test",
        )

        assert "ERROR" in result
        assert "no existe" in result

    def test_path_traversal_blocked(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _update_document_impl(
            path="../../etc/passwd",
            titulo="Hacked",
        )

        assert "ERROR" in result


# ---------------------------------------------------------------------------
# Tests de create_document_from_template
# ---------------------------------------------------------------------------


class TestCreateDocumentFromTemplate:
    def test_uses_procedimiento_template(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _create_document_from_template_impl(
            tipo="PR",
            codigo="PR-SGC-77",
            titulo="Procedimiento Desde Template",
            proceso="SGC / Template",
            elaboro="Tester",
            reviso="Revisor",
            aprobo="Aprobador",
        )

        assert "OK:" in result
        assert "plantilla" in result

        expected = root / "docs/03_procedimientos/PR-SGC-77_Procedimiento_Desde_Template.md"
        assert expected.exists()

        content = expected.read_text(encoding="utf-8")
        # Has section headings from template
        assert "Objetivo" in content
        assert "Alcance" in content
        assert "Control de cambios" in content
        # Frontmatter is real, not placeholder
        assert "PR-SGC-77" in content
        assert "BORRADOR" in content

    def test_replaces_placeholders_in_body(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _create_document_from_template_impl(
            tipo="PR",
            codigo="PR-SGC-88",
            titulo="Mi Procedimiento",
            proceso="SGC / Ops",
            elaboro="Tester",
            reviso="Revisor",
            aprobo="Aprobador",
        )

        assert "OK:" in result

        expected = root / "docs/03_procedimientos/PR-SGC-88_Mi_Procedimiento.md"
        content = expected.read_text(encoding="utf-8")
        # TITULO placeholder replaced
        assert "Mi Procedimiento" in content
        # YYYY-MM-DD placeholder replaced with actual date
        assert "YYYY-MM-DD" not in content

    def test_rejects_duplicate_codigo(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        _write(
            root / "docs/03_procedimientos/PR-SGC-01_Existente.md",
            _existing_doc("PR-SGC-01"),
        )

        result = _create_document_from_template_impl(
            tipo="PR",
            codigo="PR-SGC-01",
            titulo="Duplicado",
            proceso="SGC",
            elaboro="Test",
            reviso="Test",
            aprobo="Test",
        )

        assert "ERROR" in result


# ---------------------------------------------------------------------------
# Helpers for promote/obsolete tests
# ---------------------------------------------------------------------------


def _promotable_doc(codigo: str = "PR-SGC-01") -> str:
    """Documento BORRADOR completo, listo para promover (sin TODO/TBD/placeholders)."""
    return f"""---
codigo: "{codigo}"
titulo: "Control de Documentos"
tipo: "PR"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "2026-02-09"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# {codigo} Control de Documentos

## 1. Objetivo
Controlar documentos del SGC.

## 2. Alcance
Todo el SGC.

## 3. Referencias
- ISO 9001:2015

## 4. Definiciones
- SGC: Sistema de Gestion de Calidad

## 5. Responsabilidades
Coordinacion de Calidad.

## 6. Desarrollo
Procedimiento base completo.

## 7. Registros asociados
- N/A

## 8. Control de cambios
| Version | Fecha | Descripcion |
|---------|-------|-------------|
| 1.0 | 2026-02-09 | Emision inicial |
"""


def _vigente_doc(codigo: str = "PR-SGC-01") -> str:
    """Documento VIGENTE."""
    return f"""---
codigo: "{codigo}"
titulo: "Control de Documentos"
tipo: "PR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# {codigo} Control de Documentos

## 1. Objetivo
Controlar documentos del SGC.

## 2. Alcance
Todo el SGC.

## 3. Responsabilidades
Coordinacion de Calidad.

## 4. Desarrollo
Procedimiento base.

## 5. Registros asociados
- REG-SGC-001

## 6. Control de cambios
| Version | Fecha | Descripcion |
|---------|-------|-------------|
| 1.0 | 2026-02-09 | Emision inicial |
"""


# ---------------------------------------------------------------------------
# Tests de promote_document
# ---------------------------------------------------------------------------


class TestPromoteDocument:
    def test_happy_path(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md"
        _write(doc_path, _promotable_doc("PR-SGC-01"))

        result = _promote_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control_de_Documentos.md",
        )

        assert "OK:" in result
        assert "VIGENTE" in result

        content = doc_path.read_text(encoding="utf-8")
        assert 'estado: "VIGENTE"' in content or "estado: VIGENTE" in content

    def test_rejects_non_borrador(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control.md"
        _write(doc_path, _vigente_doc("PR-SGC-01"))

        result = _promote_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control.md",
        )

        assert "ERROR" in result
        assert "BORRADOR" in result

    def test_rejects_placeholders(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_with_placeholder = _promotable_doc("PR-SGC-02").replace(
            "Coordinacion de Calidad.", "<NOMBRE DEL RESPONSABLE>"
        )
        doc_path = root / "docs/03_procedimientos/PR-SGC-02_Test.md"
        _write(doc_path, doc_with_placeholder)

        result = _promote_document_impl(
            path="docs/03_procedimientos/PR-SGC-02_Test.md",
        )

        assert "ERROR" in result
        assert "placeholder" in result.lower()

    def test_rejects_todo(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_with_todo = _promotable_doc("PR-SGC-03").replace(
            "Procedimiento base completo.", "TODO: Completar procedimiento."
        )
        doc_path = root / "docs/03_procedimientos/PR-SGC-03_Test.md"
        _write(doc_path, doc_with_todo)

        result = _promote_document_impl(
            path="docs/03_procedimientos/PR-SGC-03_Test.md",
        )

        assert "ERROR" in result
        assert "TODO" in result

    def test_rejects_tbd_in_frontmatter(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_with_tbd = _promotable_doc("PR-SGC-04").replace(
            'elaboro: "Calidad"', 'elaboro: "TBD"'
        )
        doc_path = root / "docs/03_procedimientos/PR-SGC-04_Test.md"
        _write(doc_path, doc_with_tbd)

        result = _promote_document_impl(
            path="docs/03_procedimientos/PR-SGC-04_Test.md",
        )

        assert "ERROR" in result
        assert "TBD" in result

    def test_nonexistent_file(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _promote_document_impl(
            path="docs/03_procedimientos/NO_EXISTE.md",
        )

        assert "ERROR" in result
        assert "no existe" in result

    def test_path_traversal_blocked(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _promote_document_impl(path="../../etc/passwd")

        assert "ERROR" in result


# ---------------------------------------------------------------------------
# Tests de obsolete_document
# ---------------------------------------------------------------------------


class TestObsoleteDocument:
    def test_happy_path_with_motivo(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control.md"
        _write(doc_path, _vigente_doc("PR-SGC-01"))

        result = _obsolete_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control.md",
            motivo="Reemplazado por PR-SGC-02",
        )

        assert "OK:" in result
        assert "OBSOLETO" in result

        content = doc_path.read_text(encoding="utf-8")
        assert "OBSOLETO" in content
        assert "Reemplazado por PR-SGC-02" in content

    def test_happy_path_without_motivo(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control.md"
        _write(doc_path, _vigente_doc("PR-SGC-01"))

        result = _obsolete_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control.md",
        )

        assert "OK:" in result
        assert "OBSOLETO" in result

    def test_rejects_non_vigente(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        doc_path = root / "docs/03_procedimientos/PR-SGC-01_Control.md"
        _write(doc_path, _existing_doc("PR-SGC-01"))  # BORRADOR

        result = _obsolete_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Control.md",
            motivo="Test",
        )

        assert "ERROR" in result
        assert "VIGENTE" in result

    def test_nonexistent_file(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        result = _obsolete_document_impl(
            path="docs/03_procedimientos/NO_EXISTE.md",
        )

        assert "ERROR" in result
        assert "no existe" in result


# ---------------------------------------------------------------------------
# Tests de audit trail
# ---------------------------------------------------------------------------


class TestAuditTrail:
    def test_create_generates_audit_event(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        _create_document_impl(
            codigo="PR-SGC-99", titulo="Audit Test", tipo="PR",
            proceso="SGC", elaboro="T", reviso="T", aprobo="T",
            content_body="# PR-SGC-99\n\n## 1. Objetivo\nTest.\n",
        )

        log = root / AUDIT_LOG_REL
        assert log.exists()
        data = yaml.safe_load(log.read_text(encoding="utf-8"))
        assert len(data["eventos"]) == 1
        assert data["eventos"][0]["evento"] == "creacion"
        assert data["eventos"][0]["codigo"] == "PR-SGC-99"

    def test_update_generates_audit_event(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        _write(
            root / "docs/03_procedimientos/PR-SGC-01_Doc.md",
            _existing_doc("PR-SGC-01"),
        )

        _update_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Doc.md",
            titulo="Titulo Nuevo",
        )

        log = root / AUDIT_LOG_REL
        assert log.exists()
        data = yaml.safe_load(log.read_text(encoding="utf-8"))
        assert data["eventos"][0]["evento"] == "actualizacion"
        assert "titulo" in data["eventos"][0]["campos_modificados"]

    def test_promote_generates_audit_event(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        _write(
            root / "docs/03_procedimientos/PR-SGC-01_Doc.md",
            _promotable_doc("PR-SGC-01"),
        )

        _promote_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Doc.md",
        )

        log = root / AUDIT_LOG_REL
        assert log.exists()
        data = yaml.safe_load(log.read_text(encoding="utf-8"))
        assert data["eventos"][0]["evento"] == "promocion"
        assert data["eventos"][0]["a"] == "VIGENTE"

    def test_obsolete_generates_audit_event(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        _write(
            root / "docs/03_procedimientos/PR-SGC-01_Doc.md",
            _vigente_doc("PR-SGC-01"),
        )

        _obsolete_document_impl(
            path="docs/03_procedimientos/PR-SGC-01_Doc.md",
            motivo="Reemplazado",
        )

        log = root / AUDIT_LOG_REL
        assert log.exists()
        data = yaml.safe_load(log.read_text(encoding="utf-8"))
        assert data["eventos"][0]["evento"] == "obsolescencia"
        assert data["eventos"][0]["motivo"] == "Reemplazado"

    def test_multiple_ops_append_events(self, tmp_path, monkeypatch):
        root = _make_repo(tmp_path)
        monkeypatch.setenv("SGC_REPO_ROOT", str(root))

        _create_document_impl(
            codigo="PR-SGC-40", titulo="Multi Test", tipo="PR",
            proceso="SGC", elaboro="T", reviso="T", aprobo="T",
            content_body="# PR-SGC-40\n\n## 1. Objetivo\nTest.\n",
        )
        _update_document_impl(
            path="docs/03_procedimientos/PR-SGC-40_Multi_Test.md",
            titulo="Multi Test v2",
        )

        log = root / AUDIT_LOG_REL
        data = yaml.safe_load(log.read_text(encoding="utf-8"))
        assert len(data["eventos"]) == 2
        assert data["eventos"][0]["evento"] == "creacion"
        assert data["eventos"][1]["evento"] == "actualizacion"
