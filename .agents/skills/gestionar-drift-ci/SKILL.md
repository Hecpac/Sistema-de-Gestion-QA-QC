---
name: gestionar-drift-ci
description: Activar cuando falle CI por drift en artefactos generados (_control/lmd.yml, matriz_registros.yml, dashboard) o por desalineacion documental; reconstituir artefactos, explicar causa y dejar commit de correccion.
---

# Objetivo
Resolver rápido fallos de CI por artefactos desactualizados o inconsistencias de generación.

# Flujo
1. Identificar fallo en CI/log:
   - drift en `_control/*`
   - hallazgos QA.
2. Reproducir localmente:
   - `build_indexes`
   - `build_dashboard`
   - QA deterministico.
3. Revisar diff:
   - si solo `_control/*` cambió, sincronizar y commitear.
   - si hay causa fuente (doc con TODO en VIGENTE, referencia rota), corregir primero y regenerar.
4. Commit recomendado:
   - `chore: sync generated control artifacts`
   - o `fix: resolve SGC QA drift in source docs`.
5. Entregar resumen de causa raíz + prevención.

# DoD
- CI reproducido localmente y resuelto.
- Sin drift pendiente en `_control/*`.
- QA deterministico en 0 hallazgos.
- Commit listo para merge.
