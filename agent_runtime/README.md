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

## Uso rapido
```bash
sgc-agent --task "Genera un borrador de PR-SGC-02 y valida control documental"
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
