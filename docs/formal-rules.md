# Formal Rules

## Telefono

### Alfabeto permitido

- Digitos: `0-9`
- Separadores: espacio y guion `-`
- Prefijo opcional: `+`

### Regla estructural

El telefono puede empezar con `+` o directamente con un digito.
Despues de eso, la cadena debe avanzar por bloques numericos.
Los separadores solo sirven para dividir bloques y nunca pueden:

- aparecer dos veces seguidas
- aparecer al final
- reemplazar digitos obligatorios

### Restriccion de longitud

La cadena debe contener entre `10` y `13` digitos reales.
Los separadores no cuentan como digitos.

### Idea de estados

- `START`: inicio del analisis
- `AFTER_PLUS`: ya se vio `+` y ahora debe venir un digito
- `IN_NUMBER`: se esta leyendo una secuencia numerica valida
- `AFTER_SEPARATOR`: se leyo un separador y debe venir un digito
- `ACCEPT`: la cadena termino con una cantidad valida de digitos
- `REJECT`: la cadena viola una regla formal

### Ejemplos validos

- `3001234567`
- `300 123 4567`
- `300-123-4567`
- `+57 300-123-4567`

### Ejemplos invalidos

- `300--1234567`
- `+ 3001234567`
- `3001234567-`
- `12345`
- `30012A4567`

## Correo electronico

### Alfabeto permitido

- Letras ASCII: `a-z`, `A-Z`
- Digitos: `0-9`
- Separadores locales: `.`, `_`, `-`
- Separador global: `@`
- Separador de dominio: `.`
- Guion interno de dominio: `-`

### Regla estructural

El correo se divide en dos partes: local y dominio.
La parte local debe iniciar con letra o digito.
Dentro de la parte local se permiten letras, digitos y algunos separadores, pero:

- no puede comenzar con separador
- no puede terminar con separador
- no puede tener separadores consecutivos

Despues debe aparecer exactamente un `@`.
El dominio debe estar formado por etiquetas separadas por punto.
Cada etiqueta del dominio debe iniciar con letra o digito.
El dominio puede usar guiones internos, pero no puede:

- empezar con punto
- tener etiquetas vacias
- terminar con guion

### Restriccion de cierre

El dominio debe contener al menos un punto.
La ultima etiqueta debe terminar con al menos `2` letras.

### Idea de estados

- `START`: inicio del analisis
- `LOCAL`: lectura normal de la parte local
- `LOCAL_SEPARATOR`: se leyo un separador local y debe venir un simbolo valido
- `AFTER_AT`: ya se vio `@` y debe iniciar el dominio
- `DOMAIN`: lectura normal de una etiqueta del dominio
- `DOMAIN_HYPHEN`: se leyo un guion y la etiqueta debe continuar
- `AFTER_DOMAIN_DOT`: se cerro una etiqueta y debe iniciar otra
- `ACCEPT`: correo valido
- `REJECT`: el correo viola una regla formal

### Ejemplos validos

- `usuario@example.com`
- `user.name-test_1@sub.domain.com`
- `a1@correo.co`

### Ejemplos invalidos

- `.usuario@example.com`
- `user..name@example.com`
- `usuario.example.com`
- `usuario@.com`
- `usuario@example.c1`

## Fecha

### Alfabeto permitido

- Digitos: `0-9`
- Separador unico: `/`

### Regla estructural

La fecha debe tener exactamente el formato `DD/MM/YYYY`.
Eso significa:

- `DD`: dia con exactamente 2 digitos
- `MM`: mes con exactamente 2 digitos
- `YYYY`: anio con exactamente 4 digitos

No se aceptan:

- otros separadores
- espacios
- bloques incompletos
- simbolos extra al final

### Restricciones de rango

- El mes debe estar entre `01` y `12`.
- El anio debe estar entre `1900` y `2100`.
- El dia debe respetar el maximo real de su mes.
- Febrero usa validacion basica de anio bisiesto.

### Idea de estados

- `START`: inicio del analisis
- `DAY_FIRST`: primer digito del dia
- `AFTER_DAY`: dia completo, se espera `/`
- `MONTH_FIRST`: primer digito del mes
- `MONTH_SECOND`: segundo digito del mes
- `AFTER_MONTH`: mes completo, se espera `/`
- `YEAR_1`: primer digito del anio
- `YEAR_2`: segundo digito del anio
- `YEAR_3`: tercer digito del anio
- `YEAR_4`: cuarto digito del anio
- `DATE_COMPLETE`: estructura completa
- `ACCEPT`: fecha valida
- `REJECT`: la fecha viola una regla formal

### Ejemplos validos

- `15/08/2024`
- `01/01/2000`
- `29/02/2024`

### Ejemplos invalidos

- `1/08/2024`
- `15-08-2024`
- `31/04/2024`
- `29/02/2023`
- `15/13/2024`

## Placa vehicular

### Alfabeto permitido

- Letras: `A-Z` (solo mayusculas)
- Digitos: `0-9`
- Separador opcional: `-`

### Regla estructural

La placa sigue uno de dos formatos segun el tipo de vehiculo:

- **Carro**: exactamente 3 letras seguidas de 3 digitos — `LLLDDD` o `LLL-DDD`
- **Moto**: exactamente 3 letras, 3 digitos y 1 letra al final — `LLLDDDL` o `LLL-DDDL`

El guion es opcional y solo puede aparecer entre el bloque de letras y el bloque de digitos.
No se permiten:

- letras minusculas
- mas de un guion
- caracteres distintos a letras, digitos y guion
- simbolos extra al final

### Restricciones

- Las letras deben pertenecer estrictamente al rango `A-Z`.
- Los digitos deben pertenecer al rango `0-9`.
- La longitud total sin guion es de 6 caracteres (carro) o 7 caracteres (moto).
- La cadena no puede terminar con guion.

### Idea de estados

- `START`: inicio del analisis
- `L1`, `L2`, `L3`: primera, segunda y tercera letra del bloque inicial
- `AFTER_L3`: se leyo el guion opcional despues de las tres letras
- `D1`, `D2`, `D3`: primer, segundo y tercer digito
- `AFTER_D3`: se leyo el guion opcional despues de los tres digitos (solo en moto)
- `L4`: septima letra opcional (moto)
- `ACCEPT`: cadena valida
- `REJECT`: cadena viola una regla formal

### Ejemplos validos

- `ABC123` — carro sin guion
- `ABC-123` — carro con guion
- `XYZ456A` — moto sin guion
- `XYZ-456A` — moto con guion separando letras y digitos

### Ejemplos invalidos

- `abc123` — letras minusculas no permitidas
- `AB123` — solo dos letras iniciales
- `ABC12` — solo dos digitos
- `ABC123X9` — caracter extra al final
- `ABC.123` — simbolo no permitido

## URL

### Alfabeto permitido

- Letras ASCII: `a-z`, `A-Z`
- Digitos: `0-9`
- Delimitadores de protocolo: `:`, `/`
- Separadores de dominio: `.`, `-`
- Caracteres de ruta y query: `_`, `?`, `=`, `&`, `#`, `~`, `%`, `+`, `@`

### Regla estructural

La URL debe comenzar con el protocolo `http` o `https` (mayusculas o minusculas).
Despues del protocolo debe aparecer exactamente `://`.
El dominio sigue inmediatamente y debe contener al menos un punto para separar
el nombre del TLD. El dominio no puede:

- empezar con punto
- terminar en guion
- tener etiquetas vacias (dos puntos consecutivos)

La ruta es opcional. Si aparece, puede contener letras, digitos y los caracteres
URL validos (`/`, `-`, `_`, `.`, `?`, `=`, `&`, `#`, `~`, `%`, `+`).

### Restricciones de cierre

- El dominio debe haber visto al menos un punto (`saw_domain_dot = True`).
- El automata debe terminar en estado `DOMAIN` (URL sin ruta) o `PATH` (con ruta).

### Idea de estados

- `START`: inicio del analisis
- `PROTO_H` → `PROTO_HT` → `PROTO_HTT` → `PROTO_HTTP`: reconocen el prefijo `http`
- `PROTO_HTTPS`: reconoce la extension `s` del protocolo seguro
- `COLON`: se leyo `:` tras el protocolo
- `SLASH1`, `SLASH2`: se leen los dos slashes del separador `://`
- `DOMAIN`: lectura normal del dominio
- `DOMAIN_HYPHEN`: se leyo guion interno — la etiqueta debe continuar
- `DOMAIN_DOT`: se leyo punto — debe iniciar una nueva etiqueta
- `PATH`: lectura de la ruta, query y fragmento
- `REJECT`: cadena invalida

### Ejemplos validos

- `http://example.com`
- `https://www.google.com`
- `https://example.com/path?q=hola&lang=es`
- `http://a.bc`

### Ejemplos invalidos

- `ftp://example.com` — protocolo no permitido
- `http://example` — dominio sin punto
- `http:/example.com` — falta un slash
- `http://example-.com` — dominio termina en guion

---

## NIT (Numero de Identificacion Tributaria)

### Alfabeto permitido

- Digitos: `0-9`
- Separadores de grupo: `.`
- Separador de verificador: `-`

### Regla estructural

El NIT tiene formato fijo `NNN.NNN.NNN-D`:

- Tres grupos de exactamente tres digitos cada uno.
- Cada par de grupos separados por un punto `.`.
- Un guion `-` separa el tercer grupo del digito verificador.
- El digito verificador es exactamente un digito.
- La cadena tiene longitud fija de 13 caracteres.

No se aceptan:

- grupos con menos o mas de 3 digitos
- separadores distintos a `.` entre grupos o a `-` antes del verificador
- caracteres extra al final
- letras en cualquier posicion

### Restriccion de cierre

El automata debe terminar en el estado `CHECK` (digito verificador completo).
Cualquier otro estado al agotar la entrada produce rechazo.

### Idea de estados

- `START`: inicio del analisis
- `D1`, `D2`, `D3`: digitos del primer grupo
- `DOT1`: primer separador `.`
- `D4`, `D5`, `D6`: digitos del segundo grupo
- `DOT2`: segundo separador `.`
- `D7`, `D8`, `D9`: digitos del tercer grupo
- `HYPHEN`: separador `-` antes del verificador
- `CHECK`: digito verificador leido — estado aceptante al cierre
- `REJECT`: cadena invalida

### Ejemplos validos

- `900.123.456-7`
- `000.000.000-0`
- `999.999.999-9`

### Ejemplos invalidos

- `900123456-7` — sin puntos separadores
- `900.123.4567` — sin guion antes del verificador
- `9AB.123.456-7` — letras en el primer grupo

---

## Contrasena segura

### Alfabeto permitido

- Letras minusculas: `a-z`
- Letras mayusculas: `A-Z`
- Digitos: `0-9`
- Simbolos especiales exactos: `! @ # $ % & * - _`

### Regla estructural

La contrasena se valida en un unico recorrido caracter por caracter.
El automata mantiene cuatro banderas booleanas que se activan a medida que aparecen los simbolos requeridos:

- `has_upper`: se activa al encontrar la primera letra mayuscula.
- `has_lower`: se activa al encontrar la primera letra minuscula.
- `has_digit`: se activa al encontrar el primer digito.
- `has_special`: se activa al encontrar el primer simbolo del conjunto permitido.

La contrasena se acepta al agotar la entrada si se cumplen todas estas condiciones:

1. Longitud minima de 8 caracteres.
2. `has_upper = true`
3. `has_lower = true`
4. `has_digit = true`
5. `has_special = true`

Si cualquier caracter no pertenece al alfabeto permitido, se rechaza de inmediato.

### Nota importante

La contrasena NO se busca en texto libre. Es un dato de entrada atomico validado unicamente en formularios interactivos (Parte B del proyecto).

### Idea de estados

- `START`: inicio del recorrido
- `SCANNING`: estado unico de recorrido, aumentado con las cuatro banderas y un contador de longitud
- `ACCEPT`: todas las condiciones se cumplen al agotar la entrada
- `REJECT`: alguna condicion falla o aparece un caracter fuera del alfabeto

### Ejemplos validos

- `Secure@1` — 8 caracteres, cumple las cuatro condiciones
- `MyP@ssw0rd!` — larga, todas las banderas activas
- `Abcde@1z` — exactamente 8 caracteres en el limite inferior

### Ejemplos invalidos

- `Ab1@` — solo 4 caracteres, longitud insuficiente
- `secure@1abc` — sin letra mayuscula
- `SECURE@1ABC` — sin letra minuscula
- `SecurePass@` — sin digito
- `SecurePass1` — sin simbolo especial
- `Secure^1ab` — `^` no pertenece al conjunto de simbolos permitidos
