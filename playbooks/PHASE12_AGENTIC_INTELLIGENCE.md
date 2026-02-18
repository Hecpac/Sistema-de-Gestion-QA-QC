# FASE 12: Inteligencia Agéntica (SGC-AI)

> **Estado:** PLANIFICADO
> **Objetivo:** Transformar el SGC de un repositorio pasivo a un sistema proactivo que asiste en la creación técnica, vigilancia de riesgos y consulta en obra.

## 1. Estrategia
Integrar capacidades de **LLM (Large Language Models)** directamente en el ciclo de vida del SGC, gobernadas por los mismos principios de trazabilidad (Git) que el resto del sistema.

No usaremos "cajas negras" SaaS. Crearemos **Agentes Especialistas** dentro de `agent_runtime/` que operan sobre los archivos Markdown.

## 2. Capacidades a Implementar

### A. Spec-to-ITP (Generador de Planes de Inspección)
**Problema:** Traducir especificaciones técnicas (PDFs de 500+ págs, normas ACI/ASME) a listas de chequeo ejecutables (`IT-SGC-xx`) es lento y propenso a error.
**Solución:** Agente `spec-parser` que ingesta texto técnico y estructura un borrador de ITP.
- **Input:** Texto crudo o Markdown de la especificación.
- **Proceso:** Extracción de "shalls" (requisitos mandatorios), tolerancias y frecuencias.
- **Output:** Archivo `docs/04_instructivos/IT-SGC-XX_Borrado.md` siguiendo la plantilla oficial.
- **KPI:** Reducción del 80% en tiempo de redacción inicial.

### B. Radar de Riesgos Dinámico (Risk Watchdog)
**Problema:** La Matriz de Riesgos (`FOR-SGC-10`) suele quedar obsoleta y desconectada de los incidentes reales.
**Solución:** Agente `risk-watchdog` que se activa al cerrar No Conformidades.
- **Trigger:** Merge de un `FOR-SGC-02` (NC) en estado "CERRADA".
- **Proceso:** Analiza la Causa Raíz y busca riesgos relacionados en la Matriz.
- **Acción:** Si el riesgo no existe o su valoración fue baja, **abre un PR** sugiriendo actualizar la Matriz de Riesgos.
- **Valor:** El SGC se "endurece" automáticamente ante fallos reales.

### C. Copiloto de Obra (SGC RAG)
**Problema:** El personal de campo no navega en carpetas de GitHub para buscar tolerancias.
**Solución:** Interfaz de consulta (CLI/Chat) sobre la "Fuente de Verdad".
- **Backend:** Índice vectorial local (ChromaDB o simple FAISS) de la carpeta `docs/`.
- **Frontend:** Comando `sgc-query "tolerancia verticalidad muros"`.
- **Respuesta:** Dato preciso + Cita del documento (`IT-SGC-02 línea 45`).

## 3. Plan de Ejecución

### Semana 1: Cimientos
- [ ] Definir arquitectura de agentes en `agent_runtime/sgc_agents/specialists.py`.
- [ ] Prototipar `spec-parser` con un documento de prueba (ej. ACI 318 parcial).

### Semana 2: Riesgos Dinámicos
- [ ] Crear script `watchdog_nc.py` que lea NCs cerradas.
- [ ] Implementar lógica de actualización de `FOR-SGC-10`.

### Semana 3: Copiloto (RAG)
- [ ] Implementar indexación de embeddings en `sgc-build-indexes`.
- [ ] Crear CLI `sgc-ask`.

## 4. Riesgos Técnicos
- **Alucinación:** El agente podría inventar tolerancias.
    - *Mitigación:* El sistema siempre cita la fuente (línea/archivo) y requiere revisión humana (PR) antes de merge.
- **Costos:** Uso excesivo de tokens en RAG.
    - *Mitigación:* Caching agresivo y uso de modelos eficientes (Gemini Flash / GPT-4o-mini).
