from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

try:
    from agents import function_tool
except Exception:  # pragma: no cover
    def function_tool(fn):
        return fn

from ..config import repo_root
from ..schemas import RecordFrontmatter
from .build_indexes import (
    RECORD_FORMAT_HINTS,
    discover_controlled_documents,
    extract_frontmatter,
    split_frontmatter_and_body,
)


FORMAT_REF_RE = re.compile(r"\bFOR-[A-Z0-9]+-[0-9]+\b")
HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", re.MULTILINE)
FORM_FILL_HEADING_RE = re.compile(r"^9\.?\s+formato de llenado\b", re.IGNORECASE)
TODO_RE = re.compile(r"\bTODO\b")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

ALLOWED_DOC_FRONTMATTER_KEYS = {
    "codigo",
    "titulo",
    "tipo",
    "version",
    "estado",
    "fecha_emision",
    "proceso",
    "elaboro",
    "reviso",
    "aprobo",
}

ALLOWED_RECORD_FRONTMATTER_KEYS = {
    "formato_origen",
    "codigo_registro",
    "fecha_registro",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _dump(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def _controlled_docs() -> list[Any]:
    return discover_controlled_documents(repo_root().resolve())


def _split_body(content: str) -> tuple[dict[str, Any] | None, str]:
    return split_frontmatter_and_body(content)


def _format_docs_by_code() -> dict[str, Any]:
    by_code: dict[str, Any] = {}
    for doc in _controlled_docs():
        if doc.frontmatter.tipo == "FOR":
            by_code[doc.frontmatter.codigo] = doc
    return by_code


def _procedure_docs() -> list[Any]:
    return [doc for doc in _controlled_docs() if doc.frontmatter.tipo == "PR"]


def _extract_for_codes(content: str) -> set[str]:
    _, body = _split_body(content)
    return set(FORMAT_REF_RE.findall(body))


def _matrix_items() -> list[dict[str, Any]]:
    matrix = repo_root() / "docs/_control/matriz_registros.yml"
    if not matrix.exists():
        return []
    data = yaml.safe_load(_read(matrix)) or {}
    items = data.get("registros", [])
    return [item for item in items if isinstance(item, dict)]


def _catalog_items() -> list[dict[str, Any]]:
    catalog = repo_root() / "docs/06_registros/catalogo_registros.yml"
    if not catalog.exists():
        return []
    data = yaml.safe_load(_read(catalog)) or {}
    items = data.get("registros", [])
    return [item for item in items if isinstance(item, dict)]


def _catalog_by_code() -> dict[str, dict[str, Any]]:
    by_code: dict[str, dict[str, Any]] = {}
    for item in _catalog_items():
        code = str(item.get("codigo", "")).strip()
        if code:
            by_code[code] = item
    return by_code


def _is_pending_value(value: Any) -> bool:
    text = str(value or "").strip().upper()
    if not text:
        return True
    return "TODO" in text or "TBD" in text or "<DEFINIR>" in text


def _matrix_format_codes() -> set[str]:
    format_codes: set[str] = set()
    for item in _matrix_items():
        explicit = str(item.get("codigo_formato", "")).strip()
        if explicit:
            format_codes.add(explicit)
            continue

        reg_code = str(item.get("codigo", "")).strip()
        hinted = RECORD_FORMAT_HINTS.get(reg_code)
        if hinted:
            format_codes.add(hinted)
    return format_codes



def _extract_headers(markdown: str) -> set[str]:
    return {header.strip().lower() for header in HEADING_RE.findall(markdown)}


def _extract_fillable_headers(markdown: str) -> set[str]:
    required: set[str] = set()
    in_fill_section = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        match = re.match(r"^(#{2,4})\s+(.+)$", line)
        if not match:
            continue

        level = len(match.group(1))
        heading = match.group(2).strip().lower()

        if not in_fill_section:
            if level == 2 and FORM_FILL_HEADING_RE.match(heading):
                in_fill_section = True
                required.add(heading)
            continue

        if level == 2 and not FORM_FILL_HEADING_RE.match(heading):
            break

        if level >= 3:
            required.add(heading)

    return required if required else _extract_headers(markdown)


def _normalize_heading(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"^\d+\.?\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _contains_required_headings(markdown: str, required_prefixes: list[str]) -> list[str]:
    raw = _extract_headers(markdown)
    normalized = {_normalize_heading(h) for h in raw}

    missing: list[str] = []
    for required in required_prefixes:
        required_norm = _normalize_heading(required)
        ok = any(h == required_norm or h.startswith(required_norm) for h in normalized)
        if not ok:
            missing.append(required)
    return missing


def _validate_traceability_for_path(record_path: Path) -> dict[str, Any]:
    findings: list[str] = []
    axioms: dict[str, bool] = {
        "P1_procedencia": False,
        "P2_existencia_canonica": False,
        "P3_vigencia_legal": False,
        "P4_sincronizacion_ssot": False,
        "P5_isomorfismo_estructural": False,
    }

    content = _read(record_path)
    meta, body = _split_body(content)

    parsed_meta: RecordFrontmatter | None = None
    if isinstance(meta, dict):
        try:
            parsed_meta = RecordFrontmatter.model_validate(meta)
        except Exception:
            parsed_meta = None

    origin = parsed_meta.formato_origen if parsed_meta else ""
    if not origin:
        findings.append(
            "[P1] El registro es huerfano (frontmatter invalido o falta 'formato_origen')."
        )
        return {
            "registro": record_path.as_posix(),
            "valido": False,
            "axiomas": axioms,
            "hallazgos": findings,
        }

    axioms["P1_procedencia"] = True

    format_doc = _format_docs_by_code().get(origin)
    if not format_doc:
        findings.append(
            f"[P2] El formato declarado '{origin}' no existe fisicamente en docs/."
        )
        return {
            "registro": record_path.as_posix(),
            "valido": False,
            "axiomas": axioms,
            "hallazgos": findings,
        }

    axioms["P2_existencia_canonica"] = True

    if format_doc.frontmatter.estado == "VIGENTE":
        axioms["P3_vigencia_legal"] = True
    else:
        findings.append(
            "[P3] Uso de plantilla ilegal. "
            f"El formato '{origin}' esta en estado '{format_doc.frontmatter.estado}'."
        )

    if origin in _matrix_format_codes():
        axioms["P4_sincronizacion_ssot"] = True
    else:
        findings.append(
            f"[P4] El formato '{origin}' no esta habilitado en la Matriz de Registros."
        )

    _, format_body = _split_body(format_doc.content)
    format_headers = _extract_fillable_headers(format_body)
    record_headers = _extract_headers(body)
    missing_headers = sorted(format_headers - record_headers)
    if missing_headers:
        findings.append(
            "[P5] El registro altero el molde oficial. "
            f"Faltan secciones: {missing_headers}"
        )
    else:
        axioms["P5_isomorfismo_estructural"] = True

    valid = len(findings) == 0
    return {
        "registro": record_path.as_posix(),
        "valido": valid,
        "axiomas": axioms,
        "hallazgos": findings if findings else ["Trazabilidad perfecta."],
    }


def _iter_record_files(relative_subfolder: str = "") -> list[Path]:
    base = (repo_root() / "docs/06_registros").resolve()
    target = (base / relative_subfolder).resolve() if relative_subfolder else base

    if base not in target.parents and target != base:
        raise ValueError("Ruta fuera de docs/06_registros")
    if not target.exists():
        return []

    files: list[Path] = []
    for path in sorted(target.rglob("*.md")):
        if path.name.upper() == "README.MD":
            continue
        files.append(path)
    return files


def auditar_invariantes_de_estado() -> str:
    """Valida invariantes en documentos VIGENTE: sin TODO/placeholders/TBD."""
    findings: list[dict[str, Any]] = []
    vigentes = 0

    for doc in _controlled_docs():
        if doc.frontmatter.estado != "VIGENTE":
            continue

        vigentes += 1
        errors: list[str] = []
        if TODO_RE.search(doc.content):
            errors.append("Contiene TODO")
        if PLACEHOLDER_RE.search(doc.content):
            errors.append("Contiene placeholders tipo <...>")
        if "TBD" in doc.content:
            errors.append("Contiene valor TBD")

        if errors:
            findings.append(
                {
                    "codigo": doc.frontmatter.codigo,
                    "ruta": doc.relative_path,
                    "hallazgos": errors,
                }
            )

    payload = {
        "skill": "auditar_invariantes_de_estado",
        "documentos_vigentes": vigentes,
        "valido": len(findings) == 0,
        "hallazgos": findings,
    }
    return _dump(payload)


def auditar_claves_frontmatter_desconocidas() -> str:
    """Detecta claves no reconocidas en frontmatter de documentos VIGENTE."""
    findings: list[dict[str, Any]] = []
    vigentes = 0

    for doc in _controlled_docs():
        if doc.frontmatter.estado != "VIGENTE":
            continue
        vigentes += 1

        raw = extract_frontmatter(doc.content) or {}
        if not isinstance(raw, dict):
            continue

        extra = sorted({str(k).strip() for k in raw.keys()} - ALLOWED_DOC_FRONTMATTER_KEYS)
        if extra:
            findings.append(
                {
                    "codigo": doc.frontmatter.codigo,
                    "ruta": doc.relative_path,
                    "claves_desconocidas": extra,
                }
            )

    payload = {
        "skill": "auditar_claves_frontmatter_desconocidas",
        "documentos_vigentes": vigentes,
        "valido": len(findings) == 0,
        "hallazgos": findings,
    }
    return _dump(payload)


def auditar_secciones_minimas() -> str:
    """Valida secciones mínimas requeridas en documentos VIGENTE."""
    findings: list[dict[str, Any]] = []
    vigentes = 0

    required_prefixes = [
        "objetivo",
        "alcance",
        "responsabilidades",
        "desarrollo",
        "registros asociados",
        "control de cambios",
    ]

    for doc in _controlled_docs():
        if doc.frontmatter.estado != "VIGENTE":
            continue
        vigentes += 1

        missing = _contains_required_headings(doc.content, required_prefixes)
        if missing:
            findings.append(
                {
                    "codigo": doc.frontmatter.codigo,
                    "ruta": doc.relative_path,
                    "faltantes": missing,
                }
            )

    payload = {
        "skill": "auditar_secciones_minimas",
        "documentos_vigentes": vigentes,
        "valido": len(findings) == 0,
        "hallazgos": findings,
    }
    return _dump(payload)


def auditar_enlaces_markdown() -> str:
    """Detecta enlaces Markdown rotos (rutas relativas) en documentos VIGENTE."""
    findings: list[dict[str, Any]] = []
    vigentes = 0
    root = repo_root().resolve()

    for doc in _controlled_docs():
        if doc.frontmatter.estado != "VIGENTE":
            continue
        vigentes += 1

        body = CODE_FENCE_RE.sub("", doc.content)
        doc_dir = (root / doc.relative_path).parent

        for raw_target in MARKDOWN_LINK_RE.findall(body):
            target = raw_target.strip()
            if not target:
                continue

            # Strip optional title: (path "title")
            if " " in target and not target.startswith(("http://", "https://")):
                target = target.split(" ", 1)[0].strip()

            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1].strip()

            # Ignore external / anchors
            if target.startswith(("#", "mailto:")):
                continue
            if "://" in target:
                continue

            # Remove querystring and fragment
            target = target.split("?", 1)[0]
            path_part = target.split("#", 1)[0].strip()
            if not path_part:
                continue

            if path_part.startswith("/"):
                resolved = (root / path_part.lstrip("/")).resolve()
            else:
                resolved = (doc_dir / path_part).resolve()

            if root not in resolved.parents and resolved != root:
                findings.append(
                    {
                        "codigo": doc.frontmatter.codigo,
                        "ruta": doc.relative_path,
                        "enlace": raw_target,
                        "error": "Ruta fuera del repositorio",
                    }
                )
                continue

            if not resolved.exists():
                findings.append(
                    {
                        "codigo": doc.frontmatter.codigo,
                        "ruta": doc.relative_path,
                        "enlace": raw_target,
                        "resuelto": resolved.relative_to(root).as_posix(),
                        "error": "Archivo no existe",
                    }
                )

    payload = {
        "skill": "auditar_enlaces_markdown",
        "documentos_vigentes": vigentes,
        "valido": len(findings) == 0,
        "hallazgos": findings,
    }
    return _dump(payload)


def auditar_pendientes_matriz_registros() -> str:
    """Detecta campos pendientes (TBD/TODO/<DEFINIR>/vacio) en matriz_registros.yml."""
    findings: list[dict[str, Any]] = []
    for row in _matrix_items():
        codigo = str(row.get("codigo", "")).strip() or "?"
        pending_fields: list[str] = []
        for key in ("responsable", "retencion", "disposicion_final", "acceso", "ubicacion"):
            if _is_pending_value(row.get(key)):
                pending_fields.append(key)
        if pending_fields:
            findings.append(
                {
                    "codigo": codigo,
                    "pendientes": pending_fields,
                }
            )

    payload = {
        "skill": "auditar_pendientes_matriz_registros",
        "registros_total": len(_matrix_items()),
        "valido": len(findings) == 0,
        "hallazgos": findings,
    }
    return _dump(payload)


def auditar_catalogo_registros() -> str:
    """Valida existencia y completitud del catalogo SSOT de registros."""
    catalog_path = repo_root() / "docs/06_registros/catalogo_registros.yml"
    if not catalog_path.exists():
        payload = {
            "skill": "auditar_catalogo_registros",
            "valido": False,
            "hallazgos": [
                {
                    "error": "No existe docs/06_registros/catalogo_registros.yml",
                }
            ],
        }
        return _dump(payload)

    by_code = _catalog_by_code()
    matrix_codes = sorted(
        {str(row.get("codigo", "")).strip() for row in _matrix_items() if str(row.get("codigo", "")).strip()}
    )

    findings: list[dict[str, Any]] = []
    for code in matrix_codes:
        row = by_code.get(code)
        if not row:
            findings.append(
                {
                    "codigo": code,
                    "error": "Falta en catalogo_registros.yml",
                }
            )
            continue

        pending_fields: list[str] = []
        for key in (
            "nombre",
            "codigo_formato",
            "proceso",
            "responsable",
            "medio",
            "ubicacion",
            "retencion",
            "disposicion_final",
            "acceso",
            "proteccion",
        ):
            if _is_pending_value(row.get(key)):
                pending_fields.append(key)

        if pending_fields:
            findings.append(
                {
                    "codigo": code,
                    "pendientes": pending_fields,
                }
            )

    payload = {
        "skill": "auditar_catalogo_registros",
        "registros_en_matriz": len(matrix_codes),
        "catalogo_total": len(by_code),
        "valido": len(findings) == 0,
        "hallazgos": findings,
    }
    return _dump(payload)


def resolver_grafo_documental() -> str:
    """Resuelve referencias PR -> FOR y detecta enlaces rotos documentales."""
    format_codes = set(_format_docs_by_code().keys())
    edges: list[dict[str, Any]] = []
    broken: list[dict[str, Any]] = []

    for pr in _procedure_docs():
        refs = sorted(_extract_for_codes(pr.content))
        for ref in refs:
            edge = {
                "origen": pr.frontmatter.codigo,
                "ruta_origen": pr.relative_path,
                "destino": ref,
            }
            edges.append(edge)
            if ref not in format_codes:
                broken.append(edge)

    payload = {
        "skill": "resolver_grafo_documental",
        "aristas": len(edges),
        "enlaces_rotos": len(broken),
        "valido": len(broken) == 0,
        "hallazgos": broken,
    }
    return _dump(payload)


def detectar_formatos_huerfanos() -> str:
    """Detecta formatos FOR sin uso por PR o sin alta en matriz de registros."""
    procedure_refs: set[str] = set()
    for pr in _procedure_docs():
        procedure_refs.update(_extract_for_codes(pr.content))

    matrix_formats = _matrix_format_codes()
    findings: list[dict[str, Any]] = []

    for code, doc in sorted(_format_docs_by_code().items()):
        reasons: list[str] = []
        if code not in procedure_refs:
            reasons.append("Sin referencia en procedimientos")
        if code not in matrix_formats:
            reasons.append("Sin alta en matriz_registros (codigo_formato)")
        if reasons:
            findings.append(
                {
                    "codigo": code,
                    "ruta": doc.relative_path,
                    "motivos": reasons,
                }
            )

    payload = {
        "skill": "detectar_formatos_huerfanos",
        "formatos_total": len(_format_docs_by_code()),
        "huerfanos": len(findings),
        "valido": len(findings) == 0,
        "hallazgos": findings,
    }
    return _dump(payload)


def validar_trazabilidad_registro(ruta_registro: str) -> str:
    """Evalua axiomas P1..P5 para un registro bajo docs/06_registros/."""
    record_path = (repo_root() / "docs/06_registros" / ruta_registro).resolve()
    base = (repo_root() / "docs/06_registros").resolve()

    if base not in record_path.parents and record_path != base:
        raise ValueError("Ruta fuera de docs/06_registros")
    if not record_path.exists() or not record_path.is_file():
        raise FileNotFoundError(f"No existe registro: {ruta_registro}")

    return _dump(_validate_traceability_for_path(record_path))


def auditar_trazabilidad_registros(subcarpeta: str = "") -> str:
    """Audita trazabilidad de todos los registros Markdown en docs/06_registros/."""
    records = _iter_record_files(subcarpeta)
    results = [_validate_traceability_for_path(path) for path in records]

    invalid = [result for result in results if not result.get("valido")]

    payload = {
        "skill": "auditar_trazabilidad",
        "fecha": date.today().isoformat(),
        "registros_auditados": len(records),
        "fallidos": len(invalid),
        "valido": len(invalid) == 0,
        "hallazgos": invalid,
    }
    return _dump(payload)


def generar_reporte_qa_compliance(
    salida: str = "docs/_control/reporte_qa_compliance.md",
) -> str:
    """Ejecuta pipeline QA y genera reporte consolidado en Markdown."""
    inv = yaml.safe_load(auditar_invariantes_de_estado())
    unknown_frontmatter = yaml.safe_load(auditar_claves_frontmatter_desconocidas())
    min_sections = yaml.safe_load(auditar_secciones_minimas())
    links = yaml.safe_load(auditar_enlaces_markdown())
    catalog = yaml.safe_load(auditar_catalogo_registros())
    graph = yaml.safe_load(resolver_grafo_documental())
    orphan = yaml.safe_load(detectar_formatos_huerfanos())
    trace = yaml.safe_load(auditar_trazabilidad_registros())

    all_findings = 0
    all_findings += len(inv.get("hallazgos", [])) if isinstance(inv, dict) else 0
    all_findings += (
        len(unknown_frontmatter.get("hallazgos", [])) if isinstance(unknown_frontmatter, dict) else 0
    )
    all_findings += len(min_sections.get("hallazgos", [])) if isinstance(min_sections, dict) else 0
    all_findings += len(links.get("hallazgos", [])) if isinstance(links, dict) else 0
    all_findings += len(catalog.get("hallazgos", [])) if isinstance(catalog, dict) else 0
    all_findings += len(graph.get("hallazgos", [])) if isinstance(graph, dict) else 0
    all_findings += len(orphan.get("hallazgos", [])) if isinstance(orphan, dict) else 0
    all_findings += len(trace.get("hallazgos", [])) if isinstance(trace, dict) else 0

    report_lines = [
        "# Reporte QA/Compliance (Neuro-Simbolico)",
        "",
        f"- Fecha: {date.today().isoformat()}",
        f"- Hallazgos totales: {all_findings}",
        "",
        "## 1. auditar_invariantes_de_estado",
        "```yaml",
        yaml.safe_dump(inv, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 2. auditar_claves_frontmatter_desconocidas",
        "```yaml",
        yaml.safe_dump(unknown_frontmatter, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 3. auditar_secciones_minimas",
        "```yaml",
        yaml.safe_dump(min_sections, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 4. auditar_enlaces_markdown",
        "```yaml",
        yaml.safe_dump(links, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 5. auditar_catalogo_registros",
        "```yaml",
        yaml.safe_dump(catalog, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 6. resolver_grafo_documental",
        "```yaml",
        yaml.safe_dump(graph, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 7. detectar_formatos_huerfanos",
        "```yaml",
        yaml.safe_dump(orphan, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 8. validar_trazabilidad (P1..P5)",
        "```yaml",
        yaml.safe_dump(trace, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
    ]

    if isinstance(trace, dict) and trace.get("hallazgos"):
        report_lines.extend(
            [
                "",
                "## No Conformidades Sugeridas",
                "- Registrar NC por cada falla P3/P4/P5 con referencia al registro afectado.",
                "- Adjuntar evidencia del incumplimiento y plan CAPA.",
            ]
        )

    output_path = (repo_root() / salida).resolve()
    repo = repo_root().resolve()
    if repo not in output_path.parents and output_path != repo:
        raise ValueError("Ruta de salida fuera del repositorio")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return f"OK: reporte generado en {output_path}"


auditar_invariantes_de_estado_tool = function_tool(auditar_invariantes_de_estado)
auditar_claves_frontmatter_desconocidas_tool = function_tool(auditar_claves_frontmatter_desconocidas)
auditar_secciones_minimas_tool = function_tool(auditar_secciones_minimas)
auditar_enlaces_markdown_tool = function_tool(auditar_enlaces_markdown)
auditar_pendientes_matriz_registros_tool = function_tool(auditar_pendientes_matriz_registros)
auditar_catalogo_registros_tool = function_tool(auditar_catalogo_registros)
resolver_grafo_documental_tool = function_tool(resolver_grafo_documental)
detectar_formatos_huerfanos_tool = function_tool(detectar_formatos_huerfanos)
validar_trazabilidad_registro_tool = function_tool(validar_trazabilidad_registro)
auditar_trazabilidad_registros_tool = function_tool(auditar_trazabilidad_registros)
generar_reporte_qa_compliance_tool = function_tool(generar_reporte_qa_compliance)


def compliance_tools() -> list[Any]:
    return [
        auditar_invariantes_de_estado_tool,
        auditar_claves_frontmatter_desconocidas_tool,
        auditar_secciones_minimas_tool,
        auditar_enlaces_markdown_tool,
        auditar_pendientes_matriz_registros_tool,
        auditar_catalogo_registros_tool,
        resolver_grafo_documental_tool,
        detectar_formatos_huerfanos_tool,
        validar_trazabilidad_registro_tool,
        auditar_trazabilidad_registros_tool,
        generar_reporte_qa_compliance_tool,
    ]
