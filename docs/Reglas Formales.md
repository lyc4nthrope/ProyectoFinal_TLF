**Reglas Formales**

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

## Teléfono

### Alfabeto permitido

- Dígitos: `0-9`  
- Separadores: espacio y guión `-`  
- Prefijo opcional: `+`


### Regla estructural

El teléfono puede empezar con `+` o directamente con un dígito. Después de eso, la cadena debe avanzar por bloques numéricos. Los separadores solo sirven para dividir bloques y nunca pueden:

- aparecer dos veces seguidas  
- aparecer al final  
- reemplazar dígitos obligatorios

### Restricción de longitud

La cadena debe contener entre `10` y `13` dígitos reales. Los separadores no cuentan como dígitos.

### Idea de estados

- `START`: inicio del análisis  
- `AFTER_PLUS`: ya se vio `+` y ahora debe venir un dígito  
- `IN_NUMBER`: se está leyendo una secuencia numérica válida  
- `AFTER_SEPARATOR`: se leyó un separador y debe venir un dígito  
- `ACCEPT`: la cadena terminó con una cantidad válida de dígitos  
- `REJECT`: la cadena viola una regla formal

### Ejemplos válidos

- `3001234567`  
- `300 123 4567`  
- `300-123-4567`  
- `+57 300-123-4567`

### Ejemplos inválidos

- `300--1234567`  
- `+ 3001234567`  
- `3001234567-`  
- `12345`  
- `30012A4567`

## 

## Correo electrónico

### Alfabeto permitido

- Letras ASCII: `a-z`, `A-Z`  
- Dígitos: `0-9`  
- Separadores locales: `.`, `_`, `-`  
- Separador global: `@`  
- Separador de dominio: `.`  
- Guión interno de dominio: `-`

### Regla estructural

El correo se divide en dos partes: local y dominio. La parte local debe iniciar con letra o dígito. Dentro de la parte local se permiten letras, dígitos y algunos separadores, pero:

- no puede comenzar con separador  
- no puede terminar con separador  
- no puede tener separadores consecutivos

Después debe aparecer exactamente un `@`. El dominio debe estar formado por etiquetas separadas por punto. Cada etiqueta del dominio debe iniciar con letra o dígito. El dominio puede usar guiones internos, pero no puede:

- empezar con punto  
- tener etiquetas vacías  
- terminar con guión

### Restricción de cierre

El dominio debe contener al menos un punto. La última etiqueta debe terminar con al menos `2` letras.

### Idea de estados

- `START`: inicio del análisis  
- `LOCAL`: lectura normal de la parte local  
- `LOCAL_SEPARATOR`: se leyó un separador local y debe venir un símbolo válido  
- `AFTER_AT`: ya se vio `@` y debe iniciar el dominio  
- `DOMAIN`: lectura normal de una etiqueta del dominio  
- `DOMAIN_HYPHEN`: se leyó un guión y la etiqueta debe continuar  
- `AFTER_DOMAIN_DOT`: se cerró una etiqueta y debe iniciar otra  
- `ACCEPT`: correo valido  
- `REJECT`: el correo viola una regla formal

### Ejemplos válidos

- `usuario@example.com`  
- `user.name-test_1@sub.domain.com`  
- `a1@correo.co`

### Ejemplos inválidos

- `.usuario@example.com`  
- `user..name@example.com`  
- `usuario.example.com`  
- `usuario@.com`  
- `usuario@example.c1`

## Fecha

### Alfabeto permitido

- Dígitos: `0-9`  
- Separador único: `/`

### Regla estructural

La fecha debe tener exactamente el formato `DD/MM/YYYY`. Eso significa:

- `DD`: dia con exactamente 2 dígitos  
- `MM`: mes con exactamente 2 dígitos  
- `YYYY`: año con exactamente 4 dígitos

No se aceptan:

- otros separadores  
- espacios  
- bloques incompletos  
- símbolos extra al final

### Restricciones de rango

- El mes debe estar entre `01` y `12`.  
- El año debe estar entre `1900` y `2100`.  
- El día debe respetar el máximo real de su mes.  
- Febrero usa validación básica de anio bisiesto.

### Idea de estados

- `START`: inicio del análisis  
- `DAY_FIRST`: primer dígito del dia  
- `AFTER_DAY`: día completo, se espera `/`  
- `MONTH_FIRST`: primer dígito del mes  
- `MONTH_SECOND`: segundo dígito del mes  
- `AFTER_MONTH`: mes completo, se espera `/`  
- `YEAR_1`: primer dígito del año  
- `YEAR_2`: segundo dígito del año  
- `YEAR_3`: tercer dígito del año  
- `YEAR_4`: cuarto dígito del año  
- `DATE_COMPLETE`: estructura completa  
- `ACCEPT`: fecha válida  
- `REJECT`: la fecha viola una regla formal

### Ejemplos válidos

- `15/08/2024`  
- `01/01/2000`  
- `29/02/2024`

### Ejemplos inválidos

- `1/08/2024`  
- `15-08-2024`  
- `31/04/2024`  
- `29/02/2023`  
- `15/13/2024`

## Placa vehicular

### Alfabeto permitido

- Letras: `A-Z` (solo mayusculas)  
- Dígitos: `0-9`  
- Separador opcional: `-`

### Regla estructural

La placa sigue uno de dos formatos según el tipo de vehiculo:

- **Carro**: exactamente 3 letras seguidas de 3 dígitos — `LLLDDD` o `LLL-DDD`  
- **Moto**: exactamente 3 letras, 3 dígitos y 1 letra al final — `LLLDDDL` o `LLL-DDDL`

El guión es opcional y sólo puede aparecer entre el bloque de letras y el bloque de dígitos. No se permiten:

- letras minúsculas  
- más de un guión  
- caracteres distintos a letras, dígitos y guion  
- símbolos extra al final

### Restricciones

- Las letras deben pertenecer estrictamente al rango `A-Z`.  
- Los dígitos deben pertenecer al rango `0-9`.  
- La longitud total sin guión es de 6 caracteres (carro) o 7 caracteres (moto).  
- La cadena no puede terminar con el guión.

### Idea de estados

- `START`: inicio del análisis  
- `L1`, `L2`, `L3`: primera, segunda y tercera letra del bloque inicial  
- `AFTER_L3`: se leyó el guión opcional después de las tres letras  
- `D1`, `D2`, `D3`: primer, segundo y tercer dígito  
- `AFTER_D3`: se leyó el guión opcional después de los tres dígitos (solo en moto)  
- `L4`: séptima letra opcional (moto)  
- `ACCEPT`: cadena válida  
- `REJECT`: cadena viola una regla formal

### Ejemplos válidos

- `ABC123` — carro sin guión  
- `ABC-123` — carro con guión  
- `XYZ456A` — moto sin guión  
- `XYZ-456A` — moto con guión separando letras y dígitos

### Ejemplos inválidos

- `abc123` — letras minúsculas no permitidas  
- `AB123` — solo dos letras iniciales  
- `ABC12` — solo dos dígitos  
- `ABC123X9` — carácter extra al final  
- `ABC.123` — símbolo no permitido

## URL

### Alfabeto permitido

- Letras ASCII: `a-z`, `A-Z`  
- Dígitos: `0-9`  
- Delimitadores de protocolo: `:`, `/`  
- Separadores de dominio: `.`, `-`  
- Caracteres de ruta y query: `_`, `?`, `=`, `&`, `#`, `~`, `%`, `+`, `@`

### Regla estructural

La URL debe comenzar con el protocolo `http` o `https` (mayusculas o minusculas). Después del protocolo debe aparecer exactamente `://`. El dominio sigue inmediatamente y debe contener al menos un punto para separar el nombre del TLD. El dominio no puede:

- empezar con punto  
- terminar en guión  
- tener etiquetas vacías (dos puntos consecutivos)

La ruta es opcional. Si aparece, puede contener letras, dígitos y los caracteres URL válidos (`/`, `-`, `_`, `.`, `?`, `=`, `&`, `#`, `~`, `%`, `+`).

### Restricciones de cierre

- El dominio debe haber visto al menos un punto (`saw_domain_dot = True`).  
- El autómata debe terminar en estado `DOMAIN` (URL sin ruta) o `PATH` (con ruta).

### Idea de estados

- `START`: inicio del análisis  
- `PROTO_H` → `PROTO_HT` → `PROTO_HTT` → `PROTO_HTTP`: reconocen el prefijo `http`  
- `PROTO_HTTPS`: reconoce la extensión `s` del protocolo seguro  
- `COLON`: se leyó `:` tras el protocolo  
- `SLASH1`, `SLASH2`: se leen los dos slashes del separador `://`  
- `DOMAIN`: lectura normal del dominio  
- `DOMAIN_HYPHEN`: se leyó guión interno — la etiqueta debe continuar  
- `DOMAIN_DOT`: se leyó punto — debe iniciar una nueva etiqueta  
- `PATH`: lectura de la ruta, query y fragmento  
- `REJECT`: cadena invalida

### Ejemplos válidos

- `http://example.com`  
- `https://www.google.com`  
- `https://example.com/path?q=hola&lang=es`  
- `http://a.bc`

### Ejemplos inválidos

- `ftp://example.com` — protocolo no permitido  
- `http://example` — dominio sin punto  
- `http:/example.com` — falta un slash  
- `http://example-.com` — dominio termina en guion

## NIT (Numero de Identificacion Tributaria)

### Alfabeto permitido

- Dígitos: `0-9`  
- Separadores de grupo: `.`  
- Separador de verificador: `-`

### Regla estructural

El NIT tiene formato fijo `NNN.NNN.NNN-D`:

- Tres grupos de exactamente tres dígitos cada uno.  
- Cada par de grupos separados por un punto `.`.  
- Un guión `-` separa el tercer grupo del dígito verificador.  
- El dígito verificador es exactamente un dígito.  
- La cadena tiene una longitud fija de 13 caracteres.

No se aceptan:

- grupos con menos o más de 3 digitos  
- separadores distintos a `.` entre grupos o a `-` antes del verificador  
- caracteres extra al final  
- letras en cualquier posición

### Restricción de cierre

El autómata debe terminar en el estado `CHECK` (dígito verificador completo). Cualquier otro estado al agotar la entrada produce rechazo.

### Idea de estados

- `START`: inicio del análisis  
- `D1`, `D2`, `D3`: dígitos del primer grupo  
- `DOT1`: primer separador `.`  
- `D4`, `D5`, `D6`: dígitos del segundo grupo  
- `DOT2`: segundo separador `.`  
- `D7`, `D8`, `D9`: dígitos del tercer grupo  
- `HYPHEN`: separador `-` antes del verificador  
- `CHECK`: digito verificador leído — estado aceptante al cierre  
- `REJECT`: cadena invalida

### Ejemplos válidos

- `900.123.456-7`  
- `000.000.000-0`  
- `999.999.999-9`

### Ejemplos inválidos

- `900123456-7` — sin puntos separadores  
- `900.123.4567` — sin guión antes del verificador  
- `9AB.123.456-7` — letras en el primer grupo

## Contraseña segura

### Alfabeto permitido

- Letras minusculas: `a-z`  
- Letras mayúsculas: `A-Z`  
- Dígitos: `0-9`  
- Símbolos especiales exactos: `! @ # $ % & * - _`

### Regla estructural

La contraseña se valida en un único recorrido caracter por caracter. El autómata mantiene cuatro banderas booleanas que se activan a medida que aparecen los símbolos requeridos:

- `has_upper`: se activa al encontrar la primera letra mayúscula.  
- `has_lower`: se activa al encontrar la primera letra minúscula.  
- `has_digit`: se activa al encontrar el primer dígito.  
- `has_special`: se activa al encontrar el primer símbolo del conjunto permitido.

La contraseña se acepta al agotar la entrada si se cumplen todas estas condiciones:

1. Longitud mínima de 8 caracteres.  
2. `has_upper = true`  
3. `has_lower = true`  
4. `has_digit = true`  
5. `has_special = true`

Si cualquier carácter no pertenece al alfabeto permitido, se rechaza de inmediato.

### Nota importante

La contraseña NO se busca en texto libre. Es un dato de entrada atómico validado únicamente en formularios interactivos (Parte B del proyecto).

### Idea de estados

- `START`: inicio del recorrido  
- `SCANNING`: estado único de recorrido, aumentado con las cuatro banderas y un contador de longitud  
- `ACCEPT`: todas las condiciones se cumplen al agotar la entrada  
- `REJECT`: alguna condición falla o aparece un caracter fuera del alfabeto

### Ejemplos válidos

- `Secure@1` — 8 caracteres, cumple las cuatro condiciones  
- `MyP@ssw0rd!` — larga, todas las banderas activas  
- `Abcde@1z` — exactamente 8 caracteres en el límite inferior

### Ejemplos inválidos

- `Ab1@` — solo 4 caracteres, longitud insuficiente  
- `secure@1abc` — sin letra mayúscula  
- `SECURE@1ABC` — sin letra minúscula  
- `SecurePass@` — sin digito  
- `SecurePass1` — sin símbolo especial  
- `Secure^1ab` — `^` no pertenece al conjunto de símbolos permitidos

