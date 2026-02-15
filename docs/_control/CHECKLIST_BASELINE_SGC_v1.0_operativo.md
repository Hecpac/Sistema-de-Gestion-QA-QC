# CHECKLIST BASELINE SGC v1.0 OPERATIVO

- Fecha de corte: 2026-02-15
- Estado objetivo: `31 VIGENTE / 0 BORRADOR`
- Alcance: baseline documental para auditoria interna/externa ISO 9001:2015

## 1) Integridad de repositorio
- [ ] `git status` limpio (sin cambios pendientes)
- [ ] Baseline commit identificado: `80e7ccb` (cierre de promocion a VIGENTE)
- [ ] Tag de baseline presente: `sgc-v1.0-operativo`

## 2) Evidencia de control documental
- [ ] Lista Maestra actualizada: `docs/_control/lmd.yml`
- [ ] Matriz de registros actualizada: `docs/_control/matriz_registros.yml`
- [ ] Dashboard de control actualizado: `docs/_control/dashboard_sgc.html`
- [ ] Reporte QA/compliance actualizado: `docs/_control/reporte_qa_compliance.md`

## 3) Evidencia de sistema documental minimo (ISO 9001)
### 3.1 Gobierno
- [ ] `docs/01_politica_objetivos/POL-SGC-01_Politica_de_Calidad.md`
- [ ] `docs/01_politica_objetivos/PLAN-SGC-01_Objetivos_de_Calidad_y_Seguimiento.md`
- [ ] `docs/03_procedimientos/PR-SGC-05_Revision_por_la_Direccion.md`

### 3.2 Control documental
- [ ] `docs/03_procedimientos/PR-SGC-01_Control_de_Documentos_y_Registros.md`
- [ ] `docs/_control/FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md`

### 3.3 Mejora / NC-CAPA
- [ ] `docs/03_procedimientos/PR-SGC-02_Control_de_No_Conformidades_y_CAPA.md`
- [ ] `docs/05_formatos/FOR-SGC-02_Registro_de_No_Conformidad.md`
- [ ] `docs/05_formatos/FOR-SGC-03_Plan_y_Registro_CAPA.md`

### 3.4 Auditoria interna
- [ ] `docs/07_auditorias/PR-SGC-03_Auditorias_Internas.md`
- [ ] `docs/07_auditorias/FOR-SGC-04_Programa_Anual_de_Auditorias.md`
- [ ] `docs/07_auditorias/FOR-SGC-05_Plan_de_Auditoria.md`
- [ ] `docs/07_auditorias/FOR-SGC-06_Informe_de_Auditoria.md`
- [ ] `docs/07_auditorias/FOR-SGC-07_Seguimiento_de_Acciones_de_Auditoria.md`

### 3.5 KPI / Desempeno
- [ ] `docs/03_procedimientos/PR-SGC-04_Gestion_de_Indicadores_y_Analisis_de_Datos.md`
- [ ] `docs/05_formatos/FOR-SGC-08_Matriz_de_KPI.md`
- [ ] `docs/05_formatos/FOR-SGC-09_Acta_de_Revision_por_la_Direccion.md`

### 3.6 Riesgos y oportunidades
- [ ] `docs/08_riesgos/PR-SGC-06_Gestion_de_Riesgos_y_Oportunidades.md`
- [ ] `docs/08_riesgos/FOR-SGC-10_Matriz_de_Riesgos_y_Oportunidades.md`
- [ ] `docs/08_riesgos/FOR-SGC-11_Plan_de_Tratamiento_y_Seguimiento_de_Riesgos.md`

### 3.7 Proveedores
- [ ] `docs/09_proveedores/PR-SGC-07_Evaluacion_y_Reevaluacion_de_Proveedores.md`
- [ ] `docs/09_proveedores/FOR-SGC-12_Matriz_de_Homologacion_y_Evaluacion_de_Proveedores.md`

### 3.8 Competencia y formacion
- [ ] `docs/10_competencia_formacion/PR-SGC-08_Competencia_y_Formacion.md`
- [ ] `docs/10_competencia_formacion/FOR-SGC-13_Matriz_de_Competencias.md`
- [ ] `docs/10_competencia_formacion/FOR-SGC-14_Plan_y_Registro_de_Capacitacion.md`
- [ ] `docs/10_competencia_formacion/FOR-SGC-15_Evaluacion_de_Eficacia_de_Capacitacion.md`

### 3.9 Arquitectura de procesos
- [ ] `docs/02_mapa_procesos/ESP-SGC-01_Mapa_de_Procesos_del_SGC.md`
- [ ] `docs/02_mapa_procesos/fichas_proceso/ESP-SGC-11_Ficha_de_Proceso_Direccion_y_Planeacion_del_SGC.md`
- [ ] `docs/02_mapa_procesos/fichas_proceso/ESP-SGC-12_Ficha_de_Proceso_Operacion_y_Prestacion_del_Servicio.md`
- [ ] `docs/02_mapa_procesos/fichas_proceso/ESP-SGC-13_Ficha_de_Proceso_Gestion_de_Soporte_y_Recursos.md`
- [ ] `docs/_control/ESP-SGC-14_Reporte_de_Trazabilidad_Documental.md`
- [ ] `docs/03_procedimientos/PLAN-SGC-02_Digitalizacion_del_SGC.md`

## 4) Gate tecnico previo a auditoria
Ejecutar antes de auditoria:

```bash
cd /Users/hector/Projects/SGC/agent_runtime
source .venv/bin/activate
PYTHONPATH=/Users/hector/Projects/SGC/agent_runtime python -m sgc_agents.tools.build_indexes --repo-root /Users/hector/Projects/SGC
PYTHONPATH=/Users/hector/Projects/SGC/agent_runtime python -m sgc_agents.tools.build_dashboard --repo-root /Users/hector/Projects/SGC
```

Y correr QA deterministico (sin dependencia del decorador `agents`):

```bash
source .venv/bin/activate
TMPDIR=$(mktemp -d)
printf 'def function_tool(fn):\n    return fn\n' > "$TMPDIR/agents.py"
PYTHONPATH="$TMPDIR:/Users/hector/Projects/SGC/agent_runtime" SGC_REPO_ROOT=/Users/hector/Projects/SGC python - <<'PY'
import sys, yaml
from sgc_agents.tools.compliance_tools import (
  auditar_invariantes_de_estado,
  resolver_grafo_documental,
  detectar_formatos_huerfanos,
  auditar_trazabilidad_registros,
  generar_reporte_qa_compliance,
)
print(generar_reporte_qa_compliance())
checks=[
 yaml.safe_load(auditar_invariantes_de_estado()) or {},
 yaml.safe_load(resolver_grafo_documental()) or {},
 yaml.safe_load(detectar_formatos_huerfanos()) or {},
 yaml.safe_load(auditar_trazabilidad_registros()) or {},
]
hallazgos=0
for c in checks:
 f=c.get('hallazgos',[])
 if isinstance(f,list): hallazgos += len(f)
print('hallazgos_totales=', hallazgos)
if hallazgos:
 sys.exit(1)
PY
```

## 5) Aprobacion interna del baseline
- [ ] Responsable de Calidad confirma baseline
- [ ] Gerencia de Operaciones revisa
- [ ] Direccion General autoriza uso para auditoria

---

> Este checklist es una guia operativa de release. No reemplaza procedimientos ni formatos del SGC.
