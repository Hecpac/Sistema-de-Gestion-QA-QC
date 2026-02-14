# SGC + Codex Starter Kit (ISO 9001)

Este repositorio es un **kit de arranque** para construir y mantener un **Sistema de Gestion de Calidad (SGC)** en formato **documental** (Markdown), pensado para trabajar con **OpenAI Codex** como agente que crea/edita archivos y mantiene la trazabilidad.

## Que incluye
- Estructura de carpetas para documentacion del SGC.
- Plantillas (procedimientos, instructivos, formatos, fichas de proceso).
- Runtime de agentes en codigo con OpenAI Agents SDK (`agent_runtime/`).
- Skills locales del proyecto para Codex (`.agents/skills/`).
- Control documental base:
  - Lista maestra de documentos (`docs/_control/lmd.yml`)
  - Matriz de registros (`docs/_control/matriz_registros.yml`)
  - Solicitud de cambio documental (`docs/_control/FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md`)
- Un procedimiento ya emitido como ejemplo:
  - `PR-SGC-01 Control de Documentos y Registros`

## Runtime de agentes (Python)
Ubicacion: `agent_runtime/`

Comandos base:
```bash
cd /Users/hector/Projects/SGC/agent_runtime
python -m venv .venv
source .venv/bin/activate
pip install -e .
sgc-agent --task "Valida trazabilidad documental del SGC"
```

Comando de control determinista:
```bash
sgc-build-indexes
sgc-build-dashboard
```

Variables:
- `OPENAI_API_KEY` (obligatoria)
- `OPENAI_MODEL` (opcional, default `gpt-4.1-mini`)
- `SGC_REPO_ROOT` (opcional)

## Como usar con Codex
1. Coloca/abre este repositorio en tu editor o terminal.
2. Asegurate de tener un `AGENTS.md` en la raiz (ya incluido). Codex lo lee antes de trabajar.
3. Trabaja por **tareas pequenas** (un documento por tarea) y pide a Codex que:
   - cree/actualice el documento,
   - valide frontmatter,
   - regenere indices con `sgc-build-indexes`.

> Nota: si necesitas exportar a Word/PDF, puedes hacerlo mas adelante. El objetivo aqui es mantener el **control de versiones y consistencia** en el repositorio.

## Fecha
Actualizado el 2026-02-14.
