# Explanation

Descripcion formal de los tres automatas implementados en el proyecto.
Cada validador modela un Automata Finito Determinista (AFD) con estados, alfabeto, funcion de transicion y condiciones de aceptacion o rechazo.

---

## Modelo comun

Los tres validadores comparten la misma arquitectura formal:

- Se define un alfabeto finito `Σ` de simbolos validos.
- Se define un conjunto finito de estados `Q`.
- Se define un estado inicial `q₀`.
- Se define un conjunto de estados de aceptacion `F ⊆ Q`.
- La funcion de transicion `δ: Q × Σ → Q` decide el siguiente estado por cada simbolo leido.
- El automata recorre la cadena un simbolo a la vez, sin retroceder.
- Si la cadena se agota en un estado de `F`, se acepta. Si no, se rechaza.
- El estado `REJECT` es un estado trampa: una vez alcanzado, ninguna transicion posterior cambia el resultado.

Esta forma de recorrido caracter por caracter corresponde directamente al modelo de un AFD procesando una cadena de entrada `w = σ₁σ₂...σₙ`.

---

## Validador de telefono

### Alfabeto

```
Σ = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, +, -, ' ' }
```

### Estados

```
Q = { START, AFTER_PLUS, IN_NUMBER, AFTER_SEPARATOR, ACCEPT, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }
```

La aceptacion no ocurre al llegar a un estado especifico durante el recorrido.
Ocurre al final: si la cadena se agota en `IN_NUMBER` o `AFTER_PLUS` y la cantidad de digitos reales esta entre 10 y 13, el automata transita a `ACCEPT`. De lo contrario transita a `REJECT`.

### Funcion de transicion

| Estado actual | Simbolo leido | Estado siguiente | Nota |
|--------------|--------------|-----------------|------|
| `START` | digito | `IN_NUMBER` | Inicia secuencia local |
| `START` | `+` | `AFTER_PLUS` | Inicia prefijo internacional |
| `START` | otro | `REJECT` | Inicio invalido |
| `AFTER_PLUS` | digito | `IN_NUMBER` | Primer digito tras el prefijo |
| `AFTER_PLUS` | otro | `REJECT` | El prefijo debe ir seguido de digito |
| `IN_NUMBER` | digito | `IN_NUMBER` | Se acumula un digito mas |
| `IN_NUMBER` | `-` o ` ` | `AFTER_SEPARATOR` | Separa bloques numericos |
| `IN_NUMBER` | otro | `REJECT` | Simbolo fuera del alfabeto |
| `AFTER_SEPARATOR` | digito | `IN_NUMBER` | Reanuda la secuencia numerica |
| `AFTER_SEPARATOR` | `-` o ` ` | `REJECT` | Separadores consecutivos prohibidos |
| `AFTER_SEPARATOR` | otro | `REJECT` | Debe venir un digito despues del separador |

### Condicion de cierre

Al agotar la entrada:
- Si estado es `AFTER_SEPARATOR`: `REJECT` — la cadena termina en separador.
- Si digitos reales `< 10` o `> 13`: `REJECT` — longitud invalida.
- En cualquier otro caso valido: `ACCEPT`.

---

## Validador de correo electronico

### Alfabeto

```
Σ = { a-z, A-Z, 0-9, ., _, -, @  }
```

### Estados

```
Q = { START, LOCAL, LOCAL_SEPARATOR, AFTER_AT, DOMAIN, DOMAIN_HYPHEN, AFTER_DOMAIN_DOT, ACCEPT, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }
```

La aceptacion ocurre al final si se cumplen todas las condiciones de cierre formales.

### Funcion de transicion

| Estado actual | Simbolo leido | Estado siguiente | Nota |
|--------------|--------------|-----------------|------|
| `START` | letra o digito | `LOCAL` | Inicia parte local |
| `START` | otro | `REJECT` | La parte local no puede iniciar con separador |
| `LOCAL` | letra o digito | `LOCAL` | Continua la parte local |
| `LOCAL` | `.`, `_`, `-` | `LOCAL_SEPARATOR` | Separador interno permitido |
| `LOCAL` | `@` | `AFTER_AT` | Cierra parte local, abre dominio |
| `LOCAL` | otro | `REJECT` | Simbolo fuera del alfabeto local |
| `LOCAL_SEPARATOR` | letra o digito | `LOCAL` | Retoma la parte local tras separador |
| `LOCAL_SEPARATOR` | otro | `REJECT` | No se permiten separadores consecutivos ni al final |
| `AFTER_AT` | letra o digito | `DOMAIN` | Inicia primera etiqueta del dominio |
| `AFTER_AT` | otro | `REJECT` | El dominio no puede iniciar con separador |
| `DOMAIN` | letra o digito | `DOMAIN` | Continua la etiqueta actual |
| `DOMAIN` | `-` | `DOMAIN_HYPHEN` | Guion interno de etiqueta |
| `DOMAIN` | `.` | `AFTER_DOMAIN_DOT` | Cierra etiqueta y abre siguiente |
| `DOMAIN` | otro | `REJECT` | Simbolo fuera del alfabeto de dominio |
| `DOMAIN_HYPHEN` | letra o digito | `DOMAIN` | Retoma la etiqueta tras guion |
| `DOMAIN_HYPHEN` | otro | `REJECT` | El guion no puede cerrar una etiqueta |
| `AFTER_DOMAIN_DOT` | letra o digito | `DOMAIN` | Inicia siguiente etiqueta del dominio |
| `AFTER_DOMAIN_DOT` | otro | `REJECT` | No pueden existir etiquetas vacias |

### Condiciones de cierre

Al agotar la entrada:
- Si no se vio `@`: `REJECT` — falta el separador obligatorio.
- Si estado es `AFTER_AT`, `AFTER_DOMAIN_DOT`, `DOMAIN_HYPHEN` o `LOCAL_SEPARATOR`: `REJECT` — cadena termina en estado incompleto.
- Si no se vio punto en el dominio: `REJECT` — el dominio debe tener al menos una etiqueta adicional.
- Si los ultimos caracteres de la ultima etiqueta tienen menos de 2 letras: `REJECT` — TLD invalido.
- En cualquier otro caso: `ACCEPT`.

---

## Validador de fecha

### Alfabeto

```
Σ = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, / }
```

### Estados

```
Q = { START, DAY_FIRST, AFTER_DAY, MONTH_FIRST, MONTH_SECOND, AFTER_MONTH,
      YEAR_1, YEAR_2, YEAR_3, YEAR_4, DATE_COMPLETE, ACCEPT, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }
```

### Funcion de transicion

| Estado actual | Simbolo leido | Estado siguiente | Nota |
|--------------|--------------|-----------------|------|
| `START` | digito | `DAY_FIRST` | Primer digito del dia |
| `START` | otro | `REJECT` | La fecha debe iniciar con digito |
| `DAY_FIRST` | digito | `AFTER_DAY` | Segundo digito del dia — dia completo |
| `DAY_FIRST` | otro | `REJECT` | El dia necesita dos digitos |
| `AFTER_DAY` | `/` | `MONTH_FIRST` | Separador correcto, inicia mes |
| `AFTER_DAY` | otro | `REJECT` | Solo se acepta `/` como separador |
| `MONTH_FIRST` | digito | `MONTH_SECOND` | Primer digito del mes |
| `MONTH_FIRST` | otro | `REJECT` | El mes debe iniciar con digito |
| `MONTH_SECOND` | digito | `AFTER_MONTH` | Segundo digito del mes — mes completo |
| `MONTH_SECOND` | otro | `REJECT` | El mes necesita dos digitos |
| `AFTER_MONTH` | `/` | `YEAR_1` | Separador correcto, inicia anio |
| `AFTER_MONTH` | otro | `REJECT` | Solo se acepta `/` como separador |
| `YEAR_1` | digito | `YEAR_2` | Primer digito del anio |
| `YEAR_1` | otro | `REJECT` | El anio debe iniciar con digito |
| `YEAR_2` | digito | `YEAR_3` | Segundo digito del anio |
| `YEAR_2` | otro | `REJECT` | El anio necesita cuatro digitos |
| `YEAR_3` | digito | `YEAR_4` | Tercer digito del anio |
| `YEAR_3` | otro | `REJECT` | El anio necesita cuatro digitos |
| `YEAR_4` | digito | `DATE_COMPLETE` | Cuarto digito del anio — estructura completa |
| `YEAR_4` | otro | `REJECT` | El anio necesita cuatro digitos |
| `DATE_COMPLETE` | cualquiera | `REJECT` | No se aceptan simbolos extra al final |

### Condiciones de cierre

Al agotar la entrada:
- Si estado no es `DATE_COMPLETE`: `REJECT` — la cadena termino antes de completar `DD/MM/YYYY`.
- Si mes `< 1` o `> 12`: `REJECT`.
- Si anio `< 1900` o `> 2100`: `REJECT`.
- Si dia `< 1` o `> max_dias_del_mes`: `REJECT`.
- Para febrero: si el anio no es bisiesto, el maximo es 28. Si es bisiesto, 29.
- Un anio es bisiesto si `(anio % 4 == 0 y anio % 100 != 0)` o `(anio % 400 == 0)`.
- En cualquier otro caso: `ACCEPT`.

### Nota sobre el modelo

El automata valida la forma (`DD/MM/YYYY`) caracter por caracter.
Las restricciones de rango y calendario (mes, dia, bisiesto) se evaluan despues del recorrido, sobre los valores numericos extraidos.
Esto corresponde a un AFD con verificacion semantica posterior: el automata acepta la sintaxis, y una capa adicional confirma el significado.

---

## Validador de placa vehicular

### Alfabeto

```
Σ = { A, B, ..., Z, 0, 1, ..., 9, - }
```

Solo letras mayusculas del rango A-Z. El guion `-` es separador opcional.

### Estados

```
Q = { START, L1, L2, L3, AFTER_L3, D1, D2, D3, AFTER_D3, L4, ACCEPT, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }
```

`ACCEPT` es alcanzable desde `D3` (carro, 6 chars) o desde `L4` (moto, 7 chars).

### Funcion de transicion

| Estado actual | Simbolo leido | Estado siguiente | Nota |
|--------------|--------------|-----------------|------|
| `START` | letra mayuscula | `L1` | Primera letra del bloque inicial |
| `START` | otro | `REJECT` | La placa debe iniciar con letra mayuscula |
| `L1` | letra mayuscula | `L2` | Segunda letra |
| `L1` | otro | `REJECT` | Se esperaba letra |
| `L2` | letra mayuscula | `L3` | Tercera letra |
| `L2` | otro | `REJECT` | Se esperaba letra |
| `L3` | `-` | `AFTER_L3` | Separador opcional entre letras y digitos |
| `L3` | digito | `D1` | Sin separador — primer digito directo |
| `L3` | otro | `REJECT` | Simbolo invalido despues de las tres letras |
| `AFTER_L3` | digito | `D1` | Primer digito despues del separador |
| `AFTER_L3` | otro | `REJECT` | El separador debe ir seguido de digito |
| `D1` | digito | `D2` | Segundo digito |
| `D1` | otro | `REJECT` | Se esperaba digito |
| `D2` | digito | `D3` | Tercer digito |
| `D2` | otro | `REJECT` | Se esperaba digito |
| `D3` | letra mayuscula | `L4` | Septima letra — indica placa de moto |
| `D3` | `-` | `AFTER_D3` | Separador antes de la letra de moto |
| `D3` | otro | `REJECT` | Simbolo inesperado despues del tercer digito |
| `AFTER_D3` | letra mayuscula | `L4` | Letra de moto despues del separador |
| `AFTER_D3` | otro | `REJECT` | El separador debe ir seguido de la letra de moto |
| `L4` | cualquiera | `REJECT` | La placa no puede tener caracteres extra |

### Condiciones de cierre

Al agotar la entrada:
- Si estado es `D3`: `ACCEPT` — placa de carro valida (`LLLDDD`).
- Si estado es `L4`: `ACCEPT` — placa de moto valida (`LLLDDDL`).
- Si estado es `D1` o `D2`: `REJECT` — faltan digitos.
- Si estado es `AFTER_D3`: `REJECT` — cadena termina en guion sin letra de moto.
- Si estado es `L1`, `L2`, `L3` o `AFTER_L3`: `REJECT` — cadena incompleta.

### Nota sobre el modelo

El mismo AFD acepta dos formatos de placa (carro y moto) con un unico conjunto de estados.
La distincion se hace al cierre: si el estado final es `D3` es carro; si es `L4` es moto.
El separador guion es absorbido por estados intermedios (`AFTER_L3`, `AFTER_D3`) y no afecta
el conteo de letras ni digitos, lo que mantiene el automata determinista y explicable en papel.

---

## Validador de contrasena segura

### Alfabeto

```
Σ = { a..z } ∪ { A..Z } ∪ { 0..9 } ∪ { !, @, #, $, %, &, *, -, _ }
```

Cualquier caracter fuera de este conjunto provoca rechazo inmediato.

### Estados

```
Q = { SCANNING, ACCEPT, REJECT }
```

El estado `SCANNING` es un estado aumentado: se le asocia un vector de banderas
`(length: int, has_upper: bool, has_lower: bool, has_digit: bool, has_special: bool)`.
Todas las banderas inician en `False` y `length` en 0.

### Estado inicial

```
q₀ = SCANNING
```

### Estados de aceptacion

```
F = { ACCEPT }
```

### Funcion de transicion

| Estado actual | Simbolo leido | Efecto sobre banderas | Estado siguiente |
|--------------|--------------|----------------------|-----------------|
| `SCANNING` | letra A-Z | activa `has_upper` si aun no estaba activa | `SCANNING` |
| `SCANNING` | letra a-z | activa `has_lower` si aun no estaba activa | `SCANNING` |
| `SCANNING` | digito 0-9 | activa `has_digit` si aun no estaba activa | `SCANNING` |
| `SCANNING` | simbolo del conjunto | activa `has_special` si aun no estaba activa | `SCANNING` |
| `SCANNING` | simbolo fuera del alfabeto | ninguno | `REJECT` (inmediato) |

En todos los casos validos, `length` se incrementa en 1 por cada simbolo consumido.

### Condiciones de cierre

Al agotar la entrada:
- Si `length >= 8` y las cuatro banderas son `True`: `ACCEPT`.
- Si cualquier condicion falla: `REJECT` con mensaje que lista todas las condiciones incumplidas.

### Nota sobre el modelo

Este automata es un **AFD aumentado con vector de banderas** (tambien llamado automata de conteo
o automata con memoria acotada). A diferencia de un AFD puro, el estado efectivo es el producto
cartesiano `SCANNING × {True,False}⁴ × ℕ`, lo que lo hace formalmente un AFD con un numero
finito de estados (acotado por la longitud maxima practica de la contrasena).

La traza registra cada activacion de bandera, lo que permite explicar paso a paso por que
una contrasena es aceptada o rechazada durante la sustentacion oral.

La contrasena **no se integra al scanner de texto libre** porque no tiene delimitadores
reconocibles en texto corriente — cualquier secuencia de caracteres podria ser una contrasena,
lo que generaria falsos positivos masivos. Es un dato de entrada atomico validado exclusivamente
en formularios interactivos (Parte B del proyecto).
