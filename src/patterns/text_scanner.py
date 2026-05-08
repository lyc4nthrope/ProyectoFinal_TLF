"""Escaneo de patrones dentro de textos completos."""

from collections.abc import Callable
from dataclasses import dataclass

from src.core.symbol_classifier import is_alphanumeric, is_digit
from src.patterns.date_validator import validate_date
from src.patterns.email_validator import validate_email
from src.patterns.phone_validator import validate_phone

DATE_LENGTH = 10


@dataclass(slots=True)
class PatternMatch:
    """Coincidencia encontrada en el texto escaneado."""

    pattern: str
    start: int
    end: int
    raw: str
    normalized: str


def _is_email_char(symbol: str) -> bool:
    return is_alphanumeric(symbol) or symbol in {"@", ".", "_", "-"}


def _is_phone_char(symbol: str) -> bool:
    return is_digit(symbol) or symbol in {"+", "-", " "}


def _collect(text: str, pos: int, predicate: Callable[[str], bool]) -> str:
    """Acumula caracteres desde pos mientras cumplan el predicado."""

    end = pos
    while end < len(text) and predicate(text[end]):
        end += 1
    return text[pos:end]


def _try_date(text: str, pos: int) -> PatternMatch | None:
    """Prueba si en pos inicia una fecha valida de exactamente DATE_LENGTH caracteres."""

    if not is_digit(text[pos]):
        return None
    if pos + DATE_LENGTH > len(text):
        return None
    candidate = text[pos : pos + DATE_LENGTH]
    result = validate_date(candidate)
    if not result.accepted:
        return None
    return PatternMatch(
        pattern="date",
        start=pos,
        end=pos + DATE_LENGTH,
        raw=candidate,
        normalized=result.normalized,
    )


def _try_email(text: str, pos: int) -> PatternMatch | None:
    """Prueba si en pos inicia un correo electronico valido."""

    if not is_alphanumeric(text[pos]):
        return None
    raw = _collect(text, pos, _is_email_char)
    # Un correo nunca puede terminar con `.` — ese punto es puntuacion de la oracion.
    candidate = raw.rstrip(".")
    if not candidate or "@" not in candidate:
        return None
    result = validate_email(candidate)
    if not result.accepted:
        return None
    return PatternMatch(
        pattern="email",
        start=pos,
        end=pos + len(candidate),
        raw=candidate,
        normalized=result.normalized,
    )


def _try_phone(text: str, pos: int) -> PatternMatch | None:
    """Prueba si en pos inicia un numero de telefono valido."""

    if not (is_digit(text[pos]) or text[pos] == "+"):
        return None
    raw = _collect(text, pos, _is_phone_char)
    candidate = raw.rstrip(" -")
    if not candidate:
        return None
    result = validate_phone(candidate)
    if not result.accepted:
        return None
    return PatternMatch(
        pattern="phone",
        start=pos,
        end=pos + len(candidate),
        raw=candidate,
        normalized=result.normalized,
    )


def scan_text(text: str) -> list[PatternMatch]:
    """Recorre el texto caracter por caracter buscando patrones validos.

    Prueba en cada posicion: fecha primero por ser formato fijo, luego
    correo por requerir @, luego telefono. Si ninguno aplica, avanza uno.
    No usa expresiones regulares. Cada candidato se valida con el automata
    formal del patron correspondiente.
    """

    matches: list[PatternMatch] = []
    i = 0

    while i < len(text):
        match = _try_date(text, i) or _try_email(text, i) or _try_phone(text, i)
        if match:
            matches.append(match)
            i = match.end
        else:
            i += 1

    return matches
