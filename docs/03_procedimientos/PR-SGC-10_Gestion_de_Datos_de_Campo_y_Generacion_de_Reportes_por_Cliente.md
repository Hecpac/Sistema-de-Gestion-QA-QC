---
codigo: "PR-SGC-10"
titulo: "Gestion de Datos de Campo y Generacion de Reportes por Cliente"
tipo: "PR"
version: "1.0"
estado: "BORRADOR"
fecha_emision: "2026-02-28"
proceso: "SGC / Operacion"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# PR-SGC-10 Gestion de Datos de Campo y Generacion de Reportes por Cliente

## 1. Objetivo
Establecer la metodologia para capturar datos y fotos de campo, consolidar evidencia tecnica y generar reportes profesionales, garantizando trazabilidad documental y capacidad de adaptacion a los requerimientos de cada empresa cliente.

## 2. Alcance
Aplica a:
1. Captura de datos de inspeccion/ejecucion en campo.
2. Carga y control de evidencia fotografica.
3. Generacion de reportes tecnicos multipagina.
4. Parametrizacion por cliente (estructura, branding, secciones, firmas y criterios de aceptacion).

Excluye:
1. Aprobacion comercial de contratos con clientes.
2. Definicion tecnica del ensayo/metodo de inspeccion fuera del alcance del SGC documental.

## 3. Referencias
1. ISO 9001:2015, 7.5 Informacion documentada.
2. ISO 9001:2015, 8.5 Control de la produccion y de la provision del servicio.
3. [PR-SGC-01 Control de Documentos y Registros](PR-SGC-01_Control_de_Documentos_y_Registros.md).
4. [PR-SGC-09 Control de Cambios del Runtime y Automatizaciones QA](PR-SGC-09_Control_de_Cambios_del_Runtime_y_Automatizaciones_QA.md).
5. [FOR-SGC-01 Solicitud de Creacion y Cambio Documental](../_control/FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md).
6. [FOR-SGC-16 Registro Integrado de Datos de Campo y Reporte por Cliente](../05_formatos/FOR-SGC-16_Registro_Integrado_de_Datos_de_Campo_y_Reporte_por_Cliente.md).
7. Modelo de prueba de reporte: `INFORME 1.pdf` (referencia externa entregada por el usuario).

## 4. Definiciones
1. Paquete de captura: conjunto de datos de campo + fotos + metadatos de contexto (fecha, ubicacion, inspector, equipo, frente).
2. Plantilla por cliente: definicion parametrica de portada, secciones, tablas, terminologia, logos, firmas y reglas de validacion.
3. Perfil de salida: configuracion de formato final del reporte (por ejemplo, PDF corporativo, idioma, pie de pagina, numeracion y anexos).
4. Evidencia primaria: foto o dato de campo que sustenta un resultado reportado.

## 5. Responsabilidades
1. Operacion de Campo:
   1. Capturar datos con integridad y oportunidad.
   2. Registrar fotos con contexto tecnico suficiente.
2. Coordinacion de Calidad:
   1. Definir campos obligatorios y criterios de aceptacion documental.
   2. Verificar que la trazabilidad del reporte sea auditable.
3. Administracion de Plataforma:
   1. Configurar y mantener plantillas por cliente.
   2. Asegurar respaldos, control de acceso y versionado de configuraciones.
4. Revisor/Aprobador del Cliente:
   1. Validar conformidad del reporte emitido frente a su requerimiento contractual.

## 6. Desarrollo / Metodologia

### 6.1 Datos de entrada obligatorios
Para cada reporte, el sistema debe recibir como minimo:
1. Identificacion del servicio (cliente, proyecto, frente o area).
2. Datos tecnicos del elemento inspeccionado (equipo, metodo, parametros relevantes).
3. Resultados medibles (valores, criterios, condicion o veredicto).
4. Evidencia fotografica vinculada por item inspeccionado.
5. Identificacion de responsables (captura, revision, aprobacion).

### 6.2 Parametrizacion por empresa cliente
Antes de emitir reportes para una empresa, se debe crear una configuracion por cliente con:
1. Estructura de secciones requerida (encabezado, tablas, anexos, firmas, observaciones).
2. Campos obligatorios y opcionales.
3. Reglas de negocio (aceptacion/rechazo, unidades, redondeos, idioma, nomenclatura).
4. Imagen corporativa (logos, paleta, tipografia, portada, pie de pagina).
5. Reglas de nomenclatura para archivos y codigos de reporte.

Toda configuracion o cambio de configuracion se controla mediante FOR-SGC-01 y registro REG-SGC-CDC.
El registro operativo de captura y emision de reporte se realiza con FOR-SGC-16.

### 6.3 Flujo operativo de generacion del reporte
1. Recibir requerimiento del cliente y confirmar alcance de la plantilla.
2. Crear o actualizar la configuracion de cliente (si aplica).
3. Capturar datos y fotos de campo con metadatos completos.
4. Ejecutar validaciones de consistencia (campos obligatorios, evidencias minimas, trazabilidad por item).
5. Generar borrador de reporte conforme al perfil del cliente.
6. Revisar tecnica y documentalmente el borrador.
7. Emitir reporte profesional en formato final aprobado.
8. Registrar y conservar evidencia de emision/distribucion segun control documental.

### 6.4 Reglas de adaptacion para multiples empresas
El sistema no debe operar con una plantilla unica fija. Debe permitir:
1. Multiempresa con configuraciones independientes y versionadas.
2. Campos dinamicos por cliente sin afectar el modelo base del SGC.
3. Secciones opcionales/obligatorias por cliente (por ejemplo, HSE, firma de testigo, anexos contractuales).
4. Distintos layouts de tabla y jerarquias de resultado (por junta, sistema, frente, lote, etc.).
5. Exportaciones diferenciadas (PDF estandar, PDF con anexos extendidos, version resumida ejecutiva).

### 6.5 Criterios de reporte profesional
Cada reporte emitido debe cumplir:
1. Legibilidad y consistencia visual (encabezados, tablas, codigos y paginacion).
2. Coherencia entre dato reportado y evidencia fotografica asociada.
3. Identificacion unica del reporte y su version.
4. Trazabilidad de autor/revisor/aprobador y fecha de emision.
5. Integridad de anexos e imagenes sin perdida de contexto tecnico.

### 6.6 Control de cambios sobre requerimientos del cliente
Cuando un cliente solicite cambio de formato o contenido:
1. Registrar solicitud en FOR-SGC-01.
2. Evaluar impacto en datos de entrada, plantilla y trazabilidad.
3. Aprobar y versionar la configuracion del cliente.
4. Validar con corrida de prueba antes de uso productivo.
5. Comunicar fecha efectiva del cambio y version aplicable.

## 7. Registros asociados
1. FOR-SGC-01 - Solicitud de Creacion y Cambio Documental.
2. FOR-SGC-16 - Registro Integrado de Datos de Campo y Reporte por Cliente.
3. REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (llenada).
4. REG-SGC-RPT-CAM - Reporte tecnico de campo por cliente (llenado).
5. REG-SGC-COM - Evidencia de distribucion/comunicacion de documentos.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-28 | Emision inicial en BORRADOR del procedimiento para captura de datos/fotos de campo y generacion de reportes adaptables por cliente | Coordinacion de Calidad | Direccion General |
