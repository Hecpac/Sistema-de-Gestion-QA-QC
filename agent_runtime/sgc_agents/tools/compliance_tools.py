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
    split_frontmatter_and_body,
)


FORMAT_REF_RE = re.compile(r"\bFOR-[A-Z0-9]+-[0-9]+\b")
HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", re.MULTILINE)
FORM_FILL_HEADING_RE = re.compile(r"^9\.?\s+formato de llenado\b", re.IGNORECASE)
TODO_RE = re.compile(r"\bTODO\b")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")


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


@function_tool
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


@function_tool
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


@function_tool
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


@function_tool
def validar_trazabilidad_registro(ruta_registro: str) -> str:
    """Evalua axiomas P1..P5 para un registro bajo docs/06_registros/."""
    record_path = (repo_root() / "docs/06_registros" / ruta_registro).resolve()
    base = (repo_root() / "docs/06_registros").resolve()

    if base not in record_path.parents and record_path != base:
        raise ValueError("Ruta fuera de docs/06_registros")
    if not record_path.exists() or not record_path.is_file():
        raise FileNotFoundError(f"No existe registro: {ruta_registro}")

    return _dump(_validate_traceability_for_path(record_path))


@function_tool
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


@function_tool
def generar_reporte_qa_compliance(
    salida: str = "docs/_control/reporte_qa_compliance.md",
) -> str:
    """Ejecuta pipeline QA y genera reporte consolidado en Markdown."""
    inv = yaml.safe_load(auditar_invariantes_de_estado())
    graph = yaml.safe_load(resolver_grafo_documental())
    orphan = yaml.safe_load(detectar_formatos_huerfanos())
    trace = yaml.safe_load(auditar_trazabilidad_registros())

    all_findings = 0
    all_findings += len(inv.get("hallazgos", [])) if isinstance(inv, dict) else 0
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
        "## 2. resolver_grafo_documental",
        "```yaml",
        yaml.safe_dump(graph, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 3. detectar_formatos_huerfanos",
        "```yaml",
        yaml.safe_dump(orphan, sort_keys=False, allow_unicode=True).rstrip(),
        "```",
        "",
        "## 4. validar_trazabilidad (P1..P5)",
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


def compliance_tools() -> list[Any]:
    return [
        auditar_invariantes_de_estado,
        resolver_grafo_documental,
        detectar_formatos_huerfanos,
        validar_trazabilidad_registro,
        auditar_trazabilidad_registros,
        generar_reporte_qa_compliance,
    ]
