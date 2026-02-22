# SGC Agent Runtime (OpenAI Agents SDK)

Este runtime implementa una orquestacion multiagente para mantener el SGC documental del repositorio.

## Requisitos
- Python 3.11+
- `OPENAI_API_KEY` configurada

## Instalacion
```bash
cd /Users/hector/Projects/SGC/agent_runtime
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Dependencias deterministas (CI/monitor)
Este repo incluye `agent_runtime/constraints-ci.txt` para reducir drift por dependencias mutables.

En CI, el workflow instala el runtime usando constraints:
```bash
pip install -c ./agent_runtime/constraints-ci.txt -e ./agent_runtime
```

## Uso rapido
```bash
sgc-agent --task "Genera un borrador de PR-SGC-02 y valida control documental"
```

### Modo multiagente (recomendado)
Ejecuta en paralelo:
- Pipeline deterministico (rebuild indices + QA report + dashboard).
- Agente writer (propuesta/redaccion).
- Agente auditoria (checklist y riesgos).

```bash
sgc-agent --mode multi --task "Valida trazabilidad documental y sugiere mejoras"
```

Modo deterministico sin LLM (sin `OPENAI_API_KEY`):
```bash
sgc-agent --mode multi --no-llm --task "Rebuild + QA"
```

## Rebuild de indices y dashboard
```bash
sgc-build-indexes
sgc-build-dashboard
```

## Monitor QA proactivo (local)
Script:
```bash
bash /Users/hector/Projects/SGC/agent_runtime/scripts/run_qa_monitor.sh
```

Salida:
- Log: `docs/_control/logs/qa-monitor-YYYY-MM-DD.log`
- Historial: `docs/_control/qa_monitor_history.yml`
- Artefactos actualizados: `lmd.yml`, `matriz_registros.yml`, `dashboard_sgc.html`, `reporte_qa_compliance.md`

## Monitor QA semanal (GitHub Actions)
Workflow: `.github/workflows/sgc-weekly-monitor.yml`
- Corre cada lunes (UTC)
- Publica artifacts del monitor
- Crea issue automatico si hay falla

## Diseno
- Agente orquestador: enruta al especialista adecuado.
- Agente writer: crea/actualiza documentos controlados.
- Agente compliance (QA): valida calidad documental y regenera indices deterministas.
- Agente de auditoria: prepara paquetes de evidencia.

## Notas
- Este runtime asume que el `cwd` es la raiz del repo SGC.
- Los cambios documentales deben respetar `AGENTS.md`.
- `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml` se consideran artefactos generados.
