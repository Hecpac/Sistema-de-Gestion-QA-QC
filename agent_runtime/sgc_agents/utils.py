"""Common utility functions for sgc_agents."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def read(path: Path) -> str:
    """Read text file with UTF-8 encoding."""
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    """Write text file with UTF-8 encoding, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def is_pending_value(value: Any) -> bool:
    """Check if value is pending (empty, TODO, TBD, or <DEFINIR>)."""
    text = str(value or "").strip().upper()
    if not text:
        return True
    return "TODO" in text or "TBD" in text or "<DEFINIR>" in text


def assert_within_repo(abs_path: Path, root: Path) -> None:
    """Verifica que la ruta resuelta esté dentro del repositorio."""
    resolved = abs_path.resolve()
    resolved_root = root.resolve()
    if resolved_root not in resolved.parents and resolved != resolved_root:
        raise ValueError("Ruta fuera del repositorio.")
