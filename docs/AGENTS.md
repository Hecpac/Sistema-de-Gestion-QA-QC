# AGENTS.md (docs)

Estas instrucciones aplican cuando trabajas dentro de la carpeta `docs/`.

## Prioridades
1. Consistencia con ISO 9001:2015 (especialmente 7.5 para control documental).
2. Trazabilidad: cada documento debe listar sus registros asociados.
3. Reutilizacion: usa/actualiza plantillas antes de crear formatos nuevos.

## Reglas de escritura
- Manten titulos y secciones consistentes entre procedimientos.
- Usa listas numeradas para flujos (1,2,3...).
- Incluye tablas cuando ayuden (matrices, control de cambios).

## Registros asociados
Al final de cada procedimiento agrega una seccion:

### Registros asociados
- `FOR-XXX-YYY ...` (si aplica)
- `REG-...` (si aplica)

Luego regenera indices con `sgc-build-indexes` para sincronizar automaticamente `docs/_control/matriz_registros.yml`.
