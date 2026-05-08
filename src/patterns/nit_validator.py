"""AFD para Numeros de Identificacion Tributaria (NIT) colombianos.

Responsabilidad unica: recorrer char-by-char y decidir si la cadena es
un NIT valido con formato NNN.NNN.NNN-D. Sin logica de UI ni de scanner.

Formato: tres grupos de tres digitos separados por punto, seguidos de
guion y un digito verificador. Ejemplo: 900.123.456-7.
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult
from src.core.symbol_classifier import is_digit


def _accepted_nit_result(
    automaton: TraceableAutomaton,
    digits: list[str],
) -> ValidationResult:
    return ValidationResult.accept(
        consumed=automaton.consumed,
        message="NIT valido.",
        trace=automaton.trace,
        normalized="".join(digits),
    )


def _rejected_nit_result(
    automaton: TraceableAutomaton,
    message: str,
    digits: list[str] | None = None,
) -> ValidationResult:
    return ValidationResult.reject(
        consumed=automaton.consumed,
        message=message,
        trace=automaton.trace,
        normalized="".join(digits) if digits else "",
    )


def validate_nit(text: str) -> ValidationResult:
    """Valida NITs colombianos con formato estricto NNN.NNN.NNN-D.

    Reglas implementadas:
    - Exactamente tres grupos de tres digitos separados por punto.
    - Un digito verificador separado por guion al final.
    - La cadena no puede tener caracteres extra al final.
    """

    automaton = TraceableAutomaton(state="START")
    digits: list[str] = []

    if not text:
        return ValidationResult.reject(
            consumed=0,
            message="La cadena esta vacia.",
            trace=["START: no hay simbolos para procesar."],
        )

    for symbol in text:
        if automaton.state == "START":
            if is_digit(symbol):
                automaton.record(symbol, "D1", "Primer digito del primer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El NIT debe iniciar con un digito.")
            return _rejected_nit_result(automaton, "El NIT no inicia con digito.")

        if automaton.state == "D1":
            if is_digit(symbol):
                automaton.record(symbol, "D2", "Segundo digito del primer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito del primer grupo.")
            return _rejected_nit_result(automaton, "El primer grupo del NIT esta incompleto.")

        if automaton.state == "D2":
            if is_digit(symbol):
                automaton.record(symbol, "D3", "Tercer digito del primer grupo — grupo completo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito del primer grupo.")
            return _rejected_nit_result(automaton, "El primer grupo del NIT esta incompleto.")

        if automaton.state == "D3":
            if symbol == ".":
                automaton.record(symbol, "DOT1", "Primer separador entre grupos.")
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '.' como separador del primer grupo.")
            return _rejected_nit_result(automaton, "El NIT no tiene el primer separador correcto.")

        if automaton.state == "DOT1":
            if is_digit(symbol):
                automaton.record(symbol, "D4", "Primer digito del segundo grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del punto debe venir un digito.")
            return _rejected_nit_result(automaton, "El segundo grupo del NIT esta vacio.")

        if automaton.state == "D4":
            if is_digit(symbol):
                automaton.record(symbol, "D5", "Segundo digito del segundo grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito del segundo grupo.")
            return _rejected_nit_result(automaton, "El segundo grupo del NIT esta incompleto.")

        if automaton.state == "D5":
            if is_digit(symbol):
                automaton.record(symbol, "D6", "Tercer digito del segundo grupo — grupo completo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito del segundo grupo.")
            return _rejected_nit_result(automaton, "El segundo grupo del NIT esta incompleto.")

        if automaton.state == "D6":
            if symbol == ".":
                automaton.record(symbol, "DOT2", "Segundo separador entre grupos.")
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '.' como separador del segundo grupo.")
            return _rejected_nit_result(automaton, "El NIT no tiene el segundo separador correcto.")

        if automaton.state == "DOT2":
            if is_digit(symbol):
                automaton.record(symbol, "D7", "Primer digito del tercer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del punto debe venir un digito.")
            return _rejected_nit_result(automaton, "El tercer grupo del NIT esta vacio.")

        if automaton.state == "D7":
            if is_digit(symbol):
                automaton.record(symbol, "D8", "Segundo digito del tercer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito del tercer grupo.")
            return _rejected_nit_result(automaton, "El tercer grupo del NIT esta incompleto.")

        if automaton.state == "D8":
            if is_digit(symbol):
                automaton.record(symbol, "D9", "Tercer digito del tercer grupo — grupo completo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito del tercer grupo.")
            return _rejected_nit_result(automaton, "El tercer grupo del NIT esta incompleto.")

        if automaton.state == "D9":
            if symbol == "-":
                automaton.record(symbol, "HYPHEN", "Separador antes del digito verificador.")
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '-' antes del digito verificador.")
            return _rejected_nit_result(automaton, "El NIT no tiene el separador del digito verificador.")

        if automaton.state == "HYPHEN":
            if is_digit(symbol):
                automaton.record(symbol, "CHECK", "Digito verificador del NIT.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El digito verificador debe ser un digito.")
            return _rejected_nit_result(automaton, "El digito verificador del NIT es invalido.")

        if automaton.state == "CHECK":
            automaton.record(symbol, "REJECT", "El NIT no puede tener caracteres extra al final.")
            return _rejected_nit_result(automaton, "El NIT tiene caracteres extra al final.", digits)

    if automaton.state == "CHECK":
        automaton.finish("ACCEPT", "NIT valido con formato NNN.NNN.NNN-D completo.")
        return _accepted_nit_result(automaton, digits)

    automaton.finish("REJECT", f"La cadena termina en estado incompleto: {automaton.state}.")
    return _rejected_nit_result(automaton, "El NIT esta incompleto.", digits)
