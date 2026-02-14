---
codigo: "ESP-SGC-14"
titulo: "Reporte de Trazabilidad Documental"
tipo: "ESP"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "2026-02-09"
proceso: "SGC / Control Documental"
elaboro: "Coordinacion de Calidad"
reviso: "TODO: <PUESTO>"
aprobo: "TODO: <PUESTO>"
---

# ESP-SGC-14 Reporte de Trazabilidad Documental

## 1. Objetivo
Documentar el resultado de la validacion transversal de trazabilidad del sistema documental del SGC, incluyendo coherencia entre LMD, archivos controlados y matriz de registros.

## 2. Alcance
Aplica a los documentos listados en `docs/_control/lmd.yml`, a los registros definidos en `docs/_control/matriz_registros.yml` y a sus referencias internas vigentes al momento de la revision.

## 3. Referencias
- PR-SGC-01 Control de Documentos y Registros.
- `docs/_control/lmd.yml`.
- `docs/_control/matriz_registros.yml`.
- ROADMAP del SGC (documental).

## 4. Definiciones
- Trazabilidad documental: capacidad de vincular codigo, version, estado, ubicacion y evidencias relacionadas entre documentos del SGC.
- LMD: Lista Maestra de Documentos.
- Matriz de registros: relacion de evidencias, responsable, medio, ubicacion, retencion y proteccion.

## 5. Responsabilidades
- Coordinacion de Calidad: ejecutar la validacion y emitir este reporte.
- Duenos de proceso: atender hallazgos que impacten sus documentos o registros.
- Direccion: revisar resultados y definir prioridad de cierre cuando existan desviaciones.

## 6. Desarrollo / Metodologia
### 6.1 Criterios de validacion aplicados
1. Existencia fisica de todos los archivos referidos en LMD.
2. Unicidad de codigos en LMD y matriz de registros.
3. Presencia de frontmatter y coherencia de campos clave (`codigo`, `titulo`, `tipo`, `version`, `estado`, `proceso`).
4. Consistencia de secciones minimas requeridas en documentos controlados.
5. Coherencia entre codigos de registro referenciados y matriz de registros.
6. Existencia de rutas/carpetas de almacenamiento declaradas para registros.

### 6.2 Resultado de la validacion (2026-02-09)
| Control revisado | Resultado |
|---|---|
| Documentos en LMD | 31 |
| Registros en matriz | 16 |
| Duplicidad de codigos LMD | 0 |
| Rutas faltantes en LMD | 0 |
| Inconsistencias frontmatter vs LMD | 0 |
| Duplicidad de codigos de registro | 0 |
| Rutas faltantes de registros | 0 |
| Referencias REG sin correspondencia en matriz | 0 |

### 6.3 Hallazgos
- Sin hallazgos de inconsistencia estructural al corte de la revision.

### 6.4 Acciones sugeridas (siguientes pasos del roadmap)
1. Priorizar aprobaciones para migrar documentos criticos de `BORRADOR` a `VIGENTE` segun flujo de PR-SGC-01.
2. Completar campos pendientes de retencion/disposicion marcados como `TODO` en la matriz de registros.
3. Ejecutar esta validacion de trazabilidad con frecuencia mensual o antes de auditorias internas/externas.

## 7. Registros asociados
- REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique una correccion).
- REG-SGC-COM - Evidencia de distribucion/comunicacion de documentos (cuando aplique publicacion).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emision inicial del reporte de trazabilidad documental | Coordinacion de Calidad | TODO: <PUESTO> |
