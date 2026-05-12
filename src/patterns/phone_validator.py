"""AFD para numeros telefonicos con deteccion dinamica de codigo de pais.

Responsabilidad unica: recorrer char-by-char con estados START /
AFTER_PLUS / IN_NUMBER / AFTER_SEPARATOR y validar cantidad de digitos
reales al cierre. Sin logica de UI ni de scanner.

Reglas de validacion:
- Sin prefijo +: exactamente 10 digitos (numero local).
- Con prefijo +: los ultimos 10 digitos son el numero local; el resto
  es el codigo de pais (cualquier longitud >= 1).
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult, build_accept, build_reject, reject_empty
from src.core.symbol_classifier import is_digit

LOCAL_DIGITS = 10


def _is_phone_separator(symbol: str) -> bool:
    """Permite separar bloques numericos sin romper la lectura del telefono."""

    return symbol in {" ", "-"}


def _is_plus(symbol: str) -> bool:
    """Reconoce el simbolo de prefijo internacional."""

    return symbol == "+"


def validate_phone(text: str) -> ValidationResult:
    """Valida telefonos mediante estados y recorrido simbolo por simbolo.

    Reglas implementadas:
    - Puede iniciar con `+` una sola vez.
    - Solo se permiten digitos, espacio y guion.
    - No se permiten dos separadores consecutivos.
    - Sin prefijo +: exactamente 10 digitos.
    - Con prefijo +: los ultimos 10 digitos son el numero local.
    - No puede terminar en separador.
    """

    automaton = TraceableAutomaton(state="START")
    digits = 0
    normalized_digits: list[str] = []
    has_plus = False
    first_block_digits = 0  # digitos antes del primer separador (codigo de pais si hay +)
    saw_separator = False

    if not text:
        return reject_empty("START")

    for symbol in text:
        # El estado START decide si la cadena entra como telefono local o internacional.
        if automaton.state == "START":
            if _is_plus(symbol):
                has_plus = True
                automaton.record(symbol, "AFTER_PLUS", "Se detecta prefijo internacional.")
                continue
            if is_digit(symbol):
                automaton.record(symbol, "IN_NUMBER", "Empieza la secuencia principal de digitos.")
                digits += 1
                first_block_digits += 1
                normalized_digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El telefono debe iniciar con '+' o un digito.")
            return build_reject(consumed=automaton.consumed, message="Inicio invalido para el telefono.", trace=automaton.trace)

        # Si ya aparecio '+', el siguiente simbolo obligatoriamente debe ser un digito.
        if automaton.state == "AFTER_PLUS":
            if is_digit(symbol):
                automaton.record(symbol, "IN_NUMBER", "Despues del prefijo solo se aceptan digitos.")
                digits += 1
                first_block_digits += 1  # primer bloque = codigo de pais
                normalized_digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues de '+' debe aparecer un digito.")
            return build_reject(consumed=automaton.consumed, message="El prefijo internacional esta mal formado.", trace=automaton.trace)

        # IN_NUMBER concentra la lectura normal del telefono mientras sigan apareciendo digitos.
        if automaton.state == "IN_NUMBER":
            if is_digit(symbol):
                automaton.stay(symbol, "Se acumula un nuevo digito del telefono.")
                digits += 1
                if not saw_separator:
                    first_block_digits += 1
                normalized_digits.append(symbol)
                continue

            if _is_phone_separator(symbol):
                saw_separator = True
                automaton.record(
                    symbol,
                    "AFTER_SEPARATOR",
                    "Se separan bloques numericos.",
                )
                continue

            automaton.record(symbol, "REJECT", "Aparece un simbolo fuera del alfabeto permitido.")
            return build_reject(consumed=automaton.consumed, message="El telefono contiene simbolos no permitidos.", trace=automaton.trace)

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
                return build_reject(consumed=automaton.consumed, message="Hay separadores consecutivos en el telefono.", trace=automaton.trace)

            automaton.record(
                symbol,
                "REJECT",
                "Despues de un separador debe venir un digito.",
            )
            return build_reject(consumed=automaton.consumed, message="El telefono tiene un bloque vacio despues de un separador.", trace=automaton.trace)

    # ── Validacion al cierre ────────────────────────────────────────
    # AFTER_SEPARATOR al cierre = termina en separador — rechazo formal sin lookahead.
    if automaton.state == "AFTER_SEPARATOR":
        automaton.finish("REJECT", "La cadena termina en separador — estado no aceptable.")
        return build_reject(consumed=automaton.consumed, message="El telefono termina con separador.", trace=automaton.trace)

    normalized = "".join(normalized_digits)

    if has_plus:
        if saw_separator:
            # Hay separadores: el primer bloque es el codigo de pais,
            # el resto son digitos locales.
            local_digits = digits - first_block_digits
            if local_digits != LOCAL_DIGITS:
                automaton.finish(
                    "REJECT",
                    f"cantidad de digitos locales {local_digits} distinta de "
                    f"{LOCAL_DIGITS} requeridos.",
                )
                return build_reject(
                    consumed=automaton.consumed,
                    message="La cantidad de digitos del telefono es invalida.",
                    trace=automaton.trace,
                    normalized=normalized,
                )
            country_code = normalized[:first_block_digits]
            local_number = normalized[first_block_digits:]
        else:
            # Sin separadores: heuristico — ultimos 10 digitos son locales,
            # el resto es codigo de pais.
            if len(normalized) < LOCAL_DIGITS + 1:
                automaton.finish(
                    "REJECT",
                    f"cantidad de digitos {len(normalized)} insuficiente: "
                    f"se necesita al menos 1 de pais + {LOCAL_DIGITS} locales.",
                )
                return build_reject(
                    consumed=automaton.consumed,
                    message="La cantidad de digitos del telefono es invalida.",
                    trace=automaton.trace,
                    normalized=normalized,
                )
            country_code = normalized[:-LOCAL_DIGITS]
            local_number = normalized[-LOCAL_DIGITS:]

        automaton.finish(
            "ACCEPT",
            f"telefono valido: pais {country_code}, numero local {local_number}.",
        )
        return build_accept(
            consumed=automaton.consumed,
            message="Telefono valido.",
            trace=automaton.trace,
            normalized=normalized,
        )

    # Sin prefijo: exactamente LOCAL_DIGITS digitos.
    if len(normalized) != LOCAL_DIGITS:
        automaton.finish(
            "REJECT",
            f"cantidad de digitos {len(normalized)} distinta de {LOCAL_DIGITS} requeridos.",
        )
        return build_reject(
            consumed=automaton.consumed,
            message="La cantidad de digitos del telefono es invalida.",
            trace=automaton.trace,
            normalized=normalized,
        )
    automaton.finish("ACCEPT", f"telefono valido con {LOCAL_DIGITS} digitos.")
    return build_accept(
        consumed=automaton.consumed,
        message="Telefono valido.",
        trace=automaton.trace,
        normalized=normalized,
    )
