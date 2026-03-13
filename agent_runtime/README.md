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

## Arquitectura interna

### config.py — Paths centralizados
Todas las rutas de control (`lmd.yml`, `matriz_registros.yml`, `audit_changelog.yml`, etc.) estan definidas como constantes en `sgc_agents/config.py` con funciones helper que resuelven la ruta absoluta via `repo_root()`. Ningun modulo debe hardcodear paths de `docs/_control/`.

### schemas.py — Validacion Pydantic
Los modelos `DocumentFrontmatter`, `LmdEntry`, `RecordFrontmatter`, `MatrixRecordEntry` validan frontmatter y entradas de indices. Los validators de `codigo` y `version` estan consolidados en `_check_doc_code()` y `_check_doc_version()`.

### compliance_tools.py — Funciones de auditoria
Las funciones `auditar_*` siguen un patron estandar via `_run_vigente_audit(skill, checker)`. Los 5 axiomas de trazabilidad (P1-P5) estan separados en funciones individuales (`_validate_p1_procedencia`, ..., `_validate_p5_isomorfismo`).

### build_indexes.py — Generacion determinista
`_yaml_items_by_code(root, rel_path, top_key)` es el helper generico para cargar items indexados por codigo desde cualquier YAML de control.

### templates/dashboard.html
Template HTML extraido de `build_dashboard.py`, editable y previsualizable independientemente.

## CI / GitHub Actions
- `sgc-qa.yml` — Quality gate en PR y push a main (tests + rebuild + anti-drift + link audit + QA checks)
- `sgc-baseline-gate.yml` — Gate estricto en tags `sgc-*` (0 hallazgos, 0 BORRADOR, 0 pendientes)
- `sgc-weekly-monitor.yml` — Monitor semanal con issue automatico si hay fallas
- `sgc-monitor-watchdog.yml` — Watchdog del monitor

## Notas
- Este runtime asume que el `cwd` es la raiz del repo SGC.
- Los cambios documentales deben respetar `AGENTS.md`.
- `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml` se consideran artefactos generados.
