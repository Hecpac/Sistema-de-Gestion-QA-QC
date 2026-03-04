#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${SGC_REPO_ROOT:-/Users/hector/Projects/SGC}"
RUNTIME_DIR="$REPO_ROOT/agent_runtime"
LOG_DIR="$REPO_ROOT/docs/_control/logs"
HISTORY_FILE="$REPO_ROOT/docs/_control/qa_monitor_history.yml"
LOG_FILE="$LOG_DIR/qa-monitor-$(date +%F).log"
CONSTRAINTS_FILE="${CONSTRAINTS_FILE:-$RUNTIME_DIR/constraints-ci.txt}"

mkdir -p "$LOG_DIR"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[SGC-MONITOR] Inicio: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[SGC-MONITOR] Repo: $REPO_ROOT"

cd "$RUNTIME_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
if [[ -f "$CONSTRAINTS_FILE" ]]; then
  pip install --quiet -c "$CONSTRAINTS_FILE" -e .
else
  pip install --quiet -e .
fi

echo "[SGC-MONITOR] Rebuild de artefactos de control..."
PYTHONPATH="$RUNTIME_DIR" python -m sgc_agents.tools.build_indexes --repo-root "$REPO_ROOT"

echo "[SGC-MONITOR] QA deterministico..."

qa_exit=0
PYTHONPATH="$RUNTIME_DIR" SGC_REPO_ROOT="$REPO_ROOT" \
  python -m sgc_agents.tools.qa_monitor \
    --repo-root "$REPO_ROOT" \
    --history-file "$HISTORY_FILE" || qa_exit=$?

echo "[SGC-MONITOR] Rebuild dashboard final (incluye tendencia)..."
PYTHONPATH="$RUNTIME_DIR" python -m sgc_agents.tools.build_dashboard --repo-root "$REPO_ROOT"

echo "[SGC-MONITOR] Generar snapshot de instrumentacion..."
PYTHONPATH="$RUNTIME_DIR" python -m sgc_agents.tools.build_instrumentation_snapshot --repo-root "$REPO_ROOT"

if [[ "$qa_exit" -ne 0 ]]; then
  echo "[SGC-MONITOR] FALLA: hay hallazgos QA"
  exit "$qa_exit"
fi

echo "[SGC-MONITOR] OK: 0 hallazgos"
echo "[SGC-MONITOR] Fin: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
