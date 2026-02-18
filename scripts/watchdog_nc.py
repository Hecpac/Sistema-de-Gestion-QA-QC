#!/usr/bin/env python3
import sys
import subprocess
import os
import re

def get_risk_analysis(nc_text, risk_matrix_text):
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
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    nc_dir = "projects/Sistema-de-Gestion-QA-QC/docs/06_registros/no_conformidades"
    risk_file = "projects/Sistema-de-Gestion-QA-QC/docs/06_registros/riesgos/REG-SGC-RISK-2026-Q1.md"
    
    print(f"🔍 RISK WATCHDOG AGENT ACTIVATED")
    print(f"Scanning closed NCs in: {nc_dir}")
    
    # Read Risk Matrix
    with open(risk_file, 'r') as f:
        risk_matrix_content = f.read()
    
    # Scan NCs
    new_risks_found = []
    
    for filename in os.listdir(nc_dir):
        if not filename.endswith(".md"): continue
        
        filepath = os.path.join(nc_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Check if CLOSED
        if "estado: \"CERRADA\"" not in content and "estado: CERRADA" not in content:
            continue
            
        # Extract Root Cause (simple regex for demo)
        match = re.search(r"Causa Raíz.*?:(.*?)(##|\Z)", content, re.DOTALL | re.IGNORECASE)
        if match:
            root_cause = match.group(1).strip()
            print(f"\n⚡ Analyzing NC: {filename}")
            print(f"   Root Cause: {root_cause[:80]}...")
            
            # Consult Agent
            analysis = get_risk_analysis(root_cause, risk_matrix_content)
            print(f"   🤖 Agent Assessment: \n{analysis}")
            
            if "|" in analysis and "RISK COVERED" not in analysis:
                new_risks_found.append(analysis)
    
    if new_risks_found:
        print("\n🚨 NEW RISKS DETECTED! Proposed updates for Risk Matrix:")
        for risk in new_risks_found:
            print(risk)
        
        # In a real agent, this would create a Pull Request.
        # Here we append to a "proposed_changes.md" file.
        with open("projects/Sistema-de-Gestion-QA-QC/docs/08_riesgos/PROPOSED_RISKS.md", "w") as f:
            f.write("# Proposed Risk Matrix Updates\n\n")
            f.write("| ID | Proceso | Riesgo | Probabilidad | Impacto | Nivel | Control Actual |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for risk in new_risks_found:
                f.write(risk + "\n")
        print("\n✅ Proposal saved to docs/08_riesgos/PROPOSED_RISKS.md")

if __name__ == "__main__":
    main()
