---
codigo: "FOR-SGC-04"
titulo: "Programa Anual de Auditorias"
tipo: "FOR"
version: "1.2"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC / Auditoria"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# FOR-SGC-04 Programa Anual de Auditorias

## 1. Objetivo
Planificar auditorias internas del ano con enfoque basado en riesgos y frecuencia definida.

## 2. Alcance
Aplica al plan anual de auditorias internas del SGC.

## 3. Referencias
- PR-SGC-03 Auditorias Internas.
- FOR-SGC-05 Plan de Auditoria.
- FOR-SGC-06 Informe de Auditoria.
- FOR-SGC-07 Seguimiento de Acciones de Auditoria.

## 4. Definiciones
- Criticidad del proceso.
- Cobertura del programa anual.

## 5. Responsabilidades
- Responsable de Calidad: preparar y actualizar el programa.
- Auditor lider: ejecutar auditorias conforme al programa aprobado.
- Direccion: aprobar el programa.

## 6. Desarrollo / Metodologia
1. Listar todos los procesos del SGC a cubrir durante el ciclo anual.
2. Asignar criticidad por proceso (Alta, Media, Baja).
3. Definir frecuencia minima segun criticidad:
- Alta: trimestral.
- Media: semestral.
- Baja: anual.
4. Programar periodo/mes de auditoria por proceso, auditor lider y auditor alterno.
5. Definir codigos esperados para trazabilidad de cada auditoria:
- `REG-SGC-PLAN-AUD-AAAA-CODPRO`
- `REG-SGC-INF-AUD-AAAA-CODPRO`
- `REG-SGC-SEG-AUD-AAAA-CODPRO`
6. Marcar estado por proceso (`Planificada`, `Reprogramada`, `Ejecutada`, `Cerrada`).
7. Revisar cumplimiento mensual y reprogramar en caso de desviaciones justificadas.

### 6.1 Reglas del programa
- Todo proceso del SGC debe tener al menos una auditoria programada en el ciclo anual.
- No asignar auditor que audite su propio proceso.
- Toda reprogramacion debe conservar trazabilidad de causa, fecha y nueva ventana.

## 7. Registros asociados
- REG-SGC-PROG-AUD - Programa anual de auditorias (llenado).
- REG-SGC-PLAN-AUD - Plan de auditoria.
- REG-SGC-INF-AUD - Informe de auditoria.
- REG-SGC-SEG-AUD - Seguimiento de acciones de auditoria.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emision inicial | | |
| 1.1 | 2026-02-09 | Se agregan campos de criticidad y frecuencia minima | Coordinacion de Calidad | Direccion General |
| 1.2 | 2026-02-09 | Se agrega trazabilidad del ciclo programa-plan-informe-seguimiento y reglas de cobertura/reprogramacion | Coordinacion de Calidad | Direccion General |

## 9. Formato de llenado
| Proceso | Criticidad | Frecuencia minima | Periodo programado | Auditor lider | Auditor alterno | Criterio | Codigo plan esperado | Codigo informe esperado | Codigo seguimiento esperado | Estado | Observaciones |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-01 Control documental | Alta/Media/Baja | Trimestral/Semestral/Anual | Trimestre/Mes | Auditor Interno 1 | Auditor Interno 2 | ISO 9001:2015 + internos | REG-SGC-PLAN-AUD-AAAA-CODPRO | REG-SGC-INF-AUD-AAAA-CODPRO | REG-SGC-SEG-AUD-AAAA-CODPRO | Planificada/Reprogramada/Ejecutada/Cerrada | Referenciar cambios y causas de reprogramacion si aplica |
