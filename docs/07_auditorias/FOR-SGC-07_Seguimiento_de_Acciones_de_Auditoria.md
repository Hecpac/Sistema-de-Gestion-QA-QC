---
codigo: "FOR-SGC-07"
titulo: "Seguimiento de Acciones de Auditoria"
tipo: "FOR"
version: "1.2"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC / Auditoria"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# FOR-SGC-07 Seguimiento de Acciones de Auditoria

## 1. Objetivo
Controlar la ejecucion y cierre de acciones derivadas de hallazgos de auditoria con seguimiento de plazo y eficacia.

## 2. Alcance
Aplica a todas las acciones abiertas por auditorias internas.

## 3. Referencias
- PR-SGC-03 Auditorias Internas.
- PR-SGC-02 Control de No Conformidades y CAPA.
- FOR-SGC-06 Informe de Auditoria.
- FOR-SGC-02 Registro de No Conformidad.
- FOR-SGC-03 Plan y Registro CAPA.

## 4. Definiciones
- Accion de auditoria.
- Eficacia de cierre.

## 5. Responsabilidades
- Dueno de Proceso: ejecutar acciones.
- Responsable de Calidad: verificar cierre y eficacia.

## 6. Desarrollo / Metodologia
1. Registrar cada accion desde el informe de auditoria con `codigo informe` y `codigo hallazgo` (`H-AUD-AAAA-###`).
2. Registrar `codigo NC` obligatorio para hallazgos `Mayor` y `Menor`.
3. Registrar `codigo CAPA` cuando aplique accion correctiva estructural.
4. Asignar responsable, fecha compromiso y criterio de cierre verificable.
5. Controlar dias abiertos y estado semaforo por accion.
6. Verificar evidencia objetiva de cierre.
7. Verificar eficacia segun ventana definida.
8. Mantener relacion trazable `Hallazgo -> NC -> CAPA` en todo momento.

### 6.1 Reglas de seguimiento
- No cerrar hallazgos `Mayor` o `Menor` sin NC asociada.
- No cerrar accion con `Resultado eficacia = Eficaz` sin evidencia de cierre adjunta o referenciada.
- Si la fecha compromiso se vence, escalar en maximo 48 horas a Responsable de Calidad y Gerencia.

### 6.2 Criterio de semaforo
- Verde: fecha compromiso con 3 o mas dias restantes.
- Amarillo: fecha compromiso entre 0 y 2 dias restantes.
- Rojo: fecha compromiso vencida.

## 7. Registros asociados
- REG-SGC-SEG-AUD - Seguimiento de acciones de auditoria (llenado).
- REG-SGC-INF-AUD - Informe de auditoria.
- REG-SGC-NC - Registro de No Conformidad.
- REG-SGC-CAPA - Plan y Registro CAPA.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emision inicial | | |
| 1.1 | 2026-02-09 | Se agregan campos de dias abiertos, semaforo y verificacion de eficacia | Coordinacion de Calidad | Direccion General |
| 1.2 | 2026-02-09 | Se agrega trazabilidad obligatoria Hallazgo-NC-CAPA y reglas de escalamiento/semaforo | Coordinacion de Calidad | Direccion General |

## 9. Formato de llenado
| Codigo informe | Codigo hallazgo | Tipo hallazgo | Codigo NC | Codigo CAPA | Accion | Responsable | Fecha compromiso | Dias abiertos | Estado semaforo | Evidencia de cierre | Fecha verificacion eficacia | Resultado eficacia | Estado |
|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|
| INF-AUD-AAAA-001 | H-AUD-AAAA-001 | Mayor/Menor/Obs. | NC-AAAA-### (obligatorio Mayor/Menor) | CAPA-AAAA-### (si aplica) | Ejecutar accion definida en informe | Responsable del proceso auditado | AAAA-MM-DD | 0 | Verde/Amarillo/Rojo | Evidencia documental de cierre | AAAA-MM-DD | Eficaz/No eficaz | Abierta/En curso/Cerrada |
