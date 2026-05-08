"""Validador manual para placas vehiculares colombianas."""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult
from src.core.symbol_classifier import is_digit, is_letter


def _is_upper(symbol: str) -> bool:
    """Indica si el simbolo es una letra mayuscula del rango A-Z."""

    return is_letter(symbol) and symbol == symbol.upper()


def _is_hyphen(symbol: str) -> bool:
    return symbol == "-"


def _accepted_plate_result(
    automaton: TraceableAutomaton,
    symbols: list[str],
    plate_type: str,
) -> ValidationResult:
    return ValidationResult.accept(
        consumed=automaton.consumed,
        message=f"Placa de {plate_type} valida.",
        trace=automaton.trace,
        normalized="".join(symbols),
    )


def _rejected_plate_result(
    automaton: TraceableAutomaton,
    message: str,
    symbols: list[str] | None = None,
) -> ValidationResult:
    return ValidationResult.reject(
        consumed=automaton.consumed,
        message=message,
        trace=automaton.trace,
        normalized="".join(symbols) if symbols else "",
    )


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
        return ValidationResult.reject(
            consumed=0,
            message="La cadena esta vacia.",
            trace=["START: no hay simbolos para procesar."],
        )

    for symbol in text:
        if automaton.state == "START":
            if _is_upper(symbol):
                automaton.record(symbol, "L1", "Primera letra de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "La placa debe iniciar con letra mayuscula.")
            return _rejected_plate_result(automaton, "La placa no inicia con letra mayuscula.")

        if automaton.state == "L1":
            if _is_upper(symbol):
                automaton.record(symbol, "L2", "Segunda letra de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba la segunda letra.")
            return _rejected_plate_result(automaton, "La placa tiene menos de tres letras iniciales.")

        if automaton.state == "L2":
            if _is_upper(symbol):
                automaton.record(symbol, "L3", "Tercera letra de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba la tercera letra.")
            return _rejected_plate_result(automaton, "La placa tiene menos de tres letras iniciales.")

        if automaton.state == "L3":
            if _is_hyphen(symbol):
                automaton.record(symbol, "AFTER_L3", "Separador opcional entre letras y digitos.")
                continue
            if is_digit(symbol):
                automaton.record(symbol, "D1", "Primer digito de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues de las tres letras debe venir digito o guion.")
            return _rejected_plate_result(automaton, "La placa tiene un simbolo invalido despues del bloque de letras.")

        if automaton.state == "AFTER_L3":
            if is_digit(symbol):
                automaton.record(symbol, "D1", "Primer digito despues del separador.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del guion debe venir un digito.")
            return _rejected_plate_result(automaton, "La placa tiene un guion mal ubicado.")

        if automaton.state == "D1":
            if is_digit(symbol):
                automaton.record(symbol, "D2", "Segundo digito de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el segundo digito.")
            return _rejected_plate_result(automaton, "La placa tiene menos de tres digitos.")

        if automaton.state == "D2":
            if is_digit(symbol):
                automaton.record(symbol, "D3", "Tercer digito de la placa.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba el tercer digito.")
            return _rejected_plate_result(automaton, "La placa tiene menos de tres digitos.")

        if automaton.state == "D3":
            # Carro termina aqui. Moto puede tener guion o letra extra.
            if _is_upper(symbol):
                automaton.record(symbol, "L4", "Letra adicional de placa de moto.")
                normalized.append(symbol)
                continue
            if _is_hyphen(symbol):
                automaton.record(symbol, "AFTER_D3", "Separador antes de la letra de moto.")
                continue
            automaton.record(symbol, "REJECT", "Simbolo inesperado despues del tercer digito.")
            return _rejected_plate_result(automaton, "La placa tiene caracteres extra al final.", normalized)

        if automaton.state == "AFTER_D3":
            if _is_upper(symbol):
                automaton.record(symbol, "L4", "Letra de moto despues del separador.")
                normalized.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del guion debe venir la letra de moto.")
            return _rejected_plate_result(automaton, "La placa termina en guion sin letra de moto.")

        if automaton.state == "L4":
            automaton.record(symbol, "REJECT", "La placa de moto no puede tener caracteres extra.")
            return _rejected_plate_result(automaton, "La placa tiene caracteres extra al final.", normalized)

    # Evaluacion del estado final al agotar la entrada.
    if automaton.state == "D3":
        automaton.finish("ACCEPT", "Placa de carro valida con formato LLLDDD.")
        return _accepted_plate_result(automaton, normalized, "carro")

    if automaton.state == "L4":
        automaton.finish("ACCEPT", "Placa de moto valida con formato LLLDDDL.")
        return _accepted_plate_result(automaton, normalized, "moto")

    if automaton.state in {"D1", "D2"}:
        automaton.finish("REJECT", "La cadena termina antes de completar los tres digitos.")
        return _rejected_plate_result(automaton, "La placa tiene menos de tres digitos.", normalized)

    if automaton.state == "AFTER_D3":
        automaton.finish("REJECT", "La cadena termina en guion sin la letra de moto.")
        return _rejected_plate_result(automaton, "La placa tiene caracteres extra al final.", normalized)

    if automaton.state in {"L1", "L2"}:
        automaton.finish("REJECT", "La cadena termina antes de completar las tres letras iniciales.")
        return _rejected_plate_result(automaton, "La placa tiene menos de tres letras iniciales.", normalized)

    if automaton.state == "AFTER_L3":
        automaton.finish("REJECT", "La cadena termina en guion sin digitos.")
        return _rejected_plate_result(automaton, "La placa tiene un guion al final sin digitos.", normalized)

    automaton.finish("REJECT", f"La cadena termina en estado incompleto: {automaton.state}.")
    return _rejected_plate_result(automaton, "La placa esta incompleta.", normalized)
