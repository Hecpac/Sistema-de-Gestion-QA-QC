# Registros del SGC

Esta carpeta contiene **evidencias** (registros) generadas por la operacion del SGC.
Recomendacion: organizar por tipo o por procedimiento.

Ejemplo de subcarpetas:
- `cambios_documentales/`
- `comunicaciones_documentales/`
- `no_conformidades/`
- `capa/`
- `auditorias/`
- `revision_direccion/`

## Contrato de trazabilidad (obligatorio)
Todo archivo Markdown en `docs/06_registros/` debe incluir frontmatter YAML con:

```yaml
---
formato_origen: "FOR-SGC-XX"
codigo_registro: "REG-SGC-..."
fecha_registro: "YYYY-MM-DD"
---
```

- `formato_origen` es obligatorio y debe apuntar a un formato canonico existente.
- El formato origen debe estar en estado `VIGENTE`.
- El formato origen debe estar habilitado en `docs/_control/matriz_registros.yml` mediante `codigo_formato`.

> Regla: si un procedimiento requiere un registro, debe existir en `docs/_control/matriz_registros.yml` con su ubicacion, retencion y formato origen.

## Catalogo de registros (SSOT)
La fuente de verdad para metadatos operativos de registros (responsable, ubicacion, retencion, acceso, etc.) es:
- `docs/06_registros/catalogo_registros.yml`

`sgc-build-indexes` usa este catalogo para generar deterministamente `docs/_control/matriz_registros.yml`.
