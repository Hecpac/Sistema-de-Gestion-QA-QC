# Skills SGC disponibles

- `crear_documento`: Crear o editar documentos controlados del SGC en `docs/` con estructura y convenciones del repo.
- `actualizar_lmd`: Sincronizar `docs/_control/lmd.yml` mediante `sgc-build-indexes` cuando cambia cualquier documento controlado.
- `actualizar_matriz_registros`: Sincronizar `docs/_control/matriz_registros.yml` mediante `sgc-build-indexes` cuando cambian registros/evidencias del SGC.
- `validar_trazabilidad`: Verificar consistencia global entre LMD, archivos, formatos y matriz de registros.
- `preparar_paquete_auditoria`: Armar paquetes de evidencia para auditorias con indice y enlaces a documentos/registros.
- `promover-vigencia-lote`: Promover lotes documentales de BORRADOR a VIGENTE con QA y commit atomico.
- `cerrar-matriz-registros`: Cerrar pendientes de la matriz de registros (`<DEFINIR>`, `TODO`, `TBD`) con consistencia documental.
- `gate-release-sgc`: Ejecutar gate de release (artefactos sincronizados, QA 0, checklist y tag).
- `monitor-qa-proactivo`: Configurar monitoreo automatico del QA/documental con scheduler y alertas.
- `paquete-auditoria-por-clausula`: Preparar paquete de evidencia ISO 9001 por clausulas 4..10.
- `gestionar-drift-ci`: Resolver fallos de CI por drift en artefactos `_control/*`.

# Invocacion explicita
Mencionar el nombre de la skill en el prompt, por ejemplo:
- "usar crear_documento para PR-SGC-09"
- "aplica actualizar_lmd para este cambio"
- "ejecuta validar_trazabilidad del repositorio"
- "aplica promover-vigencia-lote para los docs de riesgos"
- "usa cerrar-matriz-registros y elimina todos los pendientes"
- "corre gate-release-sgc y crea tag baseline"

# Nota
Las descripciones deben ser especificas para disparo implicito.
