"""Validador manual para numeros telefonicos."""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult
from src.core.symbol_classifier import is_digit

MIN_DIGITS = 10
MAX_DIGITS = 13


def _is_phone_separator(symbol: str) -> bool:
    """Permite separar bloques numericos sin romper la lectura del telefono."""

    return symbol in {" ", "-"}


def _is_plus(symbol: str) -> bool:
    """Reconoce el simbolo de prefijo internacional."""

    return symbol == "+"


def _accepted_phone_result(
    automaton: TraceableAutomaton,
    normalized_digits: list[str],
) -> ValidationResult:
    """Normaliza la salida aceptada para reutilizar el mismo formato."""

    return ValidationResult.accept(
        consumed=automaton.consumed,
        message="Telefono valido.",
        trace=automaton.trace,
        normalized="".join(normalized_digits),
    )


def _rejected_phone_result(
    automaton: TraceableAutomaton,
    message: str,
    normalized_digits: list[str] | None = None,
) -> ValidationResult:
    """Centraliza la salida rechazada sin duplicar la construccion del resultado."""

    normalized = ""
    if normalized_digits is not None:
        normalized = "".join(normalized_digits)

    return ValidationResult.reject(
        consumed=automaton.consumed,
        message=message,
        trace=automaton.trace,
        normalized=normalized,
    )


def validate_phone(text: str) -> ValidationResult:
    """Valida telefonos mediante estados y recorrido simbolo por simbolo.

    Reglas implementadas:
    - Puede iniciar con `+` una sola vez.
    - Solo se permiten digitos, espacio y guion.
    - No se permiten dos separadores consecutivos.
    - Debe contener entre 10 y 13 digitos.
    - No puede terminar en separador.
    """

    automaton = TraceableAutomaton(state="START")
    digits = 0
    normalized_digits: list[str] = []

    if not text:
        return ValidationResult.reject(
            consumed=0,
            message="La cadena esta vacia.",
            trace=["START: no hay simbolos para procesar."],
        )

    for index, symbol in enumerate(text):
        # El estado START decide si la cadena entra como telefono local o internacional.
        if automaton.state == "START":
            if _is_plus(symbol):
                automaton.record(symbol, "AFTER_PLUS", "Se detecta prefijo internacional.")
                continue
            if is_digit(symbol):
                automaton.record(symbol, "IN_NUMBER", "Empieza la secuencia principal de digitos.")
                digits += 1
                normalized_digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El telefono debe iniciar con '+' o un digito.")
            return _rejected_phone_result(automaton, "Inicio invalido para el telefono.")

        # Si ya aparecio '+', el siguiente simbolo obligatoriamente debe ser un digito.
        if automaton.state == "AFTER_PLUS":
            if is_digit(symbol):
                automaton.record(symbol, "IN_NUMBER", "Despues del prefijo solo se aceptan digitos.")
                digits += 1
                normalized_digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues de '+' debe aparecer un digito.")
            return _rejected_phone_result(automaton, "El prefijo internacional esta mal formado.")

        # IN_NUMBER concentra la lectura normal del telefono mientras sigan apareciendo digitos.
        if automaton.state == "IN_NUMBER":
            if is_digit(symbol):
                automaton.stay(symbol, "Se acumula un nuevo digito del telefono.")
                digits += 1
                normalized_digits.append(symbol)
                continue

            if _is_phone_separator(symbol):
                if index == len(text) - 1:
                    automaton.record(
                        symbol,
                        "REJECT",
                        "El telefono no puede terminar con separador.",
                    )
                    return _rejected_phone_result(automaton, "El telefono termina con separador.")

                automaton.record(
                    symbol,
                    "AFTER_SEPARATOR",
                    "Se separan bloques numericos sin cerrar la cadena.",
                )
                continue

            automaton.record(symbol, "REJECT", "Aparece un simbolo fuera del alfabeto permitido.")
            return _rejected_phone_result(automaton, "El telefono contiene simbolos no permitidos.")

        # AFTER_SEPARATOR obliga a reanudar la cadena con un digito real.
        if automaton.state == "AFTER_SEPARATOR":
            if is_digit(symbol):
                automaton.record(symbol, "IN_NUMBER", "Despues del separador debe aparecer un digito.")
                digits += 1
                normalized_digits.append(symbol)
                continue

            if _is_phone_separator(symbol):
                automaton.record(
                    symbol,
                    "REJECT",
                    "No se permiten separadores consecutivos.",
                )
                return _rejected_phone_result(
                    automaton,
                    "Hay separadores consecutivos en el telefono.",
                )

            automaton.record(
                symbol,
                "REJECT",
                "Despues de un separador debe venir un digito.",
            )
            return _rejected_phone_result(
                automaton,
                "El telefono tiene un bloque vacio despues de un separador.",
            )

    # La aceptacion final depende del total de digitos reales, no de la longitud cruda.
    if digits < MIN_DIGITS or digits > MAX_DIGITS:
        automaton.finish(
            "REJECT",
            f"cantidad de digitos {digits} fuera del rango {MIN_DIGITS}-{MAX_DIGITS}.",
        )
        return _rejected_phone_result(
            automaton,
            "La cantidad de digitos del telefono es invalida.",
            normalized_digits,
        )

    automaton.finish("ACCEPT", f"telefono valido con {digits} digitos.")
    return _accepted_phone_result(automaton, normalized_digits)
