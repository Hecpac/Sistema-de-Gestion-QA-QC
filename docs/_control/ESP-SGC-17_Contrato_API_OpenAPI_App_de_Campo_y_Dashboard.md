---
codigo: "ESP-SGC-17"
titulo: "Contrato API OpenAPI para App de Campo y Dashboard"
tipo: "ESP"
version: "1.1"
estado: "VIGENTE"
fecha_emision: "2026-03-03"
proceso: "SGC / Transformacion Digital"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# ESP-SGC-17 Contrato API OpenAPI para App de Campo y Dashboard

## 1. Objetivo
Definir el contrato tecnico de APIs para la app de campo y el dashboard, usando OpenAPI como estandar de interoperabilidad, control de cambios y validacion de integracion.

## 2. Alcance
Aplica a:
1. Endpoints de autenticacion y autorizacion.
2. Endpoints de captura operativa de inspecciones.
3. Endpoints de carga de evidencia fotografica.
4. Endpoints de generacion y consulta de reportes.
5. Endpoints de resumen analitico para dashboard por disciplina y proyecto.

Excluye:
1. API internas no expuestas fuera de la plataforma.
2. Integraciones legacy fuera del alcance de `PR-SGC-10`.

## 3. Referencias
1. [ESP-SGC-16 Arquitectura de App de Campo y Dashboard por Disciplina y Proyecto](ESP-SGC-16_Arquitectura_de_App_de_Campo_y_Dashboard_por_Disciplina_y_Proyecto.md).
2. [PR-SGC-10 Gestion de Datos de Campo y Generacion de Reportes por Cliente](../03_procedimientos/PR-SGC-10_Gestion_de_Datos_de_Campo_y_Generacion_de_Reportes_por_Cliente.md).
3. [FOR-SGC-16 Registro Integrado de Datos de Campo y Reporte por Cliente](../05_formatos/FOR-SGC-16_Registro_Integrado_de_Datos_de_Campo_y_Reporte_por_Cliente.md).
4. [docs/_control/matriz_registros.yml](matriz_registros.yml).
5. ISO 9001:2015, 7.5 Informacion documentada.

## 4. Definiciones
1. OpenAPI: especificacion estandar para describir contratos de API REST.
2. Contrato API: definicion versionada de endpoints, payloads, reglas y respuestas.
3. Error de contrato: incompatibilidad entre consumidor y proveedor por cambio no controlado.
4. Version mayor: cambio incompatible hacia atras en endpoints o esquemas.
5. Version menor: cambio compatible (campos opcionales o endpoints nuevos).

## 5. Responsabilidades
1. Coordinacion de Calidad:
   1. Aprobar reglas de versionado y trazabilidad del contrato.
   2. Verificar consistencia con documentos SGC aplicables.
2. Equipo de Producto/Tecnologia:
   1. Mantener especificacion OpenAPI alineada con implementacion.
   2. Publicar changelog por version y evidencias de pruebas.
3. Gerencia de Operaciones:
   1. Validar que la API cubra necesidades de captura y dashboard.
   2. Priorizar cambios funcionales por disciplina/proyecto.

## 6. Desarrollo / Metodologia

### 6.1 Politica de versionado del contrato
1. Version del contrato: `v1` para endpoints productivos iniciales.
2. Cambios incompatibles se publican como `v2`.
3. Cambios compatibles se publican en revision menor y se documentan en control de cambios.
4. No se retira un endpoint sin periodo de convivencia definido y comunicado.

### 6.2 Seguridad y autorizacion
1. Mecanismo: `Bearer JWT`.
2. Roles minimos: `campo`, `supervisor`, `calidad`, `cliente_lectura`.
3. Todo endpoint, salvo login, requiere token valido.
4. Los permisos se validan por rol y ambito (empresa/proyecto/disciplina).

### 6.3 OpenAPI base (v1)
```yaml
openapi: 3.0.3
info:
  title: SGC Field App API
  version: 1.0.0
  description: API para captura de campo, generacion de reportes y resumen de dashboard.
servers:
  - url: https://api.sgc.local
    description: Ambiente base
security:
  - bearerAuth: []
tags:
  - name: Auth
  - name: Plantillas
  - name: Inspecciones
  - name: Evidencias
  - name: Reportes
  - name: Dashboard
paths:
  /api/v1/auth/login:
    post:
      tags: [Auth]
      summary: Autenticar usuario
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        '200':
          description: Login exitoso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
  /api/v1/clientes/{clienteId}/perfil-reporte:
    get:
      tags: [Plantillas]
      summary: Obtener perfil de reporte por cliente
      parameters:
        - in: path
          name: clienteId
          required: true
          schema: { type: string }
      responses:
        '200':
          description: Perfil vigente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PerfilReporte'
  /api/v1/inspecciones:
    post:
      tags: [Inspecciones]
      summary: Crear inspeccion de campo
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InspeccionCreate'
      responses:
        '201':
          description: Inspeccion creada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Inspeccion'
  /api/v1/inspecciones/{inspeccionId}/items:
    post:
      tags: [Inspecciones]
      summary: Crear item inspeccionado
      parameters:
        - in: path
          name: inspeccionId
          required: true
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ItemInspeccionCreate'
      responses:
        '201':
          description: Item creado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ItemInspeccion'
  /api/v1/inspecciones/{inspeccionId}/evidencias:
    post:
      tags: [Evidencias]
      summary: Adjuntar evidencia fotografica
      parameters:
        - in: path
          name: inspeccionId
          required: true
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EvidenciaFotoCreate'
      responses:
        '201':
          description: Evidencia registrada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvidenciaFoto'
  /api/v1/reportes/{inspeccionId}/generar:
    post:
      tags: [Reportes]
      summary: Generar reporte profesional de inspeccion
      parameters:
        - in: path
          name: inspeccionId
          required: true
          schema: { type: string }
      responses:
        '202':
          description: Generacion iniciada
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReporteGeneracion'
  /api/v1/reportes/{codigoReporte}:
    get:
      tags: [Reportes]
      summary: Consultar estado y metadatos del reporte
      parameters:
        - in: path
          name: codigoReporte
          required: true
          schema: { type: string }
      responses:
        '200':
          description: Estado de reporte
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Reporte'
  /api/v1/dashboard/resumen:
    get:
      tags: [Dashboard]
      summary: Resumen KPI por disciplina y proyecto
      parameters:
        - in: query
          name: empresaId
          required: true
          schema: { type: string }
        - in: query
          name: proyectoId
          required: false
          schema: { type: string }
        - in: query
          name: disciplinaId
          required: false
          schema: { type: string }
        - in: query
          name: fechaDesde
          required: true
          schema: { type: string, format: date }
        - in: query
          name: fechaHasta
          required: true
          schema: { type: string, format: date }
      responses:
        '200':
          description: Resumen consolidado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DashboardResumen'
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    LoginRequest:
      type: object
      required: [email, password]
      properties:
        email: { type: string, format: email }
        password: { type: string, minLength: 8 }
    LoginResponse:
      type: object
      required: [token, rol, usuarioId]
      properties:
        token: { type: string }
        rol:
          type: string
          enum: [campo, supervisor, calidad, cliente_lectura]
        usuarioId: { type: string }
    PerfilReporte:
      type: object
      required: [clienteId, versionPlantilla, estructura]
      properties:
        clienteId: { type: string }
        versionPlantilla: { type: string }
        estructura:
          type: array
          items: { type: string }
    InspeccionCreate:
      type: object
      required: [empresaId, proyectoId, disciplinaId, fechaInspeccion]
      properties:
        empresaId: { type: string }
        proyectoId: { type: string }
        disciplinaId: { type: string }
        fechaInspeccion: { type: string, format: date }
        frente: { type: string }
    Inspeccion:
      allOf:
        - $ref: '#/components/schemas/InspeccionCreate'
        - type: object
          required: [inspeccionId, estado]
          properties:
            inspeccionId: { type: string }
            estado:
              type: string
              enum: [abierta, en_revision, cerrada]
    ItemInspeccionCreate:
      type: object
      required: [criterio, resultado, veredicto]
      properties:
        criterio: { type: string }
        resultado: { type: string }
        veredicto:
          type: string
          enum: [aprobada, rechazada, conforme, no_conforme]
        observaciones: { type: string }
    ItemInspeccion:
      allOf:
        - $ref: '#/components/schemas/ItemInspeccionCreate'
        - type: object
          required: [itemId]
          properties:
            itemId: { type: string }
    EvidenciaFotoCreate:
      type: object
      required: [itemId, url, timestamp]
      properties:
        itemId: { type: string }
        url: { type: string }
        timestamp: { type: string, format: date-time }
        descripcion: { type: string }
    EvidenciaFoto:
      allOf:
        - $ref: '#/components/schemas/EvidenciaFotoCreate'
        - type: object
          required: [evidenciaId]
          properties:
            evidenciaId: { type: string }
    ReporteGeneracion:
      type: object
      required: [codigoReporte, estado]
      properties:
        codigoReporte: { type: string }
        estado:
          type: string
          enum: [en_cola, procesando, emitido, error]
    Reporte:
      type: object
      required: [codigoReporte, estado, versionPlantilla, codigoRegistro]
      properties:
        codigoReporte: { type: string }
        estado:
          type: string
          enum: [en_cola, procesando, emitido, error]
        versionPlantilla: { type: string }
        codigoRegistro: { type: string }
        urlDescarga: { type: string }
    DashboardResumen:
      type: object
      required: [kpis, matrizDisciplinaProyecto, tendencia]
      properties:
        kpis:
          type: object
          properties:
            inspeccionesTotales: { type: integer }
            tasaAprobacion: { type: number, format: float }
            hallazgosCriticos: { type: integer }
            reportesEmitidos: { type: integer }
        matrizDisciplinaProyecto:
          type: array
          items:
            type: object
            properties:
              disciplinaId: { type: string }
              proyectoId: { type: string }
              inspecciones: { type: integer }
              porcentajeConformidad: { type: number, format: float }
        tendencia:
          type: array
          items:
            type: object
            properties:
              fecha: { type: string, format: date }
              disciplinaId: { type: string }
              inspecciones: { type: integer }
              aprobadas: { type: integer }
```

### 6.4 Reglas de validacion de contrato
1. Todo endpoint nuevo debe agregarse en OpenAPI antes de liberacion.
2. Toda propiedad `required` debe justificarse funcionalmente.
3. Se debe incluir ejemplo minimo de request/response en pruebas de integracion.
4. El pipeline CI debe validar sintaxis OpenAPI y compatibilidad de contrato.

### 6.5 Errores estandar
| HTTP | Codigo negocio | Uso |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Payload invalido o incompleto |
| 401 | `UNAUTHORIZED` | Token ausente o invalido |
| 403 | `FORBIDDEN` | Rol sin permiso para el recurso |
| 404 | `NOT_FOUND` | Recurso inexistente |
| 409 | `CONFLICT` | Estado incompatible (por ejemplo, inspeccion cerrada) |
| 422 | `BUSINESS_RULE_ERROR` | Regla documental u operativa incumplida |
| 500 | `INTERNAL_ERROR` | Falla interna no controlada |

### 6.6 Criterios de aceptacion
1. El contrato cubre todos los endpoints definidos en `ESP-SGC-16`.
2. El contrato permite filtrar resumen por disciplina y proyecto.
3. El contrato incorpora seguridad por token y roles.
4. La salida de reporte incluye `codigoRegistro` para trazabilidad SGC.

## 7. Registros asociados
1. REG-SGC-RPT-CAM - Reporte tecnico de campo por cliente (llenado).
2. REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique cambio de contrato).
3. REG-SGC-COM - Evidencia de distribucion/comunicacion de versiones del contrato API.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Reviso | Aprobo |
|---|---:|---|---|---|---|
| 1.1 | 2026-03-03 | Promocion a VIGENTE del contrato API OpenAPI tras validacion de cobertura funcional, seguridad y trazabilidad documental | Coordinacion de Calidad | Gerencia de Operaciones | Direccion General |
| 1.0 | 2026-02-28 | Emision inicial en BORRADOR del contrato API OpenAPI para app de campo y dashboard | Coordinacion de Calidad | Gerencia de Operaciones | Direccion General |
