"""Fuente unica de verdad para clasificar caracteres del alfabeto del proyecto.

Todos los validadores y el scanner importan SOLO de aqui.
Ningun modulo usa .isdigit(), .isupper() ni metodos de stdlib para clasificar.
"""


def is_letter(symbol: str) -> bool:
    """Indica si el simbolo pertenece al alfabeto de letras ASCII."""

    return len(symbol) == 1 and (
        "a" <= symbol <= "z" or "A" <= symbol <= "Z"
    )


def is_digit(symbol: str) -> bool:
    """Indica si el simbolo pertenece al alfabeto de digitos decimales."""

    return len(symbol) == 1 and "0" <= symbol <= "9"


def is_alphanumeric(symbol: str) -> bool:
    """Indica si el simbolo es letra o digito."""

    return is_letter(symbol) or is_digit(symbol)


def is_upper_letter(symbol: str) -> bool:
    """Indica si el simbolo es letra mayuscula ASCII A-Z."""

    return is_letter(symbol) and "A" <= symbol <= "Z"


def is_lower_letter(symbol: str) -> bool:
    """Indica si el simbolo es letra minuscula ASCII a-z."""

    return is_letter(symbol) and "a" <= symbol <= "z"
