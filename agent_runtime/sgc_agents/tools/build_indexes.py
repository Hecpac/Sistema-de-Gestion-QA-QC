from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from ..config import repo_root
from ..schemas import DocumentFrontmatter, LmdEntry, MatrixRecordEntry


FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?\s*---\s*\n(.*?)\n---\s*", re.DOTALL)
REG_CODE_RE = re.compile(r"\b(REG-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b")
REGISTROS_SECTION_RE = re.compile(
    r"^\s*#{2,3}\s+\d*\.?\s*Registros asociados\b", re.IGNORECASE
)
MARKDOWN_HEADING_RE = re.compile(r"^\s*#{2,6}\s+")

RECORD_NAME_HINTS = {
    "REG-SGC-CDC": "Solicitud de Creacion/Cambio Documental (llenada)",
    "REG-SGC-COM": "Evidencia de distribucion/comunicacion de documentos",
    "REG-SGC-NC": "Registro de No Conformidad",
    "REG-SGC-CAPA": "Plan y Registro CAPA",
    "REG-SGC-PROG-AUD": "Programa anual de auditorias",
    "REG-SGC-PLAN-AUD": "Plan de auditoria",
    "REG-SGC-INF-AUD": "Informe de auditoria",
    "REG-SGC-SEG-AUD": "Seguimiento de acciones de auditoria",
    "REG-SGC-KPI": "Matriz de KPI",
    "REG-SGC-RD": "Acta de revision por la direccion",
    "REG-SGC-RISK": "Matriz de riesgos y oportunidades",
    "REG-SGC-RISK-PLAN": "Plan de tratamiento y seguimiento de riesgos",
    "REG-SGC-PROV": "Matriz de homologacion y evaluacion de proveedores",
    "REG-SGC-COMP": "Matriz de competencias",
    "REG-SGC-CAP": "Plan y registro de capacitacion",
    "REG-SGC-EFI-CAP": "Evaluacion de eficacia de capacitacion",
}

RECORD_PROCESS_HINTS = {
    "REG-SGC-CDC": "SGC",
    "REG-SGC-COM": "SGC",
    "REG-SGC-NC": "SGC / Mejora",
    "REG-SGC-CAPA": "SGC / Mejora",
    "REG-SGC-PROG-AUD": "SGC / Auditoria",
    "REG-SGC-PLAN-AUD": "SGC / Auditoria",
    "REG-SGC-INF-AUD": "SGC / Auditoria",
    "REG-SGC-SEG-AUD": "SGC / Auditoria",
    "REG-SGC-KPI": "SGC / Desempeno",
    "REG-SGC-RD": "SGC / Direccion",
    "REG-SGC-RISK": "SGC / Riesgos",
    "REG-SGC-RISK-PLAN": "SGC / Riesgos",
    "REG-SGC-PROV": "SGC / Proveedores",
    "REG-SGC-COMP": "SGC / Talento",
    "REG-SGC-CAP": "SGC / Talento",
    "REG-SGC-EFI-CAP": "SGC / Talento",
}

RECORD_FORMAT_HINTS = {
    "REG-SGC-CDC": "FOR-SGC-01",
    "REG-SGC-COM": "FOR-SGC-01",
    "REG-SGC-NC": "FOR-SGC-02",
    "REG-SGC-CAPA": "FOR-SGC-03",
    "REG-SGC-PROG-AUD": "FOR-SGC-04",
    "REG-SGC-PLAN-AUD": "FOR-SGC-05",
    "REG-SGC-INF-AUD": "FOR-SGC-06",
    "REG-SGC-SEG-AUD": "FOR-SGC-07",
    "REG-SGC-KPI": "FOR-SGC-08",
    "REG-SGC-RD": "FOR-SGC-09",
    "REG-SGC-RISK": "FOR-SGC-10",
    "REG-SGC-RISK-PLAN": "FOR-SGC-11",
    "REG-SGC-PROV": "FOR-SGC-12",
    "REG-SGC-COMP": "FOR-SGC-13",
    "REG-SGC-CAP": "FOR-SGC-14",
    "REG-SGC-EFI-CAP": "FOR-SGC-15",
}

LMD_HEADER = (
    "# Lista Maestra de Documentos (LMD)\n"
    "# Archivo autogenerado. Fuente de verdad: frontmatter en docs/*.md\n"
    "# No editar manualmente. Ejecutar: sgc-build-indexes\n\n"
)

MATRIX_HEADER = (
    "# Matriz de Control de Registros\n"
    "# Archivo autogenerado desde secciones 'Registros asociados'\n"
    "# No editar manualmente. Ejecutar: sgc-build-indexes\n\n"
)


@dataclass(frozen=True)
class ControlledDocument:
    absolute_path: Path
    relative_path: str
    frontmatter: DocumentFrontmatter
    content: str


@dataclass(frozen=True)
class BuildIndexesSummary:
    scanned_documents: int
    lmd_entries: int
    matrix_entries: int

    def as_text(self) -> str:
        return (
            f"Documentos controlados: {self.scanned_documents} | "
            f"LMD: {self.lmd_entries} | "
            f"Matriz: {self.matrix_entries}"
        )


def extract_frontmatter(content: str) -> dict[str, Any] | None:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None
    parsed = yaml.safe_load(match.group(1))
    return parsed if isinstance(parsed, dict) else None


def split_frontmatter_and_body(content: str) -> tuple[dict[str, Any] | None, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None, content
    parsed = yaml.safe_load(match.group(1))
    payload = parsed if isinstance(parsed, dict) else None
    body = content[match.end() :].lstrip("\n")
    return payload, body


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(_read(path)) or {}
    return data if isinstance(data, dict) else {}


def _dump_yaml_with_header(path: Path, header: str, payload: dict[str, Any]) -> None:
    rendered = header + yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    _write(path, rendered)


def _is_controlled_doc(path: Path, content: str) -> bool:
    if path.name.startswith("TEMPLATE_"):
        return False
    return extract_frontmatter(content) is not None


def discover_controlled_documents(root: Path) -> list[ControlledDocument]:
    docs_root = root / "docs"
    if not docs_root.exists():
        raise FileNotFoundError(f"No existe carpeta docs/: {docs_root}")

    discovered: list[ControlledDocument] = []
    seen_codes: dict[str, str] = {}

    for abs_path in sorted(docs_root.rglob("*.md")):
        rel_path = abs_path.relative_to(root).as_posix()

        # Los registros operativos no forman parte de la LMD.
        if rel_path.startswith("docs/06_registros/"):
            continue

        content = _read(abs_path)
        if not _is_controlled_doc(abs_path, content):
            continue

        raw_frontmatter = extract_frontmatter(content)
        if raw_frontmatter is None:
            continue

        try:
            frontmatter = DocumentFrontmatter.model_validate(raw_frontmatter)
        except ValidationError as exc:
            raise ValueError(f"Frontmatter invalido en {rel_path}: {exc}") from exc

        previous = seen_codes.get(frontmatter.codigo)
        if previous:
            raise ValueError(
                "Codigo documental duplicado "
                f"{frontmatter.codigo}: {previous} y {rel_path}"
            )
        seen_codes[frontmatter.codigo] = rel_path

        discovered.append(
            ControlledDocument(
                absolute_path=abs_path,
                relative_path=rel_path,
                frontmatter=frontmatter,
                content=content,
            )
        )

    return sorted(discovered, key=lambda d: d.frontmatter.codigo)


def _existing_lmd_by_code(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "docs/_control/lmd.yml"
    data = _load_yaml(path)
    items = data.get("documentos", [])
    if not isinstance(items, list):
        return {}

    by_code: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        code = str(item.get("codigo", "")).strip()
        if code:
            by_code[code] = item
    return by_code


def _existing_matrix_by_code(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "docs/_control/matriz_registros.yml"
    data = _load_yaml(path)
    items = data.get("registros", [])
    if not isinstance(items, list):
        return {}

    by_code: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        code = str(item.get("codigo", "")).strip()
        if code:
            by_code[code] = item
    return by_code


def _compute_fecha_vigencia(
    doc: ControlledDocument, existing_entry: dict[str, Any] | None
) -> str:
    if doc.frontmatter.estado != "VIGENTE":
        return "TBD"

    if existing_entry:
        existing_value = str(existing_entry.get("fecha_vigencia", "")).strip()
        if existing_value and existing_value != "TBD":
            return existing_value

    return doc.frontmatter.fecha_emision


def build_lmd_payload(
    documents: list[ControlledDocument],
    existing_by_code: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    for doc in documents:
        existing = existing_by_code.get(doc.frontmatter.codigo)
        entry = LmdEntry.model_validate(
            {
                "codigo": doc.frontmatter.codigo,
                "titulo": doc.frontmatter.titulo,
                "tipo": doc.frontmatter.tipo,
                "proceso": doc.frontmatter.proceso,
                "version": doc.frontmatter.version,
                "estado": doc.frontmatter.estado,
                "fecha_vigencia": _compute_fecha_vigencia(doc, existing),
                "ubicacion": doc.relative_path,
            }
        )
        entries.append(entry.model_dump())

    return {"documentos": entries}


def _iter_registros_section_lines(content: str) -> list[str]:
    _, body = split_frontmatter_and_body(content)
    lines = body.splitlines()
    in_section = False
    section_lines: list[str] = []

    for line in lines:
        if not in_section:
            if REGISTROS_SECTION_RE.match(line):
                in_section = True
            continue

        if MARKDOWN_HEADING_RE.match(line):
            break

        section_lines.append(line)

    return section_lines


def _extract_name_for_code(line: str, code: str) -> str:
    right = line.split(code, 1)[1]
    cleaned = right.strip().strip("`")
    cleaned = cleaned.lstrip("-: ")
    cleaned = cleaned.strip().rstrip(".")
    return cleaned


def _extract_record_refs(content: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for line in _iter_registros_section_lines(content):
        if "REG-" not in line:
            continue
        codes = REG_CODE_RE.findall(line)
        if not codes:
            continue
        for code in codes:
            refs.append((code, _extract_name_for_code(line, code)))
    return refs


def _default_record_location(code: str) -> str:
    if "AUD" in code:
        return "docs/06_registros/auditorias/"
    if "CAPA" in code:
        return "docs/06_registros/capa/"
    if code.endswith("-NC"):
        return "docs/06_registros/no_conformidades/"
    if "RISK" in code:
        return "docs/06_registros/riesgos/"
    if "PROV" in code:
        return "docs/06_registros/proveedores/"
    if "COMP" in code or "CAP" in code:
        return "docs/06_registros/competencia/"
    return "docs/06_registros/"


def build_matrix_payload(
    documents: list[ControlledDocument],
    existing_by_code: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    discovered: dict[str, dict[str, str]] = {}

    for doc in documents:
        for code, name in _extract_record_refs(doc.content):
            row = discovered.setdefault(
                code,
                {
                    "nombre": "",
                    "proceso": doc.frontmatter.proceso,
                },
            )
            if name and len(name) > len(row.get("nombre", "")):
                row["nombre"] = name

    records: list[dict[str, Any]] = []
    for code in sorted(discovered):
        discovered_row = discovered[code]
        existing = existing_by_code.get(code, {})

        existing_format = str(existing.get("codigo_formato", "")).strip()

        payload = {
            "nombre": RECORD_NAME_HINTS.get(code)
            or existing.get("nombre")
            or discovered_row.get("nombre")
            or code,
            "codigo": code,
            "codigo_formato": existing_format or RECORD_FORMAT_HINTS.get(code),
            "proceso": RECORD_PROCESS_HINTS.get(code)
            or existing.get("proceso")
            or discovered_row.get("proceso")
            or "SGC",
            "responsable": existing.get("responsable", "<DEFINIR>"),
            "medio": existing.get("medio", "Digital"),
            "ubicacion": existing.get("ubicacion", _default_record_location(code)),
            "retencion": existing.get("retencion", "TBD"),
            "disposicion_final": existing.get(
                "disposicion_final", "TODO: Definir (eliminar/archivar/destruir)"
            ),
            "acceso": existing.get("acceso", "TODO: Definir"),
            "proteccion": existing.get(
                "proteccion", "Control de acceso + respaldos"
            ),
        }
        record = MatrixRecordEntry.model_validate(payload)
        records.append(record.model_dump(exclude_none=True))

    return {"registros": records}


def build_indexes(root: Path | None = None) -> BuildIndexesSummary:
    resolved_root = root.resolve() if root else repo_root().resolve()

    documents = discover_controlled_documents(resolved_root)

    lmd_payload = build_lmd_payload(documents, _existing_lmd_by_code(resolved_root))
    matrix_payload = build_matrix_payload(documents, _existing_matrix_by_code(resolved_root))

    lmd_path = resolved_root / "docs/_control/lmd.yml"
    matrix_path = resolved_root / "docs/_control/matriz_registros.yml"

    _dump_yaml_with_header(lmd_path, LMD_HEADER, lmd_payload)
    _dump_yaml_with_header(matrix_path, MATRIX_HEADER, matrix_payload)

    return BuildIndexesSummary(
        scanned_documents=len(documents),
        lmd_entries=len(lmd_payload["documentos"]),
        matrix_entries=len(matrix_payload["registros"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Genera docs/_control/lmd.yml y docs/_control/matriz_registros.yml "
            "a partir de frontmatter y referencias de registros"
        )
    )
    parser.add_argument(
        "--repo-root",
        help=(
            "Ruta del repositorio SGC. Si no se indica, usa "
            "SGC_REPO_ROOT o auto-deteccion."
        ),
    )
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else None
    summary = build_indexes(root)
    print(summary.as_text())


if __name__ == "__main__":
    main()
