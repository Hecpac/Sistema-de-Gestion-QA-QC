---
codigo: "ESP-SGC-16"
titulo: "Arquitectura de App de Campo y Dashboard por Disciplina y Proyecto"
tipo: "ESP"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-28"
proceso: "SGC / Transformacion Digital"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# ESP-SGC-16 Arquitectura de App de Campo y Dashboard por Disciplina y Proyecto

## 1. Objetivo
Definir la arquitectura funcional y tecnica de una aplicacion conectada al SGC para recopilar datos y fotos de campo, generar reportes profesionales y visualizar resultados consolidados por disciplina y proyecto.

## 2. Alcance
Aplica al diseno de:
1. App de captura en campo (movil/tablet).
2. Backend de integracion y trazabilidad SGC.
3. Motor de generacion de reportes profesionales.
4. Dashboard ejecutivo-operativo por disciplina y proyecto.
5. Plan MVP de implementacion en 3 sprints.

Excluye:
1. Desarrollo de interfaz final pixel-perfect.
2. Definicion contractual especifica con clientes (se parametriza por plantilla).

## 3. Referencias
1. ISO 9001:2015, 7.5 Informacion documentada.
2. [PR-SGC-01 Control de Documentos y Registros](../03_procedimientos/PR-SGC-01_Control_de_Documentos_y_Registros.md).
3. [PR-SGC-10 Gestion de Datos de Campo y Generacion de Reportes por Cliente](../03_procedimientos/PR-SGC-10_Gestion_de_Datos_de_Campo_y_Generacion_de_Reportes_por_Cliente.md).
4. [FOR-SGC-16 Registro Integrado de Datos de Campo y Reporte por Cliente](../05_formatos/FOR-SGC-16_Registro_Integrado_de_Datos_de_Campo_y_Reporte_por_Cliente.md).
5. [docs/_control/lmd.yml](lmd.yml).
6. [docs/_control/matriz_registros.yml](matriz_registros.yml).
7. Modelo de prueba de reporte: `INFORME 1.pdf` (referencia externa).

## 4. Definiciones
1. App de campo: cliente movil para captura estructurada de datos, fotos y firmas.
2. Perfil de cliente: configuracion por empresa para formato, branding, campos y reglas de salida.
3. Disciplina: especialidad operativa (por ejemplo, Civil, Mecanica, Electrica).
4. Proyecto: unidad contractual/operativa donde se ejecutan actividades de campo.
5. Reporte profesional: salida formal (PDF) con trazabilidad de datos, evidencias y aprobaciones.

## 5. Responsabilidades
1. Coordinacion de Calidad:
   1. Definir reglas documentales y de trazabilidad.
   2. Validar correspondencia entre registros operativos y SGC.
2. Gerencia de Operaciones:
   1. Definir flujo de captura y validacion tecnica por disciplina.
   2. Priorizar tableros y KPI de gestion.
3. Equipo de Producto/Tecnologia:
   1. Implementar app, APIs, motor de reportes y dashboard.
   2. Asegurar seguridad, sincronizacion y disponibilidad del sistema.
4. Usuario de Campo:
   1. Capturar datos y fotos con integridad y oportunidad.
   2. Cumplir validaciones minimas antes de sincronizar.

## 6. Desarrollo / Metodologia

### 6.1 Principios de diseno
1. Trazabilidad de extremo a extremo: dato de campo -> reporte -> registro -> dashboard.
2. Offline-first: operacion sin conectividad con sincronizacion confiable.
3. Multiempresa: separacion logica por cliente y perfil de plantilla.
4. Configurable sin romper base SGC: campos y secciones adaptables por cliente.
5. Evidencia verificable: foto vinculada a item inspeccionado y resultado.

### 6.2 Arquitectura de solucion (alto nivel)
1. Capa de captura (App de Campo):
   1. Formularios dinamicos por perfil de cliente.
   2. Captura de fotos, firma y metadatos (fecha, usuario, geolocalizacion opcional).
   3. Cola local de sincronizacion (eventos pendientes).
2. Capa de servicios (Backend SGC):
   1. API de autenticacion y autorizacion por rol.
   2. API de captura operativa (inspecciones, items, evidencias).
   3. API de plantillas y versionado por cliente.
   4. API de generacion de reporte y consulta de estado.
3. Capa documental y analitica:
   1. Registro normalizado para `FOR-SGC-16` y `REG-SGC-RPT-CAM-*`.
   2. Almacen de evidencias multimedia.
   3. Modelo analitico para dashboard por disciplina/proyecto.

### 6.3 Modelo de datos minimo (MVP)
| Entidad | Campos clave | Relacion principal |
|---|---|---|
| empresa | id_empresa, nombre, estado | 1:N con proyecto y perfil_cliente |
| proyecto | id_proyecto, id_empresa, nombre, disciplina_principal | 1:N con inspeccion |
| disciplina | id_disciplina, codigo, nombre | 1:N con inspeccion |
| inspeccion | id_inspeccion, id_proyecto, id_disciplina, fecha, estado | 1:N con item_inspeccion |
| item_inspeccion | id_item, id_inspeccion, criterio, resultado, veredicto | 1:N con evidencia_foto |
| evidencia_foto | id_foto, id_item, url, timestamp, autor | N:1 con item_inspeccion |
| reporte_emitido | codigo_reporte, id_inspeccion, version_plantilla, estado_emision | 1:1 con inspeccion |
| auditoria_trazabilidad | codigo_registro, formato_origen, hash, fecha_evento | N:1 con reporte_emitido |

### 6.4 Flujo operativo de captura y emision
1. Usuario selecciona empresa, proyecto y disciplina.
2. App descarga plantilla vigente del perfil de cliente.
3. Usuario captura encabezado tecnico, items y fotos de evidencia.
4. App valida campos obligatorios y consistencia minima.
5. App sincroniza eventos al backend cuando hay conectividad.
6. Backend consolida datos, aplica reglas y genera borrador de reporte.
7. Revisor tecnico valida y aprueba emision.
8. Sistema emite PDF profesional y registra `REG-SGC-RPT-CAM-*`.
9. Dashboard actualiza indicadores por disciplina/proyecto.

### 6.5 APIs base recomendadas (MVP)
| Metodo | Endpoint | Proposito |
|---|---|---|
| POST | `/api/v1/auth/login` | Autenticar usuario de campo/supervisor |
| GET | `/api/v1/clientes/{id}/perfil-reporte` | Obtener plantilla y reglas por cliente |
| POST | `/api/v1/inspecciones` | Crear inspeccion de campo |
| POST | `/api/v1/inspecciones/{id}/items` | Registrar item inspeccionado |
| POST | `/api/v1/inspecciones/{id}/evidencias` | Adjuntar foto y metadatos |
| POST | `/api/v1/reportes/{id_inspeccion}/generar` | Generar reporte profesional |
| GET | `/api/v1/reportes/{codigo}` | Consultar estado/descarga del reporte |
| GET | `/api/v1/dashboard/resumen` | KPI agregados por disciplina y proyecto |

### 6.6 Diseno funcional del dashboard (resumen por disciplina y proyecto)
El dashboard debe incluir, como minimo:
1. Filtros globales: empresa, proyecto, disciplina, fecha y estado.
2. Tarjetas KPI:
   1. Inspecciones ejecutadas.
   2. Tasa de aprobacion.
   3. Hallazgos criticos.
   4. Reportes emitidos.
3. Matriz Disciplina x Proyecto:
   1. Volumen de inspecciones.
   2. Porcentaje de conformidad.
   3. Tendencia vs periodo anterior.
4. Tendencia temporal (semanal/mensual) por disciplina.
5. Top hallazgos y drill-down a reporte/evidencia.

### 6.7 Mock operativo del dashboard (wireframe textual)
| Bloque | Contenido | Interaccion esperada |
|---|---|---|
| Cabecera | Filtros globales + selector de periodo | Actualiza todos los widgets |
| KPI cards | Inspecciones, Aprobacion, Hallazgos, Reportes | Click para detalle |
| Matriz central | Filas=disciplinas, columnas=proyectos | Heatmap + click a tabla de inspecciones |
| Grafico tendencia | Serie temporal por disciplina | Comparativo periodo actual/anterior |
| Tabla detalle | Reportes recientes y estado | Acceso a PDF y evidencia fotografica |

### 6.8 Requisitos no funcionales
1. Seguridad:
   1. Control de acceso por roles (`campo`, `supervisor`, `calidad`, `cliente_lectura`).
   2. Trazabilidad de cambios (quien, cuando, que).
2. Rendimiento:
   1. Sincronizacion de lote de campo <= 60 segundos para 100 items sin imagen.
   2. Generacion de reporte <= 120 segundos en plantilla estandar.
3. Disponibilidad y resiliencia:
   1. Cola offline con reintentos idempotentes.
   2. Alerta de fallas de sincronizacion no resueltas.
4. Calidad de dato:
   1. Validaciones obligatorias antes de emision.
   2. Integridad entre item inspeccionado y evidencia.

### 6.9 Backlog MVP (3 sprints)
| Sprint | Objetivo | Entregables |
|---|---|---|
| Sprint 1 | Captura de campo base | Login, formulario dinamico, carga de fotos, cola offline, API de inspecciones |
| Sprint 2 | Reporte profesional y trazabilidad | Motor PDF por plantilla, flujo revision/aprobacion, registro `REG-SGC-RPT-CAM-*` |
| Sprint 3 | Dashboard por disciplina/proyecto | KPI, matriz Disciplina x Proyecto, tendencias, drill-down a reporte/evidencia |

### 6.10 Criterios de aceptacion de la especificacion
1. El sistema captura datos y fotos con trazabilidad completa.
2. El reporte generado replica estructura profesional del modelo de prueba y se adapta por cliente.
3. El dashboard permite analisis por disciplina y proyecto con filtros y detalle.
4. Toda salida documental se vincula a `FOR-SGC-16` y `REG-SGC-RPT-CAM`.

## 7. Registros asociados
1. REG-SGC-RPT-CAM - Reporte tecnico de campo por cliente (llenado).
2. REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique cambio de plantilla/reglas).
3. REG-SGC-COM - Evidencia de distribucion/comunicacion de documentos.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Reviso | Aprobo |
|---|---:|---|---|---|---|
| 1.0 | 2026-02-28 | Emision inicial vigente de la arquitectura de app de campo y dashboard por disciplina/proyecto | Coordinacion de Calidad | Gerencia de Operaciones | Direccion General |
