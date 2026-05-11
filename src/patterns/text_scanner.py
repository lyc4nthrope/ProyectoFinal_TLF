"""Scanner char-by-char sin regex para detectar patrones en texto libre.

Responsabilidad unica: recorrer texto posicion por posicion, intentar
cada patron en orden de prioridad (fecha > email > url > telefono > nit > placa)
y retornar lista de PatternMatch. No valida — delega a cada AFD.
"""

from collections.abc import Callable
from dataclasses import dataclass

from src.core.result import ValidationResult
from src.core.symbol_classifier import is_alphanumeric, is_digit, is_letter
from src.patterns.date_validator import validate_date
from src.patterns.email_validator import validate_email
from src.patterns.nit_validator import validate_nit
from src.patterns.phone_validator import validate_phone
from src.patterns.plate_validator import validate_plate
from src.patterns.url_validator import validate_url

# La contrasena NO se integra al scanner: es entrada atomica de formulario
# (Parte B del proyecto), no un patron buscable en texto libre.

DATE_LENGTH = 10


@dataclass(slots=True)
class PatternMatch:
    """Coincidencia encontrada en el texto escaneado."""

    pattern: str
    start: int
    end: int
    raw: str
    normalized: str
    result: ValidationResult


def _is_email_char(symbol: str) -> bool:
    return is_alphanumeric(symbol) or symbol in {"@", ".", "_", "-"}


def _is_phone_char(symbol: str) -> bool:
    return is_digit(symbol) or symbol in {"+", "-", " "}


def _is_plate_char(symbol: str) -> bool:
    return is_letter(symbol) or is_digit(symbol) or symbol == "-"


def _is_url_char(symbol: str) -> bool:
    return is_alphanumeric(symbol) or symbol in {
        ":", "/", ".", "-", "_", "?", "=", "&", "#", "~", "%", "+", "@",
    }


def _is_nit_char(symbol: str) -> bool:
    return is_digit(symbol) or symbol in {".", "-"}


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
        result=result,
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
        result=result,
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
        result=result,
    )


def _try_url(text: str, pos: int) -> PatternMatch | None:
    """Prueba si en pos inicia una URL valida con protocolo http o https."""

    if text[pos] not in {"h", "H"}:
        return None
    raw = _collect(text, pos, _is_url_char)
    # Quita puntuacion de oracion que pueda haberse pegado al final de la URL.
    candidate = raw.rstrip(".,!)")
    if not candidate:
        return None
    result = validate_url(candidate)
    if not result.accepted:
        return None
    return PatternMatch(
        pattern="url",
        start=pos,
        end=pos + len(candidate),
        raw=candidate,
        normalized=result.normalized,
        result=result,
    )


def _try_nit(text: str, pos: int) -> PatternMatch | None:
    """Prueba si en pos inicia un NIT colombiano valido (NNN.NNN.NNN-D)."""

    if not is_digit(text[pos]):
        return None
    raw = _collect(text, pos, _is_nit_char)
    # Un NIT nunca termina en punto — el punto final puede ser puntuacion de oracion.
    candidate = raw.rstrip(".")
    if not candidate:
        return None
    result = validate_nit(candidate)
    if not result.accepted:
        return None
    return PatternMatch(
        pattern="nit",
        start=pos,
        end=pos + len(candidate),
        raw=candidate,
        normalized=result.normalized,
        result=result,
    )


def _try_plate(text: str, pos: int) -> PatternMatch | None:
    """Prueba si en pos inicia una placa vehicular colombiana valida."""

    if not ("A" <= text[pos] <= "Z"):
        return None
    raw = _collect(text, pos, _is_plate_char)
    candidate = raw.rstrip("-")
    if not candidate:
        return None
    result = validate_plate(candidate)
    if not result.accepted:
        return None
    return PatternMatch(
        pattern="plate",
        start=pos,
        end=pos + len(candidate),
        raw=candidate,
        normalized=result.normalized,
        result=result,
    )


def scan_text(text: str) -> list[PatternMatch]:
    """Recorre el texto caracter por caracter buscando patrones validos.

    Orden de prioridad en cada posicion:
    fecha (formato fijo) > correo (requiere @) > url (requiere http/https) >
    telefono (digitos con separadores) > nit (NNN.NNN.NNN-D) > placa (letras+digitos).
    Si ninguno aplica, avanza un caracter.
    No usa expresiones regulares. Cada candidato se valida con el automata
    formal del patron correspondiente.
    """

    matches: list[PatternMatch] = []
    i = 0

    while i < len(text):
        match = (
            _try_date(text, i)
            or _try_email(text, i)
            or _try_url(text, i)
            or _try_phone(text, i)
            or _try_nit(text, i)
            or _try_plate(text, i)
        )
        if match:
            matches.append(match)
            i = match.end
        else:
            i += 1

    return matches
