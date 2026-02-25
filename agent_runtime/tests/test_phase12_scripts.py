from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_watchdog_extract_root_cause_accepts_accent_and_colon(tmp_path):
    watchdog = _load_module(
        "watchdog_nc",
        Path(__file__).resolve().parents[2] / "scripts/watchdog_nc.py",
    )

    markdown = """---
formato_origen: "FOR-SGC-02"
codigo_registro: "REG-SGC-NC-2026-999"
fecha_registro: "2026-02-21"
ubicacion_fisica: "Repo"
---

## 9. Formato de llenado
- Estado: Cerrada
- Causa Raíz: Falta de calibración del sensor.
"""

    assert watchdog.is_nc_closed(markdown) is True
    assert watchdog.extract_root_cause(markdown) == "Falta de calibración del sensor"


def test_watchdog_extract_root_cause_from_section_header(tmp_path):
    watchdog = _load_module(
        "watchdog_nc2",
        Path(__file__).resolve().parents[2] / "scripts/watchdog_nc.py",
    )

    markdown = """# REG-SGC-NC-2026-999

## Causa Raiz (5 porques)
1. Fallo en control.
2. Falta de mantenimiento preventivo.

## Cierre
- Estado: Cerrada
"""

    assert watchdog.extract_root_cause(markdown)


def test_sgc_ask_retrieval_scores_path_and_content(tmp_path):
    sgc_ask = _load_module(
        "sgc_ask",
        Path(__file__).resolve().parents[2] / "scripts/sgc_ask.py",
    )

    docs = [
        {"path": "docs/05_formatos/FOR-SGC-10_Matriz_de_Riesgos_y_Oportunidades.md", "name": "FOR", "content": "Matriz de riesgos"},
        {"path": "docs/03_procedimientos/PR-SGC-06_Gestion_de_Riesgos_y_Oportunidades.md", "name": "PR", "content": "Gestion de riesgos y oportunidades"},
        {"path": "docs/01_politica_objetivos/POL-SGC-01_Politica_de_Calidad.md", "name": "POL", "content": "Politica"},
    ]

    top = sgc_ask.retrieve_relevant_docs("riesgos oportunidades", docs, top_k=2)
    assert len(top) == 2
    assert any("Riesgos" in item["path"] or "riesgos" in item["content"].lower() for item in top)


def test_sgc_ask_load_docs_skips_unreadable_file(tmp_path, capsys):
    sgc_ask = _load_module(
        "sgc_ask2",
        Path(__file__).resolve().parents[2] / "scripts/sgc_ask.py",
    )

    docs_root = tmp_path / "docs"
    docs_root.mkdir()

    (docs_root / "ok.md").write_text("# OK", encoding="utf-8")
    (docs_root / "bad.md").write_bytes(b"\xff\xfe\xff")

    loaded = sgc_ask.load_docs(docs_root)
    assert any(d.name == "ok.md" for d in loaded)
    assert all(d.name != "bad.md" for d in loaded)
