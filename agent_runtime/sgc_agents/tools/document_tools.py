from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

import yaml

try:
    from agents import function_tool
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    def function_tool(fn):
        return fn

from pydantic import ValidationError

from ..config import repo_root
from ..schemas import DOC_CODE_PATTERN, DocumentFrontmatter
from ..utils import read, write, assert_within_repo
from .build_indexes import (
    build_indexes,
    discover_controlled_documents,
    extract_frontmatter,
    split_frontmatter_and_body,
)
from .compliance_tools import compliance_tools

# ---------------------------------------------------------------------------
# Constantes: mapeo tipo -> directorio y tipo -> plantilla
# ---------------------------------------------------------------------------

TIPO_DIRECTORY_MAP: dict[str, str] = {
    "POL": "docs/01_politica_objetivos",
    "ESP": "docs/02_mapa_procesos",
    "PR": "docs/03_procedimientos",
    "IT": "docs/04_instructivos",
    "FOR": "docs/05_formatos",
    "PLAN": "docs/03_procedimientos",
    "MAN": "docs/03_procedimientos",
}

TIPO_TEMPLATE_MAP: dict[str, str] = {
    "PR": "TEMPLATE_Procedimiento.md",
    "IT": "TEMPLATE_Instructivo.md",
    "FOR": "TEMPLATE_Formato.md",
    "ESP": "TEMPLATE_Ficha_de_Proceso.md",
    "POL": "TEMPLATE_Documento_SGC.md",
    "PLAN": "TEMPLATE_Documento_SGC.md",
    "MAN": "TEMPLATE_Documento_SGC.md",
}

# ---------------------------------------------------------------------------
# Helpers internos para escritura
# ---------------------------------------------------------------------------


# _read and _write are now imported from utils module


def _sanitize_filename(titulo: str) -> str:
    """Convierte titulo a nombre de archivo sin acentos: Titulo_Sin_Acentos."""
    nfkd = unicodedata.normalize("NFKD", titulo)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    cleaned = re.sub(r"[^\w\s-]", "", ascii_text).strip()
    cleaned = re.sub(r"[\s]+", "_", cleaned)
    return cleaned


def _resolve_target_path(root: Path, tipo: str, codigo: str, titulo: str) -> Path:
    """Resuelve la ruta destino para un documento nuevo segun su tipo."""
    directory = TIPO_DIRECTORY_MAP.get(tipo)
    if directory is None:
        raise ValueError(f"Tipo de documento no soportado: {tipo}")
    filename = f"{codigo}_{_sanitize_filename(titulo)}.md"
    return root / directory / filename


def _check_no_duplicate_codigo(root: Path, codigo: str) -> None:
    """Verifica que el codigo no exista ya en documentos controlados."""
    try:
        docs = discover_controlled_documents(root.resolve())
    except (FileNotFoundError, ValueError):
        return
    for doc in docs:
        if doc.frontmatter.codigo == codigo:
            raise ValueError(
                f"Codigo duplicado: {codigo} ya existe en {doc.relative_path}"
            )


# _assert_within_repo is now imported from utils module as assert_within_repo


def _render_document(frontmatter: dict[str, Any], body: str) -> str:
    """Renderiza un documento completo con frontmatter YAML y cuerpo Markdown."""
    fm_text = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).rstrip("\n")
    return f"---\n{fm_text}\n---\n\n{body}"


def _bump_minor_version(version: str) -> str:
    """Incrementa la version menor: 1.0 -> 1.1, 2.3 -> 2.4."""
    parts = version.split(".")
    if len(parts) != 2:
        raise ValueError(f"Formato de version invalido: {version}")
    major, minor = int(parts[0]), int(parts[1])
    return f"{major}.{minor + 1}"


AUDIT_LOG_REL = "docs/_control/audit_changelog.yml"
_AUDIT_HEADER = (
    "# Audit changelog — generado automaticamente\n"
    "# Fuente: sgc_agents/tools/document_tools.py\n"
    "# No editar manualmente\n\n"
)


def _append_audit_event(root: Path, event: dict[str, Any]) -> None:
    """Append un evento de auditoria al changelog YAML."""
    event["timestamp"] = datetime.now().isoformat(timespec="seconds")
    log_path = root / AUDIT_LOG_REL
    if log_path.exists():
        data = yaml.safe_load(log_path.read_text(encoding="utf-8")) or {}
    else:
        data = {}
    eventos = data.get("eventos", [])
    eventos.append(event)
    data["eventos"] = eventos
    content = _AUDIT_HEADER + yaml.safe_dump(
        data, sort_keys=False, allow_unicode=True, default_flow_style=False
    )
    write(log_path, content)


@function_tool
def list_controlled_docs() -> str:
    """Lista documentos controlados existentes en la LMD autogenerada."""
    lmd = repo_root() / "docs/_control/lmd.yml"
    if not lmd.exists():
        return "No existe docs/_control/lmd.yml"

    data = yaml.safe_load(read(lmd)) or {}
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
    return read(abs_path)


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
    content = read(abs_path).lower()
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

    data = yaml.safe_load(read(m_path)) or {}
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
    content = read(skill_file)
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
    return read(skill_file)


# ---------------------------------------------------------------------------
# Tools de escritura — implementaciones (testables sin @function_tool)
# ---------------------------------------------------------------------------


def _create_document_impl(
    codigo: str,
    titulo: str,
    tipo: str,
    proceso: str,
    elaboro: str,
    reviso: str,
    aprobo: str,
    content_body: str,
) -> str:
    """Crea un nuevo documento controlado del SGC con frontmatter valido y cuerpo Markdown."""
    root = repo_root()

    # 1. Build and validate frontmatter
    today = date.today().isoformat()
    fm_data: dict[str, Any] = {
        "codigo": codigo,
        "titulo": titulo,
        "tipo": tipo,
        "version": "1.0",
        "estado": "BORRADOR",
        "fecha_emision": today,
        "proceso": proceso,
        "elaboro": elaboro,
        "reviso": reviso,
        "aprobo": aprobo,
    }

    try:
        parsed = DocumentFrontmatter.model_validate(fm_data)
    except ValidationError as exc:
        return f"ERROR: frontmatter invalido: {exc}"

    # 2. Check no duplicate
    try:
        _check_no_duplicate_codigo(root, codigo)
    except ValueError as exc:
        return f"ERROR: {exc}"

    # 3. Resolve path
    try:
        target = _resolve_target_path(root, tipo, codigo, titulo)
    except ValueError as exc:
        return f"ERROR: {exc}"

    # 4. Security: assert within repo
    try:
        assert_within_repo(target, root)
    except ValueError as exc:
        return f"ERROR: {exc}"

    # 5. Check file doesn't already exist
    if target.exists():
        return f"ERROR: ya existe archivo en {target.relative_to(root)}"

    # 6. Render and write
    content = _render_document(fm_data, content_body)
    write(target, content)

    # 6b. Audit trail
    try:
        _append_audit_event(root, {
            "evento": "creacion",
            "codigo": codigo,
            "titulo": titulo,
            "tipo": tipo,
            "path": str(target.relative_to(root)),
            "version": "1.0",
            "estado": "BORRADOR",
            "elaboro": elaboro,
            "reviso": reviso,
            "aprobo": aprobo,
        })
    except (OSError, IOError, ValueError):
        pass  # audit log failure must not block document creation

    # 7. Rebuild indexes
    try:
        summary = build_indexes(root)
    except (OSError, ValueError, RuntimeError) as exc:
        return (
            f"ADVERTENCIA: documento creado en {target.relative_to(root)} "
            f"pero fallo la reconstruccion de indices: {exc}"
        )

    rel = target.relative_to(root)
    return (
        f"OK: documento creado en {rel} "
        f"({parsed.codigo} v{parsed.version} {parsed.estado}). "
        f"Indices: {summary.as_text()}"
    )


def _update_document_impl(
    path: str,
    titulo: str = "",
    content_body: str = "",
    proceso: str = "",
    elaboro: str = "",
    reviso: str = "",
    aprobo: str = "",
    estado: str = "",
    version: str = "",
    fecha_emision: str = "",
) -> str:
    """Actualiza un documento controlado existente (cuerpo y/o campos de frontmatter)."""
    root = repo_root()
    abs_path = (root / path).resolve()

    # 1. Security check
    try:
        assert_within_repo(abs_path, root)
    except ValueError as exc:
        return f"ERROR: {exc}"

    if not abs_path.exists():
        return f"ERROR: no existe: {path}"

    # 2. Read existing content
    existing_content = read(abs_path)
    existing_fm, existing_body = split_frontmatter_and_body(existing_content)

    if existing_fm is None:
        return "ERROR: el documento no tiene frontmatter YAML valido."

    # 3. Merge updates
    updated_fm = dict(existing_fm)

    field_updates = {
        "titulo": titulo,
        "proceso": proceso,
        "elaboro": elaboro,
        "reviso": reviso,
        "aprobo": aprobo,
        "estado": estado,
        "version": version,
        "fecha_emision": fecha_emision,
    }
    for key, value in field_updates.items():
        if value:
            updated_fm[key] = value

    # 4. Determine body
    new_body = content_body if content_body else existing_body

    # 5. Auto-bump version if body changed and no explicit version
    if content_body and not version:
        try:
            updated_fm["version"] = _bump_minor_version(str(updated_fm.get("version", "1.0")))
        except (ValueError, KeyError):
            pass

    # 6. Validate merged frontmatter
    try:
        parsed = DocumentFrontmatter.model_validate(updated_fm)
    except ValidationError as exc:
        return f"ERROR: frontmatter invalido despues de merge: {exc}"

    # 7. Render and write
    content = _render_document(updated_fm, new_body)
    write(abs_path, content)

    # 7b. Audit trail
    try:
        campos_mod = [k for k, v in field_updates.items() if v]
        if content_body:
            campos_mod.append("content_body")
        _append_audit_event(root, {
            "evento": "actualizacion",
            "codigo": str(updated_fm.get("codigo", "")),
            "path": path,
            "version_anterior": str(existing_fm.get("version", "")),
            "version_nueva": str(updated_fm.get("version", "")),
            "campos_modificados": campos_mod,
        })
    except (OSError, IOError, ValueError):
        pass

    # 8. Rebuild indexes
    try:
        summary = build_indexes(root)
    except (OSError, ValueError, RuntimeError) as exc:
        return (
            f"ADVERTENCIA: documento actualizado en {path} "
            f"pero fallo la reconstruccion de indices: {exc}"
        )

    return (
        f"OK: documento actualizado en {path} "
        f"({parsed.codigo} v{parsed.version} {parsed.estado}). "
        f"Indices: {summary.as_text()}"
    )


def _create_document_from_template_impl(
    tipo: str,
    codigo: str,
    titulo: str,
    proceso: str,
    elaboro: str,
    reviso: str,
    aprobo: str,
) -> str:
    """Crea un nuevo documento pre-llenado desde la plantilla correspondiente al tipo."""
    root = repo_root()
    today = date.today().isoformat()

    # 1. Find template
    template_file_name = TIPO_TEMPLATE_MAP.get(tipo)
    if template_file_name is None:
        return f"ERROR: no hay plantilla para tipo: {tipo}"

    template_path = root / "templates" / template_file_name
    if not template_path.exists():
        return f"ERROR: plantilla no encontrada: {template_file_name}"

    # 2. Read template
    template_content = read(template_path)
    _, template_body = split_frontmatter_and_body(template_content)

    # 3. Build frontmatter
    fm_data: dict[str, Any] = {
        "codigo": codigo,
        "titulo": titulo,
        "tipo": tipo,
        "version": "1.0",
        "estado": "BORRADOR",
        "fecha_emision": today,
        "proceso": proceso,
        "elaboro": elaboro,
        "reviso": reviso,
        "aprobo": aprobo,
    }

    try:
        parsed = DocumentFrontmatter.model_validate(fm_data)
    except ValidationError as exc:
        return f"ERROR: frontmatter invalido: {exc}"

    # 4. Check no duplicate
    try:
        _check_no_duplicate_codigo(root, codigo)
    except ValueError as exc:
        return f"ERROR: {exc}"

    # 5. Resolve path
    try:
        target = _resolve_target_path(root, tipo, codigo, titulo)
    except ValueError as exc:
        return f"ERROR: {exc}"

    # 6. Security
    try:
        assert_within_repo(target, root)
    except ValueError as exc:
        return f"ERROR: {exc}"

    if target.exists():
        return f"ERROR: ya existe archivo en {target.relative_to(root)}"

    # 7. Replace placeholders in template body
    body = template_body
    body = body.replace("<Nombre>", titulo)
    body = body.replace("<Nombre del proceso>", proceso)
    body = body.replace("TITULO", titulo)
    body = body.replace("YYYY-MM-DD", today)

    # 8. Render and write
    content = _render_document(fm_data, body)
    write(target, content)

    # 9. Rebuild indexes
    try:
        summary = build_indexes(root)
    except (OSError, ValueError, RuntimeError) as exc:
        return (
            f"ADVERTENCIA: documento creado en {target.relative_to(root)} "
            f"pero fallo la reconstruccion de indices: {exc}"
        )

    rel = target.relative_to(root)
    return (
        f"OK: documento creado desde plantilla en {rel} "
        f"({parsed.codigo} v{parsed.version} {parsed.estado}). "
        f"Indices: {summary.as_text()}"
    )


PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
TODO_RE = re.compile(r"\bTODO\b")


def _promote_document_impl(path: str) -> str:
    """Promueve un documento de BORRADOR a VIGENTE con gates de validacion.

    Gates requeridos:
    - Estado actual debe ser BORRADOR
    - Sin placeholders (<...>) en el cuerpo
    - Sin TODO en el cuerpo
    - Sin TBD en campos de frontmatter (excepto fecha_vigencia)
    - Secciones minimas presentes
    - Frontmatter valido
    """
    root = repo_root()
    abs_path = (root / path).resolve()

    try:
        assert_within_repo(abs_path, root)
    except ValueError as exc:
        return f"ERROR: {exc}"

    if not abs_path.exists():
        return f"ERROR: no existe: {path}"

    content = read(abs_path)
    existing_fm, body = split_frontmatter_and_body(content)

    if existing_fm is None:
        return "ERROR: el documento no tiene frontmatter YAML valido."

    # Gate 1: Must be BORRADOR
    estado_actual = str(existing_fm.get("estado", "")).strip()
    if estado_actual != "BORRADOR":
        return f"ERROR: solo se puede promover documentos en BORRADOR (actual: {estado_actual})"

    # Gate 2: No placeholders in body
    placeholders = PLACEHOLDER_RE.findall(body)
    if placeholders:
        return f"ERROR: el documento contiene placeholders que deben resolverse: {', '.join(placeholders[:5])}"

    # Gate 3: No TODO in body
    if TODO_RE.search(body):
        return "ERROR: el documento contiene marcas TODO que deben resolverse antes de promover."

    # Gate 4: No TBD in frontmatter values
    tbd_fields: list[str] = []
    for key, value in existing_fm.items():
        if key == "fecha_vigencia":
            continue
        text = str(value).strip().upper()
        if "TBD" in text:
            tbd_fields.append(key)
    if tbd_fields:
        return f"ERROR: campos con TBD que deben definirse: {', '.join(tbd_fields)}"

    # Gate 5: Required sections
    sections_result = _validate_required_sections_impl(path)
    if sections_result != "OK":
        return f"ERROR: {sections_result}"

    # All gates passed — promote
    updated_fm = dict(existing_fm)
    updated_fm["estado"] = "VIGENTE"
    updated_fm["fecha_emision"] = date.today().isoformat()

    try:
        parsed = DocumentFrontmatter.model_validate(updated_fm)
    except ValidationError as exc:
        return f"ERROR: frontmatter invalido al promover: {exc}"

    new_content = _render_document(updated_fm, body)
    write(abs_path, new_content)

    # Audit trail
    try:
        _append_audit_event(root, {
            "evento": "promocion",
            "codigo": str(updated_fm.get("codigo", "")),
            "path": path,
            "version": str(updated_fm.get("version", "")),
            "de": "BORRADOR",
            "a": "VIGENTE",
        })
    except (OSError, IOError, ValueError):
        pass

    try:
        summary = build_indexes(root)
    except (OSError, ValueError, RuntimeError) as exc:
        return (
            f"ADVERTENCIA: documento promovido a VIGENTE en {path} "
            f"pero fallo la reconstruccion de indices: {exc}"
        )

    return (
        f"OK: documento promovido a VIGENTE en {path} "
        f"({parsed.codigo} v{parsed.version}). "
        f"Indices: {summary.as_text()}"
    )


def _obsolete_document_impl(path: str, motivo: str = "") -> str:
    """Marca un documento VIGENTE como OBSOLETO con motivo opcional."""
    root = repo_root()
    abs_path = (root / path).resolve()

    try:
        assert_within_repo(abs_path, root)
    except ValueError as exc:
        return f"ERROR: {exc}"

    if not abs_path.exists():
        return f"ERROR: no existe: {path}"

    content = read(abs_path)
    existing_fm, body = split_frontmatter_and_body(content)

    if existing_fm is None:
        return "ERROR: el documento no tiene frontmatter YAML valido."

    estado_actual = str(existing_fm.get("estado", "")).strip()
    if estado_actual != "VIGENTE":
        return f"ERROR: solo se puede obsolescer documentos VIGENTE (actual: {estado_actual})"

    updated_fm = dict(existing_fm)
    updated_fm["estado"] = "OBSOLETO"

    try:
        parsed = DocumentFrontmatter.model_validate(updated_fm)
    except ValidationError as exc:
        return f"ERROR: frontmatter invalido al obsolescer: {exc}"

    # Append obsolescence note to body
    if motivo:
        today = date.today().isoformat()
        body = body.rstrip("\n") + f"\n\n---\n**OBSOLETO** ({today}): {motivo}\n"

    new_content = _render_document(updated_fm, body)
    write(abs_path, new_content)

    # Audit trail
    try:
        _append_audit_event(root, {
            "evento": "obsolescencia",
            "codigo": str(updated_fm.get("codigo", "")),
            "path": path,
            "version": str(updated_fm.get("version", "")),
            "motivo": motivo or "(sin motivo)",
        })
    except (OSError, IOError, ValueError):
        pass

    try:
        summary = build_indexes(root)
    except (OSError, ValueError, RuntimeError) as exc:
        return (
            f"ADVERTENCIA: documento obsolescido en {path} "
            f"pero fallo la reconstruccion de indices: {exc}"
        )

    return (
        f"OK: documento marcado como OBSOLETO en {path} "
        f"({parsed.codigo} v{parsed.version}). "
        f"Indices: {summary.as_text()}"
    )


# ---------------------------------------------------------------------------
# Wrappers @function_tool (delegados a las _impl para testabilidad)
# ---------------------------------------------------------------------------


@function_tool
def create_document(
    codigo: str,
    titulo: str,
    tipo: str,
    proceso: str,
    elaboro: str,
    reviso: str,
    aprobo: str,
    content_body: str,
) -> str:
    """Crea un nuevo documento controlado del SGC con frontmatter valido y cuerpo Markdown.

    El documento se crea como BORRADOR v1.0 con fecha de hoy.
    Regenera automaticamente LMD y matriz de registros despues de crear.
    """
    return _create_document_impl(codigo, titulo, tipo, proceso, elaboro, reviso, aprobo, content_body)


@function_tool
def update_document(
    path: str,
    titulo: str = "",
    content_body: str = "",
    proceso: str = "",
    elaboro: str = "",
    reviso: str = "",
    aprobo: str = "",
    estado: str = "",
    version: str = "",
    fecha_emision: str = "",
) -> str:
    """Actualiza un documento controlado existente (cuerpo y/o campos de frontmatter).

    Solo los campos proporcionados (no vacios) se actualizan.
    Si se modifica content_body, la version menor se incrementa automaticamente
    a menos que se proporcione una version explicita.
    Regenera automaticamente LMD y matriz despues de actualizar.
    """
    return _update_document_impl(path, titulo, content_body, proceso, elaboro, reviso, aprobo, estado, version, fecha_emision)


@function_tool
def create_document_from_template(
    tipo: str,
    codigo: str,
    titulo: str,
    proceso: str,
    elaboro: str,
    reviso: str,
    aprobo: str,
) -> str:
    """Crea un nuevo documento pre-llenado desde la plantilla correspondiente al tipo.

    Carga la plantilla de templates/TEMPLATE_*.md, reemplaza frontmatter
    con los datos proporcionados, y crea el archivo. Siempre BORRADOR v1.0.
    Regenera automaticamente LMD y matriz despues de crear.
    """
    return _create_document_from_template_impl(tipo, codigo, titulo, proceso, elaboro, reviso, aprobo)


@function_tool
def promote_document(path: str) -> str:
    """Promueve un documento de BORRADOR a VIGENTE con gates de validacion.

    Verifica: sin TODO, sin placeholders, sin TBD, secciones completas.
    Solo documentos en BORRADOR pueden ser promovidos.
    Actualiza fecha_emision a hoy y regenera indices.
    """
    return _promote_document_impl(path)


@function_tool
def obsolete_document(path: str, motivo: str = "") -> str:
    """Marca un documento VIGENTE como OBSOLETO.

    Solo documentos en VIGENTE pueden ser obsolescidos.
    El motivo se agrega como nota al final del documento.
    Regenera indices automaticamente.
    """
    return _obsolete_document_impl(path, motivo)


# ---------------------------------------------------------------------------
# Conjuntos de herramientas por rol
# ---------------------------------------------------------------------------


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
        create_document,
        update_document,
        create_document_from_template,
        promote_document,
        obsolete_document,
    ]
    return base + compliance_tools()


def writer_tools() -> list[Any]:
    """Toolset para redaccion: lectura, validacion y escritura de documentos controlados."""
    return [
        # Lectura y validacion
        list_controlled_docs,
        read_document,
        validate_frontmatter,
        validate_doc_filename,
        validate_required_sections,
        list_missing_record_dirs,
        validate_code_pattern,
        list_available_project_skills,
        read_project_skill,
        # Escritura
        create_document,
        update_document,
        create_document_from_template,
        promote_document,
        obsolete_document,
        rebuild_control_indexes,
    ]
