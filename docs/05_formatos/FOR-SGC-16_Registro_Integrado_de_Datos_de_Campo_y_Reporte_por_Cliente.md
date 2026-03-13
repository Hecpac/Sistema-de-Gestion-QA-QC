---
codigo: "FOR-SGC-16"
titulo: "Registro Integrado de Datos de Campo y Reporte por Cliente"
tipo: "FOR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-28"
proceso: "SGC / Operacion"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# FOR-SGC-16 Registro Integrado de Datos de Campo y Reporte por Cliente

## 1. Objetivo
Estandarizar el registro operativo para capturar datos y fotos de campo y emitir reportes tecnicos profesionales, con estructura adaptable al requerimiento de cada empresa cliente.

## 2. Alcance
Aplica a reportes de campo emitidos para servicios de inspeccion, control de calidad o verificacion tecnica donde se requiera:
1. Trazabilidad por elemento o junta inspeccionada.
2. Evidencia fotografica asociada al resultado.
3. Presentacion formal en reporte multipagina.

## 3. Referencias
1. PR-SGC-10 Gestion de Datos de Campo y Generacion de Reportes por Cliente.
2. PR-SGC-01 Control de Documentos y Registros.
3. FOR-SGC-01 Solicitud de Creacion y Cambio Documental (para cambios de plantilla por cliente).
4. Modelo de prueba base: `INFORME 1.pdf` (referencia externa).

## 4. Definiciones
1. Item inspeccionado: unidad de analisis (por ejemplo, junta, sistema, tramo o componente) sobre la que se registra resultado.
2. Evidencia fotografica: imagen vinculada a un item inspeccionado que sustenta el resultado reportado.
3. Perfil de cliente: parametros de salida del reporte (estructura, branding, firmas y reglas de presentacion).

## 5. Responsabilidades
1. Personal de Campo:
   1. Registrar datos tecnicos y evidencia fotografica de manera completa.
   2. Validar que cada foto tenga contexto y correspondencia con el item inspeccionado.
2. Coordinacion de Operaciones:
   1. Revisar integridad tecnica del registro antes de generar reporte final.
   2. Asegurar que se use el perfil de cliente correcto.
3. Coordinacion de Calidad:
   1. Verificar cumplimiento documental y trazabilidad.
   2. Controlar versiones del formato y cambios solicitados por cliente.

## 6. Desarrollo / Metodologia
1. Registrar encabezado del servicio y datos generales.
2. Registrar condiciones tecnicas y parametros de ejecucion.
3. Documentar resultados por item inspeccionado.
4. Asociar evidencia fotografica por item (codigo o referencia unica).
5. Consolidar firmas de revision y aprobacion.
6. Emitir reporte segun perfil de cliente vigente.

### 6.1 Reglas obligatorias de diligenciamiento
1. No dejar campos criticos vacios: cliente, proyecto, fecha, responsable y resultado.
2. Cada item inspeccionado debe tener veredicto documentado.
3. Toda imagen referenciada debe existir y ser legible.
4. Todo cambio de estructura por cliente debe quedar versionado y aprobado.

### 6.2 Parametros adaptables por cliente
Los siguientes campos/secciones son configurables sin romper la base del formato:
1. Logo, encabezado corporativo y pie de pagina.
2. Nombres de columnas tecnicas.
3. Escala de veredicto (por ejemplo: Aprobada/Rechazada o Conforme/No conforme).
4. Firmas requeridas (interna, cliente, testigo).
5. Anexos contractuales o HSE.

## 7. Registros asociados
1. REG-SGC-RPT-CAM - Reporte tecnico de campo por cliente (llenado).
2. REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique cambio de plantilla).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-28 | Emision inicial vigente del formato para captura y emision de reportes de campo adaptables por cliente | Coordinacion de Calidad | Direccion General |

## 9. Formato de llenado

### 9.1 Encabezado del reporte
| Campo | Descripcion | Obligatorio |
|---|---|---|
| Codigo de reporte | Identificador unico del reporte emitido | Si |
| Cliente | Empresa cliente del servicio | Si |
| Proyecto / Contrato | Identificacion del proyecto o contrato | Si |
| Fecha de inspeccion | Fecha de ejecucion en campo | Si |
| Fecha de emision | Fecha de emision del reporte | Si |
| Ubicacion / Frente | Lugar o frente de trabajo | Si |
| Responsable de campo | Nombre y rol de quien captura datos | Si |
| Perfil de cliente aplicado | Codigo o nombre de la plantilla aplicada | Si |

### 9.2 Resultados por item inspeccionado
| Item | Sistema/Componente | Parametro medido | Criterio | Resultado | Veredicto | Evidencia |
|---|---|---|---|---|---|---|
| IT-001 | Definir | Definir | Definir | Definir | Aprobada/Rechazada | IMG-001 |

### 9.3 Evidencia fotografica
| Codigo foto | Item asociado | Descripcion tecnica | Fecha/Hora | Ubicacion archivo |
|---|---|---|---|---|
| IMG-001 | IT-001 | Describir evidencia observable | AAAA-MM-DD HH:MM | Ruta o URL declarada |

### 9.4 Cierre y aprobacion
| Rol | Nombre | Fecha | Firma/validacion |
|---|---|---|---|
| Tecnico de campo |  |  |  |
| Supervisor |  |  |  |
| Revisor calidad |  |  |  |
| Inspector cliente (si aplica) |  |  |  |
