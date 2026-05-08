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
