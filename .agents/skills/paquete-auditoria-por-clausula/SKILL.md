---
name: paquete-auditoria-por-clausula
description: Activar cuando se solicite preparar evidencia de auditoria ISO 9001 organizada por clausulas (4 a 10), con indice navegable, rutas a documentos/registros y resumen de brechas.
---

# Objetivo
Armar paquete de auditoría trazable por cláusula ISO, no solo por proceso.

# Flujo
1. Crear carpeta `audit_packages/YYYY-MM-DD_iso9001/`.
2. Generar `README.md` con secciones:
   - Clausula 4 Contexto
   - Clausula 5 Liderazgo
   - Clausula 6 Planificacion
   - Clausula 7 Soporte
   - Clausula 8 Operacion
   - Clausula 9 Evaluacion del desempeno
   - Clausula 10 Mejora
3. Mapear para cada cláusula:
   - documentos `VIGENTE` relevantes
   - formatos/registros clave (`REG-*`)
   - evidencia de estado (ruta y codigo).
4. Incluir snapshot de control:
   - `lmd.yml`
   - `matriz_registros.yml`
   - `reporte_qa_compliance.md`
5. Señalar brechas reales en una sección `Pendientes` (sin inventar evidencias).

# DoD
- Carpeta de paquete creada con indice por clausula.
- Enlaces/rutas funcionales a evidencia.
- Brechas y pendientes claramente identificados.
