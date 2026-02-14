---
name: actualizar_lmd
description: Activar cuando se cree/actualice/obsoleto cualquier documento del SGC y se requiera sincronizar la Lista Maestra (LMD) en `docs/_control/lmd.yml`; NO activar para cambios que no afecten documentos.
---

# Objetivo
Mantener `docs/_control/lmd.yml` sincronizado con los documentos controlados reales del repositorio mediante **generacion determinista**.

# Cuando usar / Cuando NO usar
- Usar despues de crear, editar, versionar, mover o marcar obsoleto un documento del SGC.
- Usar cuando cambien `codigo`, `titulo`, `version`, `estado` o `ubicacion` de un documento.
- NO usar para cambios de contenido que no afecten documentos controlados.
- NO usar para tareas de analisis teorico sin cambios de archivos.

# Regla de operacion
- No editar `docs/_control/lmd.yml` manualmente.
- Ejecutar `sgc-build-indexes` (o herramienta `rebuild_control_indexes`) para regenerar la LMD desde frontmatter.

# Flujo paso a paso
1. Validar frontmatter del/los documento(s) impactados.
2. Ejecutar `sgc-build-indexes`.
3. Confirmar que la entrada de `codigo` existe en LMD con `version`, `estado` y `ubicacion` correctos.
4. Verificar que no existan codigos duplicados.

# Reglas
- No duplicar `codigo`.
- Mantener estado valido: `BORRADOR`, `VIGENTE`, `OBSOLETO`.
- No declarar `VIGENTE` sin instruccion/aprobacion explicita.
- Preservar rutas relativas correctas y existentes.

# Definicion de Terminado (DoD)
- `docs/_control/lmd.yml` regenerado correctamente.
- El archivo referido por `ubicacion` existe y corresponde al `codigo`.
- No hay discrepancias entre frontmatter y LMD.
