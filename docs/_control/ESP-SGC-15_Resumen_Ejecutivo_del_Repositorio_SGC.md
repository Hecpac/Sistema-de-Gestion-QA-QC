---
codigo: "ESP-SGC-15"
titulo: "Resumen Ejecutivo del Repositorio SGC"
tipo: "ESP"
version: "1.1"
estado: "VIGENTE"
fecha_emision: "2026-02-17"
proceso: "SGC / Control Documental"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# ESP-SGC-15 Resumen Ejecutivo del Repositorio SGC

## 1. Objetivo
Describir el propósito, principios de diseño, estructura y mecanismo de control del repositorio del Sistema de Gestión de Calidad (SGC), para facilitar su uso operativo y su auditoría.

## 2. Alcance
Aplica a la estructura documental del repositorio (documentos controlados, registros y artefactos de control), así como al runtime y automatizaciones asociadas para mantener trazabilidad y consistencia.

## 3. Referencias
- ISO 9001:2015, 7.5 Información documentada.
- [PR-SGC-01 Control de Documentos y Registros](../03_procedimientos/PR-SGC-01_Control_de_Documentos_y_Registros.md).
- [README.md](../../README.md).
- [AGENTS.md](../../AGENTS.md) y [docs/AGENTS.md](../AGENTS.md).
- [STRUCTURE.md](../../STRUCTURE.md), [ROADMAP.md](../../ROADMAP.md) y [CODEX_WORKFLOW.md](../../CODEX_WORKFLOW.md).
- [agent_runtime/README.md](../../agent_runtime/README.md) y [agent_runtime/pyproject.toml](../../agent_runtime/pyproject.toml).
- [docs/_control/lmd.yml](lmd.yml) y [docs/_control/matriz_registros.yml](matriz_registros.yml).

## 4. Definiciones
- Documento controlado: archivo Markdown bajo `docs/` con frontmatter YAML válido (`codigo`, `tipo`, `version`, `estado`, `proceso`) y secciones mínimas.
- Registro: evidencia operativa generada por la ejecución del SGC, ubicada bajo `docs/06_registros/`.
- SSOT (Single Source of Truth): la única fuente de verdad para índices de control es el frontmatter YAML de los documentos controlados.
- Artefacto generado: archivo de control autogenerado (por ejemplo, LMD, matriz de registros, dashboard y reporte de QA) que no debe editarse manualmente.

## 5. Responsabilidades
- Coordinación de Calidad: mantener este resumen, definir reglas de control documental y ejecutar la regeneración de artefactos cuando existan cambios.
- Dueños de proceso: asegurar que sus documentos y registros asociados sean coherentes, trazables y se encuentren actualizados.
- Dirección: aprobar cambios mayores al modelo documental y asegurar recursos para sostener el control del SGC.
- Administración del repositorio SGC: mantener el runtime, pipelines y automatizaciones de QA, y atender alertas del gate/monitor.

## 6. Desarrollo / Metodología
### 6.1 Propósito del proyecto
Este repositorio implementa un SGC documental alineado a ISO 9001:2015 bajo el enfoque Docs-as-Code:
1. Los documentos controlados viven como Markdown versionado en Git.
2. La información de control se deriva de metadatos (frontmatter), no de índices mantenidos manualmente.
3. La trazabilidad y coherencia se validan con reglas deterministas (QA) y se reportan como artefactos auditablemente reproducibles.

### 6.2 Principios de control documental (SSOT)
1. Todo documento controlado en `docs/` debe iniciar con frontmatter YAML conforme al esquema del runtime.
2. `docs/_control/lmd.yml` (Lista Maestra de Documentos) y `docs/_control/matriz_registros.yml` (Matriz de Registros) son artefactos generados.
3. No se permite editar manualmente los artefactos generados; el cambio válido es actualizar documentos fuente y regenerar índices.
4. En caso de discrepancia entre texto del cuerpo y metadatos, prevalece el frontmatter YAML.

### 6.3 Estructura principal del repositorio
La estructura se organiza por componentes con responsabilidades claras:
- `docs/`: sistema documental del SGC (documentos controlados, registros y control).
- `templates/`: plantillas canónicas para crear documentos del SGC con estructura estándar.
- `agent_runtime/`: runtime en Python que implementa herramientas para generar indices, ejecutar QA y producir reportes/dashboards.
- `.agents/skills/`: guias operativas (skills) para estandarizar tareas recurrentes al trabajar con Codex.
- `.github/workflows/`: automatización CI para gate de QA y monitor semanal.

### 6.4 Estructura de `docs/` (documentos y registros)
Dentro de `docs/` se distinguen tres categorias:
1. `docs/_control/`: artefactos y documentos de control documental (LMD, matriz de registros, dashboard, reportes).
2. Carpetas temáticas del SGC (documentos controlados), por ejemplo:
   - `01_politica_objetivos/`, `02_mapa_procesos/`, `03_procedimientos/`, `04_instructivos/`, `05_formatos/`.
   - `07_auditorias/`, `08_riesgos/`, `09_proveedores/`, `10_competencia_formacion/`.
3. `docs/06_registros/`: registros operativos (evidencia). Su contrato de trazabilidad se define en `docs/06_registros/README.md`.

### 6.5 Generación determinista de control (índices y dashboard)
El runtime expone comandos para regenerar artefactos desde la fuente de verdad:
- `sgc-build-indexes`: genera `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml`.
- `sgc-build-dashboard`: genera `docs/_control/dashboard_sgc.html` y consolida la salida de QA.

### 6.6 QA determinístico (gate de consistencia)
El repositorio aplica un gate QA determinístico para prevenir degradación documental:
1. Invariantes de estado: documentos `VIGENTE` sin notas pendientes ni placeholders.
2. Grafo documental: referencias de procedimientos a formatos (PR -> FOR) sin enlaces rotos.
3. Formatos huérfanos: formatos FOR sin uso o sin alta en matriz, según reglas del runtime.
4. Trazabilidad de registros: registros bajo `docs/06_registros/` con frontmatter requerido y consistencia con formatos origen.

### 6.7 Automatización (CI y monitor)
En `.github/workflows/` se definen automatizaciones que soportan el control:
- Gate QA en PR/push: ejecuta tests, regenera artefactos y verifica que no haya drift de artefactos generados.
- Monitor semanal: ejecuta el script `agent_runtime/scripts/run_qa_monitor.sh`, publica artefactos y crea issue si detecta fallas.

### 6.8 Uso recomendado (operación diaria)
1. Crear o editar un documento controlado usando una plantilla en `templates/`.
2. Verificar frontmatter, codigo y nombre de archivo conforme a `AGENTS.md`.
3. Regenerar indices con `sgc-build-indexes` y, si aplica, dashboard con `sgc-build-dashboard`.
4. Ejecutar QA determinístico y corregir hallazgos antes de promover cambios relevantes.

## 7. Registros asociados
- REG-SGC-CDC - Solicitud de Creación/Cambio Documental (cuando aplique creación o modificación de documentos controlados).
- REG-SGC-COM - Evidencia de distribución/comunicación de documentos (cuando aplique publicación o comunicación).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Reviso | Aprobo |
|---|---:|---|---|---|---|
| 1.0 | 2026-02-17 | Emision inicial del resumen ejecutivo del repositorio | Coordinacion de Calidad | Gerencia de Operaciones | Direccion General |
| 1.1 | 2026-02-17 | Correccion de referencias con hipervinculos, ajuste de responsabilidades y normalizacion ortografica | Coordinacion de Calidad | Gerencia de Operaciones | Direccion General |
