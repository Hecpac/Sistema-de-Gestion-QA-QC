from __future__ import annotations

from agents import Agent

from .config import model_name
from .tools.document_tools import all_tools


def writer_agent() -> Agent:
    return Agent(
        name="SGC-Writer",
        model=model_name(),
        instructions=(
            "Eres especialista en redaccion documental SGC ISO 9001:2015. "
            "Creas y actualizas documentos Markdown controlados con frontmatter YAML valido, "
            "siguiendo AGENTS.md y estructura minima. "
            "No inventes datos organizacionales; usa placeholders TODO y <NOMBRE_EMPRESA>/<PUESTO>/<AREA>."
        ),
        tools=list(all_tools()),
    )


def compliance_agent() -> Agent:
    return Agent(
        name="SGC-Compliance",
        model=model_name(),
        instructions=(
            "Eres responsable de cumplimiento documental con enfoque neuro-simbolico. "
            "Ejecuta pipeline determinista: "
            "1) auditar_invariantes_de_estado, "
            "2) resolver_grafo_documental, "
            "3) detectar_formatos_huerfanos, "
            "4) auditar_trazabilidad_registros (P1..P5). "
            "No edites manualmente docs/_control/lmd.yml ni docs/_control/matriz_registros.yml; "
            "siempre ejecuta rebuild_control_indexes para regenerar indices antes de cerrar. "
            "Si hay incumplimientos, genera reporte con generar_reporte_qa_compliance y redacta hallazgos claros."
        ),
        tools=list(all_tools()),
    )


def audit_agent() -> Agent:
    return Agent(
        name="SGC-Auditoria",
        model=model_name(),
        instructions=(
            "Eres auditor interno ISO 9001. Preparas paquetes de auditoria con hallazgos, "
            "evidencias requeridas, riesgos de trazabilidad y plan de cierre."
        ),
        tools=list(all_tools()),
    )


# Backward compatibility names.
def documentation_agent() -> Agent:
    return writer_agent()


# Backward compatibility names.
def control_agent() -> Agent:
    return compliance_agent()
