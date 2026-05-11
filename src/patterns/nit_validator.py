"""AFD para Numeros de Identificacion Tributaria (NIT) colombianos.

Responsabilidad unica: recorrer char-by-char y decidir si la cadena es
un NIT valido con formato NNN.NNN.NNN-D. Sin logica de UI ni de scanner.

Formato: tres grupos de tres digitos separados por punto, seguidos de
guion y un digito verificador. Ejemplo: 900.123.456-7.
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult, build_accept, build_reject, reject_empty
from src.core.symbol_classifier import is_digit

# ── Estados del automata ──────────────────────────────────────────────
# N1_BLOCK1/N2_BLOCK1/N3_BLOCK1 = digitos del primer grupo (NNN.)
# DOT1                           = primer separador
# N1_BLOCK2/N2_BLOCK2/N3_BLOCK2 = digitos del segundo grupo (.NNN.)
# DOT2                           = segundo separador
# N1_BLOCK3/N2_BLOCK3/N3_BLOCK3 = digitos del tercer grupo (.NNN-)
# HYPHEN                         = separador antes del digito verificador
# CHECK                          = digito verificador


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
        return reject_empty("START")

    for symbol in text:
        if automaton.state == "START":
            if is_digit(symbol):
                automaton.record(symbol, "N1_BLOCK1", "Primer digito del primer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El NIT debe iniciar con un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT no inicia con digito.",
                trace=automaton.trace,
            )

        if automaton.state == "N1_BLOCK1":
            if is_digit(symbol):
                automaton.record(symbol, "N2_BLOCK1", "Segundo digito del primer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito del primer grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El primer grupo del NIT esta incompleto.",
                trace=automaton.trace,
            )

        if automaton.state == "N2_BLOCK1":
            if is_digit(symbol):
                automaton.record(symbol, "N3_BLOCK1", "Tercer digito del primer grupo — grupo completo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito del primer grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El primer grupo del NIT esta incompleto.",
                trace=automaton.trace,
            )

        if automaton.state == "N3_BLOCK1":
            if symbol == ".":
                automaton.record(symbol, "DOT1", "Primer separador entre grupos.")
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '.' como separador del primer grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT no tiene el primer separador correcto.",
                trace=automaton.trace,
            )

        if automaton.state == "DOT1":
            if is_digit(symbol):
                automaton.record(symbol, "N1_BLOCK2", "Primer digito del segundo grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del punto debe venir un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El segundo grupo del NIT esta vacio.",
                trace=automaton.trace,
            )

        if automaton.state == "N1_BLOCK2":
            if is_digit(symbol):
                automaton.record(symbol, "N2_BLOCK2", "Segundo digito del segundo grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito del segundo grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El segundo grupo del NIT esta incompleto.",
                trace=automaton.trace,
            )

        if automaton.state == "N2_BLOCK2":
            if is_digit(symbol):
                automaton.record(symbol, "N3_BLOCK2", "Tercer digito del segundo grupo — grupo completo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito del segundo grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El segundo grupo del NIT esta incompleto.",
                trace=automaton.trace,
            )

        if automaton.state == "N3_BLOCK2":
            if symbol == ".":
                automaton.record(symbol, "DOT2", "Segundo separador entre grupos.")
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '.' como separador del segundo grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT no tiene el segundo separador correcto.",
                trace=automaton.trace,
            )

        if automaton.state == "DOT2":
            if is_digit(symbol):
                automaton.record(symbol, "N1_BLOCK3", "Primer digito del tercer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del punto debe venir un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El tercer grupo del NIT esta vacio.",
                trace=automaton.trace,
            )

        if automaton.state == "N1_BLOCK3":
            if is_digit(symbol):
                automaton.record(symbol, "N2_BLOCK3", "Segundo digito del tercer grupo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito del tercer grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El tercer grupo del NIT esta incompleto.",
                trace=automaton.trace,
            )

        if automaton.state == "N2_BLOCK3":
            if is_digit(symbol):
                automaton.record(symbol, "N3_BLOCK3", "Tercer digito del tercer grupo — grupo completo.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito del tercer grupo.")
            return build_reject(
                consumed=automaton.consumed,
                message="El tercer grupo del NIT esta incompleto.",
                trace=automaton.trace,
            )

        if automaton.state == "N3_BLOCK3":
            if symbol == "-":
                automaton.record(symbol, "HYPHEN", "Separador antes del digito verificador.")
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '-' antes del digito verificador.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT no tiene el separador del digito verificador.",
                trace=automaton.trace,
            )

        if automaton.state == "HYPHEN":
            if is_digit(symbol):
                automaton.record(symbol, "CHECK", "Digito verificador del NIT.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El digito verificador debe ser un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El digito verificador del NIT es invalido.",
                trace=automaton.trace,
            )

        if automaton.state == "CHECK":
            automaton.record(symbol, "REJECT", "El NIT no puede tener caracteres extra al final.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT tiene caracteres extra al final.",
                trace=automaton.trace,
                normalized="".join(digits),
            )

    if automaton.state == "CHECK":
        automaton.finish("ACCEPT", "NIT valido con formato NNN.NNN.NNN-D completo.")
        return build_accept(
            consumed=automaton.consumed,
            message="NIT valido.",
            trace=automaton.trace,
            normalized="".join(digits),
        )

    automaton.finish("REJECT", f"La cadena termina en estado incompleto: {automaton.state}.")
    return build_reject(
        consumed=automaton.consumed,
        message="El NIT esta incompleto.",
        trace=automaton.trace,
        normalized="".join(digits),
    )
