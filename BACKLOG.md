# BACKLOG inicial (tareas sugeridas para Codex)

> Cada tarea debe terminar con:
> 1) documento creado/actualizado en su ruta,
> 2) validacion de frontmatter,
> 3) regeneracion de `docs/_control/lmd.yml` y `docs/_control/matriz_registros.yml` via `sgc-build-indexes`.

## 1) Gobierno y estructura
- [x] Crear/actualizar `docs/02_mapa_procesos/ESP-SGC-01_Mapa_de_Procesos_del_SGC.md` (borrador).
- [x] Crear fichas de proceso de nivel minimo viable (estrategico/operativo/soporte).

## 2) Documentacion base
- [x] POL-SGC-01 Politica de Calidad.
- [x] PLAN-SGC-01 Objetivos de Calidad (y metodo de seguimiento).
- [x] PR-SGC-02 Control de No Conformidades y CAPA.
- [x] PR-SGC-03 Auditorias internas.
- [x] PR-SGC-04 Gestion de Indicadores y Analisis de Datos.
- [x] PR-SGC-05 Revision por la Direccion.
- [x] PR-SGC-06 Gestion de Riesgos y Oportunidades.
- [x] PR-SGC-07 Evaluacion de Proveedores (si aplica).
- [x] PR-SGC-08 Competencia y Formacion.
- [x] PLAN-SGC-02 Digitalizacion del SGC (fase opcional).

## 3) Formatos y registros minimos
- [x] FOR-SGC-02 Registro de No Conformidad.
- [x] FOR-SGC-03 Plan/Registro CAPA + verificacion de eficacia.
- [x] FOR-SGC-04 Programa de auditorias.
- [x] FOR-SGC-05 Plan de auditoria.
- [x] FOR-SGC-06 Informe de auditoria.
- [x] FOR-SGC-07 Seguimiento de acciones.
- [x] FOR-SGC-08 Matriz de KPI.
- [x] FOR-SGC-09 Acta de Revision por la Direccion.
- [x] FOR-SGC-10 Matriz de riesgos.
- [x] FOR-SGC-11 Plan de tratamiento y seguimiento de riesgos.
- [x] FOR-SGC-12 Matriz de homologacion y evaluacion de proveedores.
- [x] FOR-SGC-13 Matriz de competencias.
- [x] FOR-SGC-14 Plan y registro de capacitacion.
- [x] FOR-SGC-15 Evaluacion de eficacia de capacitacion.

## 4) Limpieza y consistencia
- [x] Revisar codificacion y versionado (consistencia).
- [x] Validar que cada procedimiento enumere registros asociados y esten en la matriz de registros.

## 5) Sprint 1 multidisciplina (Civil / Mecanica / Electrica)
- [ ] Publicar taxonomia oficial por disciplina y subdisciplina.
- [ ] Definir campos tecnicos minimos de metadatos (`disciplina`, `criticidad_tecnica`, `norma_aplicable`, `proyecto_referencia`).
- [ ] Crear plantillas por disciplina:
  - [ ] `templates/TEMPLATE_Ficha_Tecnica_Disciplina.md`
  - [ ] `templates/TEMPLATE_ITP_Disciplina.md`
  - [ ] `templates/TEMPLATE_Checklist_Liberacion_Disciplina.md`
- [ ] Definir gobernanza de aprobaciones tecnicas por disciplina en `CODEOWNERS`.
- [ ] Ejecutar 1 piloto real por disciplina y conservar evidencia (PR + run CI + REG-SGC-CDC).
