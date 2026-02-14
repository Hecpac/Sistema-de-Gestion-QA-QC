# Workflow recomendado para trabajar con Codex en este repo

## 1) Principio: prompts estilo "Issue"
Estructura cada tarea como si fuera un issue:
- Contexto
- Objetivo
- Alcance (que si / que no)
- Archivos involucrados (paths)
- Reglas de aceptacion (Definition of Done)

## 2) Ask -> Code
Para cambios medianos/grandes:
1. Pide a Codex un plan breve (Ask mode).
2. Revisa/ajusta.
3. Ejecuta (Code mode) en incrementos.

## 3) Plantilla de prompt (copiar/pegar)
**Tarea:** <Titulo corto>

**Contexto**
- Estamos construyendo documentacion del SGC en Markdown (ver `AGENTS.md`).

**Objetivo**
- Crear/actualizar: <documento(s)>

**Requisitos**
- Usar plantilla: <ruta>
- Incluir secciones minimas y metadatos YAML.
- Validar frontmatter con esquema del runtime.
- Regenerar indices con `sgc-build-indexes`.
- Verificar que no exista drift en artefactos generados (`docs/_control/lmd.yml`, `docs/_control/matriz_registros.yml`).
- Ejecutar QA deterministico (`auditar_invariantes_de_estado`, `resolver_grafo_documental`, `detectar_formatos_huerfanos`, `auditar_trazabilidad_registros`) cuando aplique.

**Archivos**
- Crear/editar: `docs/...`
- Regenerar automaticamente: `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml`

**Criterios de aceptacion**
- El documento queda completo y consistente con el resto del SGC.
- No hay referencias rotas (codigos/formularios/registros).
- Los indices generados reflejan el estado actual de `docs/`.
