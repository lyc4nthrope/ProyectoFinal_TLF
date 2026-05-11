**Descripción formal de los autómatas**

**Cristhian Eduardo Osorio Restrepo**

**CC: 1092850782**

**Daniel Stiven Perez Cordoba**

**CC:** 

 

 

**Ing. Ana Maria Tamayo Ocampo Mg**

**Universidad del Quindío**

**Facultad de Ingeniería**

**Ingeniería de Sistemas y Computación**

**Teoría de Lenguajes Formales**

**Armenia-Quindío**

# Descripción formal de los autómatas

Descripción rigurosa de los siete autómatas implementados en el proyecto. Cada validador modela un Autómata Finito Determinista (AFD) explicable en papel: estados explícitos, alfabeto finito, función de transición total y condición de aceptación verificable al agotar la entrada.

## Modelo común a todos los validadores

Cada validador implementa un AFD con la quíntupla:

M \= (Q, Σ, δ, q₀, F)

| Componente | Significado |
| :---- | :---- |
| Q | Conjunto finito de estados |
| Σ | Alfabeto finito de símbolos permitidos |
| δ: Q × Σ → Q | Funcion de transicion determinista |
| q₀ ∈ Q | Estado inicial |
| F ⊆ Q | Conjunto de estados de aceptación |

**Principios de implementación que garantizan la trazabilidad en cuaderno:**

- La función δ nunca lee más de un símbolo a la vez (sin lookahead).  
- El estado REJECT es un estado trampa: ninguna transición posterior lo abandona.  
- La aceptación o rechazo final se decide al agotar la entrada (condición de cierre).  
- Ningún validador usa librerías de expresiones regulares ni métodos de clasificación de la librería estándar (isdigit, isupper, etc.).  
- Toda clasificación de símbolos se delega a src/core/symbol\_classifier.py.

## 1\. Validador de Teléfono

### Descripción

Acepta números telefónicos con 10 a 13 dígitos reales, prefijo internacional \+ opcional al inicio, y separadores   o \- entre bloques numéricos.

### Alfabeto

Σ \= { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, \+, \-, ' ' }

### Estados

Q \= { START, AFTER\_PLUS, IN\_NUMBER, AFTER\_SEPARATOR, REJECT }

No existe estado ACCEPT dentro del recorrido. La aceptación se decide al cierre según el estado final y el conteo de dígitos reales.

### Estado inicial

q₀ \= START

### Estados de aceptación

F \= { ACCEPT }  (estado virtual determinado al cierre)

La cadena se acepta solo si al agotar la entrada se cumplen TODAS:

- El Estado no es AFTER\_SEPARATOR (no puede terminar en separador).  
- 10 ≤ digitos\_reales ≤ 13.

### Funcion de transicion δ — tabla completa

| Estado actual | Símbolo | Estado siguiente | Acción adicional |
| :---- | :---- | :---- | :---- |
| START | dígito | IN\_NUMBER | dígitos \+= 1 |
| START | \+ | AFTER\_PLUS | — |
| START | otro | REJECT | — |
| AFTER\_PLUS | dígito | IN NUMBER | dígitos \+= 1 |
| AFTER\_PLUS | otro | REJECT | — |
| IN\_NUMBER | dígito | IN\_NUMBER | dígitos \+= 1 |
| IN\_NUMBER | \- o   | AFTER\_SEPARATOR | — |
| IN\_NUMBER | otro | REJECT | — |
| AFTER\_SEPARATOR | dígito | IN\_NUMBER | dígitos \+= 1 |
| AFTER\_SEPARATOR | \- o   | REJECT | separadores consecutivos |
| AFTER\_SEPARATOR | otro | REJECT | — |

### Condiciones de cierre

Al agotar la entrada, en orden de evaluación:

si estado \== AFTER\_SEPARATOR → REJECT  (cadena termina en separador)

si digitos \< 10 o digitos \> 13  → REJECT  (longitud inválida)

en cualquier otro caso          → ACCEPT

### 

### Justificación formal

**Determinismo:** para cada par (estado, símbolo) existe exactamente un estado siguiente. Los símbolos \- y   se clasifican por el mismo predicado \_is\_phone\_separator, por lo que no hay ambigüedad de transición.

**Correctitud de la regla de separadores:** AFTER\_SEPARATOR rechaza todo símbolo que no sea dígito. Si la cadena termina en AFTER\_SEPARATOR, el cierre rechaza sin lookahead (no se necesita verificar el índice del carácter actual).

**Correctitud del conteo:** el contador digits solo se incrementa cuando el autómata transita desde IN\_NUMBER \--\[digito\]--\> IN\_NUMBER o cuando entra a IN\_NUMBER desde START o AFTER\_PLUS. Los separadores nunca incrementan el contador. Esto garantiza que digits refleja exactamente los dígitos reales de la cadena.

**Cobertura de tests que verifican cada regla:**

| Regla | Test que la verifica |
| :---- | :---- |
| 10 dígitos válidos | test\_finds\_phone\_in\_text — 3001234567 |
| Prefijo \+ | test\_finds\_international\_phone — \+57 300-123-4567 |
| Separadores válidos | casos validos con \- y   en test\_phone\_validator.py |
| Separadores consecutivos | invalido 300--1234567 |
| Termina en separador | invalido 3001234- |
| Menos de 10 dígitos | invalido 12345, borde 300  |
| Mas de 13 dígitos | borde 30012345678901 |

## 2\. Validador de Correo Electrónico

### Descripción

Acepta correos con formato local@dominio.tld, donde la parte local puede contener letras, dígitos y separadores internos (., \_, \-), el dominio tiene etiquetas separadas por punto con guiones internos opcionales, y el TLD tiene al menos 2 letras.

### Alfabeto

Σ \= { a-z, A-Z, 0-9, ., \_, \-, @ }

### Estados

Q \= { START, LOCAL, LOCAL\_SEPARATOR, AFTER\_AT, DOMAIN, DOMAIN\_HYPHEN,

      AFTER\_DOMAIN\_DOT, REJECT }

### Estado inicial

q₀ \= START

### Estados de aceptación

F \= { ACCEPT }  (estado virtual determinado al cierre)

### Funcion de transicion δ — tabla completa

| Estado actual | Símbolo | Estado siguiente | Acción adicional |
| :---- | :---- | :---- | :---- |
| START | letra o dígito | LOCAL | — |
| START | otro | REJECT | — |
| LOCAL | letra o dígito | LOCAL | — |
| LOCAL | ., \_, \- | LOCAL\_SEPARATOR | — |
| LOCAL | @ | AFTER\_AT | saw\_at \= True |
| LOCAL | otro | REJECT | — |
| LOCAL\_SEPARATOR | letra o dígito | LOCAL | — |
| LOCAL\_SEPARATOR | otro | REJECT | sep. consecutivo o al final |
| AFTER\_AT | letra o dígito | DOMAIN | tld\_letters \= 1 si letra |
| AFTER\_AT | otro | REJECT | — |
| DOMAIN | letra o dígito | DOMAIN | tld\_letters \= cont+1 o 0 |
| DOMAIN | \- | DOMAIN\_HYPHEN | tld\_letters \= 0 |
| DOMAIN | . | AFTER\_DOMAIN\_DOT | saw\_dot \= True; tld\_letters \= 0 |
| DOMAIN | otro | REJECT | — |
| DOMAIN\_HYPHEN | letra o dígito | DOMAIN | tld\_letters \= 1 si letra |
| DOMAIN\_HYPHEN | otro | REJECT | guion al final de etiqueta |
| AFTER\_DOMAIN\_DOT | letra o dígito | DOMAIN | tld\_letters \= 1 si letra; saw\_dot=True |
| AFTER\_DOMAIN\_DOT | otro | REJECT | etiqueta vacía |

### 

### Condiciones de cierre

si not saw\_at                                          → REJECT

si estado ∈ {AFTER\_AT, AFTER\_DOMAIN\_DOT,

              DOMAIN\_HYPHEN, LOCAL\_SEPARATOR}          → REJECT

si not saw\_domain\_dot                                  → REJECT

si tld\_letters \< 2                                     → REJECT

en cualquier otro caso                                 → ACCEPT

### 

### Justificación formal

**Por que tld\_letters es correcto:** el contador se reinicia a 0 cada vez que aparece un guión o un punto dentro del dominio. Solo cuenta letras consecutivas al final de la última etiqueta. Un TLD como .c1 termina con un dígito, lo que pone tld\_letters \= 0 al procesar 1. El cierre detecta tld\_letters \< 2 y rechaza.

**Por que los separadores consecutivos se rechazan:** desde LOCAL\_SEPARATOR, cualquier símbolo que no sea letra o dígito transita a REJECT. Eso incluye ., \_, \-, y @. No es posible formar user..name ni user.@dom.

**Por que el dominio sin punto se rechaza:** saw\_domain\_dot solo se activa en la transición DOMAIN \--\[.\]--\> AFTER\_DOMAIN\_DOT. Si esa transición nunca ocurre, el cierre detecta saw\_domain\_dot \= False y rechaza.

**Cobertura de tests:**

| Regla | Test que la verifica |
| :---- | :---- |
| Estructura básica | usuario@example.com |
| Separadores locales | user.name-test\_1@sub.domain.com |
| TLD mínimo 2 letras | invalido usuario@example.c1 |
| Dominio sin punto | invalido usuario@example → a@b rechazado |
| Empieza con sep. local | invalido .usuario@example.com |
| Sep. consecutivos | invalido user..name@example.com |
| Guión final dominio | invalido usuario@example-.com |

## 3\. Validador de Fecha

### Descripción

Acepta fechas con formato estricto DD/MM/YYYY. La estructura se valida caracter por caracter con estados lineales. Luego se aplica una capa semántica que verifica rangos de día, mes, año y el cálculo de año bisiesto.

### Alfabeto

Σ \= { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, / }

### Estados

Q \= { START, DAY\_FIRST, AFTER\_DAY, MONTH\_FIRST, MONTH\_SECOND, AFTER\_MONTH,

      YEAR\_1, YEAR\_2, YEAR\_3, YEAR\_4, DATE\_COMPLETE, REJECT }

### Estado inicial

q₀ \= START

### Estados de aceptación

F \= { ACCEPT }  (estado virtual determinado al cierre tras validación semántica)

### Funcion de transicion δ — tabla completa

| Estado actual | Símbolo | Estado siguiente |
| :---- | :---- | :---- |
| START | dígito | DAY\_FIRST |
| START | otro | REJECT |
| DAY\_FIRST | dígito | AFTER\_DAY |
| DAY\_FIRST | otro | REJECT |
| AFTER\_DAY | / | MONTH\_FIRST |
| AFTER\_DAY | otro | REJECT |
| MONTH\_FIRST | dígito | MONTH\_SECOND |
| MONTH\_FIRST | otro | REJECT |
| MONTH\_SECOND | dígito | AFTER\_MONTH |
| MONTH\_SECOND | otro | REJECT |
| AFTER\_MONTH | / | YEAR\_1 |
| AFTER\_MONTH | otro | REJECT |
| YEAR\_1 | dígito | YEAR\_2 |
| YEAR\_1 | otro | REJECT |
| YEAR\_2 | dígito | YEAR\_3 |
| YEAR\_2 | otro | REJECT |
| YEAR\_3 | dígito | YEAR\_4 |
| YEAR\_3 | otro | REJECT |
| YEAR\_4 | dígito | DATE\_COMPLETE |
| YEAR\_4 | otro | REJECT |
| DATE\_COMPLETE | cualquiera | REJECT |

### Condiciones de cierre

si estado \!= DATE\_COMPLETE           → REJECT  (estructura incompleta)

si mes \< 1 o mes \> 12               → REJECT

si anio \< 1900 o año \> 2100        → REJECT

si dia \< 1 o dia \> max\_dias(mes, anio) → REJECT

en cualquier otro caso              → ACCEPT

### Regla de año bisiesto

bisiesto(y) \= (y % 4 \== 0 AND y % 100 \!= 0\) OR (y % 400 \== 0\)

Esto implementa el calendario gregoriano exacto:

- 2024: divisible entre 4, no entre 100 → bisiesto ✓  
- 1900: divisible entre 4 y entre 100, no entre 400 → NO bisiesto ✓  
- 2000: divisible entre 400 → bisiesto ✓

### 

### Justificación formal

**Separación entre sintaxis y semántica:** el AFD válida la forma DD/MM/YYYY sin interpretar los valores numéricos. Los estados YEAR\_1..4 no saben si el anio es 1900 o 9999; solo garantizan que sean exactamente 4 dígitos. La semántica (rangos de mes, dia, anio bisiesto) se evalúa después del recorrido sobre los valores extraídos de posiciones fijas en la cadena original.

**Por que DATE\_COMPLETE rechaza simbolos extra:** la transición DATE\_COMPLETE \--\[cualquiera\]--\> REJECT cubre todo el alfabeto. Un carácter extra al final genera rechazo inmediato sin necesidad de mirar el tipo de carácter.

**Cobertura de tests:**

| Regla | Test que la verifica |
| :---- | :---- |
| Formato DD/MM/YYYY | 15/08/2024 aceptado |
| Separador incorrecto | 15-08-2024 rechazado |
| Dia sin cero | 1/08/2024 rechazado |
| Mes invalido | 15/13/2024 rechazado; 15/00/2024 rechazado |
| Dia 0 | 00/08/2024 rechazado |
| Abril con 31 días | 31/04/2024 rechazado |
| Febrero bisiesto | 29/02/2024 aceptado; 29/02/2023 rechazado |
| 1900 no bisiesto | 29/02/1900 rechazado; 28/02/1900 aceptado |
| 2000 bisiesto | 29/02/2000 aceptado |
| Año fuera de rango | 15/08/2201 rechazado |
| Símbolo extra final | 15/08/2024x rechazado |

## 4\. Validador de Placa Vehicular

### Descripción

Acepta placas vehiculares colombianas en dos formatos:

- Carro: LLLDDD o LLL-DDD — 3 letras mayúsculas \+ 3 dígitos.  
- Moto: LLLDDDL o LLL-DDDL — 3 letras \+ 3 dígitos \+ 1 letra final.

El guión es separador opcional. La distinción carro/moto se hace al cierre.

### Alfabeto

Σ \= { A, B, ..., Z, 0, 1, ..., 9, \- }

Solo letras mayúsculas del rango A-Z. Letras minúsculas rechazan de inmediato.

### Estados

Q \= { START, L1, L2, L3, AFTER\_L3, D1, D2, D3, AFTER\_D3, L4, REJECT }

### Estado inicial

q₀ \= START

### Estados de aceptación

F \= { ACCEPT }  determinado al cierre: estado D3 → carro; estado L4 → moto.

### Funcion de transicion δ — tabla completa

| Estado actual | Símbolo | Estado siguiente | Nota |
| :---- | :---- | :---- | :---- |
| START | letra mayúscula | L1 | — |
| START | otro | REJECT | letras minúsculas incluidas |
| L1 | letra mayúscula | L2 | — |
| L1 | otro | REJECT | — |
| L2 | letra mayúscula | L3 | — |
| L2 | otro | REJECT | — |
| L3 | \- | AFTER\_L3 | separador opcional |
| L3 | dígito | D1 | — |
| L3 | otro | REJECT | — |
| AFTER\_L3 | dígito | D1 | — |
| AFTER\_L3 | otro | REJECT | — |
| D1 | dígito | D2 | — |
| D1 | otro | REJECT | — |
| D2 | dígito | D3 | — |
| D2 | otro | REJECT | — |
| D3 | letra mayúscula | L4 | indica moto |
| D3 | \- | AFTER\_D3 | separador antes de letra de moto |
| D3 | otro | REJECT | — |
| AFTER\_D3 | letra mayúscula | L4 | — |
| AFTER\_D3 | otro | REJECT | — |
| L4 | cualquiera | REJECT | no hay caracteres extra |

### Condiciones de cierre

estado \== D3    → ACCEPT (placa de carro: LLLDDD)

estado \== L4    → ACCEPT (placa de moto:  LLLDDDL)

estado \== D1    → REJECT (faltan dos dígitos)

estado \== D2    → REJECT (falta un digito)

estado \== AFTER\_D3 → REJECT (guión sin letra de moto)

estado ∈ {L1, L2}  → REJECT (menos de tres letras)

estado \== L3       → REJECT (faltan los dígitos)

estado \== AFTER\_L3 → REJECT (guión al final sin dígitos)

### Justificación formal

**Mismo AFD para dos formatos:** el estado D3 puede transitar a L4 (moto) o terminar ahí (carro). La distinción no requiere dos autómatas separados ni retroceso; se resuelve determinantemente al cierre mirando el estado final.

**Por que letras minúsculas rechazan:** is\_upper\_letter verifica is\_letter(s) AND "A" \<= s \<= "Z". Una letra minúscula pasa is\_letter pero falla el rango A-Z, por lo que nunca genera una transición distinta a REJECT.

**Normalización sin guión:** el guión es absorbido por AFTER\_L3 y AFTER\_D3 sin agregarse al arreglo normalized. Al cierre, "".join(normalized) produce ABC123 tanto para ABC123 como para ABC-123.

**Cobertura de tests:**

| Regla | Test que la verifica |
| :---- | :---- |
| Carro sin guión | ABC123 |
| Carro con guión | ABC-123 |
| Moto sin guión | XYZ456A |
| Moto con guión | XYZ-456A |
| Letras minúsculas | abc123 rechazado |
| Solo 2 letras | AB123 rechazado |
| Solo 2 dígitos | ABC12 rechazado |
| Doble guión | ABC--123 rechazado |
| Char extra carro | ABC123X9 rechazado |
| Guión final | ABC123- rechazado |

## 5\. Validador de Contraseña Segura

### Descripción

Acepta contraseñas con longitud mínima 8, al menos una letra mayúscula, una minúscula, un digito y un símbolo del conjunto \! @ \# $ % & \* \- \_. Cualquier carácter fuera del alfabeto genera rechazo inmediato. La contraseña nunca se integra al scanner de texto libre.

### Alfabeto

Σ \= { a-z } ∪ { A-Z } ∪ { 0-9 } ∪ { \!, @, \#, $, %, &, \*, \-, \_ }

### Estados

Q \= { SCANNING, REJECT }

SCANNING es un estado aumentado con un vector de banderas y un contador de longitud. El estado efectivo es el producto cartesiano:

SCANNING × {True,False}⁴ × ℕ

### Estado inicial

q₀ \= SCANNING  con  (length=0, has\_upper=F, has\_lower=F, has\_digit=F, has\_special=F)

### Estados de aceptación

F \= { ACCEPT }  (estado virtual determinado al cierre)

### Funcion de transicion δ — tabla completa

| Estado | Símbolo | Efecto sobre banderas | Estado siguiente |
| :---- | :---- | :---- | :---- |
| SCANNING | A-Z | has\_upper \= True; length \+= 1 | SCANNING |
| SCANNING | a-z | has\_lower \= True; length \+= 1 | SCANNING |
| SCANNING | 0-9 | has\_digit \= True; length \+= 1 | SCANNING |
| SCANNING | símbolo ∈ Σ\_especial | has\_special \= True; length \+= 1 | SCANNING |
| SCANNING | cualquier otro | length \+= 1 | REJECT (inmediato) |

### 

### Condiciones de cierre

si length \>= 8

   AND has\_upper AND has\_lower

   AND has\_digit AND has\_special  → ACCEPT

en cualquier otro caso             → REJECT  (con mensaje que lista condiciones fallidas)

### Justificación formal

**Por que es un AFD aumentado y no un AFD puro:** un AFD puro necesitaria estados separados para cada combinación posible de banderas. Con 4 banderas booleanas son 2⁴ \= 16 combinaciones posibles. Combinado con un contador de longitud de hasta N caracteres, el número de estados sería 16 × N. Para N practico (ej. 128 chars max) son 2048 estados. El AFD aumentado con vector de banderas es equivalente pero notablemente más compacto para explicar en papel.

**Por que el rechazo inmediato es correcto:** un símbolo fuera de Σ hace invalida la contraseña completa, independientemente de cuántos caracteres válidos haya antes o después. El modelo de bandera garantiza que un carácter invalido siempre produce REJECT sin necesidad de continuar el recorrido.

**Por que normalized="" es correcto:** la contraseña no genera valor normalizado por razón de privacidad. El campo existe en ValidationResult por contrato de interfaz.

**Cobertura de tests:**

| Regla | Test que la verifica |
| :---- | :---- |
| 8 chars exactos, todas banderas | Secure@1 aceptado |
| Sin mayúscula | secure@1abc rechazado |
| Sin minúscula | SECURE@1ABC rechazado |
| Sin dígito | SecurePass@ rechazado |
| Sin símbolo | SecurePass1 rechazado |
| Char fuera de alfabeto | Secure^1ab rechazado (^ no está en Σ) |
| 7 chars, todas banderas | Abc@1zX rechazado (longitud) |
| 8 chars sin banderas | abcdefgh rechazado (faltan 3 banderas) |

## 6\. Validador de URL

### Descripción

Acepta URLs con protocolo http o https, seguidas de dominio con al menos un punto y ruta opcional. La URL puede incluir query string (?) y fragmento (\#).

### Alfabeto

Σ \= { a-z, A-Z, 0-9, :, /, ., \-, \_, ?, \=, &, \#, \~, %, \+, @, h, H }

El protocolo se acepta en mayuscula o minuscula (HTTP:// y http:// son equivalentes).

### Estados

Q \= { START, PROTO\_H, PROTO\_HT, PROTO\_HTT, PROTO\_HTTP, PROTO\_HTTPS,

      COLON, SLASH1, SLASH2, DOMAIN, DOMAIN\_HYPHEN, DOMAIN\_DOT,

      PATH, REJECT }

### Estado inicial

q₀ \= START

### Estados de aceptación

F \= { ACCEPT }  (estado virtual determinado al cierre)

### Funcion de transicion δ — tabla completa

| Estado actual | Símbolo | Estado siguiente | Nota |
| :---- | :---- | :---- | :---- |
| START | h o H | PROTO\_H | — |
| START | otro | REJECT | — |
| PROTO\_H | t o T | PROTO\_HT | — |
| PROTO\_H | otro | REJECT | — |
| PROTO\_HT | t o T | PROTO\_HTT | — |
| PROTO\_HT | otro | REJECT | — |
| PROTO\_HTT | p o P | PROTO\_HTTP | — |
| PROTO\_HTT | otro | REJECT | — |
| PROTO\_HTTP | s o S | PROTO\_HTTPS | — |
| PROTO\_HTTP | : | COLON | — |
| PROTO\_HTTP | otro | REJECT | — |
| PROTO\_HTTPS | : | COLON | — |
| PROTO\_HTTPS | otro | REJECT | — |
| COLON | / | SLASH1 | — |
| COLON | otro | REJECT | — |
| SLASH1 | / | SLASH2 | — |
| SLASH1 | otro | REJECT | — |
| SLASH2 | letra o dígito | DOMAIN | — |
| SLASH2 | otro | REJECT | — |
| DOMAIN | letra o dígito | DOMAIN | — |
| DOMAIN | \- | DOMAIN\_HYPHEN | — |
| DOMAIN | . | DOMAIN\_DOT | — |
| DOMAIN | /, ? o \# | PATH | solo si saw\_domain\_dot |
| DOMAIN | /, ? o \# | REJECT | si not saw\_domain\_dot |
| DOMAIN | otro | REJECT | — |
| DOMAIN\_HYPHEN | letra o dígito | DOMAIN | — |
| DOMAIN\_HYPHEN | otro | REJECT | guion al final de etiqueta |
| DOMAIN\_DOT | letra o dígito | DOMAIN | saw\_domain\_dot \= True |
| DOMAIN\_DOT | otro | REJECT | etiqueta vacía |
| PATH | carácter URL valido | PATH | — |
| PATH | otro | REJECT | — |

### 

### Condiciones de cierre

si estado \== DOMAIN AND saw\_domain\_dot → ACCEPT

si estado \== PATH                      → ACCEPT

en cualquier otro caso                 → REJECT

### Justificación formal

**Protocolo lineal como cadena fija:** los estados PROTO\_H → PROTO\_HT → PROTO\_HTT → PROTO\_HTTP son estados de prefijo que reconocen http caracter por caracter. No hay ramificación hasta PROTO\_HTTP, donde s lleva a PROTO\_HTTPS y : confirma http:. Este patrón es equivalente a un AFD que reconoce el lenguaje (http|https).

**Por que saw\_domain\_dot es necesario:** el AFD no puede distinguir en el estado DOMAIN si ya pasó por un punto o no. La variable booleana extiende el estado efectivo sin necesitar estados adicionales. Sin ella, habría que crear estados DOMAIN\_BEFORE\_DOT y DOMAIN\_AFTER\_DOT, lo que duplicaria parte del grafo.

**Normalizacion en scanner:** \_try\_url aplica .rstrip(".,\!)") al candidato antes de validarlo. Esto evita que puntuacion de oracion adyacente a la URL sea incluida en el patrón.

**Cobertura de tests:**

| Regla | Test que la verifica |
| :---- | :---- |
| http básico | http://example.com |
| https | https://example.com |
| Con ruta | https://example.com/path/to/page |
| Con query | https://example.com/search?q=hola\&lang=es |
| Con fragmento | https://example.com/page\#section |
| Protocolo ftp | ftp://example.com rechazado |
| Dominio sin punto | http://example rechazado |
| Dominio guión final | http://example-.com rechazado |
| Dominio punto inicial | http://.example.com rechazado |
| Sin protocolo | example.com rechazado |

## 7\. Validador de NIT

### Descripción

Acepta Números de Identificación Tributaria (NIT) colombianos con el formato exacto NNN.NNN.NNN-D: tres grupos de tres dígitos separados por punto, seguidos de guion y un digito verificador.

### Alfabeto

Σ \= { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ., \- }

### Estados

Q \= { START, D1, D2, D3, DOT1, D4, D5, D6, DOT2, D7, D8, D9, HYPHEN, CHECK, REJECT }

### Estado inicial

q₀ \= START

### Estados de aceptación

F \= { ACCEPT }  (estado virtual determinado al cierre cuando estado \== CHECK)

### Funcion de transicion δ — tabla completa

| Estado actual | Símbolo | Estado siguiente | Posición en NNN.NNN.NNN-D |
| :---- | :---- | :---- | :---- |
| START | dígito | D1 | primer dígito del grupo 1 |
| START | otro | REJECT | — |
| D1 | dígito | D2 | segundo dígito del grupo 1 |
| D1 | otro | REJECT | — |
| D2 | dígito | D3 | tercer dígito del grupo 1 |
| D2 | otro | REJECT | — |
| D3 | . | DOT1 | primer separador |
| D3 | otro | REJECT | — |
| DOT1 | dígito | D4 | primer dígito del grupo 2 |
| DOT1 | otro | REJECT | — |
| D4 | dígito | D5 | segundo dígito del grupo 2 |
| D4 | otro | REJECT | — |
| D5 | dígito | D6 | tercer dígito del grupo 2 |
| D5 | otro | REJECT | — |
| D6 | . | DOT2 | segundo separador |
| D6 | otro | REJECT | — |
| DOT2 | dígito | D7 | primer dígito del grupo 3 |
| DOT2 | otro | REJECT | — |
| D7 | dígito | D8 | segundo dígito del grupo 3 |
| D7 | otro | REJECT | — |
| D8 | dígito | D9 | tercer dígito del grupo 3 |
| D8 | otro | REJECT | — |
| D9 | \- | HYPHEN | separador del dígito verificador |
| D9 | otro | REJECT | — |
| HYPHEN | dígito | CHECK | dígito verificador |
| HYPHEN | otro | REJECT | — |
| CHECK | cualquiera | REJECT | no se permiten caracteres extra |

### 

### Condiciones de cierre

si estado \== CHECK → ACCEPT

en cualquier otro caso → REJECT

### Justificación formal

**AFD puro lineal:** el NIT tiene exactamente 13 caracteres (NNN.NNN.NNN-D). El camino de aceptación es una secuencia lineal de 13 transiciones sin ramificación. Cada estado acepta exactamente un tipo de símbolo (digito, punto o guión) en su posición. El grafo tiene forma de cadena (chain) sin bucles ni estados con múltiples transiciones válidas.

**Normalización sin separadores:** el arreglo digits solo acumula los 10 dígitos reales (9 del NIT \+ 1 verificador). La cadena normalizada es "".join(digits) \= secuencia pura de digitos, útil para procesamiento posterior.

**Ambigüedad con otros patrones en el scanner:** el NIT NNN.NNN.NNN-D usa . como separador, mientras que el teléfono nunca se usa .. El email necesita @. La fecha usa /. No hay colisión entre patrones: el scanner intenta en orden \`fecha \> email \> url \> teléfono

nit \> placa y el NIT solo es aceptado cuando el formato completoNNN.NNN.NNN-D\` está presente.  
   
**Cobertura de tests:**

| Regla | Test que la verifica |
| :---- | :---- |
| Formato válido | 900.123.456-7 aceptado |
| Sin puntos | 900123456-7 rechazado |
| Sin guión | 900.123.4567 rechazado |
| Solo un grupo | 900 rechazado |
| Letras en grupo | 9AB.123.456-7 rechazado |
| Separador incorrecto | 900-123-456-7 rechazado |
| Caracteres extra | 900.123.456-7X rechazado |
| Grupo de 2 dígitos | 90.123.456-7 rechazado |
| Dos dígitos verificadores | 900.123.456-77 rechazado |

## 8\. Scanner de texto libre

### Descripción

El scanner recorre el texto caracter por caracter, sin expresiones regulares, intentando cada patrón desde la posición actual en orden de prioridad. Si un patrón es aceptado, registra la coincidencia y avanza al siguiente carácter después de la coincidencia.

### Orden de prioridad

fecha \> email \> url \> teléfono \> nit \> placa

**Justificación del orden:**

| Patrón | Por que tiene esta prioridad |
| :---- | :---- |
| fecha | Formato fijo de 10 chars con / — sin ambigüedad con otros |
| email | Requiere @ — identificable antes que URL o teléfono |
| url | Requiere http(s):// — empieza con letra, viene después de email |
| teléfono | Dígitos con separadores — más común que NIT en texto |
| nit | Dígitos con puntos y guion — formato menos frecuente |
| placa | Solo letras mayúsculas — no conflictiva con ninguno anterior |

### 

### Limpieza de candidatos

| Patrón | Carácter eliminado al final | Justificación |
| :---- | :---- | :---- |
| email | . final | Punto de oracion nunca es parte válida del TLD |
| url | .,\!) finales | Puntuación de oracion adyacente a la URL |
| nit | . final | Un NIT nunca termina en punto |

### 

### Contraseña excluida del scanner

La contraseña no tiene delimitadores naturales en texto libre. Cualquier secuencia de 8+ caracteres podría ser interpretada como contraseña, generando falsos positivos masivos. Se valida exclusivamente en los formularios.  
