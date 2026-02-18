#!/usr/bin/env python3
import sys
import subprocess
import os

def generate_itp(spec_text):
    prompt = f"""
Act as a QA/QC Engineer for a construction project.
Read the following technical specification text for Concrete (Cast-in-Place).
Extract all mandatory requirements, tolerances, and inspection points.

Create a structured Markdown Inspection Test Plan (ITP) following this format:

# IT-SGC-XX [Title based on spec]

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
    
    # Use gemini CLI
    try:
        result = subprocess.run(
            ["gemini", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error calling gemini: {e.stderr}"
    except FileNotFoundError:
        return "Error: 'gemini' CLI not found. Please install it."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python demo_spec_parser.py <spec_file>")
        sys.exit(1)
        
    spec_file = sys.argv[1]
    with open(spec_file, "r") as f:
        spec_text = f.read()
        
    print(f"Reading {spec_file}...")
    print("Generating ITP with Gemini...")
    markdown_itp = generate_itp(spec_text)
    
    output_file = "projects/Sistema-de-Gestion-QA-QC/docs/04_instructivos/IT-SGC-XX_Generated_Concrete_Plan.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        f.write(markdown_itp)
        
    print(f"✅ ITP Generated: {output_file}")
    print("-" * 40)
    print(markdown_itp[:500] + "...\n(truncated)")
