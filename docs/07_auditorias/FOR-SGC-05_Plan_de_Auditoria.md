---
codigo: "FOR-SGC-05"
titulo: "Plan de Auditoria"
tipo: "FOR"
version: "1.2"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC / Auditoria"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# FOR-SGC-05 Plan de Auditoria

## 1. Objetivo
Documentar el plan operativo de cada auditoria interna, incluyendo muestra y tiempos.

## 2. Alcance
Aplica a cada auditoria interna programada.

## 3. Referencias
- PR-SGC-03 Auditorias Internas.
- FOR-SGC-04 Programa Anual de Auditorias.
- FOR-SGC-06 Informe de Auditoria.
- FOR-SGC-07 Seguimiento de Acciones de Auditoria.

## 4. Definiciones
- Muestra de auditoria.
- Criterio de auditoria.
- Independencia del auditor.

## 5. Responsabilidades
- Auditor lider: elaborar plan.
- Auditado: confirmar disponibilidad y evidencias.

## 6. Desarrollo / Metodologia
1. Definir codigo del programa anual y codigo del plan de auditoria.
2. Definir objetivo, alcance y criterios de auditoria.
3. Confirmar independencia del auditor (no auditar su propio proceso).
4. Definir muestra minima de registros/evidencias:
- 3 evidencias por criterio auditado, o
- 10% de registros del periodo, lo que sea mayor.
5. Establecer agenda y tiempos por actividad.
6. Definir entregables esperados y codigos relacionados:
- Informe de auditoria (`REG-SGC-INF-AUD-AAAA-CODPRO`).
- Seguimiento de acciones (`REG-SGC-SEG-AUD-AAAA-CODPRO`).
7. Confirmar recursos, participantes y comunicacion previa (>= 5 dias habiles antes de ejecucion).

### 6.1 Reglas de planificacion
- No ejecutar auditoria sin plan comunicado y validado por Responsable de Calidad.
- Todo criterio auditado debe tener evidencia objetivo definida en el plan.
- Incluir riesgos de auditoria y controles preventivos antes de la ejecucion.

## 7. Registros asociados
- REG-SGC-PLAN-AUD - Plan de auditoria (llenado).
- REG-SGC-INF-AUD - Informe de auditoria.
- REG-SGC-SEG-AUD - Seguimiento de acciones de auditoria.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emision inicial | | |
| 1.1 | 2026-02-09 | Se agregan campos de muestreo y duracion planificada | Coordinacion de Calidad | Direccion General |
| 1.2 | 2026-02-09 | Se agregan campos de trazabilidad programa-informe-seguimiento y reglas de independencia/muestreo | Coordinacion de Calidad | Direccion General |

## 9. Formato de llenado
- Codigo programa: REG-SGC-PROG-AUD-AAAA
- Codigo plan: REG-SGC-PLAN-AUD-AAAA-CODPRO
- Codigo informe esperado: REG-SGC-INF-AUD-AAAA-CODPRO
- Codigo seguimiento esperado: REG-SGC-SEG-AUD-AAAA-CODPRO
- Proceso auditado: ____
- Objetivo: ____
- Alcance: ____
- Criterio(s): ISO 9001:2015 + criterios internos aplicables
- Auditor(es): ____
- Declaracion de independencia del auditor: Si / No
- Fecha y horario: ____
- Muestra planificada (cantidad y tipo): ____ (>= 3 evidencias por criterio o 10% del periodo)
- Duracion estimada (horas): ____
- Riesgos de auditoria identificados: ____
- Controles preventivos de auditoria: ____

| Criterio auditado | Tipo de evidencia | Cantidad planificada | Fuente/Ubicacion |
|---|---|---:|---|
| ISO 9001:2015 8.5 | Registro/Documento/Entrevista/Observacion | 3 | Repositorio oficial del proceso auditado |

| Actividad | Responsable | Inicio | Fin |
|---|---|---|---|
| Reunion de apertura | Auditor lider | HH:MM | HH:MM |
| Ejecucion de auditoria | Equipo auditor | HH:MM | HH:MM |
| Reunion de cierre | Auditor lider | HH:MM | HH:MM |
