"""AFD para correos electronicos (local@dominio.tld).

Responsabilidad unica: recorrer char-by-char con estados LOCAL /
LOCAL_SEPARATOR / AFTER_AT / DOMAIN / DOMAIN_HYPHEN / AFTER_DOMAIN_DOT
y verificar TLD con al menos 2 letras al cierre. Sin logica de UI.
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult, build_accept, build_reject, reject_empty
from src.core.symbol_classifier import is_alphanumeric, is_letter

MIN_TLD_LETTERS = 2
MAX_EMAIL_LENGTH = 254       # RFC 5321
MAX_LOCAL_LENGTH = 64        # RFC 5321
MAX_LABEL_LENGTH = 63        # RFC 1035


def _is_local_separator(symbol: str) -> bool:
    """Separadores permitidos dentro de la parte local del correo."""

    return symbol in {".", "_", "-", "+"}


def _is_domain_separator(symbol: str) -> bool:
    """Separador entre etiquetas del dominio."""

    return symbol == "."


def _is_at_symbol(symbol: str) -> bool:
    """Reconoce el separador entre parte local y dominio."""

    return symbol == "@"


def _is_domain_hyphen(symbol: str) -> bool:
    """Permite guiones internos dentro de una etiqueta del dominio."""

    return symbol == "-"


def _handle_local_exceeded(
    automaton: TraceableAutomaton,
    symbol: str,
) -> ValidationResult:
    """Registra y retorna un rechazo por exceder MAX_LOCAL_LENGTH."""
    automaton.record(symbol, "REJECT", "La parte local excede la longitud maxima.")
    return build_reject(
        consumed=automaton.consumed,
        message="La parte local del correo es demasiado larga.",
        trace=automaton.trace,
    )


def validate_email(text: str) -> ValidationResult:
    """Valida correos con un automata explicable y restricciones controladas.

    Reglas implementadas:
    - La parte local debe iniciar con letra o digito.
    - La parte local puede contener letras, digitos, punto, guion y guion bajo.
    - La parte local no puede terminar en separador ni repetir separadores.
    - Debe existir exactamente un `@`.
    - Cada etiqueta del dominio debe iniciar con letra o digito.
    - El dominio puede contener guiones internos.
    - El dominio debe tener al menos un punto.
    - La ultima etiqueta del dominio debe terminar con al menos 2 letras.
    """

    if len(text) > MAX_EMAIL_LENGTH:
        return build_reject(
            consumed=0,
            message=f"El correo excede la longitud maxima de {MAX_EMAIL_LENGTH} caracteres.",
            trace=[],
        )

    automaton = TraceableAutomaton(state="START")
    normalized_symbols: list[str] = []
    saw_at_symbol = False
    saw_domain_dot = False
    tld_letters = 0
    local_length = 0
    current_label_length = 0

    if not text:
        return reject_empty("START")

    for symbol in text:
        # START decide si la parte local arranca con un simbolo valido.
        if automaton.state == "START":
            if is_alphanumeric(symbol):
                automaton.record(symbol, "LOCAL", "Empieza la parte local del correo.")
                normalized_symbols.append(symbol)
                local_length = 1
                continue

            automaton.record(
                symbol,
                "REJECT",
                "La parte local debe iniciar con letra o digito.",
            )
            return build_reject(
                consumed=automaton.consumed,
                message="La parte local del correo inicia de forma invalida.",
                trace=automaton.trace,
            )

        # LOCAL concentra la lectura normal antes de llegar al simbolo '@'.
        if automaton.state == "LOCAL":
            if is_alphanumeric(symbol):
                automaton.stay(symbol, "Se acumula un simbolo valido en la parte local.")
                normalized_symbols.append(symbol)
                local_length += 1
                if local_length > MAX_LOCAL_LENGTH:
                    return _handle_local_exceeded(automaton, symbol)
                continue

            if _is_local_separator(symbol):
                automaton.record(
                    symbol,
                    "LOCAL_SEPARATOR",
                    "La parte local usa un separador interno permitido.",
                )
                normalized_symbols.append(symbol)
                continue

            if _is_at_symbol(symbol):
                automaton.record(
                    symbol,
                    "AFTER_AT",
                    "Termina la parte local e inicia el dominio.",
                )
                normalized_symbols.append(symbol)
                saw_at_symbol = True
                continue

            automaton.record(
                symbol,
                "REJECT",
                "Aparece un simbolo no permitido en la parte local.",
            )
            return build_reject(
                consumed=automaton.consumed,
                message="La parte local del correo contiene simbolos no permitidos.",
                trace=automaton.trace,
            )

        # LOCAL_SEPARATOR obliga a retomar la parte local con letra o digito.
        if automaton.state == "LOCAL_SEPARATOR":
            if is_alphanumeric(symbol):
                automaton.record(
                    symbol,
                    "LOCAL",
                    "Despues del separador la parte local debe retomar con simbolo valido.",
                )
                normalized_symbols.append(symbol)
                local_length += 1
                if local_length > MAX_LOCAL_LENGTH:
                    return _handle_local_exceeded(automaton, symbol)
                continue

            automaton.record(
                symbol,
                "REJECT",
                "La parte local no puede terminar ni repetir separadores.",
            )
            return build_reject(
                consumed=automaton.consumed,
                message="La parte local del correo tiene separadores mal ubicados.",
                trace=automaton.trace,
            )

        # AFTER_AT valida el inicio formal de la primera etiqueta del dominio.
        if automaton.state == "AFTER_AT":
            if is_alphanumeric(symbol):
                automaton.record(
                    symbol,
                    "DOMAIN",
                    "Empieza la primera etiqueta del dominio.",
                )
                normalized_symbols.append(symbol)
                tld_letters = 1 if is_letter(symbol) else 0
                current_label_length = 1
                continue

            automaton.record(
                symbol,
                "REJECT",
                "Despues de '@' debe empezar una etiqueta valida del dominio.",
            )
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio del correo inicia de forma invalida.",
                trace=automaton.trace,
            )

        # DOMAIN procesa letras y digitos normales dentro de cada etiqueta.
        if automaton.state == "DOMAIN":
            if is_alphanumeric(symbol):
                automaton.stay(symbol, "Se acumula un simbolo dentro de la etiqueta del dominio.")
                normalized_symbols.append(symbol)
                tld_letters = tld_letters + 1 if is_letter(symbol) else 0
                current_label_length += 1
                if current_label_length > MAX_LABEL_LENGTH:
                    automaton.record(symbol, "REJECT", "La etiqueta del dominio excede la longitud maxima.")
                    return build_reject(
                        consumed=automaton.consumed,
                        message="El dominio del correo tiene una etiqueta demasiado larga.",
                        trace=automaton.trace,
                    )
                continue

            if _is_domain_hyphen(symbol):
                automaton.record(
                    symbol,
                    "DOMAIN_HYPHEN",
                    "Se detecta un guion interno en la etiqueta del dominio.",
                )
                normalized_symbols.append(symbol)
                tld_letters = 0
                continue

            if _is_domain_separator(symbol):
                automaton.record(
                    symbol,
                    "AFTER_DOMAIN_DOT",
                    "Se cierra una etiqueta del dominio y debe iniciar otra.",
                )
                normalized_symbols.append(symbol)
                saw_domain_dot = True
                tld_letters = 0
                current_label_length = 0
                continue

            automaton.record(
                symbol,
                "REJECT",
                "Aparece un simbolo no permitido en el dominio.",
            )
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio del correo contiene simbolos no permitidos.",
                trace=automaton.trace,
            )

        # DOMAIN_HYPHEN evita que el guion cierre una etiqueta del dominio.
        if automaton.state == "DOMAIN_HYPHEN":
            if is_alphanumeric(symbol):
                automaton.record(
                    symbol,
                    "DOMAIN",
                    "Despues del guion la etiqueta del dominio debe continuar con simbolo valido.",
                )
                normalized_symbols.append(symbol)
                tld_letters = 1 if is_letter(symbol) else 0
                current_label_length += 1
                if current_label_length > MAX_LABEL_LENGTH:
                    automaton.record(symbol, "REJECT", "La etiqueta del dominio excede la longitud maxima.")
                    return build_reject(
                        consumed=automaton.consumed,
                        message="El dominio del correo tiene una etiqueta demasiado larga.",
                        trace=automaton.trace,
                    )
                continue

            automaton.record(
                symbol,
                "REJECT",
                "El guion del dominio no puede quedar al final de una etiqueta.",
            )
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio del correo tiene un guion mal ubicado.",
                trace=automaton.trace,
            )

        # AFTER_DOMAIN_DOT obliga a que cada nueva etiqueta del dominio no quede vacia.
        if automaton.state == "AFTER_DOMAIN_DOT":
            if is_alphanumeric(symbol):
                automaton.record(
                    symbol,
                    "DOMAIN",
                    "Despues del punto debe iniciar una nueva etiqueta valida.",
                )
                normalized_symbols.append(symbol)
                tld_letters = 1 if is_letter(symbol) else 0
                current_label_length = 1
                continue

            automaton.record(
                symbol,
                "REJECT",
                "Despues del punto del dominio debe venir una nueva etiqueta.",
            )
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio del correo tiene etiquetas vacias.",
                trace=automaton.trace,
            )

    # El cierre exige dominio con punto y una terminacion alfabetica suficiente.
    if not saw_at_symbol:
        automaton.finish("REJECT", "No aparecio el separador obligatorio '@'.")
        return build_reject(
            consumed=automaton.consumed,
            message="El correo no contiene el simbolo '@'.",
            trace=automaton.trace,
            normalized="".join(normalized_symbols),
        )

    if automaton.state in {"AFTER_AT", "AFTER_DOMAIN_DOT", "DOMAIN_HYPHEN", "LOCAL_SEPARATOR"}:
        automaton.finish("REJECT", "La cadena termina en un estado no aceptable.")
        return build_reject(
            consumed=automaton.consumed,
            message="El correo termina en una estructura incompleta.",
            trace=automaton.trace,
            normalized="".join(normalized_symbols),
        )

    if not saw_domain_dot:
        automaton.finish("REJECT", "El dominio no contiene el punto obligatorio.")
        return build_reject(
            consumed=automaton.consumed,
            message="El dominio del correo debe contener al menos un punto.",
            trace=automaton.trace,
            normalized="".join(normalized_symbols),
        )

    if tld_letters < MIN_TLD_LETTERS:
        automaton.finish(
            "REJECT",
            f"La ultima etiqueta del dominio debe terminar con al menos {MIN_TLD_LETTERS} letras.",
        )
        return build_reject(
            consumed=automaton.consumed,
            message="La terminacion del dominio del correo es invalida.",
            trace=automaton.trace,
            normalized="".join(normalized_symbols),
        )

    automaton.finish("ACCEPT", "Correo valido con estructura local y dominio correctos.")
    return build_accept(
        consumed=automaton.consumed,
        message="Correo valido.",
        trace=automaton.trace,
        normalized="".join(normalized_symbols),
    )
