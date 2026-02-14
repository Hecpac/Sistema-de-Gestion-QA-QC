---
name: validar_trazabilidad
description: Activar cuando se requiera verificar consistencia/trazabilidad del sistema documental (LMD ↔ archivos ↔ formatos ↔ matriz de registros ↔ registros operativos); NO activar para redaccion de un solo documento si no hay cambios globales.
---

# Objetivo
Verificar coherencia y trazabilidad con un pipeline neuro-simbolico antes de cierre o auditoria transversal.

# Cuando usar / Cuando NO usar
- Usar para revisiones globales del sistema documental.
- Usar antes de auditorias o entregas de varios documentos.
- NO usar para redactar un unico documento sin impacto transversal.
- NO usar como sustituto de `crear_documento` o actualizaciones puntuales.

# Pipeline determinista obligatorio
1. `auditar_invariantes_de_estado`
2. `resolver_grafo_documental`
3. `detectar_formatos_huerfanos`
4. `auditar_trazabilidad_registros` (axiomas P1..P5)
5. `generar_reporte_qa_compliance`

# Axiomas de trazabilidad por registro (P1..P5)
- P1 Procedencia: `formato_origen` obligatorio en frontmatter del registro.
- P2 Existencia canonica: `formato_origen` existe fisicamente en docs.
- P3 Vigencia legal: formato origen en estado `VIGENTE`.
- P4 Sincronizacion SSOT: formato origen habilitado en `matriz_registros.yml` (`codigo_formato`).
- P5 Isomorfismo estructural: headers del formato `H(F)` incluidos en registro `H(R)`.

# Salida requerida
Generar reporte en Markdown en `docs/_control/reporte_qa_compliance.md` con:
- Fecha de revision.
- Resultado por skill.
- Hallazgos con evidencia y severidad.
- No conformidades sugeridas cuando haya incumplimientos.

# Regla operativa
No cerrar una tarea con hallazgos criticos sin registrar accion correctiva sugerida.
