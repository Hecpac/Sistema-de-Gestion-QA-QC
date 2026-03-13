from __future__ import annotations

import os
from pathlib import Path


DEFAULT_MODEL = "gpt-4.1-mini"

# Control directory paths
CONTROL_DIR = "docs/_control"
LMD_PATH = f"{CONTROL_DIR}/lmd.yml"
MATRIX_PATH = f"{CONTROL_DIR}/matriz_registros.yml"
QA_REPORT_PATH = f"{CONTROL_DIR}/reporte_qa_compliance.md"
QA_HISTORY_PATH = f"{CONTROL_DIR}/qa_monitor_history.yml"
DASHBOARD_PATH = f"{CONTROL_DIR}/dashboard_sgc.html"
AUDIT_LOG_PATH = f"{CONTROL_DIR}/audit_changelog.yml"
SNAPSHOT_PATH = f"{CONTROL_DIR}/instrumentacion_sgc.json"
CATALOG_PATH = "docs/06_registros/catalogo_registros.yml"


def repo_root() -> Path:
    raw = os.getenv("SGC_REPO_ROOT", "")
    if raw:
        return Path(raw).resolve()
    # Assume this file is under agent_runtime/sgc_agents
    return Path(__file__).resolve().parents[2]


def model_name() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


def control_dir_path() -> Path:
    """Returns absolute path to control directory."""
    return repo_root() / CONTROL_DIR


def lmd_path() -> Path:
    """Returns absolute path to lmd.yml."""
    return repo_root() / LMD_PATH


def matrix_path() -> Path:
    """Returns absolute path to matriz_registros.yml."""
    return repo_root() / MATRIX_PATH


def qa_report_path() -> Path:
    """Returns absolute path to reporte_qa_compliance.md."""
    return repo_root() / QA_REPORT_PATH


def qa_history_path() -> Path:
    """Returns absolute path to qa_monitor_history.yml."""
    return repo_root() / QA_HISTORY_PATH


def dashboard_path() -> Path:
    """Returns absolute path to dashboard_sgc.html."""
    return repo_root() / DASHBOARD_PATH


def audit_log_path() -> Path:
    """Returns absolute path to audit_changelog.yml."""
    return repo_root() / AUDIT_LOG_PATH


def snapshot_path() -> Path:
    """Returns absolute path to instrumentacion_sgc.json."""
    return repo_root() / SNAPSHOT_PATH


def catalog_path() -> Path:
    """Returns absolute path to catalogo_registros.yml."""
    return repo_root() / CATALOG_PATH
