---
codigo: "IT-SGC-06"
titulo: "Instructivo de Vigilancia de Riesgos con IA (Risk Watchdog)"
tipo: "IT"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-18"
proceso: "SGC / Riesgos"
elaboro: "Lider SGC AI"
reviso: "Gerencia de Calidad"
aprobo: "Direccion General"
---

# IT-SGC-06 Instructivo de Vigilancia de Riesgos con IA

## 1. Objetivo
Establecer el mecanismo automatico para que el Sistema de Gestion de Calidad "aprenda" de sus fallos, actualizando la Matriz de Riesgos basada en las Causas Raiz de No Conformidades cerradas.

## 2. Alcance
Aplica a todas las No Conformidades (`FOR-SGC-02`) en estado CERRADA y a la Matriz de Riesgos (`FOR-SGC-10`).

## 3. Referencias
- PR-SGC-02 Control de No Conformidades y CAPA.
- PR-SGC-06 Gestion de Riesgos y Oportunidades.
- Script de Vigilancia: `scripts/watchdog_nc.py`.

## 4. Definiciones
- **Risk Watchdog:** Agente de IA que monitorea NCs cerradas y busca huecos en la cobertura de riesgos.
- **Aprendizaje Organizacional:** Capacidad del SGC de evitar la recurrencia sistemica mediante la actualizacion de controles preventivos.

## 5. Responsabilidades
- Ingeniero de Calidad: cerrar NC con causa raiz documentada y verificar la pertinencia de propuestas generadas.
- Dueno del Proceso de Riesgos: revisar y decidir la incorporacion de propuestas en la matriz oficial.
- Administracion del repositorio SGC (si aplica): operar la automatizacion (CI/monitor) y asegurar evidencia trazable.

## 6. Desarrollo / Metodologia

### 5.1 Cierre de No Conformidad
El Ingeniero de Calidad debe cerrar la NC documentando explicitamente la "Causa Raiz" en el archivo Markdown o sistema origen.

### 5.2 Ejecucion del Watchdog
Periodicamente (o disparado por CI/CD al hacer merge de una NC cerrada), se ejecuta:
```bash
python scripts/watchdog_nc.py
```

### 5.3 Analisis del Agente
El agente:
1. Lee la Causa Raiz de la NC.
2. Lee la Matriz de Riesgos vigente.
3. Evalua semanticamente si el riesgo ya esta cubierto.
4. Si NO esta cubierto, genera una propuesta en `docs/08_riesgos/PROPOSED_RISKS.md`.

### 5.4 Aprobacion del Cambio
El Dueno del Proceso de Riesgos revisa el archivo de propuestas:
- Si es valida: Copia la linea a la Matriz de Riesgos oficial (`REG-SGC-RISK-xxxx`).
- Si es invalida: Descarta la propuesta y ajusta el prompt si es necesario.

## 6. Ejemplo Real
**Caso:** Falla de resistencia de concreto por sensor descalibrado.
**Analisis Watchdog:** Detecto que "Fallo de proveedor externo / Calibracion" no estaba en la matriz.
**Propuesta Generada:** Riesgo R-004 "Desviacion por falta de calibracion...".
**Accion:** Se incorporo a la matriz para prevenir futuros incidentes similares.

## 7. Registros asociados
- REG-SGC-NC - Registro de No Conformidad (llenado).
- REG-SGC-RISK - Matriz de riesgos y oportunidades (llenada).
- REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (cuando aplique).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-18 | Emision inicial (vigente) del instructivo de vigilancia de riesgos con IA (Risk Watchdog) | Lider SGC AI | Direccion General |
