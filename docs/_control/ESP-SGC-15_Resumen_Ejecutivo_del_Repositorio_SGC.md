---
codigo: "ESP-SGC-15"
titulo: "Resumen Ejecutivo del Repositorio SGC"
tipo: "ESP"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-17"
proceso: "SGC / Control Documental"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# ESP-SGC-15 Resumen Ejecutivo del Repositorio SGC

## 1. Objetivo
Describir el proposito, principios de diseno, estructura y mecanismo de control del repositorio del Sistema de Gestion de Calidad (SGC), para facilitar su uso operativo y su auditoria.

## 2. Alcance
Aplica a la estructura documental del repositorio (documentos controlados, registros y artefactos de control), asi como al runtime y automatizaciones asociadas para mantener trazabilidad y consistencia.

## 3. Referencias
- ISO 9001:2015, 7.5 Informacion documentada.
- PR-SGC-01 Control de Documentos y Registros.
- `README.md`.
- `AGENTS.md` y `docs/AGENTS.md`.
- `STRUCTURE.md`, `ROADMAP.md` y `CODEX_WORKFLOW.md`.
- `agent_runtime/README.md` y `agent_runtime/pyproject.toml`.
- `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml`.

## 4. Definiciones
- Documento controlado: archivo Markdown bajo `docs/` con frontmatter YAML valido (`codigo`, `tipo`, `version`, `estado`, `proceso`) y secciones minimas.
- Registro: evidencia operativa generada por la ejecucion del SGC, ubicada bajo `docs/06_registros/`.
- SSOT (Single Source of Truth): la unica fuente de verdad para indices de control es el frontmatter YAML de los documentos controlados.
- Artefacto generado: archivo de control autogenerado (por ejemplo, LMD, matriz de registros, dashboard y reporte de QA) que no debe editarse manualmente.

## 5. Responsabilidades
- Coordinacion de Calidad: mantener este resumen, definir reglas de control documental y ejecutar la regeneracion de artefactos cuando existan cambios.
- Duenos de proceso: asegurar que sus documentos y registros asociados sean coherentes, trazables y se encuentren actualizados.
- Direccion: aprobar cambios mayores al modelo documental y asegurar recursos para sostener el control del SGC.
- Equipo tecnico (si aplica): mantener el runtime, pipelines y automatizaciones de QA.

## 6. Desarrollo / Metodologia
### 6.1 Proposito del proyecto
Este repositorio implementa un SGC documental alineado a ISO 9001:2015 bajo el enfoque Docs-as-Code:
1. Los documentos controlados viven como Markdown versionado en Git.
2. La informacion de control se deriva de metadatos (frontmatter), no de indices mantenidos manualmente.
3. La trazabilidad y coherencia se validan con reglas deterministas (QA) y se reportan como artefactos auditablemente reproducibles.

### 6.2 Principios de control documental (SSOT)
1. Todo documento controlado en `docs/` debe iniciar con frontmatter YAML conforme al esquema del runtime.
2. `docs/_control/lmd.yml` (Lista Maestra de Documentos) y `docs/_control/matriz_registros.yml` (Matriz de Registros) son artefactos generados.
3. No se permite editar manualmente los artefactos generados; el cambio valido es actualizar documentos fuente y regenerar indices.

### 6.3 Estructura principal del repositorio
La estructura se organiza por componentes con responsabilidades claras:
- `docs/`: sistema documental del SGC (documentos controlados, registros y control).
- `templates/`: plantillas canonicas para crear documentos del SGC con estructura estandar.
- `agent_runtime/`: runtime en Python que implementa herramientas para generar indices, ejecutar QA y producir reportes/dashboards.
- `.agents/skills/`: guias operativas (skills) para estandarizar tareas recurrentes al trabajar con Codex.
- `.github/workflows/`: automatizacion CI para gate de QA y monitor semanal.

### 6.4 Estructura de `docs/` (documentos y registros)
Dentro de `docs/` se distinguen tres categorias:
1. `docs/_control/`: artefactos y documentos de control documental (LMD, matriz de registros, dashboard, reportes).
2. Carpetas tematicas del SGC (documentos controlados), por ejemplo:
   - `01_politica_objetivos/`, `02_mapa_procesos/`, `03_procedimientos/`, `04_instructivos/`, `05_formatos/`.
   - `07_auditorias/`, `08_riesgos/`, `09_proveedores/`, `10_competencia_formacion/`.
3. `docs/06_registros/`: registros operativos (evidencia). Su contrato de trazabilidad se define en `docs/06_registros/README.md`.

### 6.5 Generacion determinista de control (indices y dashboard)
El runtime expone comandos para regenerar artefactos desde la fuente de verdad:
- `sgc-build-indexes`: genera `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml`.
- `sgc-build-dashboard`: genera `docs/_control/dashboard_sgc.html` y consolida la salida de QA.

### 6.6 QA deterministico (gate de consistencia)
El repositorio aplica un gate QA deterministico para prevenir degradacion documental:
1. Invariantes de estado: documentos `VIGENTE` sin notas pendientes ni placeholders.
2. Grafo documental: referencias de procedimientos a formatos (PR -> FOR) sin enlaces rotos.
3. Formatos huerfanos: formatos FOR sin uso o sin alta en matriz, segun reglas del runtime.
4. Trazabilidad de registros: registros bajo `docs/06_registros/` con frontmatter requerido y consistencia con formatos origen.

### 6.7 Automatizacion (CI y monitor)
En `.github/workflows/` se definen automatizaciones que soportan el control:
- Gate QA en PR/push: ejecuta tests, regenera artefactos y verifica que no haya drift de artefactos generados.
- Monitor semanal: ejecuta el script `agent_runtime/scripts/run_qa_monitor.sh`, publica artefactos y crea issue si detecta fallas.

### 6.8 Uso recomendado (operacion diaria)
1. Crear o editar un documento controlado usando una plantilla en `templates/`.
2. Verificar frontmatter, codigo y nombre de archivo conforme a `AGENTS.md`.
3. Regenerar indices con `sgc-build-indexes` y, si aplica, dashboard con `sgc-build-dashboard`.
4. Ejecutar QA deterministico y corregir hallazgos antes de promover cambios relevantes.

## 7. Registros asociados
- REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique creacion o modificacion de documentos controlados).
- REG-SGC-COM - Evidencia de distribucion/comunicacion de documentos (cuando aplique publicacion o comunicacion).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-17 | Emision inicial del resumen ejecutivo del repositorio | Coordinacion de Calidad | Direccion General |
