---
name: gate-release-sgc
description: >
  Activar cuando se prepare un release/tag del SGC y se requiera un gate final: repo limpio,
  artefactos _control sincronizados, QA en cero, checklist baseline listo y creacion de tag anotado.
---

# Objetivo
Ejecutar un gate de salida antes de publicar baseline/tag del SGC.

# Flujo
1. Verificar `git status` limpio o con cambios solo esperados.
2. Regenerar artefactos:
   - `build_indexes`
   - `build_dashboard`
3. Ejecutar QA deterministico y exigir 0 hallazgos.
4. Verificar condiciones de release:
   - conteo `estado: VIGENTE` esperado en `lmd.yml`
   - opcional: 0 `BORRADOR` si es baseline total.
5. Confirmar existencia de checklist:
   - `docs/_control/CHECKLIST_BASELINE_SGC_v1.0_operativo.md` (o la version solicitada).
6. Commit de sincronizacion si hubo drift.
7. Crear tag anotado y mostrar `git show --no-patch <tag>`.

# Comandos
```bash
git status --short
grep -c "estado: VIGENTE" docs/_control/lmd.yml
grep -c "estado: BORRADOR" docs/_control/lmd.yml || true
git tag -a <tag> -m "<mensaje>"
```

# DoD
- QA 0 hallazgos.
- Artefactos `_control/*` sincronizados.
- Tag anotado creado sobre commit limpio.
- Resumen final con hash, tag y conteos VIGENTE/BORRADOR.
