"""Tests for sgc_agents.specialists module."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from sgc_agents.specialists import (
    audit_agent,
    compliance_agent,
    control_agent,
    documentation_agent,
    writer_agent,
)


class TestWriterAgent:
    def test_returns_agent(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            agent = writer_agent()
            assert agent is not None

    def test_name(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            writer_agent()
            assert MockAgent.call_args.kwargs["name"] == "SGC-Writer"

    def test_uses_writer_tools(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            writer_agent()
            tools = MockAgent.call_args.kwargs["tools"]
            assert isinstance(tools, list)
            assert len(tools) > 0

    def test_instructions_mention_iso(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            writer_agent()
            instructions = MockAgent.call_args.kwargs["instructions"]
            assert "ISO 9001" in instructions


class TestComplianceAgent:
    def test_returns_agent(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            agent = compliance_agent()
            assert agent is not None

    def test_name(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            compliance_agent()
            assert MockAgent.call_args.kwargs["name"] == "SGC-Compliance"

    def test_uses_all_tools(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            compliance_agent()
            tools = MockAgent.call_args.kwargs["tools"]
            assert isinstance(tools, list)


class TestAuditAgent:
    def test_returns_agent(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            agent = audit_agent()
            assert agent is not None

    def test_name(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            audit_agent()
            assert MockAgent.call_args.kwargs["name"] == "SGC-Auditoria"


class TestBackwardCompat:
    def test_documentation_agent_is_writer(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            documentation_agent()
            assert MockAgent.call_args.kwargs["name"] == "SGC-Writer"

    def test_control_agent_is_compliance(self) -> None:
        with patch("sgc_agents.specialists.Agent") as MockAgent:
            MockAgent.return_value = MagicMock()
            control_agent()
            assert MockAgent.call_args.kwargs["name"] == "SGC-Compliance"
