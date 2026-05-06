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
