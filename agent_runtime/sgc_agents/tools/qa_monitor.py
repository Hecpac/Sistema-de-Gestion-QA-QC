"""QA Monitor — deterministic compliance pipeline.

Extraído del heredoc de ``run_qa_monitor.sh`` para hacerlo testeable.
Ejecutar como módulo::

    python -m sgc_agents.tools.qa_monitor [--repo-root PATH] [--history-file PATH]
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ..config import qa_history_path
from .compliance_tools import (
    auditar_catalogo_registros,
    auditar_claves_frontmatter_desconocidas,
    auditar_enlaces_markdown,
    auditar_invariantes_de_estado,
    auditar_secciones_minimas,
    auditar_trazabilidad_registros,
    detectar_formatos_huerfanos,
    generar_reporte_qa_compliance,
    resolver_grafo_documental,
)

# ── public helpers ─────────────────────────────────────────────────────

CHECKS = [
    auditar_invariantes_de_estado,
    auditar_claves_frontmatter_desconocidas,
    auditar_secciones_minimas,
    auditar_enlaces_markdown,
    auditar_catalogo_registros,
    resolver_grafo_documental,
    detectar_formatos_huerfanos,
    auditar_trazabilidad_registros,
]

MAX_HISTORY_RUNS = 60

HISTORY_HEADER = (
    "# Historial de monitor QA del SGC\n"
    "# Archivo autogenerado por run_qa_monitor.sh\n"
    "# No editar manualmente\n\n"
)


def run_checks() -> tuple[int, list[dict[str, Any]]]:
    """Execute all compliance checks and return (total_hallazgos, parsed_results)."""
    results: list[dict[str, Any]] = []
    hallazgos = 0
    for check_fn in CHECKS:
        raw = check_fn()
        parsed = yaml.safe_load(raw) or {}
        results.append(parsed)
        findings = parsed.get("hallazgos", [])
        if isinstance(findings, list):
            hallazgos += len(findings)
    return hallazgos, results


def append_history(
    history_path: Path,
    hallazgos: int,
    *,
    now: datetime | None = None,
    source: str | None = None,
    max_runs: int = MAX_HISTORY_RUNS,
) -> dict[str, Any]:
    """Append a run entry to the YAML history file and return the payload.

    Keeps at most *max_runs* entries sorted by timestamp.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    if source is None:
        source = (
            "github-actions"
            if os.getenv("GITHUB_ACTIONS") == "true"
            else "local"
        )

    history_path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {}
    if history_path.exists():
        try:
            payload = yaml.safe_load(history_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            payload = {}
    if not isinstance(payload, dict):
        payload = {}

    runs: list[dict[str, Any]] = payload.get("runs", [])
    if not isinstance(runs, list):
        runs = []

    runs.append(
        {
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "date": now.strftime("%Y-%m-%d"),
            "hallazgos": int(hallazgos),
            "source": source,
        }
    )

    runs = sorted(
        [r for r in runs if isinstance(r, dict)],
        key=lambda r: (str(r.get("timestamp", "")), str(r.get("date", ""))),
    )

    payload["runs"] = runs[-max_runs:]

    history_path.write_text(
        HISTORY_HEADER
        + yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return payload


def run_pipeline(
    *,
    history_path: Path | None = None,
    generate_report: bool = True,
) -> int:
    """Full QA monitor pipeline. Returns 0 on success, 1 if hallazgos found."""
    if generate_report:
        result = generar_reporte_qa_compliance()
        print(result)

    hallazgos, _ = run_checks()
    print(f"hallazgos_totales={hallazgos}")

    if history_path is not None:
        append_history(history_path, hallazgos)

    return 1 if hallazgos else 0


# ── CLI entry point ────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SGC QA Monitor")
    parser.add_argument(
        "--repo-root",
        default=os.getenv("SGC_REPO_ROOT", ""),
        help="Root del repositorio SGC",
    )
    parser.add_argument(
        "--history-file",
        default=os.getenv(
            "HISTORY_FILE", str(qa_history_path())
        ),
        help="Ruta del archivo de historial",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Omitir generación de reporte MD",
    )
    args = parser.parse_args(argv)

    if args.repo_root:
        os.environ["SGC_REPO_ROOT"] = args.repo_root

    history = Path(args.history_file)
    if not history.is_absolute() and args.repo_root:
        history = Path(args.repo_root) / history

    return run_pipeline(
        history_path=history,
        generate_report=not args.no_report,
    )


if __name__ == "__main__":
    sys.exit(main())
