---
marp: true
theme: default
paginate: true
size: 16:9
title: SGC Autónomo (Docs-as-Code + IA)
description: Presentación ejecutiva del sistema de gestión de calidad ISO 9001
---

# SGC Autónomo (Docs-as-Code + IA)
## Gestión de Calidad en la Era del Código

- Repositorio: `/Users/hector/Projects/SGC`
- Corte del repositorio: **14-feb-2026**
- Enfoque: ISO 9001 + ingeniería de software + agentes IA

**Nota del orador**
Transformamos la gestión documental del SGC en un sistema auditable como software: versionado, validado y trazable.

---

# 1) El Nuevo Paradigma del SGC

- Sistema ISO 9001 modelado en **Markdown + YAML**.
- Todos los documentos viven en repositorio Git con historial completo.
- IA acelera redacción y revisión semántica.
- Cumplimiento crítico se garantiza con validaciones deterministas.

**Nota del orador**
No dependemos de archivos estáticos ni controles manuales frágiles. El sistema se comporta como un pipeline de calidad reproducible.

---

# 2) Principio Arquitectónico Clave (SSOT)

- La **única fuente de verdad** es el `frontmatter` YAML de cada `.md`.
- Se prohíbe edición manual de índices de control.
- `sgc-build-indexes` autogenera:
  - `lmd.yml` (Lista Maestra de Documentos)
  - `matriz_registros.yml` (Matriz de Registros)
- `lmd.yml` y `matriz_registros.yml` son **artefactos generados**.

**Nota del orador**
La lista maestra deja de ser un documento “mantenido a mano” y pasa a ser un resultado compilado desde la evidencia real.

---

# 3) Arquitectura del Runtime

- `orchestrator.py`: enrutamiento y coordinación de tareas.
- `specialists.py`: segregación de roles (Writer, Compliance, Auditoría).
- `build_indexes.py`: generación determinista de índices.
- `compliance_tools.py`: motor QA neuro-simbólico.

**Nota del orador**
Separamos responsabilidades como en un equipo de calidad real: quien redacta no es quien aprueba ni quien audita.

---

# 4) Auditoría Neuro-Simbólica

- Capa simbólica (determinista):
  - invariantes de estado
  - grafo documental y enlaces rotos
  - formatos huérfanos
  - trazabilidad P1..P5
- Capa neuronal (LLM):
  - análisis semántico
  - redacción de hallazgos y no conformidades

**Nota del orador**
La IA no “adivina” cumplimiento. La lógica lo valida primero; el LLM interpreta y explica después.

---

# 5) Flujo End-to-End ("Si falla, no compila")

1. Se crea/edita documento en `docs/`.
2. Se valida frontmatter y codificación.
3. Se ejecuta `sgc-build-indexes`.
4. Se corre pipeline QA (`auditar_*`, `resolver_*`, `detectar_*`, `trazabilidad`).
5. Si falla una regla, el cambio no debe promoverse a vigente.
6. Se emite `reporte_qa_compliance.md`.

**Nota del orador**
Aplicamos disciplina CI/CD a ISO 9001: la no conformidad se bloquea antes de contaminar el sistema.

---

# 6) Estado Actual (Corte: 14-feb-2026)

- Índices consolidados: **31** documentos controlados.
- Matriz autogenerada: **16** entradas de registro.
- Auditoría de trazabilidad: **8 registros auditados (muestra actual)**.
- Resultado QA en el corte: **0 hallazgos**.
- Remediaciones ejecutadas:
  - migración de `06_registros` al contrato `formato_origen`
  - corrección de referencias rotas
  - limpieza de placeholders críticos en vigentes

**Nota del orador**
El “0 hallazgos” corresponde a la muestra auditada de 8 registros del corte, no a una garantía eterna sin ejecución continua.

---

# 7) Valor Estratégico (ROI)

- Trazabilidad ISO verificable y repetible.
- Menor riesgo por error manual en listas y matrices.
- Auditorías más rápidas con evidencia reproducible.
- Base escalable para operación 24/7 con agentes.

**Nota del orador**
Se reduce fricción operativa y riesgo de auditoría externa, manteniendo gobernanza documental estricta.

---

# 8) Roadmap 30 / 60 / 90 días

- **30 días**
  - completar `responsable`, `retencion`, `disposicion_final`, `acceso` en matriz
  - publicar política de no edición manual de artefactos generados
- **60 días**
  - integrar QA en CI (bloqueo automático de cambios no conformes)
  - políticas de branch/protección para índices
- **90 días**
  - consolidación topológica por dominio/proceso
  - ampliar QA semántico para eficacia CAPA y causa raíz

**Nota del orador**
La fase actual asegura forma y trazabilidad; el siguiente salto es asegurar eficacia real de mejora continua.
