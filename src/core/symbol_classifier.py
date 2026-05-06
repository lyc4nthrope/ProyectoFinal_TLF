"""Utilidades para clasificar simbolos de entrada."""


def is_digit(symbol: str) -> bool:
    """Indica si el simbolo pertenece al alfabeto de digitos decimales."""

    return len(symbol) == 1 and "0" <= symbol <= "9"
