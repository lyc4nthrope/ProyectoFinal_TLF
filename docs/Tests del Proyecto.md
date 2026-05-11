**Tests del Proyecto**

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

# Test Cases

Casos de prueba para los tres validadores formales del proyecto. Cada caso indica la entrada, el resultado esperado, la regla que se activa y el estado final del autómata.

## Teléfono

Formato aceptado: secuencia de 10 a 13 dígitos reales, con `+` opcional al inicio y separadores   o `-` entre bloques.

### Válidos

| Entrada | Resultado | Regla activada |
| :---- | :---- | :---- |
| `3001234567` | ACEPTADO | 10 dígitos sin separadores, rango válido |
| `300 123 4567` | ACEPTADO | 10 dígitos con espacios como separadores |
| `300-123-4567` | ACEPTADO | 10 dígitos con guiones como separadores |
| `+57 300-123-4567` | ACEPTADO | Prefijo internacional \+ 12 dígitos válidos |
| `+573001234567` | ACEPTADO | Prefijo internacional \+ 12 dígitos sin separadores |
| `3001234567890` | ACEPTADO | 13 dígitos, límite superior del rango |

### Inválidos

| Entrada | Resultado | Regla violada |
| :---- | :---- | :---- |
| `300--1234567` | RECHAZADO | Dos separadores consecutivos — estado `AFTER_SEPARATOR` rechaza segundo separador |
| `30012A4567` | RECHAZADO | Símbolo `A` fuera del alfabeto permitido |
| `12345` | RECHAZADO | Solo 5 dígitos — mínimo es 10 |
| `3001234-` | RECHAZADO | Termina en separador — la cadena no puede cerrar en `-` o   |
| `+ 3001234567` | RECHAZADO | Espacio después de `+` — `AFTER_PLUS` solo acepta dígito |
| \`\` | RECHAZADO | Cadena vacia — sin símbolos para procesar |
| `abc1234567` | RECHAZADO | La cadena no inicia con `+` ni dígito |

### Borde

| Entrada | Resultado | Por que es borde |
| :---- | :---- | :---- |
| `1234567890` | ACEPTADO | Exactamente 10 digitos — límite inferior |
| `30012345678901` | RECHAZADO | 14 digitos — supera el límite superior de 13 |
| `+5730012345` | ACEPTADO | 11 digitos con prefijo — dentro del rango |
| `300`  | RECHAZADO | Termina en espacio — separador al final sin dígito posterior |

## Correo electrónico

Formato aceptado: `local@dominio.tld` donde la parte local y el dominio siguen reglas formales de composición de etiquetas.

### Válidos

| Entrada | Resultado | Regla activada |
| :---- | :---- | :---- |
| `usuario@example.com` | ACEPTADO | Estructura básica [local@dominio.tld](mailto:local@dominio.tld) valida |
| `user.name-test_1@sub.domain.com` | ACEPTADO | Separadores `.`, `-`, `_` válidos en parte local; subdominio válido |
| `a1@correo.co` | ACEPTADO | Parte local mínima con dígito; TLD de 2 letras |
| `abc@dominio.org` | ACEPTADO | Estructura simple sin separadores en parte local |

### Inválidos

| Entrada | Resultado | Regla violada |
| :---- | :---- | :---- |
| `.usuario@example.com` | RECHAZADO | Parte local inicia con separador — `START` solo acepta letra o dígito |
| `user..name@example.com` | RECHAZADO | Separadores consecutivos — `LOCAL_SEPARATOR` solo acepta letra o dígito siguiente |
| `usuario.example.com` | RECHAZADO | No existe `@` — cierre con `saw_at_symbol = False` |
| `usuario@.com` | RECHAZADO | Dominio inicia con punto — `AFTER_AT` solo acepta letra o dígito |
| `usuario@example.c1` | RECHAZADO | TLD termina en dígito — `tld_letters < 2` al cierre |
| `usuario@example-.com` | RECHAZADO | Etiqueta del dominio termina en guión — `DOMAIN_HYPHEN` exige continuación |
| \`\` | RECHAZADO | Cadena vacía — sin símbolos para procesar |
| `usuario@` | RECHAZADO | Cadena termina en estado `AFTER_AT` — dominio nunca inicio |

### Borde

| Entrada | Resultado | Por que es borde |
| :---- | :---- | :---- |
| `a@b.co` | ACEPTADO | Mínimo estructuralmente válido |
| `a@b.c` | RECHAZADO | TLD de 1 sola letra — mínimo es 2 |
| `a@b` | RECHAZADO | Dominio sin punto — `saw_domain_dot = False` al cierre |
| `usuario@sub.sub.domain.com` | ACEPTADO | Múltiples etiquetas de dominio, todas válidas |
| `1@1.co` | ACEPTADO | Parte local y dominio con dígitos, TLD alfabético |

## Fecha

Formato aceptado: `DD/MM/YYYY` con separador único `/`, rangos de día y mes válidos, y año entre 1900 y 2100\.

### Válidos

| Entrada | Resultado | Regla activada |
| :---- | :---- | :---- |
| `15/08/2024` | ACEPTADO | Fecha estandar con dia, mes y anio válidos |
| `01/01/2000` | ACEPTADO | Primer dia del anio, anio límite inferior valido |
| `29/02/2024` | ACEPTADO | 2024 es bisiesto — febrero acepta dia 29 |
| `31/12/2100` | ACEPTADO | Ultimo dia del anio en el límite superior del rango |
| `29/02/2000` | ACEPTADO | 2000 es bisiesto — divisible entre 400 |

### Inválidos

| Entrada | Resultado | Regla violada |
| :---- | :---- | :---- |
| `1/08/2024` | RECHAZADO | Dia sin cero inicial — `DAY_FIRST` exige segundo dígito, no `/` |
| `15-08-2024` | RECHAZADO | Separador incorrecto — `AFTER_DAY` exige `/` |
| `31/04/2024` | RECHAZADO | Abril tiene 30 días — `day > max_day` |
| `29/02/2023` | RECHAZADO | 2023 no es bisiesto — febrero tiene 28 días |
| `15/13/2024` | RECHAZADO | Mes 13 no existe — `month > 12` |
| `15/00/2024` | RECHAZADO | Mes 0 no existe — `month < 1` |
| `00/08/2024` | RECHAZADO | Dia 0 no existe — `day < 1` |
| `15/08/2201` | RECHAZADO | Año 2201 supera el límite de 2100 |
| `15/08/2024x` | RECHAZADO | Símbolo extra al final — `DATE_COMPLETE` no acepta mas entrada |
| \`\` | RECHAZADO | Cadena vacia — sin símbolos para procesar |

### Borde

| Entrada | Resultado | Por que es borde |
| :---- | :---- | :---- |
| `01/01/1900` | ACEPTADO | Límite inferior exacto del rango de años |
| `31/12/2100` | ACEPTADO | Límite superior exacto del rango de años |
| `28/02/1900` | ACEPTADO | 1900 no es bisiesto — divisible entre 100 pero no entre 400 |
| `29/02/1900` | RECHAZADO | Confirma que 1900 no es bisiesto — febrero solo tiene 28 días |
| `31/01/2024` | ACEPTADO | Enero tiene 31 dias — límite correcto |
| `32/01/2024` | RECHAZADO | Dia 32 no existe para ningún mes |

---

## Placa vehicular

Formato carro: `LLLDDD` o `LLL-DDD`. Formato moto: `LLLDDDL` o `LLL-DDDL`. Solo letras mayúsculas A-Z y dígitos 0-9. Guión opcional entre bloques.

### Válidos

| Entrada | Resultado | Regla activada |
| :---- | :---- | :---- |
| `ABC123` | ACEPTADO | Carro sin guión — 3 letras \+ 3 dígitos, estado final D3 |
| `ABC-123` | ACEPTADO | Carro con guión — separador opcional entre L3 y D1 |
| `XYZ456A` | ACEPTADO | Moto sin guión — 3 letras \+ 3 dígitos \+ 1 letra, estado final L4 |
| `XYZ-456A` | ACEPTADO | Moto con guión — separador entre letras y dígitos |
| `AAA000` | ACEPTADO | Carro con letras y dígitos mínimos válidos |
| `ZZZ999Z` | ACEPTADO | Moto con todos los valores al límite superior del alfabeto |

### Inválidos

| Entrada | Resultado | Regla violada |
| :---- | :---- | :---- |
| `abc123` | RECHAZADO | Letras minusculas — `START` exige letra mayúscula A-Z |
| `AB123` | RECHAZADO | Solo 2 letras iniciales — L2 no puede recibir dígito |
| `ABC12` | RECHAZADO | Solo 2 dígitos — cadena termina en D2, estado incompleto |
| `ABC123X9` | RECHAZADO | Carácter extra despues del carro — L4 no acepta otro simbolo |
| `ABC.123` | RECHAZADO | Símbolo `.` fuera del alfabeto permitido |
| `1BC123` | RECHAZADO | La placa no puede iniciar con dígito — `START` rechaza |
| `ABC--123` | RECHAZADO | Doble guión — `AFTER_L3` rechaza segundo guión consecutivo |

### Borde

| Entrada | Resultado | Por que es borde |
| :---- | :---- | :---- |
| `ABC123-` | RECHAZADO | Guion al final — cadena termina en AFTER\_D3, estado incompleto |
| `ABC` | RECHAZADO | Solo letras — cadena termina en L3, sin dígitos |
| `ABC-` | RECHAZADO | Guión sin dígitos — cadena termina en AFTER\_L3 |
| `ABC123Z` | ACEPTADO | Exactamente el formato moto — L4 como estado final válido |

## 

## 

## URL

Formato aceptado: `http://` o `https://` seguido de dominio con al menos un punto y ruta opcional.

### Válidos

| Entrada | Resultado | Regla activada |
| :---- | :---- | :---- |
| `http://example.com` | ACEPTADO | Protocolo http \+ dominio con punto |
| `https://example.com` | ACEPTADO | Protocolo https válido |
| `https://www.google.com` | ACEPTADO | Subdominio www válido |
| `https://example.com/path/to/page` | ACEPTADO | Ruta con múltiples segmentos |
| `https://example.com/search?q=hola&lang=es` | ACEPTADO | Query string con multiples parametros |
| `https://api.sub.example.org` | ACEPTADO | Múltiples subdominios |
| `https://example.co.uk` | ACEPTADO | TLD de país compuesto |
| `http://example.com/` | ACEPTADO | Barra final de ruta válida |
| `https://example.com/page#section` | ACEPTADO | Fragmento con `#` |
| `https://example.com?q=test` | ACEPTADO | Query sin ruta previa |
| `HTTP://example.com` | ACEPTADO | Protocolo en minúsculas — case insensitive |

### Inválidos

| Entrada | Resultado | Regla violada |
| :---- | :---- | :---- |
| `ftp://example.com` | RECHAZADO | Protocolo `ftp` no es `http` ni `https` |
| `http://example` | RECHAZADO | Dominio sin punto — `saw_domain_dot = False` al cierre |
| `http:/example.com` | RECHAZADO | Solo un slash — `SLASH1` exige segundo `/` |
| `http://` | RECHAZADO | Dominio vacio — `SLASH2` exige letra o dígito |
| \`\` | RECHAZADO | Cadena vacía |
| `http://example-.com` | RECHAZADO | Etiqueta termina en guión — `DOMAIN_HYPHEN` exige continuación |
| `http://.example.com` | RECHAZADO | Dominio inicia con punto — `DOMAIN_DOT` exige letra o dígito |
| `example.com` | RECHAZADO | Sin protocolo — `START` solo acepta `h` o `H` |

### Borde

| Entrada | Resultado | Por que es borde |
| :---- | :---- | :---- |
| `http://a.bc` | ACEPTADO | Dominio mínimo valido: una letra \+ punto \+ dos letras |
| `https://example.com/page?a=1&b=2` | ACEPTADO | Combinación de ruta y query |
| `http://sub.sub.domain.org` | ACEPTADO | Múltiples etiquetas de dominio |

## NIT (Numero de Identificacion Tributaria)

Formato aceptado: `NNN.NNN.NNN-D` — tres grupos de tres dígitos separados por punto, guión y un dígito verificador al final.

### Válidos

| Entrada | Resultado | Regla activada |
| :---- | :---- | :---- |
| `900.123.456-7` | ACEPTADO | Formato completo con todos los grupos y verificador |
| `000.000.000-0` | ACEPTADO | Dígitos mínimos válidos en todos los grupos |
| `999.999.999-9` | ACEPTADO | Dígitos máximos válidos |
| `800.100.200-0` | ACEPTADO | Dígito verificador cero — válido |
| `123.456.789-1` | ACEPTADO | Grupos distintos, estructura correcta |

### Inválidos

| Entrada | Resultado | Regla violada |
| :---- | :---- | :---- |
| `900123456-7` | RECHAZADO | Sin puntos — `D3` exige `.`, recibe dígito |
| `900.123.4567` | RECHAZADO | Sin guión al final — `D9` exige `-` |
| `900` | RECHAZADO | Solo primer grupo — cadena termina en `D3` |
| `900.123` | RECHAZADO | Solo dos grupos — cadena termina en `D6` |
| `9AB.123.456-7` | RECHAZADO | Letras en grupo — `D1` exige dígito |
| `900-123-456-7` | RECHAZADO | Separador incorrecto — `D3` exige `.`, recibe `-` |
| `900.123.456-7X` | RECHAZADO | Carácter extra — `CHECK` rechaza cualquier símbolo |
| \`\` | RECHAZADO | Cadena vacía |

### Borde

| Entrada | Resultado | Por que es borde |
| :---- | :---- | :---- |
| `900.123.456-77` | RECHAZADO | Dos dígitos verificadores — `CHECK` no acepta mas entrada |
| `90.123.456-7` | RECHAZADO | Primer grupo con 2 dígitos — `D2` exige digito, recibe `.` |
| `9000.123.456-7` | RECHAZADO | Primer grupo con 4 dígitos — `D3` exige `.`, recibe digito |

## Contraseña segura

Longitud mínima 8\. Requiere mayúscula, minúscula, dígito y símbolo especial del conjunto `! @ # $ % & * - _`. No se busca en texto libre — solo validación directa en formularios (Parte B).

### Válidos

| Entrada | Resultado | Regla activada |
| :---- | :---- | :---- |
| `Secure@1` | ACEPTADO | 8 chars exactos — todas las banderas activas al cierre |
| `MyP@ssw0rd!` | ACEPTADO | Larga, múltiples símbolos y tipos mezclados |
| `Abcde@1z` | ACEPTADO | Límite inferior de longitud — exactamente 8 caracteres |
| `A1@bcdefg` | ACEPTADO | Mayúscula, dígito y símbolo al inicio — resto minúsculas |
| `ZzZzZz1@` | ACEPTADO | Alternancia de mayúsculas y minúsculas, dígito y símbolo |

### Inválidos

| Entrada | Resultado | Regla violada |
| :---- | :---- | :---- |
| `Ab1@` | RECHAZADO | 4 caracteres — longitud menor a 8 |
| `secure@1abc` | RECHAZADO | Sin letra mayúscula — bandera `has_upper` nunca activada |
| `SECURE@1ABC` | RECHAZADO | Sin letra minúscula — bandera `has_lower` nunca activada |
| `SecurePass@` | RECHAZADO | Sin dígito — bandera `has_digit` nunca activada |
| `SecurePass1` | RECHAZADO | Sin símbolo especial — bandera `has_special` nunca activada |
| `Secure^1ab` | RECHAZADO | `^` no pertenece al conjunto de símbolos permitidos — rechazo inmediato |
| \`\` | RECHAZADO | Cadena vacía — sin símbolos para procesar |

### Borde

| Entrada | Resultado | Por que es borde |
| :---- | :---- | :---- |
| `Abc@1zX` | RECHAZADO | 7 caracteres — todas las banderas activas pero longitud insuficiente |
| `Abcde@1z` | ACEPTADO | Exactamente 8 — límite inferior válido |
| `abcdefgh` | RECHAZADO | 8 chars pero sin mayúscula, dígito ni símbolo — tres banderas inactivas |
| `A1@bbbbb` | ACEPTADO | Mínimo de tipos en primeros 3 chars, resto minúsculas completan longitud |

