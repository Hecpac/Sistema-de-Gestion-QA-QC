---
codigo: "IT-SGC-07"
titulo: "Instructivo de Consulta en Obra (SGC Copilot)"
tipo: "IT"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-18"
proceso: "SGC / Transformacion Digital"
elaboro: "Lider SGC AI"
reviso: "Gerencia de Calidad"
aprobo: "Direccion General"
---

# IT-SGC-07 Instructivo de Consulta en Obra (SGC Copilot)

## 1. Objetivo
Proveer acceso inmediato a la informacion tecnica y normativa del SGC para el personal de campo, utilizando lenguaje natural y citando siempre la fuente documental aprobada.

## 2. Alcance
Aplica a consultas sobre tolerancias, procedimientos, formatos y criterios de aceptacion contenidos en el repositorio `docs/`.

## 3. Referencias
- PR-SGC-01 Control de Documentos y Registros.
- Script de Consulta: `scripts/sgc_ask.py`.

## 4. Definiciones
- **SGC Copilot:** Herramienta de busqueda semantica y generacion de respuestas basada en la documentacion vigente.
- **RAG (Retrieval-Augmented Generation):** Tecnica que combina busqueda de documentos relevantes con la capacidad de respuesta de un LLM.

## 5. Procedimiento

### 5.1 Realizacion de Consulta
El usuario (Ingeniero, Supervisor, Auditor) ejecuta el comando de consulta desde la terminal o interfaz de chat habilitada:

```bash
python scripts/sgc_ask.py "Cual es la tolerancia de asentamiento?"
```

### 5.2 Procesamiento del Sistema
El sistema realiza los siguientes pasos (transparentes al usuario):
1.  **Indexado:** Escanea todos los archivos Markdown en `docs/`.
2.  **Recuperacion:** Filtra los documentos mas relevantes por palabras clave.
3.  **Generacion:** Envia el contexto recuperado al modelo de IA (Gemini) con la instruccion de responder SOLO basado en la evidencia.

### 5.3 Interpretacion de la Respuesta
El usuario recibe:
- **Respuesta directa:** "La tolerancia es 4 pulgadas ± 1 pulgada."
- **Cita documental:** "Fuente: IT-SGC-XX Seccion 4.7."

### 5.4 Limitaciones
- Si el documento no existe o no contiene la respuesta, el sistema dira: "Data not found".
- La herramienta es de **consulta rapida**; en caso de duda o conflicto contractual, prevalece el documento firmado en PDF/Papel.

## 6. Mantenimiento
El indice se actualiza automaticamente cada vez que se modifica un archivo Markdown en el repositorio, ya que el script lee en tiempo real.
