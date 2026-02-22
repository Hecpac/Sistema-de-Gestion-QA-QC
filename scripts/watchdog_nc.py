#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


DEFAULT_TIMEOUT_S = 90


def repo_root() -> Path:
    raw = os.getenv("SGC_REPO_ROOT", "")
    if raw:
        return Path(raw).resolve()
    return Path(__file__).resolve().parents[1]


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u")
    return lowered


def parse_frontmatter(markdown: str) -> dict[str, Any] | None:
    if not markdown.lstrip().startswith("---\n"):
        return None
    end = markdown.find("\n---\n", 4)
    if end == -1:
        return None
    payload = yaml.safe_load(markdown[4:end]) or {}
    return payload if isinstance(payload, dict) else None


def is_nc_closed(markdown: str) -> bool:
    # Los registros (wrappers) no estandarizan estado en frontmatter; inferir desde el cuerpo.
    text = _normalize(markdown)
    return "- estado:" in text and "cerrada" in text


def extract_root_cause(markdown: str) -> str | None:
    # Prioridad 1: linea explicita con "Causa Raiz:" (con o sin acento)
    for raw in markdown.splitlines():
        line = raw.strip().lstrip("-").strip()
        norm = _normalize(line)
        if norm.startswith("causa raiz"):
            if ":" in line:
                return line.split(":", 1)[1].strip().strip(".")
            return line

    # Prioridad 2: buscar en seccion "Causa Raiz" y capturar primeras lineas
    pattern = re.compile(r"^##+\s+causa\s+ra[ií]z\b.*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return None

    after = markdown[match.end() :].strip()
    chunk: list[str] = []
    for raw in after.splitlines():
        if raw.strip().startswith("#"):
            break
        if raw.strip():
            chunk.append(raw.strip())
        if len(chunk) >= 8:
            break
    return " ".join(chunk).strip() if chunk else None


def build_prompt(root_cause: str, risk_matrix_text: str) -> str:
    return f"""
Act as a QA/QC Risk Manager ISO 9001.
Analyze the following CLOSED Non-Conformity (NC) root cause and the current Risk Matrix.

NON-CONFORMITY ROOT CAUSE:
{root_cause}

CURRENT RISK MATRIX:
{risk_matrix_text}

TASK:
1) Determine if the Root Cause represents a risk that is MISSING or UNDER-RATED in the current matrix.
2) If missing, propose a NEW row for the risk matrix.
3) If covered, output exactly: RISK COVERED

OUTPUT FORMAT:
- If missing: output ONLY the Markdown table row (no header).
  Example: | R-NEW | Proceso | Riesgo | Media | Alto | Alto | Control propuesto |
- If covered: output ONLY: RISK COVERED
""".strip()


def run_gemini(prompt: str, *, gemini_bin: str = "gemini", timeout_s: int = DEFAULT_TIMEOUT_S) -> str:
    result = subprocess.run(
        [gemini_bin],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
    return (result.stdout or "").strip()


@dataclass(frozen=True)
class WatchdogPaths:
    nc_dir: Path
    risk_file: Path
    output_file: Path


def default_paths(root: Path) -> WatchdogPaths:
    return WatchdogPaths(
        nc_dir=(root / "docs/06_registros/no_conformidades").resolve(),
        risk_file=(root / "docs/06_registros/riesgos/REG-SGC-RISK-2026-Q1.md").resolve(),
        output_file=(root / "docs/08_riesgos/PROPOSED_RISKS.md").resolve(),
    )

def main():
    parser = argparse.ArgumentParser(description="Risk Watchdog (NC -> propuesta de riesgos)")
    parser.add_argument("--repo-root", default=os.getenv("SGC_REPO_ROOT", ""), help="Ruta raiz del repo SGC")
    parser.add_argument("--nc-dir", default="", help="Carpeta de NCs (default: docs/06_registros/no_conformidades)")
    parser.add_argument("--risk-file", default="", help="Archivo matriz de riesgos (default: docs/06_registros/riesgos/...)")
    parser.add_argument("--output", default="", help="Archivo de salida propuestas (default: docs/08_riesgos/PROPOSED_RISKS.md)")
    parser.add_argument("--gemini-bin", default="gemini", help="Nombre/ruta del binario gemini")
    parser.add_argument("--timeout-s", type=int, default=DEFAULT_TIMEOUT_S, help="Timeout de ejecucion gemini")
    parser.add_argument("--dry-run", action="store_true", help="No escribe archivo, solo imprime propuestas")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else repo_root()
    defaults = default_paths(root)
    paths = WatchdogPaths(
        nc_dir=Path(args.nc_dir).resolve() if args.nc_dir else defaults.nc_dir,
        risk_file=Path(args.risk_file).resolve() if args.risk_file else defaults.risk_file,
        output_file=Path(args.output).resolve() if args.output else defaults.output_file,
    )

    print("[SGC-WATCHDOG] Activated")
    print(f"[SGC-WATCHDOG] Repo: {root}")
    print(f"[SGC-WATCHDOG] NC dir: {paths.nc_dir}")
    print(f"[SGC-WATCHDOG] Risk file: {paths.risk_file}")

    if not paths.nc_dir.exists():
        print(f"ERROR: nc_dir no existe: {paths.nc_dir}", file=sys.stderr)
        sys.exit(2)
    if not paths.risk_file.exists():
        print(f"ERROR: risk_file no existe: {paths.risk_file}", file=sys.stderr)
        sys.exit(2)

    risk_matrix_content = paths.risk_file.read_text(encoding="utf-8")

    new_risks_found: list[str] = []
    analyzed: list[str] = []

    for filepath in sorted(paths.nc_dir.glob("*.md")):
        content = filepath.read_text(encoding="utf-8")

        if not is_nc_closed(content):
            continue

        root_cause = extract_root_cause(content)
        if not root_cause:
            continue

        analyzed.append(filepath.name)
        print(f"\n[SGC-WATCHDOG] Analizando NC: {filepath.name}")
        print(f"[SGC-WATCHDOG] Causa raiz: {root_cause[:120]}")

        prompt = build_prompt(root_cause, risk_matrix_content)
        try:
            analysis = run_gemini(prompt, gemini_bin=args.gemini_bin, timeout_s=args.timeout_s)
        except FileNotFoundError:
            print("ERROR: 'gemini' CLI no encontrado.", file=sys.stderr)
            sys.exit(2)
        except subprocess.TimeoutExpired:
            print(f"ERROR: timeout gemini ({args.timeout_s}s).", file=sys.stderr)
            sys.exit(2)
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: gemini fallo: {exc.stderr or exc}", file=sys.stderr)
            sys.exit(2)

        print(f"[SGC-WATCHDOG] Evaluacion:\n{analysis}")
        if "|" in analysis and "RISK COVERED" not in analysis:
            new_risks_found.append(analysis.strip())

    if not new_risks_found:
        print(f"\n[SGC-WATCHDOG] Sin nuevos riesgos. NC analizadas={len(analyzed)}")
        return

    print(f"\n[SGC-WATCHDOG] Nuevos riesgos detectados: {len(new_risks_found)}")
    for risk in new_risks_found:
        print(risk)

    if args.dry_run:
        print("\n[SGC-WATCHDOG] dry-run: no se escribe archivo.")
        return

    paths.output_file.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Proposed Risk Matrix Updates\n\n"
        f"- Timestamp (UTC): {_now_utc_iso()}\n"
        f"- NCs analizadas: {', '.join(analyzed) if analyzed else 'N/A'}\n\n"
        "| ID | Proceso | Riesgo | Probabilidad | Impacto | Nivel | Control Actual |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    if not paths.output_file.exists():
        paths.output_file.write_text(header, encoding="utf-8")
    else:
        paths.output_file.write_text(paths.output_file.read_text(encoding="utf-8") + "\n" + header, encoding="utf-8")

    with paths.output_file.open("a", encoding="utf-8") as f:
        for risk in new_risks_found:
            f.write(risk.rstrip() + "\n")

    print(f"\nOK: propuestas guardadas en {paths.output_file}")

if __name__ == "__main__":
    main()
