"""Validador manual para correos electronicos."""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult
from src.core.symbol_classifier import is_alphanumeric, is_letter

MIN_TLD_LETTERS = 2


def _is_local_separator(symbol: str) -> bool:
    """Separadores permitidos dentro de la parte local del correo."""

    return symbol in {".", "_", "-"}


def _is_domain_separator(symbol: str) -> bool:
    """Separador entre etiquetas del dominio."""

    return symbol == "."


def _is_at_symbol(symbol: str) -> bool:
    """Reconoce el separador entre parte local y dominio."""

    return symbol == "@"


def _is_domain_hyphen(symbol: str) -> bool:
    """Permite guiones internos dentro de una etiqueta del dominio."""

    return symbol == "-"


def _accepted_email_result(
    automaton: TraceableAutomaton,
    normalized_symbols: list[str],
) -> ValidationResult:
    """Normaliza la salida aceptada del correo."""

    return ValidationResult.accept(
        consumed=automaton.consumed,
        message="Correo valido.",
        trace=automaton.trace,
        normalized="".join(normalized_symbols),
    )


def _rejected_email_result(
    automaton: TraceableAutomaton,
    message: str,
    normalized_symbols: list[str] | None = None,
) -> ValidationResult:
    """Centraliza la salida rechazada del correo."""

    normalized = ""
    if normalized_symbols is not None:
        normalized = "".join(normalized_symbols)

    return ValidationResult.reject(
        consumed=automaton.consumed,
        message=message,
        trace=automaton.trace,
        normalized=normalized,
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

    automaton = TraceableAutomaton(state="START")
    normalized_symbols: list[str] = []
    saw_at_symbol = False
    saw_domain_dot = False
    tld_letters = 0

    if not text:
        return ValidationResult.reject(
            consumed=0,
            message="La cadena esta vacia.",
            trace=["START: no hay simbolos para procesar."],
        )

    for index, symbol in enumerate(text):
        # START decide si la parte local arranca con un simbolo valido.
        if automaton.state == "START":
            if is_alphanumeric(symbol):
                automaton.record(symbol, "LOCAL", "Empieza la parte local del correo.")
                normalized_symbols.append(symbol)
                continue

            automaton.record(
                symbol,
                "REJECT",
                "La parte local debe iniciar con letra o digito.",
            )
            return _rejected_email_result(
                automaton,
                "La parte local del correo inicia de forma invalida.",
            )

        # LOCAL concentra la lectura normal antes de llegar al simbolo '@'.
        if automaton.state == "LOCAL":
            if is_alphanumeric(symbol):
                automaton.stay(symbol, "Se acumula un simbolo valido en la parte local.")
                normalized_symbols.append(symbol)
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
            return _rejected_email_result(
                automaton,
                "La parte local del correo contiene simbolos no permitidos.",
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
                continue

            automaton.record(
                symbol,
                "REJECT",
                "La parte local no puede terminar ni repetir separadores.",
            )
            return _rejected_email_result(
                automaton,
                "La parte local del correo tiene separadores mal ubicados.",
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
                continue

            automaton.record(
                symbol,
                "REJECT",
                "Despues de '@' debe empezar una etiqueta valida del dominio.",
            )
            return _rejected_email_result(
                automaton,
                "El dominio del correo inicia de forma invalida.",
            )

        # DOMAIN procesa letras y digitos normales dentro de cada etiqueta.
        if automaton.state == "DOMAIN":
            if is_alphanumeric(symbol):
                automaton.stay(symbol, "Se acumula un simbolo dentro de la etiqueta del dominio.")
                normalized_symbols.append(symbol)
                tld_letters = tld_letters + 1 if is_letter(symbol) else 0
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
                continue

            automaton.record(
                symbol,
                "REJECT",
                "Aparece un simbolo no permitido en el dominio.",
            )
            return _rejected_email_result(
                automaton,
                "El dominio del correo contiene simbolos no permitidos.",
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
                continue

            automaton.record(
                symbol,
                "REJECT",
                "El guion del dominio no puede quedar al final de una etiqueta.",
            )
            return _rejected_email_result(
                automaton,
                "El dominio del correo tiene un guion mal ubicado.",
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
                continue

            automaton.record(
                symbol,
                "REJECT",
                "Despues del punto del dominio debe venir una nueva etiqueta.",
            )
            return _rejected_email_result(
                automaton,
                "El dominio del correo tiene etiquetas vacias.",
            )

    # El cierre exige dominio con punto y una terminacion alfabetica suficiente.
    if not saw_at_symbol:
        automaton.finish("REJECT", "No aparecio el separador obligatorio '@'.")
        return _rejected_email_result(
            automaton,
            "El correo no contiene el simbolo '@'.",
            normalized_symbols,
        )

    if automaton.state in {"AFTER_AT", "AFTER_DOMAIN_DOT", "DOMAIN_HYPHEN", "LOCAL_SEPARATOR"}:
        automaton.finish("REJECT", "La cadena termina en un estado no aceptable.")
        return _rejected_email_result(
            automaton,
            "El correo termina en una estructura incompleta.",
            normalized_symbols,
        )

    if not saw_domain_dot:
        automaton.finish("REJECT", "El dominio no contiene el punto obligatorio.")
        return _rejected_email_result(
            automaton,
            "El dominio del correo debe contener al menos un punto.",
            normalized_symbols,
        )

    if tld_letters < MIN_TLD_LETTERS:
        automaton.finish(
            "REJECT",
            f"La ultima etiqueta del dominio debe terminar con al menos {MIN_TLD_LETTERS} letras.",
        )
        return _rejected_email_result(
            automaton,
            "La terminacion del dominio del correo es invalida.",
            normalized_symbols,
        )

    automaton.finish("ACCEPT", "Correo valido con estructura local y dominio correctos.")
    return _accepted_email_result(automaton, normalized_symbols)
