from __future__ import annotations

import os
from pathlib import Path


DEFAULT_MODEL = "gpt-4.1-mini"


def repo_root() -> Path:
    raw = os.getenv("SGC_REPO_ROOT", "")
    if raw:
        return Path(raw).resolve()
    # Assume this file is under agent_runtime/sgc_agents
    return Path(__file__).resolve().parents[2]


def model_name() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
