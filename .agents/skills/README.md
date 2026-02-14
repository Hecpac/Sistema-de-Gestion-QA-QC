# Skills SGC disponibles

- `crear_documento`: Crear o editar documentos controlados del SGC en `docs/` con estructura y convenciones del repo.
- `actualizar_lmd`: Sincronizar `docs/_control/lmd.yml` mediante `sgc-build-indexes` cuando cambia cualquier documento controlado.
- `actualizar_matriz_registros`: Sincronizar `docs/_control/matriz_registros.yml` mediante `sgc-build-indexes` cuando cambian registros/evidencias del SGC.
- `validar_trazabilidad`: Verificar consistencia global entre LMD, archivos, formatos y matriz de registros.
- `preparar_paquete_auditoria`: Armar paquetes de evidencia para auditorias con indice y enlaces a documentos/registros.

# Invocacion explicita
Mencionar el nombre de la skill en el prompt, por ejemplo:
- "usar crear_documento para PR-SGC-09"
- "aplica actualizar_lmd para este cambio"
- "ejecuta validar_trazabilidad del repositorio"

# Nota
Las descripciones deben ser especificas para disparo implicito.
