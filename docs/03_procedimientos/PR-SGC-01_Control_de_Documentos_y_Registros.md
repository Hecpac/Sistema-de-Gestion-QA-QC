---
codigo: "PR-SGC-01"
titulo: "Control de Documentos y Registros"
tipo: "PR"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-09"
proceso: "SGC"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# PR-SGC-01 Procedimiento de Control de Documentos y Registros

## 1. Objetivo
Establecer la metodología para **crear, revisar, aprobar, publicar, actualizar, distribuir y controlar** los **documentos del SGC**, así como para **identificar, almacenar, proteger, retener y disponer** los **registros** que evidencian la conformidad y la operación eficaz del sistema.

## 2. Alcance
Aplica a:
- Toda la **documentación interna** del SGC (políticas, manuales, procedimientos, instructivos, formatos, planes, especificaciones internas, etc.).
- Los **registros** generados por los procesos del SGC (digitales o físicos).
- Los **documentos externos** necesarios para la operación (normas, reglamentos, fichas técnicas, manuales del fabricante, requisitos del cliente, etc.).

## 3. Referencias
- ISO 9001:2015, **7.5 Información documentada**.
- Normativa aplicable del sector (si corresponde).
- Políticas internas de TI / seguridad de la información (si aplica).

## 4. Definiciones
- **Documento:** Información que describe “qué se hace y cómo se hace” (p. ej. procedimiento, instructivo, formato en blanco).
- **Registro:** Evidencia de que algo se realizó (p. ej. formato llenado, reporte, bitácora, acta, evidencia fotográfica).
- **Información documentada:** Conjunto de documentos y registros que el SGC requiere controlar.
- **Vigente:** Versión aprobada y disponible para uso.
- **Obsoleto:** Documento reemplazado o retirado, no permitido para uso operativo.
- **Lista Maestra de Documentos (LMD):** Relación controlada de documentos vigentes y su estado.
- **Dueño de Proceso (DP):** Responsable del proceso y de la integridad de su documentación.
- **Responsable de Calidad (RC):** Responsable de administrar el control documental del SGC (o rol equivalente).

## 5. Responsabilidades
### 5.1 Responsable de Calidad (RC)
- Administrar la **Lista Maestra de Documentos** y la **Matriz de Registros**.
- Verificar el cumplimiento del flujo de control (revisión/aprobación/estado).
- Asegurar disponibilidad del documento vigente y retiro de obsoletos.
- Realizar revisiones periódicas del sistema documental.

### 5.2 Dueño de Proceso (DP)
- Definir/validar contenidos técnicos de documentos de su proceso.
- Revisar y autorizar técnicamente los documentos (según esquema de aprobación).
- Asegurar que el personal use documentos vigentes y genere registros requeridos.

### 5.3 Elaborador
- Redactar/actualizar el documento según formato y lineamientos.
- Incluir cambios y justificación cuando aplique.

### 5.4 Aprobador (Dirección / Gerencia / Jefatura)
- Aprobar documentos según matriz de autoridad (política, procedimientos, etc.).

### 5.5 Usuarios
- Consultar y utilizar únicamente documentos vigentes.
- Generar y resguardar registros conforme a este procedimiento.

### 5.6 TI / Administrador de plataforma (si aplica)
- Respaldo, control de accesos, disponibilidad del repositorio documental.

## 6. Desarrollo del procedimiento

### 6.1 Clasificación de documentos
Se clasifica la información documentada del SGC como:
- **POL**: Política  
- **MAN**: Manual (si se usa)  
- **PR**: Procedimiento  
- **IT**: Instructivo / guía  
- **FOR**: Formato (plantilla en blanco)  
- **PLAN**: Plan (auditorías, calidad, etc.)  
- **ESP**: Especificación / estándar interno  

> Nota: Los **registros** se controlan por su **matriz de registros**; los **formatos** sí se controlan como documentos (porque tienen versión).

### 6.2 Estructura e identificación (codificación)
Cada documento del SGC debe tener como mínimo:
- **Código**
- **Título**
- **Versión**
- **Fecha de emisión/vigencia**
- **Estado** (borrador / en revisión / aprobado-vigente / obsoleto)
- **Propietario (DP)**
- **Elaboró / revisó / aprobó**
- **Historial de cambios**

**Codificación sugerida:**  
`[TIPO]-[PROCESO]-[CONSECUTIVO]`  
Ejemplos:
- PR-OP-001 (Procedimiento Operación #001)
- IT-COM-002 (Instructivo Compras #002)
- FOR-SGC-01 (Formato SGC #001)

**Versionado:**
- **1.0** para primera emisión.
- Aumenta **decimal** para cambios menores (1.1, 1.2) y **entero** para cambios mayores (2.0, 3.0).

### 6.3 Elaboración de documentos
1) El DP o RC identifica necesidad de documento nuevo o actualización.  
2) El **Elaborador** redacta usando el **formato estándar** del SGC.  
3) El documento se guarda como **BORRADOR** en el repositorio definido.

**Criterios de calidad del documento**
- Lenguaje claro, instrucciones verificables.
- Incluye registros asociados y responsabilidades.
- Referencia a formatos y anexos vigentes.
- Coherente con el proceso y riesgos aplicables.

### 6.4 Revisión
1) El **DP** revisa contenido técnico.  
2) El **RC** revisa consistencia con SGC (estructura, codificación, controles).  
3) Se registran comentarios y se ajusta el documento.

### 6.5 Aprobación
Los documentos deben aprobarse antes de su uso.

**Matriz de aprobación recomendada**
- POL / objetivos: **Dirección** + RC
- PR (procedimientos): **DP** + RC (y Dirección si es crítico)
- IT: **DP** + RC (según impacto)
- FOR: **DP** + RC

La aprobación queda evidenciada mediante:
- Firma en documento físico, o
- Flujo de aprobación digital (usuario, fecha/hora, comentario).

### 6.6 Publicación y disponibilidad de documentos vigentes
1) El RC asigna estado **APROBADO / VIGENTE**.  
2) Se publica en el repositorio oficial (“Documentos Vigentes”).  
3) Se registra/actualiza en la **Lista Maestra de Documentos**.  
4) Se comunica a usuarios afectados.

**Reglas**
- El documento vigente debe ser **fácilmente accesible** donde se usa.
- Debe existir **un único punto de verdad** (repositorio maestro).

### 6.7 Control de copias impresas (si aplica)
- Por defecto, toda copia impresa se considera **“NO CONTROLADA”**, salvo que esté marcada como **“COPIA CONTROLADA”**.
- Las **copias controladas** deben:
  - Tener identificación (código, versión, número de copia).
  - Tener responsable de custodia.
  - Ser retiradas y reemplazadas al cambiar versión.

### 6.8 Cambios y actualización de documentos
**Disparadores**
- No conformidades / CAPA
- Auditorías
- Cambio de proceso/equipo/tecnología
- Cambio regulatorio / requisitos cliente
- Mejora continua

**Flujo**
1) Levantar **Solicitud de creación/cambio** usando el formato **FOR-SGC-01** (ver `docs/_control/FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md`).  
2) DP y RC evalúan impacto (riesgos, capacitación, registros).  
3) Actualizar documento (nueva versión) en BORRADOR.  
4) Repetir revisión y aprobación.  
5) Publicar nueva versión y comunicar.  
6) Retirar versión anterior (6.9).

### 6.9 Control de documentos obsoletos
1) Al aprobar una nueva versión, la anterior se marca como **OBSOLETA**.  
2) El RC asegura que:
   - No permanezca disponible en carpetas operativas.
   - Se evite su uso accidental (sello “OBSOLETO” / control de acceso).
3) Conservar obsoletos solo para trazabilidad si aplica.

### 6.10 Control de documentos externos
1) El DP identifica documentos externos requeridos.  
2) El RC los registra en un listado (puede integrarse a la LMD o un archivo dedicado).  
3) Se controla: fuente oficial, versión/edición, fecha de consulta, ubicación, responsable de monitoreo.

## 7. Control de registros

### 7.1 Requisitos mínimos
Todo registro debe ser:
- **Identificable** (nombre/código, proceso, fecha, responsable si aplica).
- **Legible**.
- **Trazable**.

### 7.2 Almacenamiento, protección y acceso
- **Digital:** repositorio con permisos, respaldos, control de acceso por roles.
- **Físico:** archivadores etiquetados, control de acceso, protección contra daño.

### 7.3 Recuperación y retención
Todos los registros se listan en la **Matriz de Control de Registros** (`docs/_control/matriz_registros.yml`), que define:
- ubicación, retención, acceso, protección y disposición final.

### 7.4 Disposición final
Al término del periodo de retención:
- Digital: eliminación controlada o archivado histórico.
- Físico: destrucción segura o archivo muerto.

## 8. Registros asociados
- REG-SGC-CDC — Solicitud de Creación/Cambio Documental (llenada)
- REG-SGC-COM — Evidencia de distribución/comunicación

## 9. Anexos
- `docs/_control/lmd.yml` — Lista Maestra de Documentos
- `docs/_control/matriz_registros.yml` — Matriz de registros
- `docs/_control/FOR-SGC-01_Solicitud_de_Creacion_y_Cambio_Documental.md` — Formato solicitud cambio

## 10. Control de cambios
| Versión | Fecha | Descripción del cambio | Elaboró | Aprobó |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emisión inicial | | |
