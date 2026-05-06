# Design: Plan Inicial del Proyecto TLF

## Technical Approach

La implementacion debe comenzar por un motor formal y no por la interfaz. La arquitectura propuesta separa reconocimiento de patrones, validacion interactiva y explicacion academica. Cada algoritmo se escribe de forma secuencial, con estados nombrados y comentarios que expliquen la logica como si se resolviera en cuaderno. El plan sigue exactamente las fases del documento: analisis, diseno, implementacion, pruebas y documentacion.

## Architecture Decisions

### Decision: Base del proyecto en Python con GUI ligera

**Choice**: Python 3.x + Tkinter.  
**Alternatives considered**: Web app, CLI pura.  
**Rationale**: el enunciado recomienda Python y `tkinter`; reduce complejidad y deja el foco en TLF.

### Decision: Motor manual de validacion

**Choice**: construir analizadores por recorrido de caracteres, tablas de transicion y funciones auxiliares.  
**Alternatives considered**: usar `re` para todo.  
**Rationale**: el proyecto exige metodos desarrollados por el estudiante y defendibles oralmente.

### Decision: Construccion incremental por evidencia academica

**Choice**: desarrollar primero patrones aislados, luego escaneo de textos, despues formulario, y al final pruebas y documentacion.  
**Alternatives considered**: construir toda la interfaz primero o mezclar modulos sin orden.  
**Rationale**: coincide con la rubrica y permite demostrar avance real en cada seguimiento.

### Decision: Separacion por capas pedagogicas

**Choice**: `core/`, `patterns/`, `ui/`, `tests/`, `docs/`.  
**Alternatives considered**: una sola carpeta monolitica.  
**Rationale**: facilita explicar responsabilidades, pruebas y separacion tecnica del proyecto.

## Project Structure

```text
ProyectoFinal_TLF/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── automaton.py
│   │   ├── result.py
│   │   └── symbol_classifier.py
│   ├── patterns/
│   │   ├── email_validator.py
│   │   ├── phone_validator.py
│   │   ├── date_validator.py
│   │   └── text_scanner.py
│   └── ui/
│       ├── app.py
│       └── forms.py
├── tests/
│   ├── test_email_validator.py
│   ├── test_phone_validator.py
│   ├── test_date_validator.py
│   └── test_text_scanner.py
├── docs/
│   ├── branching.md
│   ├── project-scope.md
│   ├── formal-rules.md
│   ├── test-cases.md
│   ├── explanation.md
│   └── final-report.md
├── assets/
│   └── evidence/
├── openspec/
└── README.md
```

## Folder Responsibilities

| Ruta | Responsabilidad |
|------|-----------------|
| `src/main.py` | Punto de entrada para ejecutar el proyecto |
| `src/core/` | Motor formal reusable: estados, transiciones, clasificacion y resultados |
| `src/patterns/` | Validadores concretos y buscador de coincidencias |
| `src/ui/` | Formularios, eventos y mensajes al usuario |
| `tests/` | Verificacion automatizada de patrones y escaneo |
| `docs/` | Documento tecnico, reglas formales, pruebas y sustentacion |
| `assets/evidence/` | Capturas y evidencias visuales para la entrega |
| `openspec/` | Fuente de verdad del plan SDD |

## Naming Rules

- Cada archivo de `src/patterns/` representa un patron o servicio puntual.
- El codigo de `src/core/` no debe depender de Tkinter.
- La carpeta `src/ui/` solo consume validadores; no debe reimplementar reglas.
- Las pruebas en `tests/` deben reflejar nombres de archivos de `src/patterns/`.
- Los documentos en `docs/` deben corresponder a entregables del curso.

## Data Flow

```text
Texto o formulario
        |
        v
Normalizador de entrada
        |
        v
Automata / validador manual
        |
        +--> resultado booleano
        +--> posicion de error o coincidencia
        +--> explicacion textual
        |
        v
Interfaz / reporte de pruebas
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `openspec/config.yaml` | Create | Configuracion SDD del proyecto |
| `openspec/changes/plan-inicial-proyecto-tlf/proposal.md` | Create | Alcance y criterios de exito |
| `openspec/changes/plan-inicial-proyecto-tlf/specs/project-plan/spec.md` | Create | Requisitos iniciales del plan |
| `openspec/changes/plan-inicial-proyecto-tlf/design.md` | Create | Arquitectura, ramas y arranque tecnico |
| `openspec/changes/plan-inicial-proyecto-tlf/tasks.md` | Create | Lista de ejecucion por fases |
| `docs/` | Planned | Documentacion academica y tecnica del proyecto |
| `src/` | Planned | Codigo fuente principal |
| `tests/` | Planned | Pruebas del comportamiento esperado |
| `assets/evidence/` | Planned | Evidencias visuales de funcionamiento |

## Interfaces / Contracts

```python
class ValidationResult:
    accepted: bool
    consumed: int
    message: str
    trace: list[str]

def validate_email(text: str) -> ValidationResult: ...
def validate_phone(text: str) -> ValidationResult: ...
def scan_text(text: str, validator) -> list[ValidationResult]: ...
```

`trace` existe para sustentar el algoritmo: guarda estados, simbolos leidos y razon de aceptacion o rechazo.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Validadores por patron | Casos validos, invalidos y borde |
| Integration | Escaneo de texto con multiples coincidencias | Textos completos y reporte de posiciones |
| Manual/UI | Formularios y mensajes de error | Pruebas guiadas en Tkinter |

## Academic Traceability

| Fase del documento | Traduccion tecnica |
|--------------------|-------------------|
| Analisis de requerimientos | Elegir patrones, restricciones y formato de salida |
| Diseno | Definir estados, transiciones, estructuras y GUI |
| Implementacion | Construir validadores, buscador y formulario |
| Pruebas y casos de uso | Probar aceptacion, rechazo y errores controlados |
| Documentacion | Explicar algoritmo, resultados, guia de uso y evidencias |

## Deliverables Mapping

| Entregable | Como se produce |
|------------|-----------------|
| Documento del proyecto | `docs/` + resumen final |
| Codigo fuente organizado | `src/` y `tests/` |
| Evidencias de busqueda y validacion | capturas y ejemplos de ejecucion |
| Evidencias de formulario | capturas de GUI y validaciones |
| Tabla de casos de prueba | `docs/test-cases.md` |
| Sustentacion breve | `docs/explanation.md` y demostracion del `trace` |

## Migration / Rollout

No migration required.

## Open Questions

- [ ] Definir si el conjunto inicial de patrones sera correo, telefono, fecha y placa, o si habra otro dominio.

## Branch Strategy

- Rama estable final: `main`
- Rama de integracion previa: `preproduccion`
- Ramas de trabajo: `feature/cristhian/<tema>` y `feature/daniel/<tema>`
- Ramas de correccion urgente: `hotfix/<tema>`
- No se define reparto tecnico entre integrantes dentro de este plan.
- Cada integrante crea su propia rama segun el tema que acuerden entre ustedes.

## Branch Flow

```text
main
  ^
  |
preproduccion
  ^       ^
  |       |
feature/* hotfix/*
```

- Las funcionalidades normales nacen desde `preproduccion` y regresan a `preproduccion`.
- `main` solo recibe cambios que ya pasaron por `preproduccion`, salvo correcciones urgentes.
- Un `hotfix/<tema>` corrige el problema urgente y luego se fusiona tanto en `main` como en `preproduccion`.

## Recommended Start Order

1. Crear la estructura de carpetas del proyecto.
2. Elegir el conjunto inicial de patrones del proyecto.
3. Implementar un automata simple y su `trace`.
4. Implementar validadores de patrones prioritarios.
5. Crear el buscador de coincidencias en textos completos.
6. Escribir pruebas manuales y unitarias.
7. Integrar la interfaz grafica sobre el nucleo estable.
8. Preparar documentacion, evidencias y sustentacion.
