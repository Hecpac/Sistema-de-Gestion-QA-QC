#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${SGC_REPO_ROOT:-/Users/hector/Projects/SGC}"
RUNTIME_DIR="$REPO_ROOT/agent_runtime"
LOG_DIR="$REPO_ROOT/docs/_control/logs"
HISTORY_FILE="$REPO_ROOT/docs/_control/qa_monitor_history.yml"
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

echo "[SGC-MONITOR] QA deterministico..."

qa_exit=0
PYTHONPATH="$RUNTIME_DIR" SGC_REPO_ROOT="$REPO_ROOT" HISTORY_FILE="$HISTORY_FILE" python - <<'PY' || qa_exit=$?
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

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

history_path = Path(os.environ["HISTORY_FILE"])
history_path.parent.mkdir(parents=True, exist_ok=True)

payload = {}
if history_path.exists():
  payload = yaml.safe_load(history_path.read_text(encoding="utf-8")) or {}
if not isinstance(payload, dict):
  payload = {}

runs = payload.get("runs", [])
if not isinstance(runs, list):
  runs = []

now = datetime.now(timezone.utc)
runs.append(
  {
    "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "date": now.strftime("%Y-%m-%d"),
    "hallazgos": int(hallazgos),
    "source": "github-actions" if os.getenv("GITHUB_ACTIONS") == "true" else "local",
  }
)

runs = sorted(
  [r for r in runs if isinstance(r, dict)],
  key=lambda r: (str(r.get("timestamp", "")), str(r.get("date", ""))),
)

payload["runs"] = runs[-60:]
header = (
  "# Historial de monitor QA del SGC\n"
  "# Archivo autogenerado por run_qa_monitor.sh\n"
  "# No editar manualmente\n\n"
)
history_path.write_text(
  header + yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
  encoding="utf-8",
)

if hallazgos:
  sys.exit(1)
PY

echo "[SGC-MONITOR] Rebuild dashboard final (incluye tendencia)..."
PYTHONPATH="$RUNTIME_DIR" python -m sgc_agents.tools.build_dashboard --repo-root "$REPO_ROOT"

if [[ "$qa_exit" -ne 0 ]]; then
  echo "[SGC-MONITOR] FALLA: hay hallazgos QA"
  exit "$qa_exit"
fi

echo "[SGC-MONITOR] OK: 0 hallazgos"
echo "[SGC-MONITOR] Fin: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
