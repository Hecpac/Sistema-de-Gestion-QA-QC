---
codigo: "FOR-SGC-06"
titulo: "Informe de Auditoria"
tipo: "FOR"
version: "1.2"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC / Auditoria"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# FOR-SGC-06 Informe de Auditoria

## 1. Objetivo
Registrar hallazgos, conclusiones y recomendaciones de una auditoria interna con clasificacion y plazos.

## 2. Alcance
Aplica a cada auditoria interna ejecutada.

## 3. Referencias
- PR-SGC-03 Auditorias Internas.
- PR-SGC-02 Control de No Conformidades y CAPA.
- FOR-SGC-02 Registro de No Conformidad.
- FOR-SGC-03 Plan y Registro CAPA.
- FOR-SGC-07 Seguimiento de Acciones de Auditoria.

## 4. Definiciones
- Hallazgo mayor.
- Hallazgo menor.
- Observacion.

## 5. Responsabilidades
- Auditor lider: emitir informe y evidencias.
- Responsable de Calidad: distribuir y controlar informe.

## 6. Desarrollo / Metodologia
1. Consolidar evidencia objetiva y trazable.
2. Clasificar hallazgos por tipo.
3. Asignar codigo de hallazgo `H-AUD-AAAA-###` a cada hallazgo.
4. Para hallazgos `Mayor` y `Menor`, registrar obligatoriamente codigo NC asociado (`NC-AAAA-###`) dentro de 24 horas habiles.
5. Cuando aplique accion correctiva estructural, registrar codigo CAPA asociado (`CAPA-AAAA-###`).
6. Definir responsable y fecha compromiso por hallazgo.
7. Emitir informe final en maximo 3 dias habiles.

### 6.1 Reglas de trazabilidad
- No cerrar informe con hallazgos `Mayor` o `Menor` sin NC asociada.
- Si no aplica CAPA, justificar con criterio objetivo en la columna de observaciones.
- Todos los codigos de NC/CAPA reportados deben existir en sus registros fuente.

## 7. Registros asociados
- REG-SGC-INF-AUD - Informe de auditoria (llenado).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emision inicial | | |
| 1.1 | 2026-02-09 | Se agregan campos de clasificacion, evidencia y plazo objetivo | Coordinacion de Calidad | Direccion General |
| 1.2 | 2026-02-09 | Se agrega trazabilidad obligatoria de hallazgos a NC/CAPA y reglas de codificacion | Coordinacion de Calidad | Direccion General |

## 9. Formato de llenado
- Codigo informe: INF-AUD-AAAA-###
- Proceso auditado: ____
- Fecha de auditoria: ____
- Equipo auditor: ____
- Criterio de auditoria: ISO 9001:2015 + criterios internos aplicables
- Fecha limite de emision del informe: ____ (<= 3 dias habiles)

| Codigo hallazgo | Tipo (Mayor/Menor/Obs.) | Requisito auditado | Evidencia objetiva | Codigo NC | Codigo CAPA | Responsable accion | Fecha compromiso | Estado |
|---|---|---|---|---|---|---|---|---|
| H-AUD-AAAA-001 | Mayor/Menor/Obs. | ISO 9001:2015 8.5 | Evidencia objetiva trazable del criterio auditado | NC-AAAA-### (obligatorio Mayor/Menor) | CAPA-AAAA-### (si aplica) | Responsable del proceso auditado | AAAA-MM-DD | Abierta/En curso/Cerrada |

- Conclusiones generales: ____
- Recomendaciones: ____
- Observaciones de trazabilidad (si aplica): ____
