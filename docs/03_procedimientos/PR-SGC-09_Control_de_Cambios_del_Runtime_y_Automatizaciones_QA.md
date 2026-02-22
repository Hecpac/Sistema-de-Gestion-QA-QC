---
codigo: "PR-SGC-09"
titulo: "Control de Cambios del Runtime y Automatizaciones QA"
tipo: "PR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-22"
proceso: "SGC / Control Documental"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# PR-SGC-09 Control de Cambios del Runtime y Automatizaciones QA

## 1. Objetivo
Establecer la metodología para controlar, revisar, aprobar y validar los cambios al runtime del SGC y a sus automatizaciones de QA, asegurando evidencia forense verificable (quién, qué, cuándo, por qué) y evitando drift en artefactos generados del control documental.

## 2. Alcance
Aplica a cambios sobre:
- Runtime y herramientas: `agent_runtime/` (generación de índices, dashboard, QA determinístico).
- Automatizaciones CI/monitor: `.github/workflows/` y `agent_runtime/scripts/`.
- Convenciones operativas del repositorio: `AGENTS.md`, `docs/AGENTS.md` y `.agents/skills/`.
- Plantillas y estructura documental: `templates/` y `STRUCTURE.md`.

Excluye:
- Cambios puramente editoriales en documentos controlados que no alteren criterios, reglas o trazabilidad (se controlan por PR-SGC-01).

## 3. Referencias
- ISO 9001:2015, 7.5 Información documentada.
- ISO 9001:2015, 8.5.6 Control de los cambios.
- [PR-SGC-01 Control de Documentos y Registros](PR-SGC-01_Control_de_Documentos_y_Registros.md).
- [SGC QA Gate](../../.github/workflows/sgc-qa.yml).
- [SGC Weekly Monitor](../../.github/workflows/sgc-weekly-monitor.yml).
- [agent_runtime/README.md](../../agent_runtime/README.md).
- [CODEX_WORKFLOW.md](../../CODEX_WORKFLOW.md).

## 4. Definiciones
- Pull Request (PR de plataforma): solicitud de cambios en Git (por ejemplo, GitHub), con revisiones y evidencias de aprobación.
- Gate QA: conjunto de verificaciones automáticas que deben pasar antes de integrar un cambio (tests, rebuild de artefactos, QA determinístico).
- Evidencia forense: trazabilidad verificable en el repositorio (hash de commit, PR aprobado, logs de CI, artefactos generados).
- Baseline del SGC: punto de liberación controlado (tag) que identifica un estado auditable del repositorio.

## 5. Responsabilidades
- Coordinación de Calidad:
  - Definir criterios de QA y aceptación para cambios de control documental.
  - Verificar impacto en LMD, matriz de registros y trazabilidad.
- Administración del repositorio SGC:
  - Mantener el runtime y la automatización (CI/monitor).
  - Atender alertas del gate/monitor y coordinar correcciones.
- Revisor técnico (runtime/CI):
  - Revisar cambios en `agent_runtime/`, `.github/workflows/` y scripts.
- Aprobación (Dirección General o rol delegado):
  - Autorizar cambios mayores que afecten el control documental, criterios de QA o el mecanismo de liberación/baseline.

## 6. Desarrollo / Metodología

### 6.1 Clasificación del cambio
Todo cambio al runtime/automatizaciones debe clasificarse antes de ejecutar:
1. Menor: ajuste sin impacto en reglas de QA, sin cambios de interfaces, sin cambios de salida en artefactos (salvo timestamps).
2. Mayor: modifica reglas de QA, estructura de índices, criterios de validación, o afecta el modelo de trazabilidad.

### 6.2 Solicitud y registro del cambio
1. Registrar la solicitud de cambio usando FOR-SGC-01:
   - Documento: [FOR-SGC-01 Solicitud de Creación / Cambio Documental](../_control/FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md).
2. Conservar el registro llenado como evidencia:
   - REG-SGC-CDC (ver ubicación definida en `docs/_control/matriz_registros.yml`).
3. En la solicitud, incluir como mínimo:
   - Justificación del cambio (riesgo o mejora).
   - Componentes afectados (rutas).
   - Criterios de aceptación.
   - Enlace/ID del PR de plataforma (si existe).

### 6.3 Revisión y aprobación (evidencia equivalente a firma)
El cambio se considera aprobado cuando se cumplan simultáneamente:
1. Existe un PR de plataforma asociado con:
   - Revisiones registradas (quién revisó).
   - Aprobación registrada (quién aprobó y cuándo).
2. Los checks del gate QA han pasado (ver 6.4).
3. El merge ocurre a la rama protegida (por ejemplo, `main`) y queda trazable por hash.

Si se requiere aprobación fuera de plataforma (por ejemplo, aprobación manual), se debe adjuntar evidencia documental al REG-SGC-CDC (por ejemplo, acta o autorización firmada) y registrar la referencia en el mismo.

### 6.4 Validación obligatoria del cambio (gate QA)
Antes de integrar un cambio al runtime/automatizaciones:
1. Ejecutar pruebas unitarias del runtime:
   - `pytest -q agent_runtime/tests`
2. Regenerar artefactos de control:
   - `sgc-build-indexes`
   - `sgc-build-dashboard`
3. Confirmar ausencia de drift en artefactos generados:
   - `docs/_control/lmd.yml`
   - `docs/_control/matriz_registros.yml`
   - `docs/_control/dashboard_sgc.html`
4. Ejecutar QA determinístico (0 hallazgos):
   - `auditar_invariantes_de_estado`
   - `resolver_grafo_documental`
   - `detectar_formatos_huerfanos`
   - `auditar_trazabilidad_registros`

### 6.5 Control de cambios del propio runtime (herramienta crítica)
Para cambios clasificados como Mayores (6.1):
1. Revisión técnica obligatoria por un revisor distinto al autor.
2. Actualización de documentación asociada (por ejemplo, `agent_runtime/README.md` y/o especificaciones en `docs/_control/`).
3. Registro explícito en el REG-SGC-CDC de:
   - Resultado de validación.
   - Riesgos introducidos y mitigaciones.

### 6.6 Liberación de baseline (tag auditable)
Cuando se requiera publicar un baseline:
1. Confirmar gate QA en cero hallazgos.
2. Crear tag anotado (patrón sugerido): `sgc-baseline-YYYY-MM-DD`.
3. Registrar en el REG-SGC-CDC el tag, hash y el resumen de resultados (conteos de LMD/matriz y hallazgos QA).

### 6.7 Configuración mínima de gobierno (para que el PR de plataforma sea evidencia válida)
Para considerar el PR de plataforma como evidencia equivalente a firma, la administración del repositorio debe asegurar, como mínimo:
1. Rama protegida (por ejemplo, `main`): no se permite push directo.
2. Aprobaciones requeridas: al menos 1 aprobación del revisor designado (Calidad y/o Administración del repositorio SGC, según el tipo de cambio).
3. Checks requeridos: gate QA obligatorio (ver `.github/workflows/sgc-qa.yml`) antes del merge.
4. Trazabilidad: el merge debe quedar reflejado como commit en rama protegida y accesible por hash.

Cuando alguna de estas condiciones no esté disponible (por ejemplo, repositorio sin plataforma de PR), se debe conservar evidencia alternativa dentro del REG-SGC-CDC (acta o autorización firmada) y registrar el hash del commit aprobado.

### 6.8 Control de cambios en reglas operativas (AGENTS.md y skills)
Los archivos `AGENTS.md`, `docs/AGENTS.md` y `.agents/skills/**/SKILL.md` se consideran reglas operativas del sistema documental. Por lo tanto:
1. Todo cambio debe registrarse en FOR-SGC-01 y conservar evidencia en REG-SGC-CDC.
2. Debe existir revisión por Coordinación de Calidad y Administración del repositorio SGC.
3. El cambio debe pasar el gate QA cuando impacte artefactos de control o trazabilidad.

## 7. Registros asociados
- REG-SGC-CDC — Solicitud de Creación/Cambio Documental (llenada) / evidencia del cambio al runtime.
- REG-SGC-COM — Evidencia de distribución/comunicación (cuando se publique baseline o se comunique cambio relevante).
- REG-SGC-NC — Registro de No Conformidad (si un cambio causa falla de gate/monitor en operación).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-22 | Emision inicial (vigente) del procedimiento de control de cambios del runtime y automatizaciones QA | Coordinacion de Calidad | Direccion General |
