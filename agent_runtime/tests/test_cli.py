"""Tests for sgc_agents.cli module."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sgc_agents.cli import _safe_int, main


class TestSafeInt:
    def test_valid_int(self) -> None:
        assert _safe_int("42") == 42

    def test_invalid_returns_fallback(self) -> None:
        assert _safe_int("abc") == 10

    def test_none_returns_fallback(self) -> None:
        assert _safe_int(None) == 10  # type: ignore[arg-type]

    def test_custom_fallback(self) -> None:
        assert _safe_int("bad", fallback=5) == 5

    def test_empty_string(self) -> None:
        assert _safe_int("") == 10


class TestMainCli:
    def test_missing_task_exits(self) -> None:
        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["sgc-agent"]):
                main()
        assert exc.value.code != 0

    def test_no_llm_with_orchestrator_mode_exits(
        self, sgc_repo: Path, capsys
    ) -> None:
        with pytest.raises(SystemExit) as exc:
            with patch(
                "sys.argv",
                ["sgc-agent", "--task", "test", "--mode", "orchestrator", "--no-llm"],
            ):
                main()
        assert exc.value.code == 2

    def test_multi_no_llm_runs(self, sgc_repo: Path, capsys) -> None:
        with patch(
            "sys.argv",
            ["sgc-agent", "--task", "test", "--mode", "multi", "--no-llm"],
        ):
            main()
        captured = capsys.readouterr()
        assert "Resultado multiagente" in captured.out
        assert "[control]" in captured.out

    def test_invalid_mode_from_env_exits(
        self, sgc_repo: Path, monkeypatch
    ) -> None:
        monkeypatch.setenv("SGC_AGENT_MODE", "invalid")
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["sgc-agent", "--task", "test"]):
                main()

    def test_missing_api_key_exits(
        self, sgc_repo: Path, monkeypatch, capsys
    ) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(SystemExit) as exc:
            with patch(
                "sys.argv",
                ["sgc-agent", "--task", "test", "--mode", "multi"],
            ):
                main()
        assert exc.value.code == 2
