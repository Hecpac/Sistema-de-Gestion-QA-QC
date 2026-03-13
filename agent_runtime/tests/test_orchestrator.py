"""Tests for sgc_agents.orchestrator module."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from sgc_agents.orchestrator import build_orchestrator


class TestBuildOrchestrator:
    def test_returns_agent(self) -> None:
        with patch("sgc_agents.orchestrator.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            agent = build_orchestrator()
            assert agent is not None

    def test_agent_name(self) -> None:
        with patch("sgc_agents.orchestrator.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            build_orchestrator()
            call_kwargs = MockAgent.call_args
            assert call_kwargs.kwargs["name"] == "SGC-Orchestrator"

    def test_uses_model_name(self, monkeypatch) -> None:
        monkeypatch.setenv("OPENAI_MODEL", "test-model")
        with patch("sgc_agents.orchestrator.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            build_orchestrator()
            assert MockAgent.call_args.kwargs["model"] == "test-model"

    def test_has_three_handoffs(self) -> None:
        with patch("sgc_agents.orchestrator.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            build_orchestrator()
            handoffs = MockAgent.call_args.kwargs["handoffs"]
            assert len(handoffs) == 3

    def test_instructions_mention_sgc(self) -> None:
        with patch("sgc_agents.orchestrator.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            build_orchestrator()
            instructions = MockAgent.call_args.kwargs["instructions"]
            assert "SGC" in instructions
