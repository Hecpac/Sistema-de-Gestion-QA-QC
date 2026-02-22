#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMEOUT_S = 120


def repo_root() -> Path:
    raw = os.getenv("SGC_REPO_ROOT", "")
    if raw:
        return Path(raw).resolve()
    return Path(__file__).resolve().parents[1]


def _run_gemini(prompt: str, *, gemini_bin: str = "gemini", timeout_s: int = DEFAULT_TIMEOUT_S) -> str:
    try:
        result = subprocess.run(
            [gemini_bin],
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout_s,
        )
        return result.stdout
    except FileNotFoundError:
        return "Error: 'gemini' CLI not found. Please install it."
    except subprocess.TimeoutExpired:
        return f"Error: gemini timeout after {timeout_s}s."
    except subprocess.CalledProcessError as exc:
        return f"Error calling gemini: {exc.stderr or exc}"


def generate_itp(spec_text: str, *, title_hint: str = "Concrete (Cast-in-Place)") -> str:
    prompt = f"""
Act as a QA/QC Engineer for a construction project.
Read the following technical specification text for: {title_hint}.
Extract all mandatory requirements, tolerances, and inspection points.

Create a structured Markdown Inspection Test Plan (ITP) following this format:

# ITP - [Title based on spec]

## 1. Objective
Define inspection criteria for [Scope].

## 2. Reference Documents
List ASTM/ACI standards mentioned.

## 3. Equipment Required
List tools needed (e.g., Slump cone, Air meter).

## 4. Inspection Checkpoints
Create a table with columns:
| Item | Description | Acceptance Criteria / Tolerance | Frequency | Type (Hold/Witness/Review) | Ref |
|---|---|---|---|---|---|
[Rows based on text]

## 5. Records
List records to be generated (e.g., Concrete Pour Log).

---
SPECIFICATION TEXT:
{spec_text}
---

Output ONLY the Markdown. Do not include introductory text.
"""
    return _run_gemini(prompt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo Spec-to-ITP (Gemini CLI)")
    parser.add_argument("spec_file", help="Ruta a archivo de especificacion (.txt/.md)")
    parser.add_argument("--repo-root", default=os.getenv("SGC_REPO_ROOT", ""), help="Ruta raiz del repo SGC")
    parser.add_argument("--output", default="", help="Ruta de salida (default bajo docs/externos/phase12/)")
    parser.add_argument("--gemini-bin", default="gemini", help="Nombre/ruta del binario gemini")
    parser.add_argument("--timeout-s", type=int, default=DEFAULT_TIMEOUT_S, help="Timeout de ejecucion gemini")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else repo_root()
    spec_path = Path(args.spec_file).expanduser().resolve()
    if not spec_path.exists():
        print(f"ERROR: spec_file no existe: {spec_path}", file=sys.stderr)
        sys.exit(2)

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else (root / "docs/externos/phase12/ITP_Generado_Concreto.md")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    spec_text = spec_path.read_text(encoding="utf-8")

    print(f"Reading: {spec_path}")
    print("Generating ITP with Gemini...")
    markdown_itp = generate_itp(spec_text, title_hint="Concrete (Cast-in-Place)")

    output_path.write_text(markdown_itp, encoding="utf-8")
    print(f"OK: ITP generado en {output_path}")
