---
codigo: "PR-SGC-03"
titulo: "Auditorias Internas"
tipo: "PR"
version: "1.2"
estado: "BORRADOR"
fecha_emision: "2026-02-09"
proceso: "SGC / Auditoria"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# PR-SGC-03 Auditorias Internas

> Nota: Criterios y umbrales de este documento son sinteticos de referencia. Ajustar con datos reales de la organizacion.

## 1. Objetivo
Establecer la metodologia para planificar, ejecutar y dar seguimiento a auditorias internas del SGC con criterios medibles.

## 2. Alcance
Aplica a auditorias de todos los procesos del SGC.

## 3. Referencias
- ISO 9001:2015, clausula 9.2 Auditoria interna.
- PR-SGC-02 Control de No Conformidades y CAPA.
- FOR-SGC-04 Programa Anual de Auditorias.
- FOR-SGC-05 Plan de Auditoria.
- FOR-SGC-06 Informe de Auditoria.
- FOR-SGC-07 Seguimiento de Acciones de Auditoria.
- FOR-SGC-02 Registro de No Conformidad.
- FOR-SGC-03 Plan y Registro CAPA.

## 4. Definiciones
- Hallazgo mayor: incumplimiento sistemico o de requisito critico.
- Hallazgo menor: incumplimiento puntual sin impacto sistemico.
- Observacion: oportunidad de mejora sin incumplimiento directo.

## 5. Responsabilidades
- Responsable de Calidad: coordinar programa y seguimiento de cierre.
- Auditor lider: preparar plan, ejecutar auditoria y emitir informe.
- Auditado/Dueno de Proceso: atender hallazgos y evidencias de cierre.

## 6. Desarrollo / Metodologia
### 6.1 Programacion basada en riesgo
Frecuencia minima por criticidad del proceso:
| Criticidad | Frecuencia minima |
|---|---|
| Alta | Trimestral |
| Media | Semestral |
| Baja | Anual |

### 6.2 Planificacion de auditoria
1. Emitir plan de auditoria al menos 5 dias habiles antes de la ejecucion.
2. Definir muestra minima:
- 3 evidencias por criterio auditado, o
- 10% de registros del periodo, lo que sea mayor.
3. Definir objetivo, alcance, criterios, equipo auditor y agenda.
4. Confirmar independencia del auditor (no auditar su propio proceso).
5. Definir codigos de registros de auditoria:
- Programa: `REG-SGC-PROG-AUD-AAAA`.
- Plan: `REG-SGC-PLAN-AUD-AAAA-<PROCESO>`.
- Informe: `REG-SGC-INF-AUD-AAAA-<PROCESO>`.

### 6.3 Ejecucion y clasificacion de hallazgos
1. Recopilar evidencia objetiva y trazable.
2. Clasificar hallazgos:
- Mayor: requiere accion inmediata y CAPA obligatoria.
- Menor: requiere accion correctiva con plazo definido.
- Observacion: seguimiento de mejora recomendado.
3. Registrar cada hallazgo con identificador unico `H-AUD-AAAA-###` en FOR-SGC-06.

### 6.4 Trazabilidad de hallazgos hacia NC/CAPA
1. Todo hallazgo `Mayor` o `Menor` debe abrir una NC en FOR-SGC-02 dentro de 24 horas habiles.
2. El informe FOR-SGC-06 debe incluir referencia cruzada a:
- Codigo de hallazgo (`H-AUD-...`).
- Codigo NC asociado (`NC-AAAA-###`).
3. Si el analisis de causa determina accion correctiva estructural, se debe abrir CAPA en FOR-SGC-03 con codigo `CAPA-AAAA-###`.
4. FOR-SGC-07 debe registrar, para cada hallazgo, la relacion `Hallazgo -> NC -> CAPA (si aplica)` y estado de cierre.
5. No cerrar hallazgos `Mayor` o `Menor` sin evidencia de cierre y verificacion de eficacia.

### 6.5 Tiempos objetivo de gestion
| Tipo de hallazgo | Emision de informe | Apertura NC | Plan de accion | Cierre objetivo |
|---|---|---|---|---|
| Mayor | <= 3 dias habiles | <= 24 h habiles | <= 5 dias habiles | <= 30 dias naturales |
| Menor | <= 3 dias habiles | <= 24 h habiles | <= 10 dias habiles | <= 45 dias naturales |
| Observacion | <= 3 dias habiles | N/A | <= 15 dias habiles (si aplica) | <= 60 dias naturales |

### 6.6 Seguimiento de acciones
- Seguimiento semanal de hallazgos abiertos.
- Escalamiento automatico de acciones vencidas (> 0 dias) a Gerencia y Calidad.
- Verificacion de eficacia al cierre para hallazgos mayores y menores.
- Revision de trazabilidad en cada corte: verificar que cada hallazgo tenga NC y CAPA cuando aplique.

### 6.7 Indicadores de desempeno de auditoria
| Indicador | Formula | Meta sintetica |
|---|---|---|
| Cumplimiento del programa | Auditorias ejecutadas / auditorias programadas x 100 | >= 90% |
| Emision oportuna de informes | Informes emitidos <= 3 dias / informes totales x 100 | >= 95% |
| Cierre en plazo de hallazgos | Hallazgos cerrados en plazo / hallazgos totales x 100 | >= 90% |
| Trazabilidad hallazgo-NC-CAPA | Hallazgos mayor/menor con NC y CAPA (si aplica) / hallazgos mayor/menor x 100 | = 100% |

## 7. Registros asociados
- REG-SGC-PROG-AUD - Programa anual de auditorias.
- REG-SGC-PLAN-AUD - Plan de auditoria.
- REG-SGC-INF-AUD - Informe de auditoria.
- REG-SGC-SEG-AUD - Seguimiento de acciones de auditoria.
- REG-SGC-NC - Registro de No Conformidad.
- REG-SGC-CAPA - Plan y Registro CAPA.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emision inicial | | |
| 1.1 | 2026-02-09 | Se agregan criterios medibles de frecuencia, muestreo, clasificacion y plazos de cierre | Coordinacion de Calidad | Direccion General |
| 1.2 | 2026-02-09 | Se agrega trazabilidad obligatoria de hallazgos hacia NC/CAPA, codificacion de hallazgos y control de tiempos de apertura NC | Coordinacion de Calidad | Direccion General |
