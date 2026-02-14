from __future__ import annotations

from pathlib import Path

import yaml

from sgc_agents.tools.build_indexes import build_indexes
from sgc_agents.tools.compliance_tools import auditar_invariantes_de_estado


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_lowercase_todo_word_is_not_flagged_as_placeholder(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SGC_REPO_ROOT", str(tmp_path))

    doc = """---
codigo: "PR-SGC-90"
titulo: "Prueba de Invariantes"
tipo: "PR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-14"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# PR-SGC-90 Prueba de Invariantes

## 1. Objetivo
Garantizar que todo el personal use la version vigente.
"""

    _write(tmp_path / "docs/03_procedimientos/PR-SGC-90_Prueba.md", doc)

    payload = yaml.safe_load(auditar_invariantes_de_estado())

    assert payload["valido"] is True
    assert payload["hallazgos"] == []


def test_matrix_hint_maps_reg_sgc_com_to_for_sgc_01(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SGC_REPO_ROOT", str(tmp_path))

    for_doc = """---
codigo: "FOR-SGC-01"
titulo: "Solicitud de Cambio"
tipo: "FOR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# FOR-SGC-01 Solicitud de Cambio

## 1. Objetivo
Control documental.
"""

    pr_doc = """---
codigo: "PR-SGC-91"
titulo: "Control de Comunicacion"
tipo: "PR"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "2026-02-14"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# PR-SGC-91 Control de Comunicacion

## 7. Registros asociados
- REG-SGC-COM - Evidencia de distribucion/comunicacion de documentos.
"""

    _write(tmp_path / "docs/_control/FOR-SGC-01_Solicitud.md", for_doc)
    _write(tmp_path / "docs/03_procedimientos/PR-SGC-91_Control.md", pr_doc)

    build_indexes(tmp_path)

    matrix = yaml.safe_load(
        (tmp_path / "docs/_control/matriz_registros.yml").read_text(encoding="utf-8")
    )
    row = next(item for item in matrix["registros"] if item["codigo"] == "REG-SGC-COM")

    assert row["codigo_formato"] == "FOR-SGC-01"
