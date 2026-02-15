---
name: cerrar-matriz-registros
description: Activar cuando se necesite completar y sanear docs/_control/matriz_registros.yml (responsable, retencion, disposicion_final, acceso, proteccion) eliminando TODO/TBD/<DEFINIR> sin romper consistencia con lmd y referencias REG-*.
---

# Objetivo
Cerrar los campos pendientes de la matriz de registros para dejarla auditable.

# Flujo
1. Revisar `docs/_control/matriz_registros.yml` y detectar pendientes:
   - `<DEFINIR>`
   - `TODO`
   - `TBD`
2. Completar campos por cada `REG-*`:
   - `responsable`
   - `retencion`
   - `disposicion_final`
   - `acceso`
   - `proteccion` (si aplica)
3. Mantener coherencia con:
   - `codigo_formato`
   - `proceso`
   - rutas en `ubicacion`.
4. Regenerar con `build_indexes` para validar que no haya drift estructural.
5. Regenerar dashboard + reporte QA.

# Comandos clave
```bash
grep -nE "TODO|TBD|<DEFINIR>" docs/_control/matriz_registros.yml
python -m sgc_agents.tools.build_indexes --repo-root /Users/hector/Projects/SGC
python -m sgc_agents.tools.build_dashboard --repo-root /Users/hector/Projects/SGC
```

# Reglas
- No inventar retenciones legales si no hay politica interna: usar valores operativos acordados por usuario.
- No alterar codigos `REG-*` ni `codigo_formato` salvo instruccion explicita.

# DoD
- `grep -nE "TODO|TBD|<DEFINIR>" docs/_control/matriz_registros.yml` sin resultados.
- QA deterministico en 0 hallazgos.
- Commit con mensaje de saneamiento de matriz.
