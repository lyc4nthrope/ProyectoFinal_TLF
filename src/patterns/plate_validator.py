"""AFD para placas vehiculares colombianas.

Responsabilidad unica: recorrer char-by-char y decidir si la cadena es
placa de carro (LLLDDD) o moto (LLLDDDL). Sin logica de UI ni de scanner.
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult, build_accept, build_reject, reject_empty
from src.core.symbol_classifier import is_digit, is_upper_letter

# ── Estados del automata ──────────────────────────────────────────────
# L1/L2/L3   = primera, segunda y tercera letra
# AFTER_L3   = separador opcional entre letras y digitos
# D1/D2/D3   = primer, segundo y tercer digito
# AFTER_D3   = separador opcional antes de letra de moto
# L4         = letra extra de moto


def _is_hyphen(symbol: str) -> bool:
    return symbol == "-"


def validate_plate(text: str) -> ValidationResult:
    """Valida placas vehiculares colombianas mediante un AFD explicito.

    Formatos aceptados:
    - Carro: LLL-DDD o LLLDDD (3 letras + 3 digitos)
    - Moto:  LLL-DDDL o LLLDDDL (3 letras + 3 digitos + 1 letra)

    Reglas:
    - Solo letras mayusculas A-Z y digitos 0-9.
    - El guion es separador opcional entre el bloque de letras y el de digitos.
    - La cadena no puede terminar en guion ni tener simbolos extra al final.
    """

    automaton = TraceableAutomaton(state="START")
    normalized: list[str] = []

    if not text:
        return reject_empty("START")

    for symbol in text:
        if automaton.state == "START":
            if is_upper_letter(symbol):
                automaton.record(symbol, "L1", "Primera letra de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "La placa debe iniciar con letra mayuscula.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa no inicia con letra mayuscula.",
                trace=automaton.trace,
            )

        if automaton.state == "L1":
            if is_upper_letter(symbol):
                automaton.record(symbol, "L2", "Segunda letra de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba la segunda letra.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene menos de tres letras iniciales.",
                trace=automaton.trace,
            )

        if automaton.state == "L2":
            if is_upper_letter(symbol):
                automaton.record(symbol, "L3", "Tercera letra de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba la tercera letra.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene menos de tres letras iniciales.",
                trace=automaton.trace,
            )

        if automaton.state == "L3":
            if _is_hyphen(symbol):
                automaton.record(symbol, "AFTER_L3", "Separador opcional entre letras y digitos.")
                continue
            if is_digit(symbol):
                automaton.record(symbol, "D1", "Primer digito de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues de las tres letras debe venir digito o guion.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene un simbolo invalido despues del bloque de letras.",
                trace=automaton.trace,
            )

        if automaton.state == "AFTER_L3":
            if is_digit(symbol):
                automaton.record(symbol, "D1", "Primer digito despues del separador.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del guion debe venir un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene un guion mal ubicado.",
                trace=automaton.trace,
            )

        if automaton.state == "D1":
            if is_digit(symbol):
                automaton.record(symbol, "D2", "Segundo digito de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene menos de tres digitos.",
                trace=automaton.trace,
            )

        if automaton.state == "D2":
            if is_digit(symbol):
                automaton.record(symbol, "D3", "Tercer digito de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene menos de tres digitos.",
                trace=automaton.trace,
            )

        if automaton.state == "D3":
            # Carro termina aqui. Moto puede tener guion o letra extra.
            if is_upper_letter(symbol):
                automaton.record(symbol, "L4", "Letra adicional de placa de moto.")
                normalized.append(symbol)
                continue
            if _is_hyphen(symbol):
                automaton.record(symbol, "AFTER_D3", "Separador antes de la letra de moto.")
                continue
            automaton.record(symbol, "REJECT", "Simbolo inesperado despues del tercer digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene caracteres extra al final.",
                trace=automaton.trace,
                normalized="".join(normalized),
            )

        if automaton.state == "AFTER_D3":
            if is_upper_letter(symbol):
                automaton.record(symbol, "L4", "Letra de moto despues del separador.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del guion debe venir la letra de moto.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa termina en guion sin letra de moto.",
                trace=automaton.trace,
            )

        if automaton.state == "L4":
            automaton.record(symbol, "REJECT", "La placa de moto no puede tener caracteres extra.")
            return build_reject(
                consumed=automaton.consumed,
                message="La placa tiene caracteres extra al final.",
                trace=automaton.trace,
                normalized="".join(normalized),
            )

    # Evaluacion del estado final al agotar la entrada.
    if automaton.state == "D3":
        automaton.finish("ACCEPT", "Placa de carro valida con formato LLLDDD.")
        return build_accept(
            consumed=automaton.consumed,
            message="Placa de carro valida.",
            trace=automaton.trace,
            normalized="".join(normalized),
        )

    if automaton.state == "L4":
        automaton.finish("ACCEPT", "Placa de moto valida con formato LLLDDDL.")
        return build_accept(
            consumed=automaton.consumed,
            message="Placa de moto valida.",
            trace=automaton.trace,
            normalized="".join(normalized),
        )

    if automaton.state in {"D1", "D2"}:
        automaton.finish("REJECT", "La cadena termina antes de completar los tres digitos.")
        return build_reject(
            consumed=automaton.consumed,
            message="La placa tiene menos de tres digitos.",
            trace=automaton.trace,
            normalized="".join(normalized),
        )

    if automaton.state == "AFTER_D3":
        automaton.finish("REJECT", "La cadena termina en guion sin la letra de moto.")
        return build_reject(
            consumed=automaton.consumed,
            message="La placa tiene caracteres extra al final.",
            trace=automaton.trace,
            normalized="".join(normalized),
        )

    if automaton.state in {"L1", "L2"}:
        automaton.finish("REJECT", "La cadena termina antes de completar las tres letras iniciales.")
        return build_reject(
            consumed=automaton.consumed,
            message="La placa tiene menos de tres letras iniciales.",
            trace=automaton.trace,
            normalized="".join(normalized),
        )

    if automaton.state == "AFTER_L3":
        automaton.finish("REJECT", "La cadena termina en guion sin digitos.")
        return build_reject(
            consumed=automaton.consumed,
            message="La placa tiene un guion al final sin digitos.",
            trace=automaton.trace,
            normalized="".join(normalized),
        )

    automaton.finish("REJECT", f"La cadena termina en estado incompleto: {automaton.state}.")
    return build_reject(
        consumed=automaton.consumed,
        message="La placa esta incompleta.",
        trace=automaton.trace,
        normalized="".join(normalized),
    )
