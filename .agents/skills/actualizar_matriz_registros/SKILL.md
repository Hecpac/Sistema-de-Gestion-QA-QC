---
name: actualizar_matriz_registros
description: Activar cuando se definan o modifiquen registros del SGC (evidencias) y sea necesario sincronizar `docs/_control/matriz_registros.yml`; NO activar si solo se esta editando texto sin impacto en registros.
---

# Objetivo
Mantener la matriz de registros alineada con las evidencias exigidas por los documentos del SGC, usando una generacion automatica y reproducible.

# Cuando usar / Cuando NO usar
- Usar cuando un documento crea, elimina o modifica un registro/evidencia.
- Usar cuando cambien referencias `REG-*` en secciones **Registros asociados**.
- NO usar para ediciones de estilo o redaccion sin impacto en registros.
- NO usar cuando no exista relacion con evidencias documentales.

# Regla de operacion
- No editar `docs/_control/matriz_registros.yml` manualmente.
- Ejecutar `sgc-build-indexes` (o `rebuild_control_indexes`) para regenerarla desde referencias `REG-*` y mantener coherencia.

# Flujo paso a paso
1. Revisar el documento fuente y su seccion `Registros asociados`.
2. Confirmar que los codigos `REG-*` sean validos y consistentes.
3. Ejecutar `sgc-build-indexes`.
4. Verificar que la matriz incluya/actualice los registros impactados.
5. Confirmar existencia de ubicaciones de registros cuando aplique.

# Reglas
- Usar codigos `REG-*` consistentes entre documento y matriz.
- No inventar requisitos legales/regulatorios no autorizados.
- Mantener trazabilidad directa entre documento/formato y registro en matriz.

# Definicion de Terminado (DoD)
- Matriz regenerada para cada registro impactado.
- Coherencia verificada con el documento o formato que lo origina.
- Sin contradicciones entre `Registros asociados` y `docs/_control/matriz_registros.yml`.
