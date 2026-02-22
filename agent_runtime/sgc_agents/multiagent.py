from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agents import Runner

from .config import repo_root
from .specialists import audit_agent, writer_agent
from .tools.build_dashboard import build_dashboard
from .tools.build_indexes import BuildIndexesSummary, build_indexes
from .tools.compliance_tools import generar_reporte_qa_compliance

_QA_REPORT_REL = "docs/_control/reporte_qa_compliance.md"

_ERR_EVENT_LOOP_ACTIVE = (
            "No se puede usar run_multiagent_task_sync() con un event loop activo. "
            "Usa: await run_multiagent_task(...)."
)


@dataclass(frozen=True)
class ComplianceArtifacts:
            indexes: BuildIndexesSummary
            qa_report_path: Path
            dashboard_path: Path


@dataclass(frozen=True)
class MultiAgentResult:
            compliance: ComplianceArtifacts
            writer_output: str | None
            auditor_output: str | None

    def render_text(self) -> str:
                    parts: list[str] = []
                    parts.append("# Resultado multiagente (SGC)")
                    parts.append("")
                    parts.append("## Compliance (deterministico)")
                    parts.append(f"- Indices: {self.compliance.indexes.as_text()}")
                    parts.append(f"- QA report: {self.compliance.qa_report_path.as_posix()}")
                    parts.append(f"- Dashboard: {self.compliance.dashboard_path.as_posix()}")
                    if self.writer_output:
                                        parts.append("")
                                        parts.append("## Writer")
                                        parts.append(self.writer_output.strip())
                                    if self.auditor_output:
                                                        parts.append("")
                                                        parts.append("## Auditoria")
                                                        parts.append(self.auditor_output.strip())

        return "\n".join(parts).rstrip() + "\n"


def _run_compliance_pipeline() -> ComplianceArtifacts:
            root = repo_root().resolve()
    indexes = build_indexes(root)
    generar_reporte_qa_compliance()
    dashboard_path = build_dashboard(root)
    return ComplianceArtifacts(
                    indexes=indexes,
                    qa_report_path=(root / _QA_REPORT_REL).resolve(),
                    dashboard_path=dashboard_path.resolve(),
    )


def _writer_prompt(task: str) -> str:
            return (
                            "Tarea (usuario):\n"
                            f"{task.strip()}\n\n"
                            "Rol: redacta/propon cambios documentales y/o instrucciones operativas para el repo SGC.\n"
                            "Reglas:\n"
                            "- Respeta AGENTS.md y docs/AGENTS.md.\n"
                            "- No inventes datos organizacionales; usa TODO/<NOMBRE_EMPRESA>/<PUESTO>/<AREA>.\n"
                            "- No ejecutes herramientas que regeneren artefactos; no edites docs/_control.\n"
                            "Entrega:\n"
                            "- Propuesta concreta (archivos a crear/editar, con rutas sugeridas) y criterios de aceptacion.\n"
            )


def _audit_prompt(task: str) -> str:
            return (
                            "Tarea (usuario):\n"
                            f"{task.strip()}\n\n"
                            "Rol: auditor interno ISO 9001.\n"
                            "Entrega:\n"
                            "- Riesgos de incumplimiento/deriva documental, evidencias requeridas y checklist de verificacion.\n"
                            "- Hallazgos potenciales (si aplica) y acciones sugeridas.\n"
            )


async def run_multiagent_task(
            task: str,
            *,
            include_llm: bool = True,
            max_turns: int = 10,
) -> MultiAgentResult:
            """Ejecuta una tarea con enfoque multiagente.

                Corre en paralelo:
                        - Pipeline deterministico (rebuild indices + QA report + dashboard).
                                - Writer (propuesta/redaccion) y Auditoria (checklist/riesgos) si `include_llm=True`.

                                    Devuelve siempre el resultado del pipeline deterministico aunque falle algun agente LLM.
                                        """
    # Lanzar todas las tareas concurrentemente
    compliance_future = asyncio.to_thread(_run_compliance_pipeline)

    writer_future: Any | None = None
    auditor_future: Any | None = None
    if include_llm:
                    writer_future = Runner.run(writer_agent(), _writer_prompt(task), max_turns=max_turns)
        auditor_future = Runner.run(audit_agent(), _audit_prompt(task), max_turns=max_turns)

    # Esperar todas las tareas en paralelo
    if include_llm and writer_future and auditor_future:
                    compliance, writer_result, auditor_result = await asyncio.gather(
                        compliance_future,
                        writer_future,
                        auditor_future,
                        return_exceptions=True,
    )
else:
        compliance = await compliance_future
        writer_result = None
        auditor_result = None

    # Si compliance fallo, propagar (es critico)
    if isinstance(compliance, Exception):
                    raise compliance

    writer_output: str | None = None
    auditor_output: str | None = None

    if writer_result is not None:
                    if isinstance(writer_result, Exception):
                                        writer_output = f"ERROR: writer fallo: {writer_result}"
else:
            writer_output = getattr(writer_result, "final_output", None)

    if auditor_result is not None:
                    if isinstance(auditor_result, Exception):
                                        auditor_output = f"ERROR: auditoria fallo: {auditor_result}"
else:
            auditor_output = getattr(auditor_result, "final_output", None)

    return MultiAgentResult(
                    compliance=compliance,
                    writer_output=writer_output,
                    auditor_output=auditor_output,
    )


def run_multiagent_task_sync(
            task: str,
            *,
            include_llm: bool = True,
            max_turns: int = 10,
) -> MultiAgentResult:
            """Wrapper sincrono.

                Nota: si ya existe un event loop corriendo (por ejemplo, Jupyter/async frameworks),
                        se debe llamar a `await run_multiagent_task(...)` directamente.
                            """
    try:
                    asyncio.get_running_loop()
except RuntimeError:
        return asyncio.run(
                            run_multiagent_task(task, include_llm=include_llm, max_turns=max_turns)
        )
    raise RuntimeError(_ERR_EVENT_LOOP_ACTIVE)
