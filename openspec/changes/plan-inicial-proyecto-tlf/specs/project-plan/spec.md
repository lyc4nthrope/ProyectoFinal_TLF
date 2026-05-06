# project-plan Specification

## Purpose

Definir como debe arrancar el proyecto para que el desarrollo sea colaborativo, explicable y alineado con Teoria de Lenguajes Formales.

## Requirements

### Requirement: Estrategia de ramas colaborativa

El proyecto MUST usar `main` como rama estable de produccion, `preproduccion` como rama de integracion previa, ramas de trabajo con el formato `feature/<integrante>/<tema>`, y ramas `hotfix/<tema>` para correcciones urgentes.

#### Scenario: Rama de Cristhian

- GIVEN que `cristhian` inicia una funcionalidad de automatas
- WHEN crea una rama nueva
- THEN el nombre MUST seguir el formato `feature/cristhian/<tema>`

#### Scenario: Rama de Daniel

- GIVEN que `daniel` inicia una funcionalidad de interfaz o pruebas
- WHEN crea una rama nueva
- THEN el nombre MUST seguir el formato `feature/daniel/<tema>`

#### Scenario: Integracion en preproduccion

- GIVEN que una funcionalidad ya fue terminada en una rama `feature`
- WHEN se prepara para revision e integracion
- THEN los cambios MUST fusionarse primero en `preproduccion` antes de llegar a `main`

#### Scenario: Correccion urgente

- GIVEN que existe un error critico detectado en una version ya integrada
- WHEN se requiere una correccion inmediata
- THEN la rama MUST crearse con el formato `hotfix/<tema>` y luego fusionarse en `main` y `preproduccion`

### Requirement: Implementacion basada en fundamentos formales

El sistema SHALL separar cada validador o detector como un algoritmo explicable mediante estados, reglas y transiciones observables.

#### Scenario: Validador de patron

- GIVEN un patron como correo o telefono
- WHEN se disena el algoritmo
- THEN el comportamiento MUST poder explicarse sin depender de `re` como caja negra

#### Scenario: Documentacion de transiciones

- GIVEN un modulo que procesa caracteres
- WHEN el estudiante lo presente
- THEN los comentarios SHOULD describir el por que de cada decision de estado

### Requirement: Restriccion de procesamiento manual

La solucion MUST implementar la logica principal de reconocimiento y validacion mediante metodos desarrollados por el estudiante, y MUST NOT depender de la libreria `re` como mecanismo principal de procesamiento.

#### Scenario: Construccion de validador

- GIVEN que se implementa un validador de correo, telefono o fecha
- WHEN se procesa la cadena de entrada
- THEN el algoritmo MUST recorrer simbolos y aplicar reglas propias de transicion o validacion

#### Scenario: Uso auxiliar permitido

- GIVEN una necesidad secundaria como limpieza o apoyo no critico
- WHEN se evalua una libreria del lenguaje
- THEN su uso SHOULD NOT reemplazar el analisis formal central del proyecto

### Requirement: Orden de construccion del proyecto

El proyecto MUST comenzar por el nucleo de validacion antes de la interfaz grafica.

#### Scenario: Inicio por motor formal

- GIVEN que el proyecto aun no tiene codigo
- WHEN se planifica la primera iteracion
- THEN primero MUST implementarse el analizador de cadenas y automatas base

#### Scenario: Integracion posterior de GUI

- GIVEN que existen validadores probados
- WHEN se construye la interfaz
- THEN la GUI SHALL consumir esos modulos sin duplicar reglas

### Requirement: Estructura de carpetas coherente

El proyecto MUST organizarse en carpetas separadas para nucleo formal, patrones, interfaz, pruebas y documentacion, de modo que cada parte del sistema sea ubicable y explicable.

#### Scenario: Separacion del nucleo y la interfaz

- GIVEN que se crean los archivos base del proyecto
- WHEN se define la estructura de carpetas
- THEN el codigo formal MUST quedar separado del codigo de interfaz

#### Scenario: Soporte a entregables academicos

- GIVEN que el proyecto requiere documento, pruebas y evidencias
- WHEN se crea la estructura inicial
- THEN deben existir ubicaciones claras para documentacion, pruebas y recursos de evidencia

### Requirement: Casos de prueba trazables

Cada patron y cada formulario MUST tener ejemplos validos, invalidos y de borde.

#### Scenario: Caso valido e invalido

- GIVEN un modulo validador
- WHEN se documentan pruebas
- THEN debe existir al menos un caso aceptado y uno rechazado

#### Scenario: Caso de borde

- GIVEN una cadena cercana al formato correcto
- WHEN se ejecuta el validador
- THEN el resultado SHOULD justificar claramente por que falla o pasa

### Requirement: Cobertura del enunciado academico

El proyecto MUST cubrir busqueda de patrones en texto, validacion de entradas en interfaz, documentacion tecnica, evidencias de funcionamiento y tabla de pruebas.

#### Scenario: Busqueda en texto

- GIVEN un texto o archivo con posibles coincidencias
- WHEN el sistema ejecuta la busqueda
- THEN debe aceptar, rechazar o extraer coincidencias segun reglas definidas

#### Scenario: Validacion de formulario

- GIVEN un usuario que diligencia campos interactivos
- WHEN ingresa datos validos o invalidos
- THEN la interfaz MUST responder con mensajes claros antes o durante el envio

#### Scenario: Entregables completos

- GIVEN que el proyecto llega a su fase final
- WHEN se prepara la entrega
- THEN deben existir documento, codigo, evidencias, tabla de pruebas y material de sustentacion
