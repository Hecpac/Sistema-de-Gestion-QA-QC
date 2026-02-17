# Sprint 1 - Habilitacion Multidisciplina (Civil / Mecanica / Electrica)

## Objetivo del sprint
Dejar el SGC listo para operar con multiples disciplinas tecnicas, sin romper los controles Zero-Trust actuales.

## Duracion sugerida
- 10 dias habiles (2 semanas)

## Entregables obligatorios
1. Taxonomia base por disciplina (catalogo y codigos).
2. Plantillas tecnicas por disciplina (ITP + Ficha tecnica + checklist).
3. Mapeo de aprobadores por disciplina (CODEOWNERS + responsabilidades).
4. Reglas QA minimas para campos de disciplina (modo no bloqueante en Sprint 1).
5. Evidencia piloto con 1 flujo por disciplina.

---

## Workstream A - Taxonomia y modelo de datos

### Tareas
- [ ] Definir catalogo oficial de disciplinas y subdisciplinas.
- [ ] Definir campos de metadatos nuevos para documentos tecnicos:
  - `disciplina`
  - `subdisciplina`
  - `criticidad_tecnica`
  - `norma_aplicable`
  - `proyecto_referencia`
- [ ] Publicar reglas de codificacion por disciplina.

### Archivos a crear/modificar
- `playbooks/SPRINT1_MULTIDISCIPLINA.md` (este documento)
- `BACKLOG.md`
- `ROADMAP.md`

---

## Workstream B - Plantillas por disciplina

### Tareas
- [ ] Crear plantilla de ficha tecnica por disciplina.
- [ ] Crear plantilla ITP (Inspection and Test Plan) por disciplina.
- [ ] Crear plantilla de checklist de liberacion tecnica.

### Archivos a crear
- `templates/TEMPLATE_Ficha_Tecnica_Disciplina.md`
- `templates/TEMPLATE_ITP_Disciplina.md`
- `templates/TEMPLATE_Checklist_Liberacion_Disciplina.md`

---

## Workstream C - Gobernanza y aprobaciones tecnicas

### Tareas
- [ ] Definir revisor tecnico por disciplina (civil/mecanica/electrica).
- [ ] Actualizar `CODEOWNERS` con rutas/owners por disciplina.
- [ ] Definir criterio de aprobacion minima por criticidad.

### Archivos a modificar
- `.github/CODEOWNERS`
- `docs/04_instructivos/IT-SGC-01_Configuracion_de_GitHub_para_Gobierno_del_SGC.md`

---

## Workstream D - QA y validacion

### Tareas
- [ ] Agregar auditoria de campos de disciplina (warning en Sprint 1, bloqueante en Sprint 2).
- [ ] Probar 1 caso real por disciplina:
  - alta del documento tecnico
  - referencia a formato
  - wrapper REG con evidencia externa
  - paso completo por QA gate

### Evidencia esperada
- PR por disciplina con CI verde.
- Run IDs de `SGC QA Gate`.
- Registro REG-SGC-CDC asociado.

---

## Definition of Done (Sprint 1)
- [ ] Existen plantillas tecnicas por disciplina.
- [ ] Existe gobernanza de aprobacion por disciplina.
- [ ] Se ejecutaron 3 pilotos (civil/mecanica/electrica) con QA verde.
- [ ] No se degrada el baseline actual (`0 BORRADOR`, `0 hallazgos`).

## Comando de validacion final
```bash
./scripts/release_preflight.sh --skip-install
```
