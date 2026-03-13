"""Tests for sgc_agents.multiagent module."""
from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sgc_agents.multiagent import (
    ComplianceArtifacts,
    MultiAgentResult,
    _audit_prompt,
    _run_compliance_pipeline,
    _writer_prompt,
    run_multiagent_task,
    run_multiagent_task_sync,
)
from sgc_agents.tools.build_indexes import BuildIndexesSummary


# --- Dataclass tests ---


class TestComplianceArtifacts:
    def test_immutable(self) -> None:
        artifacts = ComplianceArtifacts(
            indexes=MagicMock(),
            qa_report_path=Path("/tmp/qa.md"),
            dashboard_path=Path("/tmp/dash.html"),
        )
        with pytest.raises(AttributeError):
            artifacts.indexes = MagicMock()  # type: ignore[misc]


class TestMultiAgentResult:
    def _make_result(
        self, writer: str | None = None, auditor: str | None = None
    ) -> MultiAgentResult:
        mock_indexes = MagicMock(spec=BuildIndexesSummary)
        mock_indexes.as_text.return_value = "lmd=5 matrix=3"
        artifacts = ComplianceArtifacts(
            indexes=mock_indexes,
            qa_report_path=Path("/tmp/qa.md"),
            dashboard_path=Path("/tmp/dash.html"),
        )
        return MultiAgentResult(
            compliance=artifacts,
            writer_output=writer,
            auditor_output=auditor,
        )

    def test_render_text_compliance_only(self) -> None:
        result = self._make_result()
        text = result.render_text()
        assert "# Resultado multiagente (SGC)" in text
        assert "## Compliance" in text
        assert "Writer" not in text
        assert "Auditoria" not in text

    def test_render_text_with_writer(self) -> None:
        result = self._make_result(writer="Propuesta de documento")
        text = result.render_text()
        assert "## Writer" in text
        assert "Propuesta de documento" in text

    def test_render_text_with_auditor(self) -> None:
        result = self._make_result(auditor="Hallazgos de auditoria")
        text = result.render_text()
        assert "## Auditoria" in text
        assert "Hallazgos de auditoria" in text

    def test_render_text_ends_with_newline(self) -> None:
        result = self._make_result()
        assert result.render_text().endswith("\n")


# --- Prompt builders ---


class TestPromptBuilders:
    def test_writer_prompt_contains_task(self) -> None:
        prompt = _writer_prompt("Crear procedimiento PR-SGC-99")
        assert "Crear procedimiento PR-SGC-99" in prompt
        assert "redacta" in prompt.lower()

    def test_audit_prompt_contains_task(self) -> None:
        prompt = _audit_prompt("Revisar trazabilidad")
        assert "Revisar trazabilidad" in prompt
        assert "auditor" in prompt.lower()

    def test_writer_prompt_strips_whitespace(self) -> None:
        prompt = _writer_prompt("  task with spaces  ")
        assert "task with spaces" in prompt

    def test_audit_prompt_strips_whitespace(self) -> None:
        prompt = _audit_prompt("  task with spaces  ")
        assert "task with spaces" in prompt


# --- Pipeline tests ---


class TestRunCompliancePipeline:
    def test_returns_compliance_artifacts(self, sgc_repo: Path) -> None:
        result = _run_compliance_pipeline()
        assert isinstance(result, ComplianceArtifacts)
        assert result.qa_report_path.is_file()
        assert result.dashboard_path.is_file()


# --- Async tests ---


class TestRunMultiagentTask:
    @pytest.mark.asyncio
    async def test_no_llm_returns_result(self, sgc_repo: Path) -> None:
        result = await run_multiagent_task(
            "Test task", include_llm=False
        )
        assert isinstance(result, MultiAgentResult)
        assert result.writer_output is None
        assert result.auditor_output is None
        assert isinstance(result.compliance, ComplianceArtifacts)


class TestRunMultiagentTaskSync:
    def test_no_llm_returns_result(self, sgc_repo: Path) -> None:
        result = run_multiagent_task_sync(
            "Test task", include_llm=False
        )
        assert isinstance(result, MultiAgentResult)
        assert result.compliance.indexes is not None

    def test_raises_in_active_loop(self, sgc_repo: Path) -> None:
        async def _inner():
            with pytest.raises(RuntimeError, match="event loop"):
                run_multiagent_task_sync("Test", include_llm=False)

        asyncio.run(_inner())
