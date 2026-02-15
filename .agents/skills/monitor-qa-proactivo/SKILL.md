---
name: monitor-qa-proactivo
description: Activar cuando el usuario pida supervision automatica del SGC (semanal/diaria) para reconstruir artefactos de control, ejecutar QA y alertar ante hallazgos mediante cron o scheduler.
---

# Objetivo
Dejar monitoreo automático que detecte drift o fallos de compliance sin intervención manual.

# Flujo
1. Crear script versionado (ej. `agent_runtime/scripts/run_qa_monitor.sh`) que:
   - active `.venv`
   - ejecute `build_indexes` y `build_dashboard`
   - ejecute QA deterministico
   - retorne `exit 1` si hay hallazgos.
2. Guardar log en ruta estable (`docs/_control/logs/qa-monitor.log`).
3. Configurar scheduler:
   - cron local (`crontab`) o CI programado (`schedule` en GitHub Actions).
4. Configurar alerta:
   - comando de notificacion (OpenClaw event, Telegram bot, mail, etc.) cuando exit code != 0.
5. Probar corrida manual y dejar evidencia en README corto del monitor.

# Reglas
- Pedir confirmacion antes de modificar `crontab` del host.
- No hardcodear secretos en script/versionado.

# DoD
- Script de monitor ejecuta en local sin errores.
- Scheduler configurado (o PR de workflow programado listo).
- Existe prueba de alerta de fallo.
