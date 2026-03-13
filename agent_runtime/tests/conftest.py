"""Shared test fixtures for SGC agent runtime tests."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def sgc_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a minimal SGC repo structure and set SGC_REPO_ROOT."""
    monkeypatch.setenv("SGC_REPO_ROOT", str(tmp_path))

    # Core directories
    for d in [
        "docs/_control",
        "docs/01_politica_objetivos",
        "docs/02_manual_calidad",
        "docs/03_procedimientos",
        "docs/04_instructivos",
        "docs/05_formatos",
        "docs/06_registros",
        "docs/07_documentos_externos",
    ]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)

    # Empty control artifacts
    (tmp_path / "docs/_control/lmd.yml").write_text(
        yaml.dump({"documentos": []}, allow_unicode=True), encoding="utf-8"
    )
    (tmp_path / "docs/_control/matriz_registros.yml").write_text(
        yaml.dump({"registros": []}, allow_unicode=True), encoding="utf-8"
    )

    return tmp_path


def write_doc(path: Path, content: str) -> None:
    """Helper to write a file, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


MINIMAL_DOC = """\
---
codigo: "{code}"
titulo: "{title}"
tipo: "{tipo}"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-01-01"
proceso: "SGC"
elaboro: "Calidad"
reviso: "Gerencia"
aprobo: "Direccion"
---

# {code} {title}

## 1. Objetivo
Placeholder.
"""
