from __future__ import annotations

from agents import Agent

from .config import model_name
from .specialists import audit_agent, compliance_agent, writer_agent


def build_orchestrator() -> Agent:
    writer = writer_agent()
    compliance = compliance_agent()
    auditor = audit_agent()

    return Agent(
        name="SGC-Orchestrator",
        model=model_name(),
        instructions=(
            "Orquesta tareas del SGC documental. "
            "Enruta a redaccion para crear/actualizar documentos, "
            "a cumplimiento para validaciones y regeneracion determinista de indices, "
            "y a auditoria para paquetes de evidencia. "
            "Prioriza consistencia, trazabilidad y cumplimiento de AGENTS.md."
        ),
        handoffs=[writer, compliance, auditor],
    )
