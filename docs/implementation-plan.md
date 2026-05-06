# Implementation Plan

## Objetivo del arranque

Construir el proyecto desde el nucleo formal hacia afuera, para que cada parte pueda explicarse con fundamentos de Teoria de Lenguajes Formales y no como una caja negra.

## Recomendacion de alcance inicial

Comenzar con tres patrones:

- telefono
- correo electronico
- fecha

Este conjunto es suficiente para demostrar:

- validacion estructural
- recorrido simbolo por simbolo
- transiciones de estado
- casos validos, invalidos y de borde
- integracion posterior en formularios y escaneo de texto

## Plan de trabajo

### Fase 1: Delimitar el problema

#### Que se va a hacer

- Elegir los patrones iniciales del proyecto.
- Definir que formatos exactos se aceptan y cuales no.
- Decidir ejemplos validos e invalidos desde el inicio.

#### Como se va a hacer

- Escribir las reglas en `docs/project-scope.md`.
- Escribir la sintaxis esperada en `docs/formal-rules.md`.
- Preparar una primera tabla de pruebas en `docs/test-cases.md`.

#### Resultado esperado

- Cada patron queda definido antes de programarlo.
- Se evita improvisar reglas mientras se implementa.

### Fase 2: Construir el nucleo formal

#### Que se va a hacer

- Crear una base comun para validaciones.
- Modelar el procesamiento caracter por caracter.
- Registrar por que una cadena se acepta o rechaza.

#### Como se va a hacer

- Implementar `src/core/result.py` para guardar el resultado.
- Implementar `src/core/symbol_classifier.py` para clasificar simbolos.
- Implementar `src/core/automaton.py` para manejar estados y transiciones.

#### Resultado esperado

- Existe una base reutilizable para todos los patrones.
- Los algoritmos quedan explicables y trazables.

### Fase 3: Implementar el primer patron

#### Que se va a hacer

- Construir primero el validador de telefono.

#### Como se va a hacer

- Definir estados simples: inicio, prefijo, cuerpo, aceptacion, rechazo.
- Recorrer la cadena simbolo por simbolo.
- Validar longitud, digitos y separadores permitidos.
- Guardar un `trace` con cada decision importante.

#### Resultado esperado

- Primer patron completamente funcional.
- Base clara para replicar el metodo en otros validadores.

### Fase 4: Extender a correo y fecha

#### Que se va a hacer

- Implementar `email_validator.py`.
- Implementar `date_validator.py`.

#### Como se va a hacer

- Reutilizar el nucleo formal.
- Definir estados y reglas especificas por patron.
- Documentar comentarios que expliquen cada transicion importante.

#### Resultado esperado

- Tres validadores independientes pero consistentes.
- El proyecto ya demuestra aplicacion real de TLF.

### Fase 5: Verificar y documentar

#### Que se va a hacer

- Probar cada patron.
- Registrar entradas correctas, incorrectas y de borde.
- Explicar formalmente cada algoritmo.

#### Como se va a hacer

- Escribir pruebas en `tests/`.
- Completar `docs/test-cases.md`.
- Redactar `docs/explanation.md` con estados, transiciones y razon de aceptacion o rechazo.

#### Resultado esperado

- El proyecto queda sustentable.
- No solo funciona: tambien se puede defender academicamente.

### Fase 6: Buscar patrones en texto

#### Que se va a hacer

- Implementar el escaneo de textos completos.

#### Como se va a hacer

- Crear `src/patterns/text_scanner.py`.
- Recorrer el texto y probar segmentos candidatos.
- Reportar coincidencias, posicion y resultado.

#### Resultado esperado

- Se cumple la parte del documento sobre busqueda y extraccion de patrones.

### Fase 7: Integrar la interfaz

#### Que se va a hacer

- Crear formularios para validar datos ingresados por el usuario.

#### Como se va a hacer

- Implementar la GUI en `src/ui/app.py` y `src/ui/forms.py`.
- Conectar los campos con los validadores ya hechos.
- Mostrar mensajes claros de aceptacion o error.

#### Resultado esperado

- Se cumple la parte del documento sobre sistemas interactivos.

## Orden recomendado

1. Definir reglas del telefono.
2. Implementar el nucleo formal.
3. Implementar el validador de telefono.
4. Escribir pruebas del telefono.
5. Repetir el metodo con correo y fecha.
6. Construir el escaner de texto.
7. Construir la interfaz.
8. Completar documentacion y evidencias.

## Por que este plan es el correcto

- Empieza por lo que mas pesa academicamente: la logica formal.
- Reduce riesgo: primero se construye lo dificil y esencial.
- Hace que la interfaz sea solo una capa final, no el centro del proyecto.
- Permite explicar el proceso como un automata o validador manual.
- Facilita las pruebas, porque cada patron nace aislado.
- Sigue el mismo orden del documento: analisis, diseno, implementacion, pruebas y documentacion.

## Recomendacion concreta

El primer entregable tecnico deberia ser este:

- `formal-rules.md` con la regla del telefono
- `result.py`
- `symbol_classifier.py`
- `automaton.py`
- `phone_validator.py`
- `test_phone_validator.py`

Ese primer bloque ya les da una base real, demostrable y correcta para empezar el proyecto.
