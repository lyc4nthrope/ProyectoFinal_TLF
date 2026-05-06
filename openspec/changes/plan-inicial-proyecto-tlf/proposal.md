# Proposal: Plan Inicial del Proyecto TLF

## Intent

Definir el arranque formal del proyecto final para construir una herramienta en Python que busque patrones en texto y valide entradas interactivas usando fundamentos de Teoria de Lenguajes Formales, cumpliendo las fases, entregables y restricciones del documento base.

## Scope

### In Scope
- Estructura SDD del proyecto y convencion de ramas.
- Arquitectura inicial basada en validadores, analizadores y automatas explicables.
- Regla de colaboracion con ramas individuales por integrante.
- Trazabilidad con las fases academicas: analisis, diseno, implementacion, pruebas y documentacion.
- Cobertura de entregables: documento, codigo fuente, evidencias, tabla de pruebas y sustentacion.

### Out of Scope
- Implementacion completa de la aplicacion.
- Integracion con servicios externos o bases de datos.
- Uso de librerias de expresiones regulares como motor principal de validacion.

## Approach

Usar `openspec/` como fuente de verdad, separar busqueda textual y validacion interactiva en modulos, construir algoritmos manuales con estados y transiciones explicables, y trabajar con flujo de ramas `main` -> `preproduccion` -> `feature/*` y `hotfix/*`. El proyecto se desarrollara en el mismo orden del documento: primero analisis de patrones y reglas, luego diseno del motor formal, despues implementacion, pruebas y por ultimo documentacion y evidencias.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/config.yaml` | New | Reglas SDD del proyecto |
| `openspec/changes/plan-inicial-proyecto-tlf/` | New | Propuesta, especificacion, diseno y tareas |
| `.atl/skill-registry.md` | New | Registro de habilidades y convenciones |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Querer resolver todo con regex nativa | High | Exigir automatas y validadores manuales por modulo |
| Mezclar cambios sin control de Git | Medium | Trabajar con `preproduccion`, ramas `feature/*` y `hotfix/*` con merge controlado |
| Diseñar una UI antes del nucleo formal | Medium | Implementar primero el motor de validacion |
| No cubrir la rubrica completa | Medium | Mapear cada fase y entregable del proyecto a tareas SDD verificables |

## Rollback Plan

Si el plan inicial no encaja, se elimina `openspec/changes/plan-inicial-proyecto-tlf/` y se redefine el alcance sin tocar codigo productivo.

## Dependencies

- Python 3.x
- Tkinter o equivalente estandar para GUI local
- Documento base del proyecto como referencia funcional y academica

## Success Criteria

- [ ] Existe una estrategia clara de ramas y colaboracion con `main`, `preproduccion`, `feature/*` y `hotfix/*`.
- [ ] El proyecto queda dividido en modulos explicables desde TLF.
- [ ] Hay tareas secuenciadas para iniciar implementacion sin ambiguedad.
- [ ] El plan cubre las fases y entregables exigidos por el documento del curso.
