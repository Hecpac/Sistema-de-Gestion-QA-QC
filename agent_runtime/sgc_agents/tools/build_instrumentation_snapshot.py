from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from ..config import repo_root
from ..schemas import RecordFrontmatter
from .build_indexes import split_frontmatter_and_body
from .compliance_tools import (
    auditar_catalogo_registros,
    auditar_claves_frontmatter_desconocidas,
    auditar_enlaces_markdown,
    auditar_invariantes_de_estado,
    auditar_pendientes_matriz_registros,
    auditar_secciones_minimas,
    auditar_trazabilidad_registros,
    detectar_formatos_huerfanos,
    resolver_grafo_documental,
)


SNAPSHOT_PATH = Path("docs/_control/instrumentacion_sgc.json")
REQUIRED_DISCIPLINE_DOCS = [
    "IT-SGC-02",
    "IT-SGC-03",
    "IT-SGC-04",
]
REQUIRED_DISCIPLINE_RECORDS = [
    "REG-SGC-CIV-2026-001",
    "REG-SGC-MEC-2026-001",
    "REG-SGC-ELE-2026-001",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(_read_text(path)) or {}
    return payload if isinstance(payload, dict) else {}


def _sorted_counter(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _findings_count(payload: dict[str, Any]) -> int:
    findings = payload.get("hallazgos", [])
    return len(findings) if isinstance(findings, list) else 0


def _audit_payloads() -> dict[str, dict[str, Any]]:
    audits: dict[str, dict[str, Any]] = {}
    mapping = {
        "auditar_invariantes_de_estado": auditar_invariantes_de_estado,
        "auditar_claves_frontmatter_desconocidas": auditar_claves_frontmatter_desconocidas,
        "auditar_secciones_minimas": auditar_secciones_minimas,
        "auditar_enlaces_markdown": auditar_enlaces_markdown,
        "auditar_catalogo_registros": auditar_catalogo_registros,
        "resolver_grafo_documental": resolver_grafo_documental,
        "detectar_formatos_huerfanos": detectar_formatos_huerfanos,
        "auditar_trazabilidad_registros": auditar_trazabilidad_registros,
        "auditar_pendientes_matriz_registros": auditar_pendientes_matriz_registros,
    }

    for name, fn in mapping.items():
        parsed = yaml.safe_load(fn()) or {}
        audits[name] = parsed if isinstance(parsed, dict) else {}

    return audits


def _record_status_for_code(root: Path, code: str) -> dict[str, Any]:
    docs_root = root / "docs/06_registros"
    matched: Path | None = None
    for path in sorted(docs_root.rglob("*.md")):
        if path.stem == code:
            matched = path
            break

    if not matched:
        return {
            "exists": False,
            "path": None,
            "pointer_ok": False,
            "error": "registro_no_encontrado",
        }

    content = _read_text(matched)
    frontmatter, _ = split_frontmatter_and_body(content)
    if not isinstance(frontmatter, dict):
        return {
            "exists": True,
            "path": matched.relative_to(root).as_posix(),
            "pointer_ok": False,
            "error": "frontmatter_invalido",
        }

    try:
        parsed = RecordFrontmatter.model_validate(frontmatter)
        pointer_ok = bool(parsed.ubicacion_externa_url or parsed.ubicacion_fisica)
        return {
            "exists": True,
            "path": matched.relative_to(root).as_posix(),
            "pointer_ok": pointer_ok,
            "error": None if pointer_ok else "sin_puntero_externo_fisico",
        }
    except Exception as exc:  # pragma: no cover
        return {
            "exists": True,
            "path": matched.relative_to(root).as_posix(),
            "pointer_ok": False,
            "error": str(exc),
        }


def build_instrumentation_snapshot(root: Path | None = None, output: Path | None = None) -> Path:
    resolved_root = root.resolve() if root else repo_root().resolve()

    lmd = _load_yaml(resolved_root / "docs/_control/lmd.yml")
    matrix = _load_yaml(resolved_root / "docs/_control/matriz_registros.yml")

    docs = lmd.get("documentos", []) if isinstance(lmd, dict) else []
    docs = docs if isinstance(docs, list) else []

    registros = matrix.get("registros", []) if isinstance(matrix, dict) else []
    registros = registros if isinstance(registros, list) else []

    by_estado = Counter(
        str(item.get("estado", "")).strip() for item in docs if isinstance(item, dict)
    )
    by_tipo = Counter(
        str(item.get("tipo", "")).strip() for item in docs if isinstance(item, dict)
    )
    by_proceso = Counter(
        str(item.get("proceso", "")).strip() for item in docs if isinstance(item, dict)
    )

    audits = _audit_payloads()
    hallazgos_total = sum(_findings_count(payload) for payload in audits.values())

    docs_present = {
        str(item.get("codigo", "")).strip()
        for item in docs
        if isinstance(item, dict)
    }
    required_docs_status = {
        code: {
            "exists": code in docs_present,
        }
        for code in REQUIRED_DISCIPLINE_DOCS
    }

    required_records_status = {
        code: _record_status_for_code(resolved_root, code)
        for code in REQUIRED_DISCIPLINE_RECORDS
    }

    pilot_docs_ok = all(v["exists"] for v in required_docs_status.values())
    pilot_records_ok = all(v.get("pointer_ok", False) for v in required_records_status.values())

    documents_borrador = by_estado.get("BORRADOR", 0)

    payload = {
        "baseline": {
            "documents_total": len(docs),
            "documents_vigente": by_estado.get("VIGENTE", 0),
            "documents_borrador": documents_borrador,
            "records_total": len(registros),
            "hallazgos_total": hallazgos_total,
        },
        "distribution": {
            "by_estado": _sorted_counter(by_estado),
            "by_tipo": _sorted_counter(by_tipo),
            "by_proceso": _sorted_counter(by_proceso),
        },
        "audits": {
            name: {
                "valido": bool(payload.get("valido", False)),
                "hallazgos": _findings_count(payload),
            }
            for name, payload in audits.items()
        },
        "multidisciplina": {
            "required_docs": required_docs_status,
            "required_records": required_records_status,
            "pilot_ready": pilot_docs_ok and pilot_records_ok,
        },
        "readiness": {
            "baseline_ready": documents_borrador == 0 and hallazgos_total == 0,
            "zero_drift_expected": True,
        },
    }

    output_path = output or (resolved_root / SNAPSHOT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera snapshot de instrumentacion SGC en docs/_control/instrumentacion_sgc.json"
    )
    parser.add_argument(
        "--repo-root",
        help="Ruta raiz del repo SGC. Si no se indica, usa SGC_REPO_ROOT o auto-deteccion.",
    )
    parser.add_argument(
        "--output",
        help="Ruta de salida del snapshot de instrumentacion.",
    )
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else None
    output = Path(args.output).resolve() if args.output else None

    path = build_instrumentation_snapshot(root, output)
    print(f"OK: instrumentacion generada en {path}")


if __name__ == "__main__":
    main()
