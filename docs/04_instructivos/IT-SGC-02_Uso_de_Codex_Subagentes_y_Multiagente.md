---
codigo: "IT-SGC-02"
titulo: "Instructivo: Uso de Codex (Subagentes y Multiagente) en el Repositorio SGC"
tipo: "IT"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "2026-02-22"
proceso: "SGC / Control Documental"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# Instructivo: Uso de Codex (Subagentes y Multiagente) en el Repositorio SGC

## 1. Objetivo
Establecer un metodo operativo para aprovechar capacidades de **subagentes** y **multiagente** de Codex al trabajar en este repositorio, manteniendo control documental, trazabilidad y artefactos generados sin drift.

## 2. Alcance
Aplica a tareas ejecutadas con Codex en este repositorio, incluyendo:
- Exploracion/lectura del repo (busqueda de codigos, referencias y plantillas).
- Creacion o actualizacion de documentos controlados en `docs/`.
- Regeneracion de indices (`sgc-build-indexes`) y verificacion de consistencia cuando aplique.

Excluye el uso de Codex fuera del repositorio SGC o para decisiones organizacionales no definidas (usar `TODO:` / placeholders segun `AGENTS.md`).

## 3. Referencias
- `AGENTS.md`
- `docs/AGENTS.md`
- `CODEX_WORKFLOW.md`
- `agent_runtime/README.md`
- ISO 9001:2015, 7.5 Informacion documentada.

## 4. Definiciones
- Subagente: instancia separada de Codex orientada a un subobjetivo acotado (por ejemplo, exploracion, redaccion, verificacion), coordinada por un agente principal.
- Multiagente: modo de trabajo donde se ejecutan varios subagentes en paralelo para reducir tiempo total, manteniendo responsabilidades separadas por archivo/tema.
- Artefacto generado: salida determinista que **no** se edita manualmente (por ejemplo, `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml`).

## 5. Responsabilidades
- Usuario solicitante: definir alcance, criterios de aceptacion y restricciones (que si / que no) antes de pedir ejecucion multiagente.
- Codex (agente principal): coordinar subagentes, consolidar resultados y aplicar cambios finales con consistencia y trazabilidad.
- Coordinacion de Calidad: validar que los cambios documentales cumplan convenciones del SGC y que los indices de control se regeneren cuando corresponda.

## 6. Desarrollo / Metodologia

### 6.1 Principios operativos (obligatorios)
1. **Separacion de responsabilidades**: cada subagente trabaja sobre un objetivo y/o conjunto de archivos definido para evitar conflictos.
2. **SSOT**: en documentos controlados, el frontmatter YAML es la unica fuente de verdad para indices.
3. **No drift**: no editar manualmente `docs/_control/lmd.yml` ni `docs/_control/matriz_registros.yml`; se regeneran desde la fuente.
4. **Trazabilidad**: mantener referencias cruzadas por codigo (PR/FOR/REG) alineadas con archivos reales.

### 6.2 Cuando usar subagentes vs. un solo agente
Usar subagentes cuando:
- Se requiere **explorar** el repositorio (codigos existentes, plantillas, referencias) antes de redactar.
- Se necesita **validacion** (por ejemplo, enlaces/referencias) en paralelo a la redaccion.
- Hay tareas independientes (por ejemplo, "buscar codigos disponibles" y "proponer estructura del instructivo").

Evitar subagentes cuando:
- La tarea es pequena y localizada (un solo archivo, cambios menores).
- Existe riesgo de cambios concurrentes sobre el mismo archivo sin una asignacion clara.

### 6.3 Patrones recomendados (prompts)
Usar prompts estilo "Issue" segun `CODEX_WORKFLOW.md`. Ejemplos (adaptar):

**Patron A: Exploracion + redaccion**
1. Subagente 1 (Exploracion): identificar documentos similares, codigos disponibles y referencias relevantes.
2. Subagente 2 (Redaccion): proponer estructura conforme a plantilla y secciones minimas.
3. Agente principal: integrar, crear/editar el documento y ejecutar `sgc-build-indexes` si aplica.

**Patron B: Redaccion + verificacion**
1. Subagente 1 (Redaccion): redactar el contenido con placeholders donde falten datos.
2. Subagente 2 (Verificacion): revisar que codigos citados existan y que rutas/links no esten rotos.
3. Agente principal: corregir hallazgos, regenerar indices y dejar el resultado consistente.

### 6.4 Reglas de integracion (evitar conflictos)
- Definir "propiedad" por archivo: un solo agente debe aplicar cambios finales a cada archivo.
- Pedir a subagentes que entreguen **hallazgos y recomendaciones**, no que apliquen parches simultaneos sobre el mismo documento.
- Cuando haya que modificar mas de un archivo, dividir por carpetas o por tipo (por ejemplo: un subagente solo `docs/04_instructivos/`, otro solo `docs/03_procedimientos/`).

### 6.5 Cierre de tarea (checklist)
1. Verificar que el documento controlado tenga frontmatter valido, secciones minimas y nombre de archivo conforme a `AGENTS.md`.
2. Si se creo/actualizo/movio/obsoleto un documento controlado, ejecutar `sgc-build-indexes`.
3. Confirmar que no existan referencias rotas (codigos y rutas reales).
4. Cuando la tarea afecte trazabilidad o registros, ejecutar el pipeline QA determinista indicado en `AGENTS.md` / `CODEX_WORKFLOW.md`.

### 6.6 Activacion del modo multiagente (si esta disponible)
Si tu instalacion de Codex soporta modo multiagente, habilitalo en tu configuracion local y reinicia la sesion. Ejemplo:

```toml
[features]
multi_agent = true
```

Si no esta disponible, aplicar los mismos principios de este instructivo en modo de un solo agente (sin paralelizacion).

### 6.7 Integracion con el runtime `sgc-agent` (multiagente)
Para tareas repetibles de control y verificacion, el runtime del repo soporta ejecucion multiagente (writer + auditoria) en paralelo al pipeline deterministico (indices + QA + dashboard):

```bash
sgc-agent --mode multi --task "Revisar consistencia del SGC y proponer mejoras"
```

Para ejecutar solo el pipeline deterministico (sin LLM):
```bash
sgc-agent --mode multi --no-llm --task "Rebuild + QA"
```

## 7. Registros asociados
- REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique).
- REG-SGC-COM - Evidencia de comunicacion/distribucion (cuando aplique).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-22 | Emision inicial (borrador) del instructivo para uso de subagentes y multiagente en Codex | Coordinacion de Calidad | Direccion General |
