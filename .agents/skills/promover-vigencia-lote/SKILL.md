---
name: promover-vigencia-lote
description: Activar cuando el usuario pida pasar uno o varios documentos de BORRADOR a VIGENTE en bloque en el repo SGC, incluyendo bump de version, limpieza de placeholders/TODO, regeneracion de artefactos de control, QA deterministico y commit atomico.
---

# Objetivo
Promover un lote documental a estado `VIGENTE` sin romper trazabilidad ni QA.

# Entradas
- Lista de documentos a promover (por codigo, ruta o lote).
- Fecha de emision (si no se indica, usar fecha actual).
- Mensaje de commit.

# Flujo
1. Actualizar frontmatter en cada documento:
   - `estado: VIGENTE`
   - `version`: bump menor (ej. 1.0 -> 1.1)
   - `fecha_emision`: fecha de promocion
   - `elaboro/reviso/aprobo`: sin placeholders.
2. Actualizar tabla `Control de cambios` con nueva fila de emision vigente.
3. Eliminar `TODO`, `TBD` y placeholders `<...>` del contenido de los documentos promovidos.
4. Normalizar comparadores `<=` y `>=` a texto (`menor o igual a`, `mayor o igual a`) para evitar falsos positivos del QA regex.
5. Regenerar artefactos:
   - `python -m sgc_agents.tools.build_indexes --repo-root <repo>`
   - `python -m sgc_agents.tools.build_dashboard --repo-root <repo>`
6. Ejecutar QA deterministico y exigir 0 hallazgos.
7. Verificar repo limpio excepto cambios esperados y hacer commit atomico.

# QA deterministico (workaround local)
Si el decorador `agents` rompe invocacion directa, crear stub temporal:

```bash
TMPDIR=$(mktemp -d)
printf 'def function_tool(fn):\n    return fn\n' > "$TMPDIR/agents.py"
PYTHONPATH="$TMPDIR:/Users/hector/Projects/SGC/agent_runtime" SGC_REPO_ROOT=/Users/hector/Projects/SGC python - <<'PY'
import sys, yaml
from sgc_agents.tools.compliance_tools import (
  auditar_invariantes_de_estado,
  resolver_grafo_documental,
  detectar_formatos_huerfanos,
  auditar_trazabilidad_registros,
)
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
if hallazgos: sys.exit(1)
PY
```

# DoD
- Documentos del lote en `VIGENTE` con control de cambios actualizado.
- `lmd.yml`, `matriz_registros.yml`, `dashboard_sgc.html`, `reporte_qa_compliance.md` sincronizados.
- QA con 0 hallazgos.
- Commit atomico realizado.
