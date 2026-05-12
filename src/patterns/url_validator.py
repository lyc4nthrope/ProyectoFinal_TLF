"""AFD para URLs con protocolo http o https.

Responsabilidad unica: recorrer char-by-char y decidir si la cadena es
una URL valida con formato http(s)://dominio.tld[/ruta]. Sin UI ni scanner.

Reglas de validacion:
- Protocolo exactamente http o https (case-insensitive).
- Separador obligatorio ://
- Dominio con al menos un punto (ej: example.com).
- TLD: al menos 2 caracteres, con al menos una letra.
- Longitud maxima total de 2048 caracteres.
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult, build_accept, build_reject, reject_empty
from src.core.symbol_classifier import is_alphanumeric, is_letter

MAX_URL_LENGTH = 2048


def _is_url_path_char(symbol: str) -> bool:
    """Caracteres permitidos en la ruta y query de una URL."""

    return is_alphanumeric(symbol) or symbol in {
        "/", "-", "_", ".", "?", "=", "&", "#", "~", "%", "+", "@", ":",
    }


def _handle_tld_invalid(
    tld_length: int,
    tld_has_letter: bool,
    automaton: TraceableAutomaton,
    normalized: str,
) -> ValidationResult:
    """Registra y retorna un rechazo por TLD invalido (< 2 chars o sin letras)."""
    automaton.finish(
        "REJECT",
        f"TLD invalido: longitud {tld_length}, tiene_letra={tld_has_letter}.",
    )
    return build_reject(
        consumed=automaton.consumed,
        message="El dominio de la URL tiene un TLD invalido.",
        trace=automaton.trace,
        normalized=normalized,
    )


def validate_url(text: str) -> ValidationResult:
    """Valida URLs con formato http:// o https:// seguido de dominio y ruta opcional.

    Reglas implementadas:
    - El protocolo debe ser exactamente 'http' o 'https'.
    - El separador obligatorio es '://'.
    - El dominio debe tener al menos un punto (ej: example.com).
    - El dominio no puede terminar en guion ni en punto.
    - La ruta es opcional; si aparece, puede contener caracteres URL validos.
    """

    if len(text) > MAX_URL_LENGTH:
        return build_reject(
            consumed=0,
            message=f"La URL excede la longitud maxima de {MAX_URL_LENGTH} caracteres.",
            trace=[],
        )

    automaton = TraceableAutomaton(state="START")
    normalized_symbols: list[str] = []
    saw_domain_dot = False
    tld_length = 0
    tld_has_letter = False

    for symbol in text:
        if automaton.state == "START":
            if symbol in {"h", "H"}:
                automaton.record(symbol, "PROTO_H", "Inicia protocolo http/https.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "La URL debe iniciar con 'h' de http o https.")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no inicia con protocolo valido.",
                trace=automaton.trace,
            )

        if automaton.state == "PROTO_H":
            if symbol in {"t", "T"}:
                automaton.record(symbol, "PROTO_HT", "Segundo caracter del protocolo.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba 't' (http/https).")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no tiene protocolo http o https.",
                trace=automaton.trace,
            )

        if automaton.state == "PROTO_HT":
            if symbol in {"t", "T"}:
                automaton.record(symbol, "PROTO_HTT", "Tercer caracter del protocolo.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba 't' (http/https).")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no tiene protocolo http o https.",
                trace=automaton.trace,
            )

        if automaton.state == "PROTO_HTT":
            if symbol in {"p", "P"}:
                automaton.record(symbol, "PROTO_HTTP", "Protocolo http reconocido.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba 'p' (http/https).")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no tiene protocolo http o https.",
                trace=automaton.trace,
            )

        if automaton.state == "PROTO_HTTP":
            if symbol in {"s", "S"}:
                automaton.record(symbol, "PROTO_HTTPS", "Protocolo https reconocido.")
                normalized_symbols.append(symbol)
                continue
            if symbol == ":":
                automaton.record(symbol, "COLON", "Inicio del separador ://.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba 's' o ':' despues de http.")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no tiene protocolo http o https.",
                trace=automaton.trace,
            )

        if automaton.state == "PROTO_HTTPS":
            if symbol == ":":
                automaton.record(symbol, "COLON", "Inicio del separador ://.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba ':' despues de https.")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no tiene el separador ':' tras el protocolo.",
                trace=automaton.trace,
            )

        if automaton.state == "COLON":
            if symbol == "/":
                automaton.record(symbol, "SLASH1", "Primer slash del separador ://.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '/' tras el ':'.")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no tiene el separador '//' tras ':'.",
                trace=automaton.trace,
            )

        if automaton.state == "SLASH1":
            if symbol == "/":
                automaton.record(symbol, "SLASH2", "Segundo slash del separador ://, dominio proxima.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Se esperaba '/' (segundo slash).")
            return build_reject(
                consumed=automaton.consumed,
                message="La URL no tiene el doble slash '//'.",
                trace=automaton.trace,
            )

        if automaton.state == "SLASH2":
            if is_alphanumeric(symbol):
                automaton.record(symbol, "DOMAIN", "Inicia la primera etiqueta del dominio.")
                normalized_symbols.append(symbol)
                tld_length = 1
                tld_has_letter = is_letter(symbol)
                continue
            automaton.record(symbol, "REJECT", "El dominio debe iniciar con letra o digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio de la URL es invalido.",
                trace=automaton.trace,
            )

        if automaton.state == "DOMAIN":
            if is_alphanumeric(symbol):
                automaton.stay(symbol, "Continua la etiqueta actual del dominio.")
                normalized_symbols.append(symbol)
                tld_length += 1
                if is_letter(symbol):
                    tld_has_letter = True
                continue
            if symbol == "-":
                automaton.record(symbol, "DOMAIN_HYPHEN", "Guion interno dentro de la etiqueta.")
                normalized_symbols.append(symbol)
                continue
            if symbol == ".":
                automaton.record(symbol, "DOMAIN_DOT", "Punto entre etiquetas del dominio.")
                normalized_symbols.append(symbol)
                continue
            if symbol in {"/", "?", "#"} and saw_domain_dot:
                automaton.record(symbol, "PATH", "Inicia la ruta, query o fragmento.")
                normalized_symbols.append(symbol)
                continue
            if symbol in {"/", "?", "#"} and not saw_domain_dot:
                automaton.record(symbol, "REJECT", "El dominio necesita punto antes de la ruta.")
                return build_reject(
                    consumed=automaton.consumed,
                    message="El dominio de la URL no tiene el punto obligatorio.",
                    trace=automaton.trace,
                )
            automaton.record(symbol, "REJECT", "Simbolo no permitido en el dominio.")
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio de la URL contiene simbolos invalidos.",
                trace=automaton.trace,
            )

        if automaton.state == "DOMAIN_HYPHEN":
            if is_alphanumeric(symbol):
                automaton.record(symbol, "DOMAIN", "La etiqueta retoma despues del guion.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El guion no puede cerrar una etiqueta del dominio.")
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio de la URL termina en guion invalido.",
                trace=automaton.trace,
            )

        if automaton.state == "DOMAIN_DOT":
            if is_alphanumeric(symbol):
                saw_domain_dot = True
                automaton.record(symbol, "DOMAIN", "Inicia una nueva etiqueta del dominio.")
                normalized_symbols.append(symbol)
                tld_length = 1
                tld_has_letter = is_letter(symbol)
                continue
            automaton.record(symbol, "REJECT", "Despues del punto debe iniciar una etiqueta valida.")
            return build_reject(
                consumed=automaton.consumed,
                message="El dominio de la URL termina en punto invalido.",
                trace=automaton.trace,
            )

        if automaton.state == "PATH":
            if _is_url_path_char(symbol):
                automaton.stay(symbol, "Continua la ruta de la URL.")
                normalized_symbols.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "Simbolo no permitido en la ruta de la URL.")
            return build_reject(
                consumed=automaton.consumed,
                message="La ruta de la URL contiene simbolos invalidos.",
                trace=automaton.trace,
            )

    if automaton.state == "DOMAIN" and saw_domain_dot:
        if tld_length < 2 or not tld_has_letter:
            return _handle_tld_invalid(
                tld_length, tld_has_letter, automaton, "".join(normalized_symbols),
            )
        automaton.finish("ACCEPT", "URL valida con protocolo y dominio completos.")
        return build_accept(
            consumed=automaton.consumed,
            message="URL valida.",
            trace=automaton.trace,
            normalized="".join(normalized_symbols),
        )

    if automaton.state == "PATH":
        if tld_length < 2 or not tld_has_letter:
            return _handle_tld_invalid(
                tld_length, tld_has_letter, automaton, "".join(normalized_symbols),
            )
        automaton.finish("ACCEPT", "URL valida con protocolo, dominio y ruta.")
        return build_accept(
            consumed=automaton.consumed,
            message="URL valida.",
            trace=automaton.trace,
            normalized="".join(normalized_symbols),
        )

    automaton.finish("REJECT", f"La cadena termina en estado incompleto: {automaton.state}.")
    return build_reject(
        consumed=automaton.consumed,
        message="La URL esta incompleta o mal formada.",
        trace=automaton.trace,
        normalized="".join(normalized_symbols),
    )
