# Test Cases

Casos de prueba para los tres validadores formales del proyecto.
Cada caso indica la entrada, el resultado esperado, la regla que se activa y el estado final del automata.

---

## Telefono

Formato aceptado: secuencia de 10 a 13 digitos reales, con `+` opcional al inicio y separadores ` ` o `-` entre bloques.

### Validos

| Entrada | Resultado | Regla activada |
|---------|-----------|---------------|
| `3001234567` | ACEPTADO | 10 digitos sin separadores, rango valido |
| `300 123 4567` | ACEPTADO | 10 digitos con espacios como separadores |
| `300-123-4567` | ACEPTADO | 10 digitos con guiones como separadores |
| `+57 300-123-4567` | ACEPTADO | Prefijo internacional + 12 digitos validos |
| `+573001234567` | ACEPTADO | Prefijo internacional + 12 digitos sin separadores |
| `3001234567890` | ACEPTADO | 13 digitos, limite superior del rango |

### Invalidos

| Entrada | Resultado | Regla violada |
|---------|-----------|--------------|
| `300--1234567` | RECHAZADO | Dos separadores consecutivos — estado `AFTER_SEPARATOR` rechaza segundo separador |
| `30012A4567` | RECHAZADO | Simbolo `A` fuera del alfabeto permitido |
| `12345` | RECHAZADO | Solo 5 digitos — minimo es 10 |
| `3001234-` | RECHAZADO | Termina en separador — la cadena no puede cerrar en `-` o ` ` |
| `+ 3001234567` | RECHAZADO | Espacio despues de `+` — `AFTER_PLUS` solo acepta digito |
| `` | RECHAZADO | Cadena vacia — sin simbolos para procesar |
| `abc1234567` | RECHAZADO | La cadena no inicia con `+` ni digito |

### Borde

| Entrada | Resultado | Por que es borde |
|---------|-----------|-----------------|
| `1234567890` | ACEPTADO | Exactamente 10 digitos — limite inferior |
| `30012345678901` | RECHAZADO | 14 digitos — supera el limite superior de 13 |
| `+5730012345` | ACEPTADO | 11 digitos con prefijo — dentro del rango |
| `300 ` | RECHAZADO | Termina en espacio — separador al final sin digito posterior |

---

## Correo electronico

Formato aceptado: `local@dominio.tld` donde la parte local y el dominio siguen reglas formales de composicion de etiquetas.

### Validos

| Entrada | Resultado | Regla activada |
|---------|-----------|---------------|
| `usuario@example.com` | ACEPTADO | Estructura basica local@dominio.tld valida |
| `user.name-test_1@sub.domain.com` | ACEPTADO | Separadores `.`, `-`, `_` validos en parte local; subdominio valido |
| `a1@correo.co` | ACEPTADO | Parte local minima con digito; TLD de 2 letras |
| `abc@dominio.org` | ACEPTADO | Estructura simple sin separadores en parte local |

### Invalidos

| Entrada | Resultado | Regla violada |
|---------|-----------|--------------|
| `.usuario@example.com` | RECHAZADO | Parte local inicia con separador — `START` solo acepta letra o digito |
| `user..name@example.com` | RECHAZADO | Separadores consecutivos — `LOCAL_SEPARATOR` solo acepta letra o digito siguiente |
| `usuario.example.com` | RECHAZADO | No existe `@` — cierre con `saw_at_symbol = False` |
| `usuario@.com` | RECHAZADO | Dominio inicia con punto — `AFTER_AT` solo acepta letra o digito |
| `usuario@example.c1` | RECHAZADO | TLD termina en digito — `tld_letters < 2` al cierre |
| `usuario@example-.com` | RECHAZADO | Etiqueta del dominio termina en guion — `DOMAIN_HYPHEN` exige continuacion |
| `` | RECHAZADO | Cadena vacia — sin simbolos para procesar |
| `usuario@` | RECHAZADO | Cadena termina en estado `AFTER_AT` — dominio nunca inicio |

### Borde

| Entrada | Resultado | Por que es borde |
|---------|-----------|-----------------|
| `a@b.co` | ACEPTADO | Minimo estructuralmente valido |
| `a@b.c` | RECHAZADO | TLD de 1 sola letra — minimo es 2 |
| `a@b` | RECHAZADO | Dominio sin punto — `saw_domain_dot = False` al cierre |
| `usuario@sub.sub.domain.com` | ACEPTADO | Multiples etiquetas de dominio, todas validas |
| `1@1.co` | ACEPTADO | Parte local y dominio con digitos, TLD alfabetico |

---

## Fecha

Formato aceptado: `DD/MM/YYYY` con separador unico `/`, rangos de dia y mes validos, y anio entre 1900 y 2100.

### Validos

| Entrada | Resultado | Regla activada |
|---------|-----------|---------------|
| `15/08/2024` | ACEPTADO | Fecha estandar con dia, mes y anio validos |
| `01/01/2000` | ACEPTADO | Primer dia del anio, anio limite inferior valido |
| `29/02/2024` | ACEPTADO | 2024 es bisiesto — febrero acepta dia 29 |
| `31/12/2100` | ACEPTADO | Ultimo dia del anio en el limite superior del rango |
| `29/02/2000` | ACEPTADO | 2000 es bisiesto — divisible entre 400 |

### Invalidos

| Entrada | Resultado | Regla violada |
|---------|-----------|--------------|
| `1/08/2024` | RECHAZADO | Dia sin cero inicial — `DAY_FIRST` exige segundo digito, no `/` |
| `15-08-2024` | RECHAZADO | Separador incorrecto — `AFTER_DAY` exige `/` |
| `31/04/2024` | RECHAZADO | Abril tiene 30 dias — `day > max_day` |
| `29/02/2023` | RECHAZADO | 2023 no es bisiesto — febrero tiene 28 dias |
| `15/13/2024` | RECHAZADO | Mes 13 no existe — `month > 12` |
| `15/00/2024` | RECHAZADO | Mes 0 no existe — `month < 1` |
| `00/08/2024` | RECHAZADO | Dia 0 no existe — `day < 1` |
| `15/08/2201` | RECHAZADO | Anio 2201 supera el limite de 2100 |
| `15/08/2024x` | RECHAZADO | Simbolo extra al final — `DATE_COMPLETE` no acepta mas entrada |
| `` | RECHAZADO | Cadena vacia — sin simbolos para procesar |

### Borde

| Entrada | Resultado | Por que es borde |
|---------|-----------|-----------------|
| `01/01/1900` | ACEPTADO | Limite inferior exacto del rango de anios |
| `31/12/2100` | ACEPTADO | Limite superior exacto del rango de anios |
| `28/02/1900` | ACEPTADO | 1900 no es bisiesto — divisible entre 100 pero no entre 400 |
| `29/02/1900` | RECHAZADO | Confirma que 1900 no es bisiesto — febrero solo tiene 28 dias |
| `31/01/2024` | ACEPTADO | Enero tiene 31 dias — limite correcto |
| `32/01/2024` | RECHAZADO | Dia 32 no existe para ningun mes |
