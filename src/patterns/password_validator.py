"""AFD para validar contrasenas con estado que refleja condiciones cumplidas.

A diferencia de los demas validadores, la contrasena no tiene una estructura
lineal (como fecha o telefono) sino un conjunto de condiciones booleanas:
mayuscula, minuscula, digito y caracter especial.

El estado del automata cambia CADA VEZ que se activa una nueva bandera,
generando una traza como:

    SCANNING --['a']--> SEEN_L: Letra minuscula detectada.
    SEEN_L --['A']--> SEEN_L_U: Letra mayuscula detectada.
    SEEN_L_U --['1']--> SEEN_L_U_D: Digito detectado.
    SEEN_L_U_D --['!']--> SEEN_L_U_D_S: Caracter especial detectado.

No se integra al scanner — solo uso en formularios interactivos (Parte B).
"""

from __future__ import annotations

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult, reject_empty
from src.core.symbol_classifier import is_digit, is_lower_letter, is_upper_letter

SPECIAL_SYMBOLS: frozenset[str] = frozenset(
    "!@#$%&*-_^+=~()[]{}|;:,.<>?"
)
MIN_LENGTH = 8
MAX_LENGTH = 128


def _is_special(symbol: str) -> bool:
    """Indica si el simbolo pertenece al conjunto de simbolos especiales permitidos."""
    return symbol in SPECIAL_SYMBOLS


def _state_name(has_lower: bool, has_upper: bool, has_digit: bool, has_special: bool) -> str:
    """Construye el nombre del estado a partir de las banderas activas.

    Ejemplos:
        (False, False, False, False) -> "SCANNING"
        (True,  False, False, False) -> "SEEN_L"
        (True,  True,  False, False) -> "SEEN_L_U"
        (True,  True,  True,  True)  -> "SEEN_L_U_D_S"
    """
    parts: list[str] = []
    if has_lower:
        parts.append("L")
    if has_upper:
        parts.append("U")
    if has_digit:
        parts.append("D")
    if has_special:
        parts.append("S")
    return "SCANNING" if not parts else f"SEEN_{'_'.join(parts)}"


def _build_rejection_message(
    length: int,
    has_upper: bool,
    has_lower: bool,
    has_digit: bool,
    has_special: bool,
) -> str:
    """Construye un mensaje que lista todas las condiciones que fallaron."""
    missing: list[str] = []
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
    """Valida contrasenas con automata de estados transicionales.

    Cada vez que se activa una nueva bandera (lower, upper, digit, special),
    el automata TRANSICIONA a un nuevo estado que refleja el conjunto de
    condiciones cumplidas hasta ese momento.

    Reglas:
    - Longitud minima de 8 caracteres.
    - Longitud maxima de 128 caracteres.
    - Al menos una letra mayuscula (A-Z).
    - Al menos una letra minuscula (a-z).
    - Al menos un digito (0-9).
    - Al menos un simbolo del conjunto: ! @ # $ % & * - _ ^ + = ~ ( ) [ ] { } | ; : , . < > ?
    - Cualquier caracter fuera del alfabeto causa rechazo inmediato.

    La contrasena no genera valor normalizado por razon de privacidad.
    """

    if len(text) > MAX_LENGTH:
        return ValidationResult.reject(
            consumed=0,
            message=f"La contrasena excede la longitud maxima de {MAX_LENGTH} caracteres.",
            trace=[],
        )

    automaton = TraceableAutomaton(state="SCANNING")
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    if not text:
        return reject_empty("START")

    for symbol in text:
        new_flag = False
        desc = ""

        if is_upper_letter(symbol):
            if not has_upper:
                has_upper = True
                new_flag = True
                desc = "Letra mayuscula detectada."
            else:
                desc = "Letra mayuscula repetida — bandera ya activa."

        elif is_lower_letter(symbol):
            if not has_lower:
                has_lower = True
                new_flag = True
                desc = "Letra minuscula detectada."
            else:
                desc = "Letra minuscula repetida — bandera ya activa."

        elif is_digit(symbol):
            if not has_digit:
                has_digit = True
                new_flag = True
                desc = "Digito detectado."
            else:
                desc = "Digito repetido — bandera ya activa."

        elif _is_special(symbol):
            if not has_special:
                has_special = True
                new_flag = True
                desc = "Caracter especial detectado."
            else:
                desc = "Caracter especial repetido — bandera ya activa."

        else:
            automaton.record(
                symbol,
                "REJECT",
                f"Simbolo {symbol!r} no pertenece al alfabeto permitido.",
            )
            return ValidationResult.reject(
                consumed=automaton.consumed,
                message=f"El simbolo {symbol!r} no esta permitido en la contrasena.",
                trace=automaton.trace,
            )

        if new_flag:
            automaton.record(symbol, _state_name(has_lower, has_upper, has_digit, has_special), desc)
        else:
            automaton.stay(symbol, desc)

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
