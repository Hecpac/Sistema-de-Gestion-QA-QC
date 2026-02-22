---
codigo: "IT-SGC-05"
titulo: "Instructivo de Generacion Automatica de ITPs (Spec-to-ITP)"
tipo: "IT"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-18"
proceso: "SGC / Transformacion Digital"
elaboro: "Lider SGC AI"
reviso: "Gerencia de Calidad"
aprobo: "Direccion General"
---

# IT-SGC-05 Instructivo de Generacion Automatica de ITPs

## 1. Objetivo
Estandarizar el uso de Agentes de IA (Spec-to-ITP) para la generacion acelerada de Planes de Inspeccion y Ensayo (ITP) a partir de especificaciones tecnicas, asegurando la consistencia y reduciendo el error humano en la transcripcion de tolerancias.

## 2. Alcance
Aplica a todas las disciplinas tecnicas (Civil, Mecanica, Electrica) que requieran generar listas de verificacion (ITP) basadas en codigos, normas o especificaciones de proyecto.

## 3. Referencias
- PR-SGC-01 Control de Documentos y Registros.
- PR-SGC-09 Control de Cambios del Runtime y Automatizaciones QA.
- Manual de Usuario: Herramienta Spec-to-ITP (`scripts/demo_spec_parser.py`).

## 4. Definiciones
- **Spec-to-ITP:** Agente de software que procesa lenguaje natural tecnico y extrae requisitos normativos.
- **ITP (Inspection and Test Plan):** Documento que detalla que, como y cuando se inspecciona una actividad.
- **Alucinacion de IA:** Riesgo de que el modelo genere un dato plausible pero falso.

## 5. Responsabilidades
- **Ingeniero de Calidad (Usuario):** Seleccionar la especificacion correcta y **validar** linea por linea el output del agente.
- **Agente (Sistema):** Extraer criterios de aceptacion, tolerancias y frecuencias sin omitir requisitos mandatorios ("shall").

## 6. Desarrollo / Metodologia

### 6.1 Preparacion del Input
El usuario debe aislar el texto de la especificacion tecnica relevante.
- Formatos aceptados: `.txt`, `.md` (texto plano extraido de PDF).
- Limpieza: Eliminar encabezados/pies de pagina repetitivos que puedan confundir al contexto.

### 6.2 Ejecucion del Agente
Ejecutar el script de generacion (via CLI o entorno OpenClaw):
```bash
python scripts/demo_spec_parser.py ruta_especificacion.txt
```

### 6.3 Revision Humana Obligatoria (Human-in-the-loop)
El agente generara un borrador en una ubicacion de salida definida (por ejemplo, bajo `docs/externos/phase12/`).
El Ingeniero de Calidad debe verificar:
1.  **Integridad:** ¿Estan todos los puntos criticos?
2.  **Precision:** ¿Las tolerancias numericas coinciden exactamente con la norma? (Ej. `± 6mm` vs `± 10mm`).
3.  **Seguridad:** ¿Se clasificaron correctamente los puntos de espera (Hold Points)?

### 6.4 Aprobacion y Publicacion
Una vez validado:
1.  Asignar un codigo definitivo conforme a `AGENTS.md` (ej. `IT-SGC-25`) y renombrar el archivo.
2.  Actualizar el frontmatter a estado `VIGENTE`.
3.  Ejecutar `sgc-build-indexes` para registrarlo en la LMD.

## 7. Control de Riesgos (IA)
| Riesgo | Mitigacion |
|---|---|
| Alucinacion de tolerancias | La revision humana es mandatoria. El agente debe citar la seccion de referencia. |
| Omicion de requisitos | El ITP generado se considera una "guia base", no un sustituto de leer la norma. |

## 8. Anexos
- N/A

## 9. Registros asociados
- REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique).
- REG-SGC-COM - Evidencia de comunicacion/distribucion (cuando aplique).

## 10. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-18 | Emision inicial (vigente) del instructivo de generacion automatica de ITPs (Spec-to-ITP) | Lider SGC AI | Direccion General |
