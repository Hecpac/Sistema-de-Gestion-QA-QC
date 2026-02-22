from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

import yaml

try:
    from agents import function_tool
except Exception:  # pragma: no cover
    def function_tool(fn):
        return fn

from pydantic import ValidationError

from ..config import repo_root
from ..schemas import DOC_CODE_PATTERN, DocumentFrontmatter
from .build_indexes import build_indexes, extract_frontmatter
from .compliance_tools import compliance_tools


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@function_tool
def list_controlled_docs() -> str:
    """Lista documentos controlados existentes en la LMD autogenerada."""
    lmd = repo_root() / "docs/_control/lmd.yml"
    if not lmd.exists():
        return "No existe docs/_control/lmd.yml"

    data = yaml.safe_load(_read(lmd)) or {}
    docs = data.get("documentos", [])
    if not docs:
        return "Sin documentos en LMD."

    lines = [
        f"{d.get('codigo','?')} | {d.get('estado','?')} | {d.get('version','?')} | {d.get('ubicacion','?')}"
        for d in docs
        if isinstance(d, dict)
    ]
    return "\n".join(lines) if lines else "Sin documentos en LMD."


@function_tool
def read_document(path: str) -> str:
    """Lee un documento del repositorio SGC por ruta relativa."""
    abs_path = (repo_root() / path).resolve()
    root = repo_root().resolve()
    if root not in abs_path.parents and abs_path != root:
        raise ValueError("Ruta fuera del repositorio.")
    if not abs_path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    return _read(abs_path)


@function_tool
def rebuild_control_indexes() -> str:
    """Regenera LMD y matriz de registros desde frontmatter y referencias REG-*."""
    summary = build_indexes(repo_root())
    return f"OK: {summary.as_text()}"


@function_tool
def validate_frontmatter(path: str) -> str:
    """Valida frontmatter YAML de un documento controlado con esquema estricto."""
    content = read_document(path)
    data = extract_frontmatter(content)
    if data is None:
        return "ERROR: no se encontro frontmatter YAML."

    try:
        parsed = DocumentFrontmatter.model_validate(data)
    except ValidationError as exc:
        return f"ERROR: frontmatter invalido: {exc}"

    return f"OK: {parsed.codigo} ({parsed.tipo}) v{parsed.version}"


@function_tool
def validate_doc_filename(path: str, codigo: str) -> str:
    """Valida que el archivo comience por el codigo documental."""
    p = Path(path)
    ok = p.name.startswith(codigo)
    return "OK" if ok else f"ERROR: {p.name} no inicia con {codigo}"


def _validate_required_sections_impl(path: str) -> str:
    abs_path = (repo_root() / path).resolve()
    root = repo_root().resolve()
    if root not in abs_path.parents and abs_path != root:
        raise ValueError("Ruta fuera del repositorio.")
    if not abs_path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    content = _read(abs_path).lower()
    required = [
        "objetivo",
        "alcance",
        "responsabilidades",
        "desarrollo",
        "registros asociados",
        "control de cambios",
    ]
    missing = [r for r in required if r not in content]
    if missing:
        return "Faltan secciones: " + ", ".join(missing)
    return "OK"


validate_required_sections_impl = _validate_required_sections_impl


@function_tool
def validate_required_sections(path: str) -> str:
    """Valida secciones minimas requeridas en un documento controlado."""
    return _validate_required_sections_impl(path)


@function_tool
def list_missing_record_dirs() -> str:
    """Detecta ubicaciones de registros declaradas que no existen."""
    m_path = repo_root() / "docs/_control/matriz_registros.yml"
    if not m_path.exists():
        return "No existe docs/_control/matriz_registros.yml"

    data = yaml.safe_load(_read(m_path)) or {}
    registros = data.get("registros", [])
    missing: list[str] = []
    for reg in registros:
        if not isinstance(reg, dict):
            continue
        rel_path = str(reg.get("ubicacion", "")).strip()
        if not rel_path:
            continue
        abs_dir = (repo_root() / rel_path).resolve()
        if not abs_dir.exists():
            missing.append(rel_path)
    return "\n".join(sorted(set(missing))) if missing else "OK"


@function_tool
def validate_code_pattern(codigo: str) -> str:
    """Valida patron [TIPO]-[PROCESO]-[NNN]."""
    if DOC_CODE_PATTERN.match(codigo):
        return "OK"
    return "ERROR: patron invalido"


def _skill_description(skill_file: Path) -> str:
    content = _read(skill_file)
    if not content.startswith("---\n"):
        return "(sin descripcion)"

    end = content.find("\n---\n", 4)
    if end == -1:
        return "(sin descripcion)"

    front = yaml.safe_load(content[4:end]) or {}
    if not isinstance(front, dict):
        return "(sin descripcion)"
    return str(front.get("description", "(sin descripcion)"))


@function_tool
def list_available_project_skills() -> str:
    """Lista skills disponibles en .agents/skills (registro dinamico)."""
    skills_root = repo_root() / ".agents/skills"
    if not skills_root.exists():
        return "No existe carpeta .agents/skills"

    lines: list[str] = []
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        name = skill_file.parent.name
        lines.append(f"{name} | {_skill_description(skill_file)}")

    return "\n".join(lines) if lines else "No hay skills locales."


@function_tool
def read_project_skill(skill_name: str) -> str:
    """Lee el contenido de una skill local por nombre (carpeta en .agents/skills)."""
    normalized = re.sub(r"[^a-zA-Z0-9_-]", "", skill_name)
    if not normalized:
        raise ValueError("Nombre de skill invalido")

    skill_file = repo_root() / ".agents/skills" / normalized / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"No existe skill: {skill_name}")
    return _read(skill_file)


def all_tools() -> Iterable:
    base = [
        list_controlled_docs,
        read_document,
        rebuild_control_indexes,
        validate_frontmatter,
        validate_doc_filename,
        validate_required_sections,
        list_missing_record_dirs,
        validate_code_pattern,
        list_available_project_skills,
        read_project_skill,
    ]
    return base + compliance_tools()


def writer_tools() -> list[Any]:
    """Toolset seguro para redaccion: lectura y validacion sin mutar artefactos generados."""
    return [
        list_controlled_docs,
        read_document,
        validate_frontmatter,
        validate_doc_filename,
        validate_required_sections,
        list_missing_record_dirs,
        validate_code_pattern,
        list_available_project_skills,
        read_project_skill,
    ]
