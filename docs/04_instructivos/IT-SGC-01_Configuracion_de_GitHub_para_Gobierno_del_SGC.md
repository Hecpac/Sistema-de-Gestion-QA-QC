---
codigo: "IT-SGC-01"
titulo: "Instructivo: Configuracion de GitHub para Gobierno del SGC"
tipo: "IT"
version: "1.0"
estado: "VIGENTE"
fecha_emision: "2026-02-17"
proceso: "SGC / Control Documental"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# Instructivo: Configuracion de GitHub para Gobierno del SGC

## 1. Objetivo
Establecer la configuracion minima en GitHub para operar el SGC documental con control de cambios exigible, evidencia de aprobacion (PR), y gates QA obligatorios antes de integrar cambios.

## 2. Alcance
Aplica al repositorio GitHub del SGC y a su operacion diaria:
- Control de acceso (permisos).
- Protecciones de rama y tags.
- Reglas de revision/aprobacion.
- Ejecucion obligatoria de workflows de QA y monitor.

Excluye la redaccion/actualizacion de documentos controlados (ver PR-SGC-01) y el control de cambios del runtime/automatizaciones (ver PR-SGC-09).

## 3. Responsabilidades
- Administracion del repositorio SGC: configura GitHub (branch protection, permisos, CODEOWNERS) y mantiene operativos los workflows.
- Coordinacion de Calidad: define criterios de aceptacion documental, revisa hallazgos y autoriza baselines para auditoria.
- Direccion General: aprueba cambios mayores de gobierno del repositorio y autoriza baselines.

## 4. Materiales / herramientas
- Acceso de administracion al repositorio GitHub.
- Navegador web (GitHub UI) o GitHub CLI (opcional).

## 5. Desarrollo / Instrucciones paso a paso

### 5.1 Reglas de acceso (permisos)
1. Definir roles:
   - Administradores (minimo necesario).
   - Maintainers/Write (equipo operativo).
   - Read (auditores internos/externos, si aplica).
2. Regla: no otorgar permisos de admin a usuarios operativos sin necesidad.

### 5.2 Proteccion de rama `main` (obligatorio)
Configurar Branch Protection para `main` con, como minimo:
1. Requerir Pull Request (no permitir push directo).
2. Requerir aprobaciones:
   - Minimo 1 aprobacion.
   - Requerir Code Owner review (si se usa CODEOWNERS).
3. Requerir que las conversaciones esten resueltas antes de merge.
4. Requerir status checks antes de merge:
   - `SGC QA Gate` (workflow).
5. Enforce para administradores (no bypass) o, si se permite bypass:
   - Definir criterio de excepcion y registrar evidencia en REG-SGC-CDC.

### 5.3 CODEOWNERS (revision por duenos)
1. Mantener archivo `.github/CODEOWNERS` con responsables para rutas criticas:
   - `agent_runtime/`, `.github/workflows/`, `docs/_control/`, `AGENTS.md`, `.agents/skills/`.
2. Regla: cambios en rutas criticas requieren revision y aprobacion del Code Owner.

### 5.4 Tags de baseline (control de releases)
1. Definir un patron de tags de baseline (sugerido): `sgc-baseline-YYYY-MM-DD`.
2. Proteger tags que cumplan `sgc-*` (tag protection) para evitar retags o tags no autorizados.
3. Regla: un baseline debe cumplir:
   - 0 hallazgos de QA.
   - 0 documentos `BORRADOR` (baseline cerrado).
   - 0 pendientes en la matriz de registros.

### 5.5 Workflows (QA gate, baseline gate y monitor)
1. Verificar que GitHub Actions este habilitado para el repositorio.
2. Verificar workflows presentes:
   - `.github/workflows/sgc-qa.yml` (gate en PR/push).
   - `.github/workflows/sgc-baseline-gate.yml` (gate estricto al crear tag `sgc-*`).
   - `.github/workflows/sgc-weekly-monitor.yml` (monitor semanal con creacion de issue ante falla).
3. Verificar permisos del workflow:
   - El monitor requiere `issues: write` para crear issue en falla.
4. Verificar que el gate QA sea requerido en Branch Protection (5.2).

## 6. Criterios de aceptacion / verificacion
- No es posible mergear a `main` sin PR y sin pasar `SGC QA Gate`.
- Cambios en rutas criticas requieren aprobacion de Code Owner.
- La creacion de un tag `sgc-*` dispara `SGC Baseline Gate (Strict)` y falla si hay BORRADOR o hallazgos.
- El monitor semanal ejecuta y, si falla, crea issue con enlace al run y artifacts.

## 7. Registros asociados
- REG-SGC-CDC - Solicitud de Creacion/Cambio Documental (usar para cambios de gobernanza: protecciones, permisos, reglas de merge, cambios en workflows).
- REG-SGC-COM - Evidencia de comunicacion de cambios (cuando se modifiquen reglas de gobierno o se publique baseline).

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-17 | Emision inicial y liberacion vigente del instructivo de gobierno GitHub para el SGC | Coordinacion de Calidad | Direccion General |
