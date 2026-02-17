from __future__ import annotations

from pathlib import Path

import pytest

from sgc_agents.schemas import DocumentFrontmatter, RecordFrontmatter
from sgc_agents.tools.build_indexes import build_indexes


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_document_frontmatter_forbids_unknown_keys() -> None:
    with pytest.raises(Exception):
        DocumentFrontmatter.model_validate(
            {
                "codigo": "PR-SGC-01",
                "titulo": "Control",
                "tipo": "PR",
                "version": "1.0",
                "estado": "VIGENTE",
                "fecha_emision": "2026-02-17",
                "proceso": "SGC",
                "elaboro": "Calidad",
                "reviso": "Gerencia",
                "aprobo": "Direccion",
                "campo_no_permitido": "boom",
            }
        )


def test_record_frontmatter_requires_external_or_physical_pointer() -> None:
    with pytest.raises(Exception):
        RecordFrontmatter.model_validate(
            {
                "formato_origen": "FOR-SGC-02",
                "codigo_registro": "REG-SGC-NC-2026-001",
                "fecha_registro": "2026-02-17",
            }
        )


def test_build_indexes_fails_when_vigente_doc_has_pending_retention_policy(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("SGC_REPO_ROOT", str(tmp_path))

    for_doc = """---
codigo: "FOR-SGC-02"
titulo: "Formato NC"
tipo: "FOR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# FOR-SGC-02

## 1. Objetivo
Control de NC.
"""

    pr_doc = """---
codigo: "PR-SGC-99"
titulo: "Proceso Critico"
tipo: "PR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-17"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# PR-SGC-99

## 7. Registros asociados
- REG-SGC-NC - Registro de no conformidad.
"""

    _write(tmp_path / "docs/05_formatos/FOR-SGC-02_Formato.md", for_doc)
    _write(tmp_path / "docs/03_procedimientos/PR-SGC-99_Proceso.md", pr_doc)

    with pytest.raises(ValueError, match="Politica de retencion incompleta"):
        build_indexes(tmp_path)
