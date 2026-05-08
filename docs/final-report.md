# Proyecto: Busqueda y Validacion de Patrones en Textos y Sistemas Interactivos

**Asignatura:** Teoria de Lenguajes Formales
**Programa:** Ingenieria de Sistemas
**Fecha:** Mayo 2026

---

## 1. Objetivo General

Desarrollar una aplicacion en Python que permita detectar y validar patrones dentro
de textos mediante automatas finitos deterministas (AFD) implementados manualmente,
sin el uso de librerias de expresiones regulares predefinidas, y verificar la entrada
de datos en interfaces interactivas garantizando que cumplan con criterios sintacticos
y estructurales previamente definidos.

---

## 2. Descripcion del Proyecto

El proyecto implementa siete validadores formales basados en AFDs explicables en papel,
un scanner de texto libre que los orquesta sin usar expresiones regulares, y una
interfaz interactiva con formularios de validacion en tiempo real.

**Parte A — Busqueda en texto libre:** el scanner recorre texto caracter por caracter,
intentando cada patron en orden de prioridad (fecha > correo > url > telefono > nit >
placa). Cada patron es validado por su AFD correspondiente.

**Parte B — Validacion en formularios:** la interfaz grafica (Tkinter) expone campos
para telefono, correo, fecha, placa, contraseña y NIT, con validacion en tiempo real
o antes del envio.

**Principio central:** ningun modulo usa `re`, `regex` ni metodos de la libreria
estandar para clasificar caracteres (`isdigit()`, `isupper()`, etc.). Toda
clasificacion proviene de `src/core/symbol_classifier.py`.

---

## 3. Arquitectura del Proyecto

```
src/
  core/
    automaton.py         -- TraceableAutomaton: base de todos los AFDs
    result.py            -- ValidationResult: tipo uniforme de resultado
    symbol_classifier.py -- Fuente unica de clasificacion de caracteres
  patterns/
    phone_validator.py   -- AFD telefono (10-13 digitos)
    email_validator.py   -- AFD correo (local@dominio.tld)
    date_validator.py    -- AFD fecha (DD/MM/YYYY)
    plate_validator.py   -- AFD placa (LLLDDD / LLLDDDL)
    password_validator.py-- AFD aumentado contrasena (flags + longitud)
    url_validator.py     -- AFD url (http/https://dominio/ruta)
    nit_validator.py     -- AFD nit (NNN.NNN.NNN-D)
    text_scanner.py      -- Scanner sin regex
  ui/
    app.py               -- Aplicacion Tkinter (Parte B)
    forms.py             -- Formularios con validacion en tiempo real
  main.py                -- CLI: scan y validate
tests/                   -- 115 pruebas unitarias, todas pasando
docs/                    -- Documentacion formal del proyecto
```

### Componentes del nucleo

**`TraceableAutomaton`** registra cada transicion en una lista `trace`, lleva un
contador `consumed` de simbolos procesados y un campo `state` con el estado actual.
El metodo `record(symbol, next_state, note)` siempre incrementa `consumed`. El metodo
`finish(next_state, note)` registra el cierre sin incrementar `consumed`.

**`ValidationResult`** estandariza la salida de todos los validadores: `accepted`,
`consumed`, `message`, `trace` y `normalized`. Los factory methods `accept()` y
`reject()` garantizan que ningun validador construya el resultado manualmente.

**`symbol_classifier`** expone seis funciones puras: `is_letter`, `is_digit`,
`is_alphanumeric`, `is_upper_letter`, `is_lower_letter`. Ninguna usa metodos de
`str` de Python; todas usan comparaciones de rango ASCII.

---

## 4. Desarrollo — Validadores

### 4.1 Validador de Telefono

**Patron reconocido:** numero telefonico con 10 a 13 digitos reales, prefijo
internacional `+` opcional, separadores ` ` o `-` entre bloques.

**AFD:**
```
Σ = { 0-9, +, -, ' ' }
Q = { START, AFTER_PLUS, IN_NUMBER, AFTER_SEPARATOR }
q₀ = START
Aceptacion al cierre: estado ≠ AFTER_SEPARATOR AND 10 ≤ digitos ≤ 13
```

**Algoritmo:** el automata cuenta digitos reales en una variable `digits` que solo
se incrementa al transitar a o permanecer en `IN_NUMBER` con un digito. Los separadores
no cuentan. La condicion de longitud se evalua al agotar la entrada.

**Justificacion de reglas:**

- *Separadores no consecutivos:* `AFTER_SEPARATOR` solo acepta digito. Un segundo
  separador transita a `REJECT` de forma determinista.
- *No termina en separador:* si la cadena se agota en `AFTER_SEPARATOR`, el cierre
  detecta este estado y rechaza. No se requiere lookahead.
- *Longitud valida:* `digits < 10 OR digits > 13` cubre el rango internacional real
  (Colombia: 10 digitos locales; con prefijo +57: 12 digitos).

**Tests clave que verifican el algoritmo:**

```
3001234567         → ACCEPT  (10 digitos exactos — limite inferior)
300 123 4567       → ACCEPT  (separadores espacio validos)
+573001234567      → ACCEPT  (prefijo + 12 digitos)
3001234567890      → ACCEPT  (13 digitos — limite superior)
30012345678901     → REJECT  (14 digitos — excede limite)
300--1234567       → REJECT  (separadores consecutivos)
3001234-           → REJECT  (termina en separador)
+ 3001234567       → REJECT  (espacio despues de +, AFTER_PLUS rechaza no-digito)
```

---

### 4.2 Validador de Correo Electronico

**Patron reconocido:** `local@dominio.tld` con separadores internos en la parte local
y TLD de al menos 2 letras.

**AFD:**
```
Σ = { a-z, A-Z, 0-9, ., _, -, @ }
Q = { START, LOCAL, LOCAL_SEPARATOR, AFTER_AT, DOMAIN, DOMAIN_HYPHEN, AFTER_DOMAIN_DOT }
q₀ = START
Aceptacion al cierre: saw_at AND saw_domain_dot AND tld_letters ≥ 2
  AND estado ∉ {AFTER_AT, AFTER_DOMAIN_DOT, DOMAIN_HYPHEN, LOCAL_SEPARATOR}
```

**Algoritmo:** cuatro variables de contexto complementan el estado del automata:
`saw_at_symbol` (se vio `@`), `saw_domain_dot` (el dominio tiene punto), y
`tld_letters` (contador de letras consecutivas al final del dominio).

**Justificacion de reglas:**

- *Parte local no inicia con separador:* `START` solo acepta `is_alphanumeric`. Un
  punto o guion al inicio transita a `REJECT` sin excepcion.
- *Sin separadores consecutivos:* `LOCAL_SEPARATOR` exige `is_alphanumeric` en el
  proximo simbolo. `.` o `_` consecutivos van a `REJECT`.
- *TLD minimo 2 letras:* `tld_letters` se reinicia a 0 con cada guion o punto. Al
  cierre, `tld_letters < 2` rechaza TLDs de una sola letra como `.c` o `.1`.
- *Dominio con punto:* `saw_domain_dot` solo se activa en `DOMAIN --[.]--> AFTER_DOMAIN_DOT`.
  Un dominio sin punto (como `usuario@localhost`) es rechazado.

**Tests clave:**

```
usuario@example.com          → ACCEPT
user.name-test_1@sub.dom.com → ACCEPT  (separadores multiples validos)
a@b.co                       → ACCEPT  (minimo valido)
.usuario@example.com         → REJECT  (inicia con separador)
user..name@example.com       → REJECT  (separadores consecutivos)
usuario@example.c1           → REJECT  (TLD termina en digito)
usuario@example-.com         → REJECT  (guion al final de etiqueta)
a@b.c                        → REJECT  (TLD de 1 letra)
```

---

### 4.3 Validador de Fecha

**Patron reconocido:** `DD/MM/YYYY` con dia, mes y anio en rangos validos, incluyendo
anio bisiesto gregoriano y limite de rango 1900-2100.

**AFD:**
```
Σ = { 0-9, / }
Q = { START, DAY_FIRST, AFTER_DAY, MONTH_FIRST, MONTH_SECOND, AFTER_MONTH,
      YEAR_1, YEAR_2, YEAR_3, YEAR_4, DATE_COMPLETE }
q₀ = START
Aceptacion al cierre: estado == DATE_COMPLETE AND rangos_validos
```

**Algoritmo en dos capas:**

*Capa 1 — sintactica (AFD):* verifica la forma `DD/MM/YYYY` caracter por caracter.
Los estados son estrictamente lineales (sin bifurcacion). Si la estructura es correcta,
el automata llega a `DATE_COMPLETE`.

*Capa 2 — semantica (post-recorrido):* sobre los valores numericos extraidos de
posiciones fijas en la cadena original (`text[0:2]`, `text[3:5]`, `text[6:10]`) se
verifican:
```
1 ≤ mes ≤ 12
1900 ≤ anio ≤ 2100
1 ≤ dia ≤ max_dias(mes, anio)
```

**Regla de anio bisiesto:**
```
bisiesto(y) = (y % 4 == 0 AND y % 100 != 0) OR (y % 400 == 0)
```

**Justificacion:**

- *Separacion sintaxis/semantica:* el AFD garantiza que la cadena tiene exactamente
  10 caracteres con `/` en posiciones 2 y 5. Luego la capa semantica extrae los
  valores numericos con certeza de que son exactamente 2, 2 y 4 digitos.
- *`DATE_COMPLETE` rechaza extra:* la transicion `DATE_COMPLETE --[cualquiera]--> REJECT`
  es total sobre todo el alfabeto, bloqueando cadenas como `15/08/2024x`.
- *1900 no bisiesto:* `1900 % 4 == 0` (True) AND `1900 % 100 != 0` (False) → primer
  termino False. `1900 % 400 == 0` (False) → segundo termino False. Resultado: no bisiesto.

**Tests clave:**

```
15/08/2024   → ACCEPT  (estandar)
29/02/2024   → ACCEPT  (2024 es bisiesto)
29/02/2000   → ACCEPT  (2000 divisible entre 400)
28/02/1900   → ACCEPT  (1900 no bisiesto — max dia = 28)
29/02/1900   → REJECT  (confirma que 1900 no es bisiesto)
29/02/2023   → REJECT  (2023 no bisiesto)
31/04/2024   → REJECT  (abril tiene 30 dias)
15/13/2024   → REJECT  (mes 13 no existe)
15/08/2024x  → REJECT  (simbolo extra — DATE_COMPLETE rechaza)
```

---

### 4.4 Validador de Placa Vehicular

**Patron reconocido:** placa colombiana en formato carro (`LLLDDD` o `LLL-DDD`) o
moto (`LLLDDDL` o `LLL-DDDL`). Solo letras mayusculas A-Z y digitos 0-9.

**AFD:**
```
Σ = { A-Z, 0-9, - }
Q = { START, L1, L2, L3, AFTER_L3, D1, D2, D3, AFTER_D3, L4 }
q₀ = START
Aceptacion al cierre: estado == D3 (carro) OR estado == L4 (moto)
```

**Algoritmo:** el mismo AFD distingue los dos formatos en el estado de cierre. El
guion es absorbido por estados intermedios (`AFTER_L3`, `AFTER_D3`) que no contribuyen
a la cadena normalizada. `is_upper_letter` garantiza que solo letras A-Z son aceptadas.

**Justificacion:**

- *Letras minusculas rechazadas:* `is_upper_letter(s)` = `is_letter(s) AND "A" ≤ s ≤ "Z"`.
  Las minusculas pasan `is_letter` pero fallan el rango. No hay caso especial.
- *Guion no suma al normalized:* el guion transita a `AFTER_L3` o `AFTER_D3` sin
  appendear el simbolo al arreglo `normalized`. La cadena normalizada es siempre `ABC123`.
- *Un solo AFD para dos formatos:* `D3` es bifurcacion natural. Desde `D3`, una letra
  mayuscula va a `L4` (moto); agotar la entrada en `D3` es aceptacion de carro.

**Tests clave:**

```
ABC123   → ACCEPT  (carro sin guion)
ABC-123  → ACCEPT  (carro con guion, normalized="ABC123")
XYZ456A  → ACCEPT  (moto sin guion)
XYZ-456A → ACCEPT  (moto con guion)
abc123   → REJECT  (letras minusculas)
AB123    → REJECT  (solo 2 letras)
ABC12    → REJECT  (solo 2 digitos — termina en D2)
ABC123-  → REJECT  (guion final — termina en AFTER_D3)
ABC--123 → REJECT  (doble guion — AFTER_L3 rechaza segundo -)
```

---

### 4.5 Validador de Contrasena Segura

**Patron reconocido:** cadena de longitud minima 8 con al menos una letra mayuscula,
una minuscula, un digito y un simbolo del conjunto `! @ # $ % & * - _`.

**AFD aumentado con vector de banderas:**
```
Σ = { a-z } ∪ { A-Z } ∪ { 0-9 } ∪ { !, @, #, $, %, &, *, -, _ }
Q_efectivo = SCANNING × {True,False}⁴ × ℕ
q₀ = (SCANNING, False, False, False, False, 0)
Aceptacion al cierre: length ≥ 8 AND todas las banderas True
```

**Algoritmo:** en un unico pase, el automata activa cada bandera la primera vez que
encuentra el tipo de caracter correspondiente. Al agotar la entrada, evalua
simultaneamente longitud y banderas. Si cualquier condicion falla, el mensaje de
rechazo lista especificamente cuales condiciones no se cumplieron.

**Justificacion:**

- *Rechazo inmediato por caracter invalido:* un simbolo fuera de Σ transita a `REJECT`
  sin continuar. Esto es formalmente correcto: la contrasena completa es invalida si
  contiene simbolos no permitidos.
- *Mensaje de rechazo enumerativo:* `_build_rejection_message` evalua independientemente
  cada condicion y lista todas las que fallaron. Esto cumple el requisito del documento
  de "emitir mensajes adecuados cuando se detecten errores".
- *Privacy en normalized:* el campo `normalized` es siempre `""`. La contrasena no
  debe ser reproducida en ningun campo de salida.

**Por que no se integra al scanner:** no existe un delimitador natural para contrasenas
en texto libre. La validacion aplica solo en formularios donde el campo es atomico.

**Tests clave:**

```
Secure@1     → ACCEPT  (exactamente 8 chars, todas las banderas)
Abcde@1z     → ACCEPT  (limite inferior de longitud)
Ab1@         → REJECT  (4 chars — longitud insuficiente)
Abc@1zX      → REJECT  (7 chars — todas las banderas pero longitud insuficiente)
secure@1abc  → REJECT  (sin mayuscula)
SecurePass1  → REJECT  (sin simbolo especial)
Secure^1ab   → REJECT  (^ fuera del alfabeto — rechazo inmediato)
abcdefgh     → REJECT  (8 chars pero sin mayuscula, digito ni simbolo)
```

---

### 4.6 Validador de URL

**Patron reconocido:** URL con protocolo `http` o `https` (case insensitive), dominio
con al menos un punto, y ruta/query/fragmento opcionales.

**AFD:**
```
Σ = { a-z, A-Z, 0-9, :, /, ., -, _, ?, =, &, #, ~, %, +, @ }
Q = { START, PROTO_H, PROTO_HT, PROTO_HTT, PROTO_HTTP, PROTO_HTTPS,
      COLON, SLASH1, SLASH2, DOMAIN, DOMAIN_HYPHEN, DOMAIN_DOT, PATH }
q₀ = START
Aceptacion al cierre:
  (estado == DOMAIN AND saw_domain_dot) OR estado == PATH
```

**Algoritmo:** los estados `PROTO_*` reconocen el protocolo como una cadena fija de
prefijo. `DOMAIN` y sus estados auxiliares validan el dominio con la misma logica que
el validador de correo para la parte del dominio. `PATH` acepta todos los caracteres
URL validos en la ruta.

**Justificacion:**

- *Protocolo case insensitive:* las transiciones comprueban `symbol in {"h","H"}`,
  `symbol in {"t","T"}`, etc. No se usa `.lower()` para evitar crear nuevos objetos
  string; las comparaciones de conjunto son O(1).
- *Dominio con punto obligatorio:* `saw_domain_dot` cumple la misma funcion que en el
  validador de correo. Solo se activa en `DOMAIN_DOT --[letra/digito]--> DOMAIN`.
- *PATH acepta amplio conjunto:* incluye `/`, `?`, `=`, `&`, `#`, `~`, `%`, `+`, `@`,
  cubriendo rutas REST, query strings y autenticacion basica.
- *Limpieza en scanner:* `.rstrip(".,!)")` elimina puntuacion de oracion antes de
  intentar la validacion, evitando falsos negativos por punto final de oración.

**Tests clave:**

```
http://example.com              → ACCEPT
https://www.google.com          → ACCEPT
https://example.com/search?q=x → ACCEPT  (ruta + query)
HTTP://example.com              → ACCEPT  (mayusculas en protocolo)
ftp://example.com               → REJECT  (protocolo invalido)
http://example                  → REJECT  (sin punto en dominio)
http://example-.com             → REJECT  (dominio termina en guion)
http://.example.com             → REJECT  (dominio inicia con punto)
```

---

### 4.7 Validador de NIT

**Patron reconocido:** Numero de Identificacion Tributaria colombiano con formato
exacto `NNN.NNN.NNN-D`.

**AFD:**
```
Σ = { 0-9, ., - }
Q = { START, D1, D2, D3, DOT1, D4, D5, D6, DOT2, D7, D8, D9, HYPHEN, CHECK }
q₀ = START
Aceptacion al cierre: estado == CHECK
```

**Algoritmo:** el camino de aceptacion es completamente lineal — 13 transiciones en
secuencia sin bifurcacion. Cada estado acepta exactamente un tipo de simbolo. Es el
AFD mas simple del proyecto y el mas trazable en cuaderno.

**Justificacion:**

- *Formato fijo como ventaja:* el NIT siempre tiene 13 caracteres con separadores en
  posiciones fijas (4 y 8). El AFD lineal garantiza exactamente eso sin contadores ni
  variables adicionales.
- *Normalizacion sin separadores:* `digits` acumula solo los 10 digitos reales (9 del
  NIT + 1 verificador). La cadena normalizada `"9001234567"` es util para busquedas en
  bases de datos que almacenan NITs sin formato.
- *Sin colision con otros patrones:* el NIT usa `.` como separador, lo que lo distingue
  del telefono (usa ` ` y `-`), la fecha (usa `/`) y el correo (requiere `@`).

**Tests clave:**

```
900.123.456-7  → ACCEPT  (formato completo)
000.000.000-0  → ACCEPT  (digitos minimos)
900123456-7    → REJECT  (sin puntos — D3 espera `.`)
900.123.4567   → REJECT  (sin guion — D9 espera `-`)
9AB.123.456-7  → REJECT  (letras en grupo)
900.123.456-77 → REJECT  (doble verificador — CHECK rechaza extra)
90.123.456-7   → REJECT  (grupo de 2 digitos — D2 espera digito, recibe `.`)
```

---

## 5. Scanner de Texto Libre

### Funcionamiento

```python
for i in range(len(texto)):
    match = (
        _try_date(text, i)
        or _try_email(text, i)
        or _try_url(text, i)
        or _try_phone(text, i)
        or _try_nit(text, i)
        or _try_plate(text, i)
    )
    if match:
        matches.append(match)
        i = match.end  # avanza despues de la coincidencia
    else:
        i += 1         # avanza un caracter
```

Cada `_try_*` colecta un candidato con `_collect` (acumula mientras el predicado
de caracteres se cumpla), aplica limpieza de puntuacion de oracion, y llama al
validador del patron. Si el resultado es aceptado, retorna un `PatternMatch`.

### Orden de prioridad y por que es correcto

| Posicion | Patron | Condicion de inicio | Conflicto evitado |
|----------|--------|--------------------|--------------------|
| 1 | fecha | digito | La fecha tiene formato fijo de 10 chars con `/` — no confundible con telefono |
| 2 | email | alfanumerico | El `@` es el discriminador principal |
| 3 | url | `h` o `H` | Email tiene prioridad; URL solo llega si email falla |
| 4 | telefono | digito o `+` | La fecha ya fue intentada y rechazada |
| 5 | nit | digito | El telefono falla en NIT (el `.` no es char de telefono) |
| 6 | placa | letra mayuscula | Unico patron que empieza con mayuscula |

---

## 6. Pruebas y Casos de Uso

El proyecto cuenta con **115 pruebas unitarias** distribuidas en 7 archivos:

| Archivo | Pruebas | Cobertura principal |
|---------|---------|---------------------|
| `test_phone_validator.py` | 5 | Estructura + longitud + separadores |
| `test_email_validator.py` | 7 | Estructura + TLD + dominio |
| `test_date_validator.py` | 9 | Estructura + rangos + bisiesto |
| `test_plate_validator.py` | 17 | Carro + moto + guion + errores |
| `test_password_validator.py` | 14 | Banderas + longitud + alfabeto |
| `test_url_validator.py` | 22 | Protocolo + dominio + ruta + query |
| `test_nit_validator.py` | 16 | Grupos + separadores + verificador |
| `test_text_scanner.py` | 25 | Todos los patrones en texto + prioridad |

Todos los tests se ejecutan con `python3 -m pytest tests/ -q` y pasan en menos de 0.2s.

### Criterio de diseño de los casos de prueba

Cada conjunto de pruebas cubre tres categorias:

1. **Validos:** cadenas que deben ser aceptadas — verifican el camino feliz del AFD.
2. **Invalidos:** cadenas que violan exactamente una regla — verifican que el AFD rechaza
   correctamente en el estado adecuado.
3. **Borde:** cadenas en el limite de lo aceptable — verifican que los rangos son exactos
   (longitud minima, longitud maxima, fecha limite de calendario, etc.).

### Ejemplo de traza de aceptacion — telefono `3001234567`

```
START   --['3']--> IN_NUMBER: Empieza la secuencia principal de digitos.
IN_NUMBER --['0']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['0']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['1']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['2']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['3']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['4']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['5']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['6']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --['7']--> IN_NUMBER: Se acumula un nuevo digito del telefono.
IN_NUMBER --[END]--> ACCEPT: telefono valido con 10 digitos.
```

### Ejemplo de traza de rechazo — telefono `300--1234567`

```
START     --['3']--> IN_NUMBER: Empieza la secuencia.
IN_NUMBER --['0']--> IN_NUMBER: digito.
IN_NUMBER --['0']--> IN_NUMBER: digito.
IN_NUMBER --['-']--> AFTER_SEPARATOR: Se separan bloques numericos.
AFTER_SEPARATOR --['-']--> REJECT: No se permiten separadores consecutivos.
```

---

## 7. Conclusiones

1. **Los AFDs implementados son formalmente correctos:** cada validador tiene estados
   explícitos, alfabeto finito, funcion de transicion determinista y condicion de
   aceptacion verificable. Todos pueden dibujarse en cuaderno como grafos de transicion.

2. **El recorrido caracter por caracter es suficiente:** ninguno de los siete patrones
   requiere retroceso ni lookahead. El telefono fue corregido durante el proyecto para
   eliminar un lookahead que usaba `index == len(text) - 1`; la version final verifica
   el estado `AFTER_SEPARATOR` al cierre.

3. **La separacion de responsabilidades simplifica el mantenimiento:** el nucleo
   (`automaton`, `result`, `symbol_classifier`) es independiente de los patrones.
   Agregar un nuevo validador solo requiere crear un archivo en `src/patterns/` e
   importarlo en el scanner y en el CLI.

4. **Las 115 pruebas validan las reglas formales:** cada test corresponde a una regla
   del AFD — no son pruebas arbitrarias sino verificaciones precisas de transiciones
   y condiciones de cierre.

5. **El scanner sin regex demuestra que los AFDs son el mecanismo subyacente de los
   patrones:** la implementacion manual hace visible lo que las librerias de expresiones
   regulares esconden.

---

## 8. Guia de Uso

### Requisitos

```
Python 3.11 o superior
pytest (para correr los tests)
```

### Instalacion

```bash
git clone https://github.com/lyc4nthrope/ProyectoFinal_TLF.git
cd ProyectoFinal_TLF
```

### Ejecutar los tests

```bash
python3 -m pytest tests/ -q
```

### Subcomando `scan` — buscar patrones en texto libre

```bash
python3 -m src.main scan "Texto con patrones a detectar"
```

Ejemplos:

```bash
python3 -m src.main scan "Llama al 3001234567 o escribe a user@example.com"
# [phone] start=9 end=19 raw='3001234567' normalized='3001234567'
# [email] start=33 end=51 raw='user@example.com' normalized='user@example.com'

python3 -m src.main scan "Web: https://example.com NIT: 900.123.456-7"
# [url] start=5 end=24 raw='https://example.com' normalized='https://example.com'
# [nit] start=30 end=43 raw='900.123.456-7' normalized='9001234567'

python3 -m src.main scan "Reunion el 15/08/2024. Placa ABC-123."
# [date] start=11 end=21 raw='15/08/2024' normalized='15/08/2024'
# [plate] start=30 end=37 raw='ABC-123' normalized='ABC123'
```

### Subcomando `validate` — validar una cadena especifica

```bash
python3 -m src.main validate <tipo> "<cadena>"
```

Tipos disponibles: `phone`, `email`, `date`, `plate`, `password`, `url`, `nit`

Ejemplos:

```bash
python3 -m src.main validate phone "3001234567"
# aceptado: True
# mensaje:  Telefono valido.
# traza: ...

python3 -m src.main validate date "29/02/2023"
# aceptado: False
# mensaje:  El dia de la fecha es invalido para el mes dado.

python3 -m src.main validate password "Secure@1"
# aceptado: True
# mensaje:  Contrasena valida.

python3 -m src.main validate nit "900.123.456-7"
# aceptado: True
# mensaje:  NIT valido.
```
