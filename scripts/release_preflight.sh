#!/usr/bin/env bash
set -euo pipefail

# Release preflight for SGC/QMSOps
# - Runs the same critical validations required before production baseline tags.
# - Default behavior installs pinned deps into .venv-ci.
#
# Usage:
#   scripts/release_preflight.sh
#   scripts/release_preflight.sh --skip-install
#   VENV_DIR=.venv-release scripts/release_preflight.sh

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "ERROR: run this script inside a git repository."
  exit 1
fi

cd "${REPO_ROOT}"

VENV_DIR="${VENV_DIR:-.venv-ci}"
SKIP_INSTALL="false"
if [[ "${1:-}" == "--skip-install" ]]; then
  SKIP_INSTALL="true"
fi

run_step() {
  local label="$1"
  shift
  echo
  echo "==> ${label}"
  "$@"
  echo "✓ ${label}"
}

if [[ ! -d "${VENV_DIR}" ]]; then
  run_step "Create virtualenv (${VENV_DIR})" python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

if [[ "${SKIP_INSTALL}" != "true" ]]; then
  run_step "Install pinned dependencies" bash -lc '
    python -m pip install --upgrade pip
    pip install -c ./agent_runtime/constraints-ci.txt -e ./agent_runtime
    pip install -c ./agent_runtime/constraints-ci.txt pytest
  '
else
  echo "==> Skip dependency install (--skip-install)"
fi

run_step "Run unit tests" pytest -q agent_runtime/tests
run_step "Rebuild control indexes" sgc-build-indexes --repo-root "${REPO_ROOT}"
run_step "Rebuild control dashboard" sgc-build-dashboard --repo-root "${REPO_ROOT}"
run_step "Anti-drift verification (docs/_control)" git diff --exit-code -- docs/_control/lmd.yml docs/_control/matriz_registros.yml docs/_control/dashboard_sgc.html

echo
echo "==> Strict baseline policy checks (0 BORRADOR, 0 hallazgos)"
PYTHONPATH=agent_runtime SGC_REPO_ROOT="${REPO_ROOT}" python - <<'PY'
import sys
from pathlib import Path
import yaml

from sgc_agents.tools.compliance_tools import (
    auditar_invariantes_de_estado,
    auditar_claves_frontmatter_desconocidas,
    auditar_secciones_minimas,
    auditar_enlaces_markdown,
    auditar_catalogo_registros,
    resolver_grafo_documental,
    detectar_formatos_huerfanos,
    auditar_trazabilidad_registros,
    auditar_pendientes_matriz_registros,
)

lmd = yaml.safe_load(Path("docs/_control/lmd.yml").read_text(encoding="utf-8")) or {}
docs = lmd.get("documentos", []) if isinstance(lmd, dict) else []
borradores = [
    d for d in docs
    if isinstance(d, dict) and str(d.get("estado", "")).strip() == "BORRADOR"
]

checks = [
    yaml.safe_load(auditar_invariantes_de_estado()) or {},
    yaml.safe_load(auditar_claves_frontmatter_desconocidas()) or {},
    yaml.safe_load(auditar_secciones_minimas()) or {},
    yaml.safe_load(auditar_enlaces_markdown()) or {},
    yaml.safe_load(auditar_catalogo_registros()) or {},
    yaml.safe_load(resolver_grafo_documental()) or {},
    yaml.safe_load(detectar_formatos_huerfanos()) or {},
    yaml.safe_load(auditar_trazabilidad_registros()) or {},
    yaml.safe_load(auditar_pendientes_matriz_registros()) or {},
]

hallazgos = 0
for check in checks:
    findings = check.get("hallazgos", [])
    if isinstance(findings, list):
        hallazgos += len(findings)

print(f"BORRADOR={len(borradores)} | HALLAZGOS={hallazgos}")

if borradores:
    for d in borradores:
        print(f"- BORRADOR: {d.get('codigo','?')} | {d.get('ubicacion','?')}")

if borradores or hallazgos:
    sys.exit(1)
PY
echo "✓ Strict baseline policy checks (0 BORRADOR, 0 hallazgos)"

echo
echo "✅ RELEASE PREFLIGHT PASS"
echo "Repo: ${REPO_ROOT}"
