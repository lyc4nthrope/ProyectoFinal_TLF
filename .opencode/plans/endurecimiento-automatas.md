# Plan: Endurecimiento de reglas de autómatas

## Contexto
Se encontró una vulnerabilidad en el validador de teléfono: números de 11 y 13 dígitos
son aceptados porque el rango `[10, 13]` es demasiado permisivo. Se auditaron los 7
autómatas en busca de vulnerabilidades similares.

---

## Fase 1 — Teléfono (`phone_validator.py`)

**Problema**: `MIN_DIGITS=10, MAX_DIGITS=13` acepta `31438080440` (11 dígitos).

**Solución**: 
- Sin prefijo `+`: exactamente 10 dígitos
- Con prefijo `+`: los últimos 10 dígitos normalizados son el número local; el resto es el código de país (cualquier longitud >= 1)

**Archivos**: `src/patterns/phone_validator.py`, `tests/test_phone_validator.py`

**Tests nuevos**:
| Input | Expected |
|-------|----------|
| `31438080440` (11 dígitos) | REJECT |
| `+57 31438080440` (11 locales) | REJECT |
| `+57 03143808044` (11 locales con 0) | REJECT |
| `+1 3143808044` (otro código) | ACCEPT |
| `3143808044` (10 dígitos) | ACCEPT (ya existe) |
| `+57 3143808044` (12 totales) | ACCEPT (ya existe) |

---

## Fase 2 — URL (`url_validator.py`)

**Problemas**:
1. Sin restricción de TLD: `http://a.b` y `http://example.123` aceptados
2. Sin límite de longitud total (DoS potencial)

**Solución**:
- Validar TLD al cierre: mínimo 2 caracteres, al menos uno debe ser letra
- Agregar límite de longitud total (ej. 2048 caracteres)

---

## Fase 3 — NIT (`nit_validator.py`)

**Problemas**:
1. Sin verificación de dígito verificador (módulo 11 colombiano)
2. Solo formato 9 dígitos (no soporta 10 dígitos para personas naturales)

**Solución**:
- Implementar algoritmo módulo 11 colombiano para verificar el dígito
- Soportar formato de 9 dígitos (`NNN.NNN.NNN-D`) y 10 dígitos (`N.NNN.NNN.NNN-D`)
- NOTA: el formato NNN.NNN.NNN-D existente requiere 3 bloques de 3 con puntos → para 10 dígitos
  sería `N.NNN.NNN.NNN-D` (1+3+3+3 dígitos). Esto requiere rediseñar el autómata.

---

## Fase 4 — Password (`password_validator.py`)

**Problemas**:
1. Sin longitud máxima (contraseña de 10,000 chars aceptada)
2. Solo 9 símbolos especiales (`!@#$%&*-_`)

**Solución**:
- Agregar `MAX_LENGTH = 128`
- Expandir set de símbolos especiales a: `!@#$%&*-_^+=~()[]{}|;:,.<>?`

---

## Fase 5 — Email (`email_validator.py`)

**Problemas**:
1. Sin longitud máxima (RFC 5321: 254 chars)
2. Sin límite de etiqueta de dominio (RFC 1035: 63 chars)
3. Sin límite de parte local (RFC 5321: 64 chars)
4. `+` subaddressing no soportado

**Solución**:
- Agregar `MAX_EMAIL_LENGTH = 254`, `MAX_LOCAL_LENGTH = 64`, `MAX_LABEL_LENGTH = 63`
- Añadir `+` al set de separadores locales (`_is_local_separator`)

---

## Fase 6 — Tests complementarios

**Date** (test_date_validator.py):
- `00/08/2024` REJECT (day = 0)
- `15/13/2024` REJECT (month = 13)
- `29/02/1900` REJECT (1900 no es bisiesto)
- `29/02/2000` ACCEPT (2000 es bisiesto)
- `01/01/1900` ACCEPT (borde inferior)
- `31/12/2100` ACCEPT (borde superior)

**Plate**: Sin cambios funcionales, solo documentar formato moto `ABC123-A`.

---

## Orden de implementación

1. Fase 1 → Phone
2. Fase 2 → URL
3. Fase 3 → NIT
4. Fase 4 → Password
5. Fase 5 → Email
6. Fase 6 → Tests date/plate
