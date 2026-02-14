---
name: crear_documento
description: Debe activar cuando el usuario pida crear/editar documentacion del SGC (politicas, procedimientos, instructivos, formatos) en /docs siguiendo las convenciones del repo; NO debe activar para discusiones teoricas sin salida documental.
---

# Objetivo
Crear o editar un documento controlado del SGC en `docs/` con estructura estandar, trazabilidad y consistencia con el resto del sistema documental.

# Cuando usar / Cuando NO usar
- Usar cuando el pedido termina en un entregable documental dentro de `docs/` (nuevo archivo o actualizacion de uno existente).
- Usar cuando se pidan politicas, procedimientos, instructivos, formatos, planes, especificaciones o manuales controlados.
- NO usar para preguntas conceptuales sin creacion/edicion de archivos.
- NO usar para auditorias de coherencia global (en ese caso, usar `validar_trazabilidad`).

# Entradas esperadas
- Tipo de documento (`POL`, `PR`, `IT`, `FOR`, `PLAN`, `ESP`, `MAN`).
- Proceso y alcance del documento.
- Objetivo operativo del documento.
- Estado deseado (`BORRADOR`, `VIGENTE`, `OBSOLETO`), si se especifica.
- Responsables (`elaboro`, `reviso`, `aprobo`) o `TODO: <dato>` si faltan.
- Referencias a formatos/registros asociados, si aplica.

# Flujo paso a paso
1. Revisar si existe un documento similar en `docs/` para mantener formato y vocabulario.
2. Definir `codigo` con el patron `[TIPO]-[AREA/PROCESO]-[NNN]` y verificar que no este duplicado.
3. Definir ruta y nombre de archivo: `CODIGO_Titulo_sin_acentos.md`.
4. Crear o actualizar el archivo con frontmatter YAML del repo:
```yaml
---
codigo: "PR-SGC-XX"
titulo: "Nombre del documento"
tipo: "PR|POL|IT|FOR|PLAN|ESP|MAN"
version: "1.0"
estado: "BORRADOR|VIGENTE|OBSOLETO"
fecha_emision: "YYYY-MM-DD"
proceso: "SGC / <Proceso>"
elaboro: "<Nombre>"
reviso: "<Nombre>"
aprobo: "<Nombre>"
---
```
5. Escribir o actualizar secciones minimas: Objetivo, Alcance, Referencias (si aplica), Definiciones (si aplica), Responsabilidades, Desarrollo/Metodologia, Registros asociados, Control de cambios.
6. Incluir estructura estandar solicitada: codigo, titulo, version, estado, responsables, historial/control de cambios y anexos cuando aplique.
7. Mantener redaccion verificable y usar placeholders cuando falten datos (`TODO: <dato>`, `<NOMBRE_EMPRESA>`, `<PUESTO>`, `<AREA>`).
8. Verificar que las referencias internas (codigos/rutas) existan realmente en el repo.
9. Ejecutar `sgc-build-indexes` para regenerar LMD y matriz de registros.

# Reglas
- Estado por defecto: `BORRADOR`.
- No marcar `VIGENTE` sin aprobacion explicita del usuario o instruccion documental equivalente.
- Primera emision: `version: "1.0"`.
- No inventar datos organizacionales o legales; usar placeholders/TODO.

# Definicion de Terminado (DoD)
- Documento creado o actualizado en la ruta correcta y con estructura completa.
- Frontmatter valido para el esquema del runtime.
- Indices (`lmd.yml`, `matriz_registros.yml`) regenerados via `sgc-build-indexes`.
- Referencias cruzadas verificadas contra archivos y codigos reales.

# Ejemplos que SI disparan
- "Crea el procedimiento PR-SGC-09 para gestion de cambios."
- "Actualiza el formato FOR-SGC-02 y agrega su control de cambios."
- "Redacta la politica de calidad en `docs/01_politica_objetivos`."

# Ejemplos que NO disparan
- "Explicame que es ISO 9001:2015."
- "Dame ideas para mejorar la cultura de calidad."
- "Compara teoricamente CAPA vs accion correctiva."
