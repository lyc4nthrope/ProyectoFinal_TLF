

**Búsqueda y Validación de Patrones en Textos**

 **y**

 **Sistemas Interactivos**

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

## 1\. Objetivo General

Desarrollar una aplicación en Python que permita detectar y validar patrones dentro de textos mediante autómatas finitos deterministas (AFD) implementados manualmente, sin el uso de librerías de expresiones regulares predefinidas, y verificar la entrada de datos en interfaces interactivas garantizando que cumplan con criterios sintácticos y estructurales previamente definidos.

## 2\. Descripción del Proyecto

El proyecto implementa siete validadores formales basados en AFDs explicables en papel, un scanner de texto libre que los orquesta sin usar expresiones regulares, y una interfaz interactiva con formularios de validación en tiempo real.

**Parte A — Búsqueda en texto libre:** el scanner recorre texto caracter por caracter, intentando cada patrón en orden de prioridad (fecha \> correo \> url \> teléfono \> nit \> placa). Cada patrón es validado por su AFD correspondiente.

**Parte B — Validación en formularios:** la interfaz gráfica (Tkinter) expone campos para teléfono, correo, fecha, placa, contraseña y NIT, con validación en tiempo real o antes del envío.

**Principio central:** ningún modulo usa re, regex ni metodos de la librería estándar para clasificar caracteres (isdigit(), isupper(), etc.). Toda clasificación proviene de src/core/symbol\_classifier.py.

## 3\. Arquitectura del Proyecto

src/

  core/

    automaton.py         \-- TraceableAutomaton: base de todos los AFDs

    result.py            \-- ValidationResult: tipo uniforme de resultado

    symbol\_classifier.py \-- Fuente unica de clasificacion de caracteres

  patterns/

    phone\_validator.py   \-- AFD telefono (10-13 digitos)

    email\_validator.py   \-- AFD correo (local@dominio.tld)

    date\_validator.py    \-- AFD fecha (DD/MM/YYYY)

    plate\_validator.py   \-- AFD placa (LLLDDD / LLLDDDL)

    password\_validator.py-- AFD aumentado contrasena (flags \+ longitud)

    url\_validator.py     \-- AFD url (http/https://dominio/ruta)

    nit\_validator.py     \-- AFD nit (NNN.NNN.NNN-D)

    text\_scanner.py      \-- Scanner sin regex

  ui/

    app.py               \-- Aplicacion Tkinter (Parte B)

    forms.py             \-- Formularios con validacion en tiempo real

  main.py                \-- CLI: scan y validate

tests/                   \-- 115 pruebas unitarias, todas pasando

docs/                    \-- Documentacion formal del proyecto

### 

### Componentes del núcleo

**TraceableAutomaton** registra cada transacción en una lista trace, lleva un contador consumed de símbolos procesados y un campo state con el estado actual. El método record(symbol, next\_state, note) siempre incrementa consumed. El método finish(next\_state, note) registra el cierre sin incrementar consumed.

**ValidationResult** estandariza la salida de todos los validadores: accepted, consumed, message, trace y normalized. Los factory methods accept() y reject() garantizan que ningún validador construya el resultado manualmente.

**symbol\_classifier** expone seis funciones puras: is\_letter, is\_digit, is\_alphanumeric, is\_upper\_letter, is\_lower\_letter. Ninguna usa métodos de str de Python; todas usan comparaciones de rango ASCII.

## 4\. Desarrollo — Validadores

### 4.1 Validador de Teléfono

**Patrón reconocido:** número telefónico con 10 a 13 dígitos reales, prefijo internacional \+ opcional, separadores   o \- entre bloques.

**AFD:**

Σ \= { 0-9, \+, \-, ' ' }

Q \= { START, AFTER\_PLUS, IN\_NUMBER, AFTER\_SEPARATOR }

q₀ \= START

Aceptación al cierre: estado ≠ AFTER\_SEPARATOR AND 10 ≤ digitos ≤ 13

**Algoritmo:** el autómata cuenta digitos reales en una variable digits que solo se incrementa al transitar o permanecer en IN\_NUMBER con un dígito. Los separadores no cuentan. La condición de longitud se evalúa al agotar la entrada.

**Justificación de reglas:**

- *Separadores no consecutivos:* AFTER\_SEPARATOR solo acepta dígito. Un segundo separador transita a REJECT de forma determinista.  
- *No termina en separador:* si la cadena se agota en AFTER\_SEPARATOR, el cierre detecta este estado y rechaza. No se requiere lookahead.  
- *Longitud válida:* digits \< 10 OR digits \> 13 cubre el rango internacional real (Colombia: 10 dígitos locales; con prefijo \+57: 12 digitos).

**Tests clave que verifican el algoritmo:**

3001234567         → ACCEPT  (10 dígitos exactos — limite inferior)

300 123 4567       → ACCEPT  (separadores espacio válidos)

\+573001234567      → ACCEPT  (prefijo \+ 12 digitos)

3001234567890      → ACCEPT  (13 dígitos — limite superior)

30012345678901     → REJECT  (14 dígitos — excede limite)

300--1234567       → REJECT  (separadores consecutivos)

3001234-           → REJECT  (termina en separador)

\+ 3001234567       → REJECT  (espacio después de \+, AFTER\_PLUS rechaza no-digito)

### 4.2 Validador de Correo Electrónico

**Patrón reconocido:** local@dominio.tld con separadores internos en la parte local y TLD de al menos 2 letras.

**AFD:**

Σ \= { a-z, A-Z, 0-9, ., \_, \-, @ }

Q \= { START, LOCAL, LOCAL\_SEPARATOR, AFTER\_AT, DOMAIN, DOMAIN\_HYPHEN, AFTER\_DOMAIN\_DOT }

q₀ \= START

Aceptacion al cierre: saw\_at AND saw\_domain\_dot AND tld\_letters ≥ 2

  AND estado ∉ {AFTER\_AT, AFTER\_DOMAIN\_DOT, DOMAIN\_HYPHEN, LOCAL\_SEPARATOR}

**Algoritmo:** cuatro variables de contexto complementan el estado del autómata: saw\_at\_symbol (se vio @), saw\_domain\_dot (el dominio tiene punto), y tld\_letters (contador de letras consecutivas al final del dominio).

**Justificación de reglas:**

- *Parte local no inicia con separador:* START solo acepta is\_alphanumeric. Un punto o guión al inicio transita a REJECT sin excepción.  
- *Sin separadores consecutivos:* LOCAL\_SEPARATOR exige is\_alphanumeric en el próximo simbolo. . o \_ consecutivos van a REJECT.  
- *TLD mínimo 2 letras:* tld\_letters se reinicia a 0 con cada guión o punto. Al cierre, tld\_letters \< 2 rechaza TLDs de una sola letra como .c o .1.  
- *Dominio con punto:* saw\_domain\_dot solo se activa en DOMAIN \--\[.\]--\> AFTER\_DOMAIN\_DOT. Un dominio sin punto (como usuario@localhost) es rechazado.

**Tests clave:**

usuario@example.com          → ACCEPT

user.name-test\_1@sub.dom.com → ACCEPT  (separadores múltiples validos)

a@b.co                       → ACCEPT  (mínimo valido)

.usuario@example.com         → REJECT  (inicia con separador)

user..name@example.com       → REJECT  (separadores consecutivos)

usuario@example.c1           → REJECT  (TLD termina en dígito)

usuario@example-.com         → REJECT  (guión al final de etiqueta)

a@b.c                        → REJECT  (TLD de 1 letra)

### 4.3 Validador de Fecha

**Patrón reconocido:** DD/MM/YYYY con día, mes y año en rangos válidos, incluyendo anio bisiesto gregoriano y limite de rango 1900-2100.

**AFD:**

Σ \= { 0-9, / }

Q \= { START, DAY\_FIRST, AFTER\_DAY, MONTH\_FIRST, MONTH\_SECOND, AFTER\_MONTH,

      YEAR\_1, YEAR\_2, YEAR\_3, YEAR\_4, DATE\_COMPLETE }

q₀ \= START

Aceptación al cierre: estado \== DATE\_COMPLETE AND rangos\_validos

**Algoritmo en dos capas:**

*Capa 1 — sintáctica (AFD):* verifica la forma DD/MM/YYYY caracter por caracter. Los estados son estrictamente lineales (sin bifurcación). Si la estructura es correcta, el autómata llega a DATE\_COMPLETE.

*Capa 2 — semantica (post-recorrido):* sobre los valores numéricos extraídos de posiciones fijas en la cadena original (text\[0:2\], text\[3:5\], text\[6:10\]) se verifican:

1 ≤ mes ≤ 12

1900 ≤ anio ≤ 2100

1 ≤ dia ≤ max\_dias(mes, anio)

**Regla de año bisiesto:**

bisiesto(y) \= (y % 4 \== 0 AND y % 100 \!= 0\) OR (y % 400 \== 0\)

**Justificación:**

- *Separación sintaxis/semántica:* el AFD garantiza que la cadena tiene exactamente 10 caracteres con / en posiciones 2 y 5\. Luego la capa semántica extrae los valores numéricos con certeza de que son exactamente 2, 2 y 4 dígitos.  
- *DATE\_COMPLETE rechaza extra:* la transicion DATE\_COMPLETE \--\[cualquiera\]--\> REJECT es total sobre todo el alfabeto, bloqueando cadenas como 15/08/2024x.  
- *1900 no bisiesto:* 1900 % 4 \== 0 (True) AND 1900 % 100 \!= 0 (False) → primer término False. 1900 % 400 \== 0 (False) → segundo término False. Resultado: no bisiesto.

**Tests clave:**

15/08/2024   → ACCEPT  (estandar)

29/02/2024   → ACCEPT  (2024 es bisiesto)

29/02/2000   → ACCEPT  (2000 divisible entre 400\)

28/02/1900   → ACCEPT  (1900 no bisiesto — max dia \= 28\)

29/02/1900   → REJECT  (confirma que 1900 no es bisiesto)

29/02/2023   → REJECT  (2023 no bisiesto)

31/04/2024   → REJECT  (abril tiene 30 dias)

15/13/2024   → REJECT  (mes 13 no existe)

15/08/2024x  → REJECT  (simbolo extra — DATE\_COMPLETE rechaza)

### 4.4 Validador de Placa Vehicular

**Patrón reconocido:** placa colombiana en formato carro (LLLDDD o LLL-DDD) o moto (LLLDDDL o LLL-DDDL). Solo letras mayúsculas A-Z y dígitos 0-9.

**AFD:**

Σ \= { A-Z, 0-9, \- }

Q \= { START, L1, L2, L3, AFTER\_L3, D1, D2, D3, AFTER\_D3, L4 }

q₀ \= START

Aceptación al cierre: estado \== D3 (carro) OR estado \== L4 (moto)

**Algoritmo:** el mismo AFD distingue los dos formatos en el estado de cierre. El guión es absorbido por estados intermedios (AFTER\_L3, AFTER\_D3) que no contribuyen a la cadena normalizada. is\_upper\_letter garantiza que solo letras A-Z son aceptadas.

**Justificación:**

- *Letras minúsculas rechazadas:* is\_upper\_letter(s) \= is\_letter(s) AND "A" ≤ s ≤ "Z". Las minúsculas pasan is\_letter pero fallan el rango. No hay un caso especial.  
- *Guión no suma al normalized:* el guión transita a AFTER\_L3 o AFTER\_D3 sin appendear el símbolo al arreglo normalized. La cadena normalizada es siempre ABC123.  
- *Un solo AFD para dos formatos:* D3 es bifurcación natural. Desde D3, una letra mayúscula va a L4 (moto); agotar la entrada en D3 es aceptación de carro.


  
**Tests clave:**

ABC123   → ACCEPT  (carro sin guión)

ABC-123  → ACCEPT  (carro con guión, normalized="ABC123")

XYZ456A  → ACCEPT  (moto sin guión)

XYZ-456A → ACCEPT  (moto con guión)

abc123   → REJECT  (letras minúsculas)

AB123    → REJECT  (solo 2 letras)

ABC12    → REJECT  (solo 2 dígitos — termina en D2)

ABC123-  → REJECT  (guion final — termina en AFTER\_D3)

ABC--123 → REJECT  (doble guión — AFTER\_L3 rechaza segundo \-)

### 4.5 Validador de Contraseña Segura

**Patrón reconocido:** cadena de longitud mínima 8 con al menos una letra mayúscula, una minúscula, un dígito y un símbolo del conjunto \! @ \# $ % & \* \- \_.

**AFD aumentado con vector de banderas:**

Σ \= { a-z } ∪ { A-Z } ∪ { 0-9 } ∪ { \!, @, \#, $, %, &, \*, \-, \_ }

Q\_efectivo \= SCANNING × {True,False}⁴ × ℕ

q₀ \= (SCANNING, False, False, False, False, 0\)

Aceptación al cierre: length ≥ 8 AND todas las banderas True

**Algoritmo:** en un único pase, el autómata activa cada bandera la primera vez que encuentra el tipo de carácter correspondiente. Al agotar la entrada, evalúa simultáneamente longitud y banderas. Si cualquier condición falla, el mensaje de rechazo lista específicamente cuáles condiciones no se cumplieron.

**Justificación:**

- *Rechazo inmediato por carácter invalido:* un símbolo fuera de Σ transita a REJECT sin continuar. Esto es formalmente correcto: la contraseña completa es inválida si contiene símbolos no permitidos.  
- *Mensaje de rechazo enumerativo:* \_build\_rejection\_message evalúa independientemente cada condición y lista todas las que fallaron. Esto cumple el requisito del documento de "emitir mensajes adecuados cuando se detecten errores".  
- *Privacy en normalized:* el campo normalized es siempre "". La contraseña no debe ser reproducida en ningún campo de salida.

**Por que no se integra al scanner:** no existe un delimitador natural para contraseñas en texto libre. La validación aplica solo en formularios donde el campo es atómico.

**Tests clave:**

Secure@1     → ACCEPT  (exactamente 8 chars, todas las banderas)

Abcde@1z     → ACCEPT  (límite inferior de longitud)

Ab1@         → REJECT  (4 chars — longitud insuficiente)

Abc@1zX      → REJECT  (7 chars — todas las banderas pero longitud insuficiente)

secure@1abc  → REJECT  (sin mayúscula)

SecurePass1  → REJECT  (sin símbolo especial)

Secure^1ab   → REJECT  (^ fuera del alfabeto — rechazo inmediato)

abcdefgh     → REJECT  (8 chars pero sin mayuscula, digito ni símbolo)

### 4.6 Validador de URL

**Patron reconocido:** URL con protocolo http o https (case insensitive), dominio con al menos un punto, y ruta/query/fragmento opcionales.

**AFD:**

Σ \= { a-z, A-Z, 0-9, :, /, ., \-, \_, ?, \=, &, \#, \~, %, \+, @ }

Q \= { START, PROTO\_H, PROTO\_HT, PROTO\_HTT, PROTO\_HTTP, PROTO\_HTTPS,

      COLON, SLASH1, SLASH2, DOMAIN, DOMAIN\_HYPHEN, DOMAIN\_DOT, PATH }

q₀ \= START

Aceptación al cierre:

  (estado \== DOMAIN AND saw\_domain\_dot) OR estado \== PATH

**Algoritmo:** los estados PROTO\_\* reconocen el protocolo como una cadena fija de prefijo. DOMAIN y sus estados auxiliares validan el dominio con la misma lógica que el validador de correo para la parte del dominio. PATH acepta todos los caracteres URL válidos en la ruta.

**Justificación:**

- *Protocolo case insensitive:* las transiciones comprueban symbol in {"h","H"}, symbol in {"t","T"}, etc. No se usa .lower() para evitar crear nuevos objetos string; las comparaciones de conjunto son O(1).  
- *Dominio con punto obligatorio:* saw\_domain\_dot cumple la misma función que en el validador de correo. Solo se activa en DOMAIN\_DOT \--\[letra/digito\]--\> DOMAIN.  
- *PATH acepta amplio conjunto:* incluye /, ?, \=, &, \#, \~, %, \+, @, cubriendo rutas REST, query strings y autenticación básica.  
- *Limpieza en scanner:* .rstrip(".,\!)") elimina puntuación de oración antes de intentar la validación, evitando falsos negativos por punto final de oración.


  
**Tests clave:**

http://example.com              → ACCEPT

https://www.google.com          → ACCEPT

https://example.com/search?q=x → ACCEPT  (ruta \+ query)

HTTP://example.com              → ACCEPT  (mayusculas en protocolo)

ftp://example.com               → REJECT  (protocolo invalido)

http://example                  → REJECT  (sin punto en dominio)

http://example-.com             → REJECT  (dominio termina en guion)

http://.example.com             → REJECT  (dominio inicia con punto)

### 4.7 Validador de NIT

**Patrón reconocido:** Número de Identificación Tributaria colombiano con formato exacto NNN.NNN.NNN-D.

**AFD:**

Σ \= { 0-9, ., \- }

Q \= { START, D1, D2, D3, DOT1, D4, D5, D6, DOT2, D7, D8, D9, HYPHEN, CHECK }

q₀ \= START

Aceptación al cierre: estado \== CHECK

**Algoritmo:** el camino de aceptación es completamente lineal — 13 transiciones en secuencia sin bifurcación. Cada estado acepta exactamente un tipo de símbolo. Es el AFD más simple del proyecto y el más trazable en cuaderno.

**Justificación:**

- *Formato fijo como ventaja:* el NIT siempre tiene 13 caracteres con separadores en posiciones fijas (4 y 8). El AFD lineal garantiza exactamente eso sin contadores ni variables adicionales.  
- *Normalización sin separadores:* digits acumula solo los 10 dígitos reales (9 del NIT \+ 1 verificador). La cadena normalizada "9001234567" es útil para búsquedas en bases de datos que almacenan NITs sin formato.  
- *Sin colisión con otros patrones:* el NIT usa . como separador, lo que lo distingue del teléfono (usa   y \-), la fecha (usa /) y el correo (requiere @).

**Tests clave:**

900.123.456-7  → ACCEPT  (formato completo)

000.000.000-0  → ACCEPT  (digitos mínimos)

900123456-7    → REJECT  (sin puntos — D3 espera \`.\`)

900.123.4567   → REJECT  (sin guión — D9 espera \`-\`)

9AB.123.456-7  → REJECT  (letras en grupo)

900.123.456-77 → REJECT  (doble verificador — CHECK rechaza extra)

90.123.456-7   → REJECT  (grupo de 2 dígitos — D2 espera digito, recibe \`.\`)

## 5\. Scanner de Texto Libre

### Funcionamiento

for i in range(len(texto)):

    match \= (

        \_try\_date(text, i)

        or \_try\_email(text, i)

        or \_try\_url(text, i)

        or \_try\_phone(text, i)

        or \_try\_nit(text, i)

        or \_try\_plate(text, i)

    )

    if match:

        matches.append(match)

        i \= match.end  \# avanza después de la coincidencia

    else:

        i \+= 1         \# avanza un carácter

Cada \_try\_\* Colecta un candidato con \_collect (acumula mientras el predicado de caracteres se cumpla), aplica limpieza de puntuación de oración, y llama al validador del patrón. Si el resultado es aceptado, retorna un PatternMatch.

### Orden de prioridad y por que es correcto

| Posición | Patrón | Condición de inicio | Conflicto evitado |
| :---- | :---- | :---- | :---- |
| 1 | fecha | dígito | La fecha tiene formato fijo de 10 chars con / — no confundible con teléfono |
| 2 | email | alfanumérico | El @ es el discriminador principal |
| 3 | url | h o H | Email tiene prioridad; URL solo llega si email falla |
| 4 | teléfono | dígito o \+ | La fecha ya fue intentada y rechazada |
| 5 | nit | dígito | El teléfono falla en NIT (el . no es char de teléfono) |
| 6 | placa | letra mayúscula | Único patrón que empieza con mayuscula |

## 6\. Pruebas y Casos de Uso

El proyecto cuenta con **115 pruebas unitarias** distribuidas en 7 archivos:

| Archivo | Pruebas | Cobertura principal |
| :---- | :---- | :---- |
| test\_phone\_validator.py | 5 | Estructura \+ longitud \+ separadores |
| test\_email\_validator.py | 7 | Estructura \+ TLD \+ dominio |
| test\_date\_validator.py | 9 | Estructura \+ rangos \+ bisiesto |
| test\_plate\_validator.py | 17 | Carro \+ moto \+ guión \+ errores |
| test\_password\_validator.py | 14 | Banderas \+ longitud \+ alfabeto |
| test\_url\_validator.py | 22 | Protocolo \+ dominio \+ ruta \+ query |
| test\_nit\_validator.py | 16 | Grupos \+ separadores \+ verificador |
| test\_text\_scanner.py | 25 | Todos los patrones en texto \+ prioridad |

Todos los tests se ejecutan con python3 \-m pytest tests/ \-q y pasan en menos de 0.2s.

### Criterio de diseño de los casos de prueba

Cada conjunto de pruebas cubre tres categorías:

1. **Válidos:** cadenas que deben ser aceptadas — verifican el camino feliz del AFD.  
2. **Inválidos:** cadenas que violan exactamente una regla — verifican que el AFD rechaza correctamente en el estado adecuado.  
3. **Borde:** cadenas en el límite de lo aceptable — verifican que los rangos son exactos (longitud mínima, longitud máxima, fecha límite de calendario, etc.).

### Ejemplo de traza de aceptación — teléfono 3001234567

START   \--\['3'\]--\> IN\_NUMBER: Empieza la secuencia principal de dígitos.

IN\_NUMBER \--\['0'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['0'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['1'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['2'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['3'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['4'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['5'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['6'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\['7'\]--\> IN\_NUMBER: Se acumula un nuevo dígito del teléfono.

IN\_NUMBER \--\[END\]--\> ACCEPT: teléfono válido con 10 dígitos.

### Ejemplo de traza de rechazo — teléfono 300--1234567

START     \--\['3'\]--\> IN\_NUMBER: Empieza la secuencia.

IN\_NUMBER \--\['0'\]--\> IN\_NUMBER: digito.

IN\_NUMBER \--\['0'\]--\> IN\_NUMBER: digito.

IN\_NUMBER \--\['-'\]--\> AFTER\_SEPARATOR: Se separan bloques numéricos.

AFTER\_SEPARATOR \--\['-'\]--\> REJECT: No se permiten separadores consecutivos.

## 7\. Conclusiones

1. **Los AFDs implementados son formalmente correctos:** cada validador tiene estados explícitos, alfabeto finito, función de transición determinista y condición de aceptación verificable. Todos pueden dibujarse en el cuaderno como grafos de transición.  
     
2. **El recorrido caracter por caracter es suficiente:** ninguno de los siete patrones requiere retroceso ni lookahead. El teléfono fue corregido durante el proyecto para eliminar un lookahead que usaba index \== len(text) \- 1; la versión final verifica el estado AFTER\_SEPARATOR al cierre.  
     
3. **La separación de responsabilidades simplifica el mantenimiento:** el núcleo (automaton, result, symbol\_classifier) es independiente de los patrones. Agregar un nuevo validador solo requiere crear un archivo en src/patterns/ e importarlo en el scanner y en el CLI.  
     
4. **Las 115 pruebas validan las reglas formales:** cada test corresponde a una regla del AFD — no son pruebas arbitrarias sino verificaciones precisas de transiciones y condiciones de cierre.  
     
5. **El scanner sin regex demuestra que los AFDs son el mecanismo subyacente de los patrones:** la implementación manual hace visible lo que las librerías de expresiones regulares esconden.

## 8\. Guia de Uso

### Requisitos

Python 3.11 o superior

pytest (para correr los tests)

### Instalación

git clone https://github.com/lyc4nthrope/ProyectoFinal\_TLF.git

cd ProyectoFinal\_TLF

### Ejecutar los tests

python3 \-m pytest tests/ \-q

### Subcomando scan — buscar patrones en texto libre

python3 \-m src.main scan "Texto con patrones a detectar"

Ejemplos:

python3 \-m src.main scan "Llama al 3001234567 o escribe a user@example.com"

\# \[phone\] start=9 end=19 raw='3001234567' normalized='3001234567'

\# \[email\] start=33 end=51 raw='user@example.com' normalized='user@example.com'

python3 \-m src.main scan "Web: https://example.com NIT: 900.123.456-7"

\# \[url\] start=5 end=24 raw='https://example.com' normalized='https://example.com'

\# \[nit\] start=30 end=43 raw='900.123.456-7' normalized='9001234567'

python3 \-m src.main scan "Reunion el 15/08/2024. Placa ABC-123."

\# \[date\] start=11 end=21 raw='15/08/2024' normalized='15/08/2024'

\# \[plate\] start=30 end=37 raw='ABC-123' normalized='ABC123'

### Subcomando validate — validar una cadena específica

python3 \-m src.main validate \<tipo\> "\<cadena\>"

Tipos disponibles: phone, email, date, plate, password, url, nit

Ejemplos:

python3 \-m src.main validate phone "3001234567"

\# aceptado: True

\# mensaje:  Telefono válido.

\# traza: ...

python3 \-m src.main validate date "29/02/2023"

\# aceptado: False

\# mensaje:  El día de la fecha es invalido para el mes dado.

python3 \-m src.main validate password "Secure@1"

\# aceptado: True

\# mensaje:  Contraseña válida.

python3 \-m src.main validate nit "900.123.456-7"

\# aceptado: True

\# mensaje:  NIT válido.  
