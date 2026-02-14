---
codigo: "PR-SGC-02"
titulo: "Control de No Conformidades y CAPA"
tipo: "PR"
version: "1.1"
estado: "BORRADOR"
fecha_emision: "2026-02-09"
proceso: "SGC / Mejora"
elaboro: "Coordinacion de Calidad"
reviso: "Gerencia de Operaciones"
aprobo: "Direccion General"
---

# PR-SGC-02 Control de No Conformidades y CAPA

> Nota: Criterios y umbrales de este documento son sinteticos de referencia. Ajustar con datos reales de la organizacion.

## 1. Objetivo
Definir la metodologia para identificar no conformidades, analizar causa raiz, implementar acciones correctivas y verificar eficacia con criterios medibles.

## 2. Alcance
Aplica a no conformidades detectadas en operacion, auditorias, reclamos, inspecciones y revision de datos.

## 3. Referencias
- ISO 9001:2015, clausula 10.2 No conformidad y accion correctiva.
- FOR-SGC-02 Registro de No Conformidad.
- FOR-SGC-03 Plan y Registro CAPA.

## 4. Definiciones
- No conformidad (NC): incumplimiento de requisito especificado.
- Causa raiz: causa principal cuya eliminacion previene recurrencia.
- CAPA: plan de acciones correctivas y de contencion orientado al cierre eficaz.
- Eficacia: condicion en la que la NC no se repite en la ventana de verificacion definida.

## 5. Responsabilidades
- Personal: reportar NC en un plazo maximo de 24 horas desde su deteccion.
- Dueno de Proceso: analizar causa raiz y ejecutar CAPA.
- Responsable de Calidad: validar clasificacion, seguimiento y cierre.
- Direccion/Gerencia: aprobar acciones de alto impacto.

## 6. Desarrollo / Metodologia
### 6.1 Registro y clasificacion de severidad
1. Registrar la NC en FOR-SGC-02 con evidencia objetiva.
2. Asignar puntaje de severidad usando matriz de impacto y frecuencia.

| Variable | Escala | Criterio sintetico |
|---|---|---|
| Impacto | 1-5 | 1 = sin efecto en cliente, 5 = afecta entrega/requisito critico |
| Frecuencia | 1-5 | 1 = evento aislado, 5 = recurrencia continua |
| Nivel de riesgo NC | Impacto x Frecuencia | Rango 1-25 |

Clasificacion:
- Baja: 1 a 6
- Media: 7 a 12
- Alta: 13 a 25

### 6.2 Analisis de causa raiz
1. Para NC media y alta, aplicar metodo 5 Porques (obligatorio).
2. Para NC alta, complementar con Ishikawa o analisis equivalente.
3. Documentar causa raiz validada por el Dueno de Proceso y Calidad.

### 6.3 Definicion de CAPA y tiempos objetivo
| Severidad | Contencion | Plan CAPA aprobado | Cierre objetivo |
|---|---|---|---|
| Alta | <= 24 horas | <= 5 dias habiles | <= 30 dias naturales |
| Media | <= 3 dias habiles | <= 10 dias habiles | <= 45 dias naturales |
| Baja | <= 5 dias habiles | <= 15 dias habiles | <= 60 dias naturales |

Reglas:
1. Toda accion CAPA debe tener responsable, fecha compromiso y evidencia esperada.
2. Si una accion se vence, se escala a Gerencia de Operaciones en un maximo de 48 horas.

### 6.4 Verificacion de eficacia
1. Definir criterio de eficacia medible en FOR-SGC-03.
2. Ventana minima de verificacion:
- NC alta/media: 60 dias sin recurrencia.
- NC baja: 30 dias sin recurrencia.
3. Si no es eficaz, reabrir NC y redefinir CAPA.

### 6.5 Seguimiento y frecuencia
- Seguimiento semanal de NC abiertas por Responsable de Calidad.
- Revision mensual de tendencia NC/CAPA en comite de calidad.

### 6.6 Indicadores de control del proceso
| Indicador | Formula | Meta sintetica |
|---|---|---|
| Cierre en plazo de NC | NC cerradas en plazo / NC cerradas x 100 | >= 90% |
| Eficacia CAPA | CAPA eficaces / CAPA verificadas x 100 | >= 85% |
| Recurrencia | NC repetidas (90 dias) / NC totales x 100 | <= 10% |

## 7. Registros asociados
- REG-SGC-NC - Registro de No Conformidad.
- REG-SGC-CAPA - Plan y Registro CAPA.

## 8. Control de cambios
| Version | Fecha | Descripcion del cambio | Elaboro | Aprobo |
|---|---:|---|---|---|
| 1.0 | 2026-02-09 | Emision inicial | | |
| 1.1 | 2026-02-09 | Se agregan criterios medibles de severidad, causa raiz, eficacia y frecuencias | Coordinacion de Calidad | Direccion General |
