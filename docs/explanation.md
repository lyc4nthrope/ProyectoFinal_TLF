# Explanation — Descripcion formal de los automatas

Descripcion rigurosa de los siete automatas implementados en el proyecto.
Cada validador modela un Automata Finito Determinista (AFD) explicable en papel:
estados explícitos, alfabeto finito, función de transicion total y condicion de aceptacion
verificable al agotar la entrada.

---

## Modelo comun a todos los validadores

Cada validador implementa un AFD con la quíntupla:

```
M = (Q, Σ, δ, q₀, F)
```

| Componente | Significado |
|------------|-------------|
| Q | Conjunto finito de estados |
| Σ | Alfabeto finito de simbolos permitidos |
| δ: Q × Σ → Q | Funcion de transicion determinista |
| q₀ ∈ Q | Estado inicial |
| F ⊆ Q | Conjunto de estados de aceptacion |

**Principios de implementacion que garantizan la trazabilidad en cuaderno:**

- La funcion `δ` nunca lee mas de un simbolo a la vez (sin lookahead).
- El estado `REJECT` es un estado trampa: ninguna transicion posterior lo abandona.
- La aceptacion o rechazo final se decide al agotar la entrada (condicion de cierre).
- Ningun validador usa librerias de expresiones regulares ni metodos de clasificacion
  de la libreria estandar (`isdigit`, `isupper`, etc.).
- Toda clasificacion de simbolos se delega a `src/core/symbol_classifier.py`.

---

## 1. Validador de Telefono

### Descripcion

Acepta numeros telefonicos con 10 a 13 digitos reales, prefijo internacional `+`
opcional al inicio, y separadores ` ` o `-` entre bloques numericos.

### Alfabeto

```
Σ = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, +, -, ' ' }
```

### Estados

```
Q = { START, AFTER_PLUS, IN_NUMBER, AFTER_SEPARATOR, REJECT }
```

No existe estado `ACCEPT` dentro del recorrido. La aceptacion se decide al cierre
segun el estado final y el conteo de digitos reales.

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }  (estado virtual determinado al cierre)
```

La cadena se acepta solo si al agotar la entrada se cumplen TODAS:
- Estado no es `AFTER_SEPARATOR` (no puede terminar en separador).
- `10 ≤ digitos_reales ≤ 13`.

### Funcion de transicion δ — tabla completa

| Estado actual | Simbolo | Estado siguiente | Accion adicional |
|---------------|---------|-----------------|-----------------|
| `START` | digito | `IN_NUMBER` | digitos += 1 |
| `START` | `+` | `AFTER_PLUS` | — |
| `START` | otro | `REJECT` | — |
| `AFTER_PLUS` | digito | `IN_NUMBER` | digitos += 1 |
| `AFTER_PLUS` | otro | `REJECT` | — |
| `IN_NUMBER` | digito | `IN_NUMBER` | digitos += 1 |
| `IN_NUMBER` | `-` o ` ` | `AFTER_SEPARATOR` | — |
| `IN_NUMBER` | otro | `REJECT` | — |
| `AFTER_SEPARATOR` | digito | `IN_NUMBER` | digitos += 1 |
| `AFTER_SEPARATOR` | `-` o ` ` | `REJECT` | separadores consecutivos |
| `AFTER_SEPARATOR` | otro | `REJECT` | — |

### Condiciones de cierre

Al agotar la entrada, en orden de evaluacion:

```
si estado == AFTER_SEPARATOR → REJECT  (cadena termina en separador)
si digitos < 10 o digitos > 13  → REJECT  (longitud invalida)
en cualquier otro caso          → ACCEPT
```

### Justificacion formal

**Determinismo:** para cada par (estado, simbolo) existe exactamente un estado siguiente.
Los simbolos `-` y ` ` se clasifican por el mismo predicado `_is_phone_separator`, por lo
que no hay ambiguedad de transicion.

**Correctitud de la regla de separadores:**
`AFTER_SEPARATOR` rechaza todo simbolo que no sea digito. Si la cadena termina en
`AFTER_SEPARATOR`, el cierre rechaza sin lookahead (no se necesita verificar el indice
del caracter actual).

**Correctitud del conteo:** el contador `digits` solo se incrementa cuando el automata
transita desde `IN_NUMBER --[digito]--> IN_NUMBER` o cuando entra a `IN_NUMBER` desde
`START` o `AFTER_PLUS`. Los separadores nunca incrementan el contador. Esto garantiza
que `digits` refleja exactamente los digitos reales de la cadena.

**Cobertura de tests que verifican cada regla:**

| Regla | Test que la verifica |
|-------|---------------------|
| 10 digitos validos | `test_finds_phone_in_text` — `3001234567` |
| Prefijo + | `test_finds_international_phone` — `+57 300-123-4567` |
| Separadores validos | casos validos con `-` y ` ` en `test_phone_validator.py` |
| Separadores consecutivos | invalido `300--1234567` |
| Termina en separador | invalido `3001234-` |
| Menos de 10 digitos | invalido `12345`, borde `300 ` |
| Mas de 13 digitos | borde `30012345678901` |

---

## 2. Validador de Correo Electronico

### Descripcion

Acepta correos con formato `local@dominio.tld`, donde la parte local puede contener
letras, digitos y separadores internos (`.`, `_`, `-`), el dominio tiene etiquetas
separadas por punto con guiones internos opcionales, y el TLD tiene al menos 2 letras.

### Alfabeto

```
Σ = { a-z, A-Z, 0-9, ., _, -, @ }
```

### Estados

```
Q = { START, LOCAL, LOCAL_SEPARATOR, AFTER_AT, DOMAIN, DOMAIN_HYPHEN,
      AFTER_DOMAIN_DOT, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }  (estado virtual determinado al cierre)
```

### Funcion de transicion δ — tabla completa

| Estado actual | Simbolo | Estado siguiente | Accion adicional |
|---------------|---------|-----------------|-----------------|
| `START` | letra o digito | `LOCAL` | — |
| `START` | otro | `REJECT` | — |
| `LOCAL` | letra o digito | `LOCAL` | — |
| `LOCAL` | `.`, `_`, `-` | `LOCAL_SEPARATOR` | — |
| `LOCAL` | `@` | `AFTER_AT` | saw_at = True |
| `LOCAL` | otro | `REJECT` | — |
| `LOCAL_SEPARATOR` | letra o digito | `LOCAL` | — |
| `LOCAL_SEPARATOR` | otro | `REJECT` | sep. consecutivo o al final |
| `AFTER_AT` | letra o digito | `DOMAIN` | tld_letters = 1 si letra |
| `AFTER_AT` | otro | `REJECT` | — |
| `DOMAIN` | letra o digito | `DOMAIN` | tld_letters = cont+1 o 0 |
| `DOMAIN` | `-` | `DOMAIN_HYPHEN` | tld_letters = 0 |
| `DOMAIN` | `.` | `AFTER_DOMAIN_DOT` | saw_dot = True; tld_letters = 0 |
| `DOMAIN` | otro | `REJECT` | — |
| `DOMAIN_HYPHEN` | letra o digito | `DOMAIN` | tld_letters = 1 si letra |
| `DOMAIN_HYPHEN` | otro | `REJECT` | guion al final de etiqueta |
| `AFTER_DOMAIN_DOT` | letra o digito | `DOMAIN` | tld_letters = 1 si letra; saw_dot=True |
| `AFTER_DOMAIN_DOT` | otro | `REJECT` | etiqueta vacia |

### Condiciones de cierre

```
si not saw_at                                          → REJECT
si estado ∈ {AFTER_AT, AFTER_DOMAIN_DOT,
              DOMAIN_HYPHEN, LOCAL_SEPARATOR}          → REJECT
si not saw_domain_dot                                  → REJECT
si tld_letters < 2                                     → REJECT
en cualquier otro caso                                 → ACCEPT
```

### Justificacion formal

**Por que `tld_letters` es correcto:** el contador se reinicia a 0 cada vez que aparece
un guion o un punto dentro del dominio. Solo cuenta letras consecutivas al final de la
ultima etiqueta. Un TLD como `.c1` termina con un digito, lo que pone `tld_letters = 0`
al procesar `1`. El cierre detecta `tld_letters < 2` y rechaza.

**Por que los separadores consecutivos se rechazan:** desde `LOCAL_SEPARATOR`, cualquier
simbolo que no sea letra o digito transita a `REJECT`. Eso incluye `.`, `_`, `-`, y `@`.
No es posible formar `user..name` ni `user.@dom`.

**Por que el dominio sin punto se rechaza:** `saw_domain_dot` solo se activa en la
transicion `DOMAIN --[.]--> AFTER_DOMAIN_DOT`. Si esa transicion nunca ocurre,
el cierre detecta `saw_domain_dot = False` y rechaza.

**Cobertura de tests:**

| Regla | Test que la verifica |
|-------|---------------------|
| Estructura basica | `usuario@example.com` |
| Separadores locales | `user.name-test_1@sub.domain.com` |
| TLD minimo 2 letras | invalido `usuario@example.c1` |
| Dominio sin punto | invalido `usuario@example` → `a@b` rechazado |
| Empieza con sep. local | invalido `.usuario@example.com` |
| Sep. consecutivos | invalido `user..name@example.com` |
| Guion final dominio | invalido `usuario@example-.com` |

---

## 3. Validador de Fecha

### Descripcion

Acepta fechas con formato estricto `DD/MM/YYYY`. La estructura se valida caracter
por caracter con estados lineales. Luego se aplica una capa semantica que verifica
rangos de dia, mes, anio y el calculo de anio bisiesto.

### Alfabeto

```
Σ = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, / }
```

### Estados

```
Q = { START, DAY_FIRST, AFTER_DAY, MONTH_FIRST, MONTH_SECOND, AFTER_MONTH,
      YEAR_1, YEAR_2, YEAR_3, YEAR_4, DATE_COMPLETE, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }  (estado virtual determinado al cierre tras validacion semantica)
```

### Funcion de transicion δ — tabla completa

| Estado actual | Simbolo | Estado siguiente |
|---------------|---------|-----------------|
| `START` | digito | `DAY_FIRST` |
| `START` | otro | `REJECT` |
| `DAY_FIRST` | digito | `AFTER_DAY` |
| `DAY_FIRST` | otro | `REJECT` |
| `AFTER_DAY` | `/` | `MONTH_FIRST` |
| `AFTER_DAY` | otro | `REJECT` |
| `MONTH_FIRST` | digito | `MONTH_SECOND` |
| `MONTH_FIRST` | otro | `REJECT` |
| `MONTH_SECOND` | digito | `AFTER_MONTH` |
| `MONTH_SECOND` | otro | `REJECT` |
| `AFTER_MONTH` | `/` | `YEAR_1` |
| `AFTER_MONTH` | otro | `REJECT` |
| `YEAR_1` | digito | `YEAR_2` |
| `YEAR_1` | otro | `REJECT` |
| `YEAR_2` | digito | `YEAR_3` |
| `YEAR_2` | otro | `REJECT` |
| `YEAR_3` | digito | `YEAR_4` |
| `YEAR_3` | otro | `REJECT` |
| `YEAR_4` | digito | `DATE_COMPLETE` |
| `YEAR_4` | otro | `REJECT` |
| `DATE_COMPLETE` | cualquiera | `REJECT` |

### Condiciones de cierre

```
si estado != DATE_COMPLETE           → REJECT  (estructura incompleta)
si mes < 1 o mes > 12               → REJECT
si anio < 1900 o anio > 2100        → REJECT
si dia < 1 o dia > max_dias(mes, anio) → REJECT
en cualquier otro caso              → ACCEPT
```

### Regla de anio bisiesto

```
bisiesto(y) = (y % 4 == 0 AND y % 100 != 0) OR (y % 400 == 0)
```

Esto implementa el calendario gregoriano exacto:
- 2024: divisible entre 4, no entre 100 → bisiesto ✓
- 1900: divisible entre 4 y entre 100, no entre 400 → NO bisiesto ✓
- 2000: divisible entre 400 → bisiesto ✓

### Justificacion formal

**Separacion entre sintaxis y semantica:** el AFD valida la forma `DD/MM/YYYY`
sin interpretar los valores numericos. Los estados `YEAR_1..4` no saben si el
anio es 1900 o 9999; solo garantizan que sean exactamente 4 digitos. La
semantica (rangos de mes, dia, anio bisiesto) se evalua despues del recorrido
sobre los valores extraidos de posiciones fijas en la cadena original.

**Por que `DATE_COMPLETE` rechaza simbolos extra:** la transicion
`DATE_COMPLETE --[cualquiera]--> REJECT` cubre todo el alfabeto. Un caracter extra
al final genera rechazo inmediato sin necesidad de mirar el tipo de caracter.

**Cobertura de tests:**

| Regla | Test que la verifica |
|-------|---------------------|
| Formato DD/MM/YYYY | `15/08/2024` aceptado |
| Separador incorrecto | `15-08-2024` rechazado |
| Dia sin cero | `1/08/2024` rechazado |
| Mes invalido | `15/13/2024` rechazado; `15/00/2024` rechazado |
| Dia 0 | `00/08/2024` rechazado |
| Abril con 31 dias | `31/04/2024` rechazado |
| Febrero bisiesto | `29/02/2024` aceptado; `29/02/2023` rechazado |
| 1900 no bisiesto | `29/02/1900` rechazado; `28/02/1900` aceptado |
| 2000 bisiesto | `29/02/2000` aceptado |
| Anio fuera de rango | `15/08/2201` rechazado |
| Simbolo extra final | `15/08/2024x` rechazado |

---

## 4. Validador de Placa Vehicular

### Descripcion

Acepta placas vehiculares colombianas en dos formatos:
- Carro: `LLLDDD` o `LLL-DDD` — 3 letras mayusculas + 3 digitos.
- Moto: `LLLDDDL` o `LLL-DDDL` — 3 letras + 3 digitos + 1 letra final.

El guion es separador opcional. La distincion carro/moto se hace al cierre.

### Alfabeto

```
Σ = { A, B, ..., Z, 0, 1, ..., 9, - }
```

Solo letras mayusculas del rango `A-Z`. Letras minusculas rechazan de inmediato.

### Estados

```
Q = { START, L1, L2, L3, AFTER_L3, D1, D2, D3, AFTER_D3, L4, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }  determinado al cierre: estado D3 → carro; estado L4 → moto.
```

### Funcion de transicion δ — tabla completa

| Estado actual | Simbolo | Estado siguiente | Nota |
|---------------|---------|-----------------|------|
| `START` | letra mayuscula | `L1` | — |
| `START` | otro | `REJECT` | letras minusculas incluidas |
| `L1` | letra mayuscula | `L2` | — |
| `L1` | otro | `REJECT` | — |
| `L2` | letra mayuscula | `L3` | — |
| `L2` | otro | `REJECT` | — |
| `L3` | `-` | `AFTER_L3` | separador opcional |
| `L3` | digito | `D1` | — |
| `L3` | otro | `REJECT` | — |
| `AFTER_L3` | digito | `D1` | — |
| `AFTER_L3` | otro | `REJECT` | — |
| `D1` | digito | `D2` | — |
| `D1` | otro | `REJECT` | — |
| `D2` | digito | `D3` | — |
| `D2` | otro | `REJECT` | — |
| `D3` | letra mayuscula | `L4` | indica moto |
| `D3` | `-` | `AFTER_D3` | separador antes de letra de moto |
| `D3` | otro | `REJECT` | — |
| `AFTER_D3` | letra mayuscula | `L4` | — |
| `AFTER_D3` | otro | `REJECT` | — |
| `L4` | cualquiera | `REJECT` | no hay caracteres extra |

### Condiciones de cierre

```
estado == D3    → ACCEPT (placa de carro: LLLDDD)
estado == L4    → ACCEPT (placa de moto:  LLLDDDL)
estado == D1    → REJECT (faltan dos digitos)
estado == D2    → REJECT (falta un digito)
estado == AFTER_D3 → REJECT (guion sin letra de moto)
estado ∈ {L1, L2}  → REJECT (menos de tres letras)
estado == L3       → REJECT (faltan los digitos)
estado == AFTER_L3 → REJECT (guion al final sin digitos)
```

### Justificacion formal

**Mismo AFD para dos formatos:** el estado `D3` puede transitar a `L4` (moto) o terminar
ahi (carro). La distincion no requiere dos automatas separados ni retroceso; se resuelve
deterministamente al cierre mirando el estado final.

**Por que letras minusculas rechazan:** `is_upper_letter` verifica `is_letter(s) AND "A" <= s <= "Z"`.
Una letra minuscula pasa `is_letter` pero falla el rango `A-Z`, por lo que nunca genera una
transicion distinta a `REJECT`.

**Normalizacion sin guion:** el guion es absorbido por `AFTER_L3` y `AFTER_D3` sin
agregarse al arreglo `normalized`. Al cierre, `"".join(normalized)` produce `ABC123`
tanto para `ABC123` como para `ABC-123`.

**Cobertura de tests:**

| Regla | Test que la verifica |
|-------|---------------------|
| Carro sin guion | `ABC123` |
| Carro con guion | `ABC-123` |
| Moto sin guion | `XYZ456A` |
| Moto con guion | `XYZ-456A` |
| Letras minusculas | `abc123` rechazado |
| Solo 2 letras | `AB123` rechazado |
| Solo 2 digitos | `ABC12` rechazado |
| Doble guion | `ABC--123` rechazado |
| Char extra carro | `ABC123X9` rechazado |
| Guion final | `ABC123-` rechazado |

---

## 5. Validador de Contrasena Segura

### Descripcion

Acepta contrasenas con longitud minima 8, al menos una letra mayuscula, una minuscula,
un digito y un simbolo del conjunto `! @ # $ % & * - _`. Cualquier caracter fuera del
alfabeto genera rechazo inmediato. La contrasena nunca se integra al scanner de texto libre.

### Alfabeto

```
Σ = { a-z } ∪ { A-Z } ∪ { 0-9 } ∪ { !, @, #, $, %, &, *, -, _ }
```

### Estados

```
Q = { SCANNING, REJECT }
```

`SCANNING` es un estado aumentado con un vector de banderas y un contador de longitud.
El estado efectivo es el producto cartesiano:

```
SCANNING × {True,False}⁴ × ℕ
```

### Estado inicial

```
q₀ = SCANNING  con  (length=0, has_upper=F, has_lower=F, has_digit=F, has_special=F)
```

### Estados de aceptacion

```
F = { ACCEPT }  (estado virtual determinado al cierre)
```

### Funcion de transicion δ — tabla completa

| Estado | Simbolo | Efecto sobre banderas | Estado siguiente |
|--------|---------|----------------------|-----------------|
| `SCANNING` | A-Z | has_upper = True; length += 1 | `SCANNING` |
| `SCANNING` | a-z | has_lower = True; length += 1 | `SCANNING` |
| `SCANNING` | 0-9 | has_digit = True; length += 1 | `SCANNING` |
| `SCANNING` | simbolo ∈ Σ_especial | has_special = True; length += 1 | `SCANNING` |
| `SCANNING` | cualquier otro | length += 1 | `REJECT` (inmediato) |

### Condiciones de cierre

```
si length >= 8
   AND has_upper AND has_lower
   AND has_digit AND has_special  → ACCEPT
en cualquier otro caso             → REJECT  (con mensaje que lista condiciones fallidas)
```

### Justificacion formal

**Por que es un AFD aumentado y no un AFD puro:** un AFD puro necesitaria estados
separados para cada combinacion posible de banderas. Con 4 banderas booleanas son
`2⁴ = 16` combinaciones posibles. Combinado con un contador de longitud de hasta N
caracteres, el numero de estados seria `16 × N`. Para N practico (ej. 128 chars max)
son 2048 estados. El AFD aumentado con vector de banderas es equivalente pero
notablemente mas compacto para explicar en papel.

**Por que el rechazo inmediato es correcto:** un simbolo fuera de Σ hace invalida la
contrasena completa, independientemente de cuantos caracteres validos haya antes o
despues. El modelo de bandera garantiza que un caracter invalido siempre produce REJECT
sin necesidad de continuar el recorrido.

**Por que normalized="" es correcto:** la contrasena no genera valor normalizado por
razon de privacidad. El campo existe en ValidationResult por contrato de interfaz.

**Cobertura de tests:**

| Regla | Test que la verifica |
|-------|---------------------|
| 8 chars exactos, todas banderas | `Secure@1` aceptado |
| Sin mayuscula | `secure@1abc` rechazado |
| Sin minuscula | `SECURE@1ABC` rechazado |
| Sin digito | `SecurePass@` rechazado |
| Sin simbolo | `SecurePass1` rechazado |
| Char fuera de alfabeto | `Secure^1ab` rechazado (`^` no esta en Σ) |
| 7 chars, todas banderas | `Abc@1zX` rechazado (longitud) |
| 8 chars sin banderas | `abcdefgh` rechazado (faltan 3 banderas) |

---

## 6. Validador de URL

### Descripcion

Acepta URLs con protocolo `http` o `https`, seguidas de dominio con al menos un punto
y ruta opcional. La URL puede incluir query string (`?`) y fragmento (`#`).

### Alfabeto

```
Σ = { a-z, A-Z, 0-9, :, /, ., -, _, ?, =, &, #, ~, %, +, @, h, H }
```

El protocolo se acepta en mayuscula o minuscula (`HTTP://` y `http://` son equivalentes).

### Estados

```
Q = { START, PROTO_H, PROTO_HT, PROTO_HTT, PROTO_HTTP, PROTO_HTTPS,
      COLON, SLASH1, SLASH2, DOMAIN, DOMAIN_HYPHEN, DOMAIN_DOT,
      PATH, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }  (estado virtual determinado al cierre)
```

### Funcion de transicion δ — tabla completa

| Estado actual | Simbolo | Estado siguiente | Nota |
|---------------|---------|-----------------|------|
| `START` | `h` o `H` | `PROTO_H` | — |
| `START` | otro | `REJECT` | — |
| `PROTO_H` | `t` o `T` | `PROTO_HT` | — |
| `PROTO_H` | otro | `REJECT` | — |
| `PROTO_HT` | `t` o `T` | `PROTO_HTT` | — |
| `PROTO_HT` | otro | `REJECT` | — |
| `PROTO_HTT` | `p` o `P` | `PROTO_HTTP` | — |
| `PROTO_HTT` | otro | `REJECT` | — |
| `PROTO_HTTP` | `s` o `S` | `PROTO_HTTPS` | — |
| `PROTO_HTTP` | `:` | `COLON` | — |
| `PROTO_HTTP` | otro | `REJECT` | — |
| `PROTO_HTTPS` | `:` | `COLON` | — |
| `PROTO_HTTPS` | otro | `REJECT` | — |
| `COLON` | `/` | `SLASH1` | — |
| `COLON` | otro | `REJECT` | — |
| `SLASH1` | `/` | `SLASH2` | — |
| `SLASH1` | otro | `REJECT` | — |
| `SLASH2` | letra o digito | `DOMAIN` | — |
| `SLASH2` | otro | `REJECT` | — |
| `DOMAIN` | letra o digito | `DOMAIN` | — |
| `DOMAIN` | `-` | `DOMAIN_HYPHEN` | — |
| `DOMAIN` | `.` | `DOMAIN_DOT` | — |
| `DOMAIN` | `/`, `?` o `#` | `PATH` | solo si saw_domain_dot |
| `DOMAIN` | `/`, `?` o `#` | `REJECT` | si not saw_domain_dot |
| `DOMAIN` | otro | `REJECT` | — |
| `DOMAIN_HYPHEN` | letra o digito | `DOMAIN` | — |
| `DOMAIN_HYPHEN` | otro | `REJECT` | guion al final de etiqueta |
| `DOMAIN_DOT` | letra o digito | `DOMAIN` | saw_domain_dot = True |
| `DOMAIN_DOT` | otro | `REJECT` | etiqueta vacia |
| `PATH` | caracter URL valido | `PATH` | — |
| `PATH` | otro | `REJECT` | — |

### Condiciones de cierre

```
si estado == DOMAIN AND saw_domain_dot → ACCEPT
si estado == PATH                      → ACCEPT
en cualquier otro caso                 → REJECT
```

### Justificacion formal

**Protocolo lineal como cadena fija:** los estados `PROTO_H → PROTO_HT → PROTO_HTT →
PROTO_HTTP` son estados de prefijo que reconocen `http` caracter por caracter. No hay
ramificacion hasta `PROTO_HTTP`, donde `s` lleva a `PROTO_HTTPS` y `:` confirma `http:`.
Este patron es equivalente a un AFD que reconoce el lenguaje `(http|https)`.

**Por que `saw_domain_dot` es necesario:** el AFD no puede distinguir en el estado `DOMAIN`
si ya paso por un punto o no. La variable booleana extiende el estado efectivo sin
necesitar estados adicionales. Sin ella, habria que crear estados `DOMAIN_BEFORE_DOT` y
`DOMAIN_AFTER_DOT`, lo que duplicaria parte del grafo.

**Normalizacion en scanner:** `_try_url` aplica `.rstrip(".,!)")` al candidato antes de
validarlo. Esto evita que puntuacion de oracion adyacente a la URL sea incluida en el patron.

**Cobertura de tests:**

| Regla | Test que la verifica |
|-------|---------------------|
| http basico | `http://example.com` |
| https | `https://example.com` |
| Con ruta | `https://example.com/path/to/page` |
| Con query | `https://example.com/search?q=hola&lang=es` |
| Con fragmento | `https://example.com/page#section` |
| Protocolo ftp | `ftp://example.com` rechazado |
| Dominio sin punto | `http://example` rechazado |
| Dominio guion final | `http://example-.com` rechazado |
| Dominio punto inicial | `http://.example.com` rechazado |
| Sin protocolo | `example.com` rechazado |

---

## 7. Validador de NIT

### Descripcion

Acepta Numeros de Identificacion Tributaria (NIT) colombianos con el formato exacto
`NNN.NNN.NNN-D`: tres grupos de tres digitos separados por punto, seguidos de guion
y un digito verificador.

### Alfabeto

```
Σ = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ., - }
```

### Estados

```
Q = { START, D1, D2, D3, DOT1, D4, D5, D6, DOT2, D7, D8, D9, HYPHEN, CHECK, REJECT }
```

### Estado inicial

```
q₀ = START
```

### Estados de aceptacion

```
F = { ACCEPT }  (estado virtual determinado al cierre cuando estado == CHECK)
```

### Funcion de transicion δ — tabla completa

| Estado actual | Simbolo | Estado siguiente | Posicion en NNN.NNN.NNN-D |
|---------------|---------|-----------------|--------------------------|
| `START` | digito | `D1` | primer digito del grupo 1 |
| `START` | otro | `REJECT` | — |
| `D1` | digito | `D2` | segundo digito del grupo 1 |
| `D1` | otro | `REJECT` | — |
| `D2` | digito | `D3` | tercer digito del grupo 1 |
| `D2` | otro | `REJECT` | — |
| `D3` | `.` | `DOT1` | primer separador |
| `D3` | otro | `REJECT` | — |
| `DOT1` | digito | `D4` | primer digito del grupo 2 |
| `DOT1` | otro | `REJECT` | — |
| `D4` | digito | `D5` | segundo digito del grupo 2 |
| `D4` | otro | `REJECT` | — |
| `D5` | digito | `D6` | tercer digito del grupo 2 |
| `D5` | otro | `REJECT` | — |
| `D6` | `.` | `DOT2` | segundo separador |
| `D6` | otro | `REJECT` | — |
| `DOT2` | digito | `D7` | primer digito del grupo 3 |
| `DOT2` | otro | `REJECT` | — |
| `D7` | digito | `D8` | segundo digito del grupo 3 |
| `D7` | otro | `REJECT` | — |
| `D8` | digito | `D9` | tercer digito del grupo 3 |
| `D8` | otro | `REJECT` | — |
| `D9` | `-` | `HYPHEN` | separador del digito verificador |
| `D9` | otro | `REJECT` | — |
| `HYPHEN` | digito | `CHECK` | digito verificador |
| `HYPHEN` | otro | `REJECT` | — |
| `CHECK` | cualquiera | `REJECT` | no se permiten caracteres extra |

### Condiciones de cierre

```
si estado == CHECK → ACCEPT
en cualquier otro caso → REJECT
```

### Justificacion formal

**AFD puro lineal:** el NIT tiene exactamente 13 caracteres (`NNN.NNN.NNN-D`). El camino
de aceptacion es una secuencia lineal de 13 transiciones sin ramificacion. Cada estado
acepta exactamente un tipo de simbolo (digito, punto o guion) en su posicion. El grafo
tiene forma de cadena (chain) sin bucles ni estados con multiples transiciones validas.

**Normalizacion sin separadores:** el arreglo `digits` solo acumula los 10 digitos reales
(9 del NIT + 1 verificador). La cadena normalizada es `"".join(digits)` = secuencia pura
de digitos, util para procesamiento posterior.

**Ambiguedad con otros patrones en el scanner:** el NIT `NNN.NNN.NNN-D` usa `.` como
separador, mientras que el telefono nunca usa `.`. El email necesita `@`. La fecha usa `/`.
No hay colision entre patrones: el scanner intenta en orden `fecha > email > url > telefono
> nit > placa` y el NIT solo es aceptado cuando el formato completo `NNN.NNN.NNN-D` esta
presente.

**Cobertura de tests:**

| Regla | Test que la verifica |
|-------|---------------------|
| Formato valido | `900.123.456-7` aceptado |
| Sin puntos | `900123456-7` rechazado |
| Sin guion | `900.123.4567` rechazado |
| Solo un grupo | `900` rechazado |
| Letras en grupo | `9AB.123.456-7` rechazado |
| Separador incorrecto | `900-123-456-7` rechazado |
| Caracteres extra | `900.123.456-7X` rechazado |
| Grupo de 2 digitos | `90.123.456-7` rechazado |
| Dos digitos verificadores | `900.123.456-77` rechazado |

---

## 8. Scanner de texto libre (Parte A)

### Descripcion

El scanner recorre el texto caracter por caracter, sin expresiones regulares, intentando
cada patron desde la posicion actual en orden de prioridad. Si un patron es aceptado,
registra la coincidencia y avanza al siguiente caracter despues de la coincidencia.

### Orden de prioridad

```
fecha > email > url > telefono > nit > placa
```

**Justificacion del orden:**

| Patron | Por que tiene esta prioridad |
|--------|------------------------------|
| fecha | Formato fijo de 10 chars con `/` — sin ambiguedad con otros |
| email | Requiere `@` — identificable antes que URL o telefono |
| url | Requiere `http(s)://` — empieza con letra, viene despues de email |
| telefono | Digitos con separadores — mas comun que NIT en texto |
| nit | Digitos con puntos y guion — formato menos frecuente |
| placa | Solo letras mayusculas — no conflicta con ninguno anterior |

### Limpieza de candidatos

| Patron | Caracter eliminado al final | Justificacion |
|--------|----------------------------|---------------|
| email | `.` final | Punto de oracion nunca es parte valida del TLD |
| url | `.,!)` finales | Puntuacion de oracion adyacente a la URL |
| nit | `.` final | Un NIT nunca termina en punto |

### Contraseña excluida del scanner

La contraseña no tiene delimitadores naturales en texto libre. Cualquier secuencia de
8+ caracteres podria ser interpretada como contraseña, generando falsos positivos masivos.
Se valida exclusivamente en formularios interactivos (Parte B).
