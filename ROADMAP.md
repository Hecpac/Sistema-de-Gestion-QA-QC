# ROADMAP del SGC (documental)

Este roadmap esta orientado a construir el SGC **por incrementos**, priorizando primero lo que sostiene al resto (control documental) y lo que genera evidencia solida (NC/CAPA, auditorias, KPI).

## Estado de implementacion (2026-02-14)
- Fases 0 a 8: documentos base creados en estado `BORRADOR` version `1.0+`.
- Fase 9 (opcional): `PLAN-SGC-02_Digitalizacion_del_SGC.md` creado en `BORRADOR`.
- Control documental sincronizado por generacion determinista:
  - `docs/_control/lmd.yml`
  - `docs/_control/matriz_registros.yml`

## Fase 0 - Gobierno del SGC (base)
**Entregables**
- Mapa de procesos (alto nivel) + duenos de proceso.
- Convenciones de codificacion y versionado (ya definidas en `AGENTS.md`).
- Estructura de carpetas + plantillas (este repo).

**Criterio de salida**
- Existe un repositorio unico con estructura y reglas claras, y cada proceso tiene un responsable asignado (al menos nominal).

---

## Fase 1 - Control de Documentos y Registros
**Entregables**
- PR-SGC-01 Control de Documentos y Registros (incluido).
- Lista Maestra de Documentos (`docs/_control/lmd.yml`) operativa.
- Matriz de Registros (`docs/_control/matriz_registros.yml`) operativa.
- Formato Solicitud de Cambio Documental (`docs/_control/FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md`) vigente.

**Criterio de salida**
- Se puede crear un documento nuevo, aprobarlo, publicarlo y dejar trazabilidad en la LMD usando `sgc-build-indexes`.

---

## Fase 2 - Mapa de procesos + Fichas de proceso
**Entregables**
- `docs/02_mapa_procesos/ESP-SGC-01_Mapa_de_Procesos_del_SGC.md`
- Una ficha por proceso (estrategico/operativo/soporte) usando la plantilla.

**Criterio de salida**
- Cada proceso tiene: proposito, entradas/salidas, responsable, riesgos, indicadores y registros clave.

---

## Fase 3 - No Conformidades y CAPA
**Entregables**
- Procedimiento de No Conformidades (NC).
- Procedimiento de Acciones Correctivas (CAPA) o uno combinado NC/CAPA.
- Formatos de NC y CAPA + criterios de severidad.
- Matriz de registros generada y consistente con referencias `REG-*`.

**Criterio de salida**
- Se puede registrar una NC, analizar causa raiz, ejecutar acciones y verificar eficacia.

---

## Fase 4 - Auditorias internas
**Entregables**
- Procedimiento de auditorias internas.
- Programa anual de auditorias (formato).
- Plan de auditoria + informe + seguimiento.

**Criterio de salida**
- Auditorias ejecutables con evidencias y hallazgos trazables a NC/CAPA.

---

## Fase 5 - KPI, analisis de datos y Revision por la Direccion
**Entregables**
- Procedimiento de indicadores y analisis de datos (o instructivo).
- Matriz de KPI por proceso.
- Minuta/acta de Revision por la Direccion.

**Criterio de salida**
- Direccion puede revisar desempeno con datos y decidir acciones.

---

## Fase 6 - Riesgos y oportunidades
**Entregables**
- Metodologia de riesgos por proceso (matriz).
- Planes de tratamiento y seguimiento.

**Criterio de salida**
- Riesgos priorizados con acciones y responsables.

---

## Fase 7 - Proveedores (si aplica)
**Entregables**
- Procedimiento de evaluacion y reevaluacion.
- Criterios de homologacion y evaluacion.

---

## Fase 8 - Competencia y formacion
**Entregables**
- Matriz de competencias por rol.
- Plan de capacitacion + evaluacion de eficacia.

---

## Fase 9 - Digitalizacion (opcional)
**Entregables**
- Tableros, automatizacion de flujos, integraciones, etc.

> Sugerencia de trabajo con Codex: pedir 1 documento por tarea y cerrar cada tarea con regeneracion de indices.

---

## Fase 10 - Migracion topologica por proceso (pendiente)
**Objetivo**
- Reducir ambiguedad de enrutamiento para agentes eliminando carpetas por tipo (`03_procedimientos`, `04_instructivos`, `05_formatos`) y pasando a agrupacion por dominio/proceso.

**Entregables**
- Plan de migracion de rutas y alias temporales.
- Reubicacion progresiva de PR/FOR/IT/PLAN en carpetas por proceso.
- Actualizacion de referencias internas y validacion de trazabilidad post-migracion.

**Criterio de salida**
- El agente puede inferir ruta objetivo por proceso sin ambiguedad y sin rutas duplicadas para el mismo codigo.

---

## Fase 11 - Escalamiento multidisciplina (Civil / Mecanica / Electrica)
**Objetivo**
- Extender el SGC para operar en empresas con multiples disciplinas tecnicas sin romper el modelo Zero-Trust.

**Entregables**
- Taxonomia oficial por disciplina/subdisciplina.
- Plantillas tecnicas por disciplina (ficha tecnica, ITP, checklist de liberacion).
- Gobernanza de aprobaciones por disciplina (CODEOWNERS + criterios por criticidad).
- Piloto real de 3 flujos (civil/mecanica/electrica) con evidencia completa en CI.

**Criterio de salida**
- Cada disciplina puede emitir, revisar y liberar documentos tecnicos con trazabilidad completa y gates QA en verde.
