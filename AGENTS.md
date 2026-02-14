# AGENTS.md (instrucciones para Codex)

## Contexto del proyecto
Estas trabajando en un repositorio documental para un **Sistema de Gestion de Calidad (SGC)** alineado a **ISO 9001:2015**.
El objetivo es generar y mantener **documentos controlados** (politicas, procedimientos, instructivos, formatos) y **registros** (evidencias) con trazabilidad y consistencia.

### Alcance del trabajo de Codex
- Crear/editar archivos **Markdown (.md)** dentro de `docs/`.
- Tratar el **frontmatter YAML de cada documento** como unica fuente de verdad (SSOT).
- Regenerar indices de control con `sgc-build-indexes`:
  - `docs/_control/lmd.yml` (Lista Maestra de Documentos)
  - `docs/_control/matriz_registros.yml` (Matriz de Registros)
- Considerar `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml` como artefactos generados (no editar manualmente).
- Mantener coherencia entre documentos (referencias cruzadas).

## Convenciones obligatorias (SGC)
### 1) Formato de cada documento (Markdown + metadatos)
Todos los documentos controlados deben iniciar con un bloque YAML:

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

Luego incluir secciones minimas:
- Objetivo
- Alcance
- Referencias (si aplica)
- Definiciones (si aplica)
- Responsabilidades
- Desarrollo / Metodologia
- Registros asociados
- Control de cambios

### 2) Codificacion y nombres de archivo
- Codigo: `[TIPO]-[AREA/PROCESO]-[NNN]` (ej: `PR-SGC-01`).
- Nombre de archivo: `CODIGO_Titulo_sin_acentos.md`
  - Ej: `PR-SGC-01_Control_de_Documentos_y_Registros.md`

### 3) Versionado
- Primera emision: `1.0`
- Cambios menores: `1.1`, `1.2`
- Cambios mayores: `2.0`, `3.0`

### 4) No inventar datos organizacionales
Si falta informacion (nombre de empresa, organigrama, etc.):
- Usa placeholders: `<NOMBRE_EMPRESA>`, `<PUESTO>`, `<AREA>`
- O marca con `TODO:` de forma explicita.

## Definicion de Terminado (DoD) por tarea
Una tarea se considera terminada solo si:
1. El/los documentos solicitados existen en la ruta correcta, con estructura completa.
2. El frontmatter del documento es valido y consistente (`codigo`, `tipo`, `version`, `estado`, `proceso`).
3. Se ejecuta `sgc-build-indexes` (o `rebuild_control_indexes`) para regenerar `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml`.
4. Las referencias internas (codigos de formatos/procedimientos/registros) coinciden con nombres reales de archivo y codigos `REG-*`.
5. Cuando la tarea afecte trazabilidad o registros, ejecutar pipeline QA: `auditar_invariantes_de_estado`, `resolver_grafo_documental`, `detectar_formatos_huerfanos`, `auditar_trazabilidad_registros`.
6. No editar manualmente `docs/_control/lmd.yml` ni `docs/_control/matriz_registros.yml`; deben provenir de `sgc-build-indexes` y sin drift en CI.

## Estilo de redaccion (documentacion)
- Espanol neutro, formal y operativo.
- Instrucciones verificables ("debe", "se realiza", "se registra").
- Evitar ambiguedades; si son inevitables, poner condicion o criterio medible.

## Como ejecutar el trabajo (recomendado)
- Para cambios grandes: primero escribe un plan corto (maximo 10 bullets), luego ejecuta.
- Trabaja incrementalmente: **1 documento por tarea**.
- Antes de crear un documento nuevo, revisa si ya existe uno similar para mantener consistencia.
