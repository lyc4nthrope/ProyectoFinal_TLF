"""Utilidades para clasificar simbolos de entrada."""


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
