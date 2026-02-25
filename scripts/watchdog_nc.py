#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


def resolve_repo_root() -> Path:
    env_root = os.getenv("SGC_REPO_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def get_risk_analysis(nc_text: str, risk_matrix_text: str) -> str:
    prompt = f"""
Act as a QA/QC Risk Manager ISO 9001.
Analyze the following CLOSED Non-Conformity (NC) and the current Risk Matrix.

NON-CONFORMITY ROOT CAUSE:
{nc_text}

CURRENT RISK MATRIX:
{risk_matrix_text}

TASK:
1. Determine if the Root Cause of the NC represents a risk that is MISSING or UNDER-RATED in the current matrix.
2. If it is missing, propose a NEW row for the risk matrix.
3. If it is covered, state "RISK COVERED".

OUTPUT FORMAT:
If missing, output ONLY the Markdown table row for the new risk (no header).
Example: | R-NEW | Process | Description | High | High | High | Proposed Control |
If covered, output ONLY: RISK COVERED
"""

    try:
        result = subprocess.run(
            ["gemini", prompt],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"


def extract_root_cause(content: str) -> str:
    patterns = [
        r"Causa\s*Ra[ií]z.*?:(.*?)(##|\Z)",
        r"causa raiz reportada\s*:\s*(.*?)(\n|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def is_nc_candidate(content: str) -> bool:
    closed_markers = ('estado: "CERRADA"', "estado: CERRADA")
    if any(marker in content for marker in closed_markers):
        return True

    # Wrapper mode (REG) for FOR-SGC-02 NC records.
    wrapper_markers = ('formato_origen: "FOR-SGC-02"', "formato_origen: FOR-SGC-02")
    return any(marker in content for marker in wrapper_markers)


def main() -> int:
    repo_root = resolve_repo_root()
    nc_dir = repo_root / "docs/06_registros/no_conformidades"
    risk_file = repo_root / "docs/06_registros/riesgos/REG-SGC-RISK-2026-Q1.md"
    output_file = repo_root / "docs/08_riesgos/PROPOSED_RISKS.md"

    print("🔍 RISK WATCHDOG AGENT ACTIVATED")
    print(f"Repo root: {repo_root}")
    print(f"Scanning closed NCs in: {nc_dir}")

    if not nc_dir.exists():
        print(f"Error: NC directory not found: {nc_dir}")
        return 1
    if not risk_file.exists():
        print(f"Error: risk matrix file not found: {risk_file}")
        return 1

    risk_matrix_content = risk_file.read_text(encoding="utf-8")
    new_risks_found: list[str] = []

    for path in sorted(nc_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")

        if not is_nc_candidate(content):
            continue

        root_cause = extract_root_cause(content)
        if not root_cause:
            print(f"- Skipping {path.name}: no root cause found")
            continue

        print(f"\n⚡ Analyzing NC: {path.name}")
        print(f"   Root Cause: {root_cause[:80]}...")

        analysis = get_risk_analysis(root_cause, risk_matrix_content)
        print(f"   🤖 Agent Assessment:\n{analysis}")

        if "|" in analysis and "RISK COVERED" not in analysis and not analysis.startswith("Error:"):
            new_risks_found.append(analysis)

    if new_risks_found:
        print("\n🚨 NEW RISKS DETECTED! Proposed updates for Risk Matrix:")
        for risk in new_risks_found:
            print(risk)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8") as handle:
            handle.write("# Proposed Risk Matrix Updates\n\n")
            handle.write("| ID | Proceso | Riesgo | Probabilidad | Impacto | Nivel | Control Actual |\n")
            handle.write("|---|---|---|---|---|---|---|\n")
            for risk in new_risks_found:
                handle.write(risk + "\n")

        print(f"\n✅ Proposal saved to {output_file}")
    else:
        print("\nℹ️ No new risks detected.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
