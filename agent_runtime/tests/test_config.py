"""Tests for sgc_agents.config module."""
from __future__ import annotations

from pathlib import Path

from sgc_agents.config import (
    CONTROL_DIR,
    DASHBOARD_PATH,
    LMD_PATH,
    MATRIX_PATH,
    QA_HISTORY_PATH,
    QA_REPORT_PATH,
    control_dir_path,
    dashboard_path,
    lmd_path,
    matrix_path,
    model_name,
    qa_history_path,
    qa_report_path,
    repo_root,
)


class TestRepoRoot:
    def test_from_env_var(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("SGC_REPO_ROOT", str(tmp_path))
        assert repo_root() == tmp_path.resolve()

    def test_fallback_to_parents(self, monkeypatch) -> None:
        monkeypatch.delenv("SGC_REPO_ROOT", raising=False)
        root = repo_root()
        assert root.is_dir()
        # Should be 2 levels up from config.py
        assert (root / "agent_runtime").is_dir() or root.name == "SGC"

    def test_empty_env_var_uses_fallback(self, monkeypatch) -> None:
        monkeypatch.setenv("SGC_REPO_ROOT", "")
        root = repo_root()
        assert root.is_dir()


class TestModelName:
    def test_default(self, monkeypatch) -> None:
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        assert model_name() == "gpt-4.1-mini"

    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("OPENAI_MODEL", "gpt-5.4")
        assert model_name() == "gpt-5.4"


class TestPathHelpers:
    def test_control_dir_path(self, sgc_repo: Path) -> None:
        assert control_dir_path() == sgc_repo / CONTROL_DIR

    def test_lmd_path(self, sgc_repo: Path) -> None:
        assert lmd_path() == sgc_repo / LMD_PATH

    def test_matrix_path(self, sgc_repo: Path) -> None:
        assert matrix_path() == sgc_repo / MATRIX_PATH

    def test_qa_report_path(self, sgc_repo: Path) -> None:
        assert qa_report_path() == sgc_repo / QA_REPORT_PATH

    def test_qa_history_path(self, sgc_repo: Path) -> None:
        assert qa_history_path() == sgc_repo / QA_HISTORY_PATH

    def test_dashboard_path(self, sgc_repo: Path) -> None:
        assert dashboard_path() == sgc_repo / DASHBOARD_PATH


class TestPathConstants:
    def test_control_dir_is_relative(self) -> None:
        assert not Path(CONTROL_DIR).is_absolute()

    def test_lmd_under_control(self) -> None:
        assert LMD_PATH.startswith(CONTROL_DIR)

    def test_matrix_under_control(self) -> None:
        assert MATRIX_PATH.startswith(CONTROL_DIR)
