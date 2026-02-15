#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${SGC_REPO_ROOT:-/Users/hector/Projects/SGC}"
RUNTIME_DIR="$REPO_ROOT/agent_runtime"
LOG_DIR="$REPO_ROOT/docs/_control/logs"
LOG_FILE="$LOG_DIR/qa-monitor-$(date +%F).log"

mkdir -p "$LOG_DIR"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[SGC-MONITOR] Inicio: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[SGC-MONITOR] Repo: $REPO_ROOT"

cd "$RUNTIME_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --quiet -e .

echo "[SGC-MONITOR] Rebuild de artefactos de control..."
PYTHONPATH="$RUNTIME_DIR" python -m sgc_agents.tools.build_indexes --repo-root "$REPO_ROOT"
PYTHONPATH="$RUNTIME_DIR" python -m sgc_agents.tools.build_dashboard --repo-root "$REPO_ROOT"

echo "[SGC-MONITOR] QA deterministico..."
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
printf 'def function_tool(fn):\n    return fn\n' > "$TMPDIR/agents.py"

PYTHONPATH="$TMPDIR:$RUNTIME_DIR" SGC_REPO_ROOT="$REPO_ROOT" python - <<'PY'
import sys
import yaml
from sgc_agents.tools.compliance_tools import (
  auditar_invariantes_de_estado,
  resolver_grafo_documental,
  detectar_formatos_huerfanos,
  auditar_trazabilidad_registros,
  generar_reporte_qa_compliance,
)

print(generar_reporte_qa_compliance())
checks = [
  yaml.safe_load(auditar_invariantes_de_estado()) or {},
  yaml.safe_load(resolver_grafo_documental()) or {},
  yaml.safe_load(detectar_formatos_huerfanos()) or {},
  yaml.safe_load(auditar_trazabilidad_registros()) or {},
]

hallazgos = 0
for check in checks:
  findings = check.get("hallazgos", [])
  if isinstance(findings, list):
    hallazgos += len(findings)

print(f"hallazgos_totales={hallazgos}")
if hallazgos:
  sys.exit(1)
PY

echo "[SGC-MONITOR] OK: 0 hallazgos"
echo "[SGC-MONITOR] Fin: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
