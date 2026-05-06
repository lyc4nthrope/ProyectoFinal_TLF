# Tasks: Plan Inicial del Proyecto TLF

## Phase 1: Base del repositorio

- [ ] 1.1 Crear estructura inicial: `src/core`, `src/patterns`, `src/ui`, `tests`, `docs`, `assets/evidence`.
- [ ] 1.2 Definir archivo de entrada del proyecto y convencion de nombres en Python.
- [ ] 1.3 Crear documento `docs/branching.md` con flujo `main`, `preproduccion`, `feature/<integrante>/<tema>` y `hotfix/<tema>`.
- [ ] 1.4 Definir en `docs/project-scope.md` los patrones iniciales a cubrir segun el documento.
- [ ] 1.5 Documentar en `docs/project-structure.md` la responsabilidad de cada carpeta y archivo principal.

## Phase 2: Analisis y nucleo formal

- [ ] 2.1 Implementar un resultado comun `ValidationResult` con `accepted`, `message` y `trace`.
- [ ] 2.2 Crear un automata base que procese caracter por caracter y registre transiciones.
- [ ] 2.3 Implementar utilidades de clasificacion de simbolos: letra, digito, separador y simbolo especial.
- [ ] 2.4 Documentar en comentarios el significado de cada estado y condicion de rechazo.
- [ ] 2.5 Escribir en `docs/formal-rules.md` las reglas sintacticas de cada patron antes de codificarlas.

## Phase 3: Patrones iniciales

- [ ] 3.1 Crear `src/patterns/email_validator.py` con estados explicables y casos validos/invalidos.
- [ ] 3.2 Crear `src/patterns/phone_validator.py` con reglas claras de longitud y prefijos.
- [ ] 3.3 Crear `src/patterns/date_validator.py` con validacion estructural y rangos basicos.
- [ ] 3.4 Crear escaneo sobre texto completo para detectar coincidencias y reportar posicion.
- [ ] 3.5 Preparar ejemplos de texto con coincidencias correctas e incorrectas para pruebas de extraccion.

## Phase 4: Interfaz interactiva

- [ ] 4.1 Crear formulario en `src/ui/` para ingresar correo, telefono y fecha.
- [ ] 4.2 Conectar cada campo al validador correspondiente sin duplicar reglas.
- [ ] 4.3 Mostrar mensajes de error comprensibles y, si aplica, el `trace` resumido.
- [ ] 4.4 Validar antes del envio o en tiempo real segun el comportamiento definido para cada campo.

## Phase 5: Verificacion y sustentacion

- [ ] 5.1 Crear tabla de casos de prueba en `docs/test-cases.md` con exitos, fallos y bordes.
- [ ] 5.2 Escribir pruebas unitarias por patron en `tests/`.
- [ ] 5.3 Preparar `docs/explanation.md` explicando estados, transiciones y decisiones por algoritmo.
- [ ] 5.4 Capturar evidencias de interfaz y de busqueda en textos para la entrega final.
- [ ] 5.5 Redactar el documento final con portada, objetivo, desarrollo y conclusiones segun el enunciado.
