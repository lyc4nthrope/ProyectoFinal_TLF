"""AFD aumentado con vector de banderas para validar contrasenas seguras.

Responsabilidad unica: recorrer char-by-char, activar banderas booleanas
(upper, lower, digit, special) y al cierre verificar longitud minima.
No se integra al scanner — solo uso en formularios interactivos (Parte B).
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult
from src.core.symbol_classifier import is_digit, is_lower_letter, is_upper_letter

SPECIAL_SYMBOLS: frozenset[str] = frozenset("!@#$%&*-_")
MIN_LENGTH = 8


def _is_special(symbol: str) -> bool:
    """Indica si el simbolo pertenece al conjunto de simbolos especiales permitidos."""

    return symbol in SPECIAL_SYMBOLS


def _build_rejection_message(
    length: int,
    has_upper: bool,
    has_lower: bool,
    has_digit: bool,
    has_special: bool,
) -> str:
    """Construye un mensaje que lista todas las condiciones que fallaron."""

    missing = []
    if length < MIN_LENGTH:
        missing.append(f"longitud minima de {MIN_LENGTH} caracteres")
    if not has_upper:
        missing.append("al menos una letra mayuscula")
    if not has_lower:
        missing.append("al menos una letra minuscula")
    if not has_digit:
        missing.append("al menos un digito")
    if not has_special:
        missing.append("al menos un simbolo especial")
    return "Faltan: " + ", ".join(missing) + "."


def validate_password(text: str) -> ValidationResult:
    """Valida contrasenas mediante un automata de banderas char-by-char.

    El automata recorre la cadena en un unico pase y activa cuatro banderas
    booleanas. Al agotar la entrada evalua longitud y banderas simultaneamente.

    Reglas:
    - Longitud minima de 8 caracteres.
    - Al menos una letra mayuscula (A-Z).
    - Al menos una letra minuscula (a-z).
    - Al menos un digito (0-9).
    - Al menos un simbolo del conjunto: ! @ # $ % & * - _
    - Cualquier caracter fuera del alfabeto causa rechazo inmediato.

    La contrasena no genera valor normalizado por razon de privacidad.
    """

    automaton = TraceableAutomaton(state="SCANNING")
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    if not text:
        return ValidationResult.reject(
            consumed=0,
            message="La cadena esta vacia.",
            trace=["START: no hay simbolos para procesar."],
        )

    for symbol in text:
        if is_upper_letter(symbol):
            if not has_upper:
                automaton.stay(symbol, "Bandera has_upper activada.")
                has_upper = True
            else:
                automaton.stay(symbol, "Letra mayuscula — bandera has_upper ya activa.")
            continue

        if is_lower_letter(symbol):
            if not has_lower:
                automaton.stay(symbol, "Bandera has_lower activada.")
                has_lower = True
            else:
                automaton.stay(symbol, "Letra minuscula — bandera has_lower ya activa.")
            continue

        if is_digit(symbol):
            if not has_digit:
                automaton.stay(symbol, "Bandera has_digit activada.")
                has_digit = True
            else:
                automaton.stay(symbol, "Digito — bandera has_digit ya activa.")
            continue

        if _is_special(symbol):
            if not has_special:
                automaton.stay(symbol, "Bandera has_special activada.")
                has_special = True
            else:
                automaton.stay(symbol, "Simbolo especial — bandera has_special ya activa.")
            continue

        automaton.record(symbol, "REJECT", f"El simbolo {symbol!r} no pertenece al alfabeto permitido.")
        return ValidationResult.reject(
            consumed=automaton.consumed,
            message=f"El simbolo {symbol!r} no esta permitido en la contrasena.",
            trace=automaton.trace,
        )

    length = automaton.consumed
    all_conditions_met = (
        length >= MIN_LENGTH
        and has_upper
        and has_lower
        and has_digit
        and has_special
    )

    if all_conditions_met:
        automaton.finish("ACCEPT", "Contrasena valida — todas las condiciones cumplidas.")
        return ValidationResult.accept(
            consumed=length,
            message="Contrasena valida.",
            trace=automaton.trace,
            normalized="",
        )

    message = _build_rejection_message(length, has_upper, has_lower, has_digit, has_special)
    automaton.finish("REJECT", message)
    return ValidationResult.reject(
        consumed=length,
        message=message,
        trace=automaton.trace,
        normalized="",
    )
