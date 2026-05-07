"""Validador manual para fechas."""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult
from src.core.symbol_classifier import is_digit

MIN_YEAR = 1900
MAX_YEAR = 2100


def _is_date_separator(symbol: str) -> bool:
    """Reconoce el separador unico permitido en la fecha."""

    return symbol == "/"


def _days_in_month(month: int, year: int) -> int:
    """Devuelve la cantidad maxima de dias para un mes dado."""

    if month == 2:
        if _is_leap_year(year):
            return 29
        return 28

    if month in {4, 6, 9, 11}:
        return 30

    return 31


def _is_leap_year(year: int) -> bool:
    """Determina si un anio es bisiesto con la regla gregoriana basica."""

    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _accepted_date_result(
    automaton: TraceableAutomaton,
    normalized_symbols: list[str],
) -> ValidationResult:
    """Normaliza la salida aceptada de la fecha."""

    return ValidationResult.accept(
        consumed=automaton.consumed,
        message="Fecha valida.",
        trace=automaton.trace,
        normalized="".join(normalized_symbols),
    )


def _rejected_date_result(
    automaton: TraceableAutomaton,
    message: str,
    normalized_symbols: list[str] | None = None,
) -> ValidationResult:
    """Centraliza la salida rechazada de la fecha."""

    normalized = ""
    if normalized_symbols is not None:
        normalized = "".join(normalized_symbols)

    return ValidationResult.reject(
        consumed=automaton.consumed,
        message=message,
        trace=automaton.trace,
        normalized=normalized,
    )


def validate_date(text: str) -> ValidationResult:
    """Valida fechas con formato estricto `DD/MM/YYYY`.

    Reglas implementadas:
    - El dia debe tener exactamente 2 digitos.
    - El mes debe tener exactamente 2 digitos.
    - El anio debe tener exactamente 4 digitos.
    - El unico separador permitido es `/`.
    - El dia y el mes deben estar dentro de rangos validos.
    - Febrero y anios bisiestos se validan con reglas basicas.
    - El anio se restringe al rango 1900-2100.
    """

    automaton = TraceableAutomaton(state="START")
    normalized_symbols: list[str] = []
    day_digits = 0
    month_digits = 0
    year_digits = 0

    if not text:
        return ValidationResult.reject(
            consumed=0,
            message="La cadena esta vacia.",
            trace=["START: no hay simbolos para procesar."],
        )

    for symbol in text:
        # START obliga a iniciar la fecha con el primer digito del dia.
        if automaton.state == "START":
            if is_digit(symbol):
                automaton.record(symbol, "DAY_FIRST", "Empieza la lectura del dia.")
                normalized_symbols.append(symbol)
                day_digits = 1
                continue

            automaton.record(symbol, "REJECT", "La fecha debe iniciar con un digito.")
            return _rejected_date_result(
                automaton,
                "La fecha inicia con un simbolo invalido.",
            )

        # DAY_FIRST obliga a completar el segundo digito del dia.
        if automaton.state == "DAY_FIRST":
            if is_digit(symbol):
                automaton.record(symbol, "AFTER_DAY", "Se completa el bloque de dos digitos del dia.")
                normalized_symbols.append(symbol)
                day_digits = 2
                continue

            automaton.record(symbol, "REJECT", "El dia debe tener exactamente dos digitos.")
            return _rejected_date_result(
                automaton,
                "El dia de la fecha esta incompleto.",
            )

        # AFTER_DAY exige el separador antes de iniciar el mes.
        if automaton.state == "AFTER_DAY":
            if _is_date_separator(symbol):
                automaton.record(symbol, "MONTH_FIRST", "Se abre la lectura del mes.")
                normalized_symbols.append(symbol)
                continue

            automaton.record(symbol, "REJECT", "Despues del dia debe aparecer '/'.")
            return _rejected_date_result(
                automaton,
                "La fecha no tiene el separador correcto despues del dia.",
            )

        # MONTH_FIRST registra el primer digito del mes.
        if automaton.state == "MONTH_FIRST":
            if is_digit(symbol):
                automaton.record(symbol, "MONTH_SECOND", "Empieza la lectura del mes.")
                normalized_symbols.append(symbol)
                month_digits = 1
                continue

            automaton.record(symbol, "REJECT", "El mes debe iniciar con un digito.")
            return _rejected_date_result(
                automaton,
                "El mes de la fecha inicia de forma invalida.",
            )

        # MONTH_SECOND obliga a completar el segundo digito del mes.
        if automaton.state == "MONTH_SECOND":
            if is_digit(symbol):
                automaton.record(symbol, "AFTER_MONTH", "Se completa el bloque de dos digitos del mes.")
                normalized_symbols.append(symbol)
                month_digits = 2
                continue

            automaton.record(symbol, "REJECT", "El mes debe tener exactamente dos digitos.")
            return _rejected_date_result(
                automaton,
                "El mes de la fecha esta incompleto.",
            )

        # AFTER_MONTH exige el separador antes del anio.
        if automaton.state == "AFTER_MONTH":
            if _is_date_separator(symbol):
                automaton.record(symbol, "YEAR_1", "Se abre la lectura del anio.")
                normalized_symbols.append(symbol)
                continue

            automaton.record(symbol, "REJECT", "Despues del mes debe aparecer '/'.")
            return _rejected_date_result(
                automaton,
                "La fecha no tiene el separador correcto despues del mes.",
            )

        # YEAR_1, YEAR_2, YEAR_3 y YEAR_4 fuerzan cuatro digitos para el anio.
        if automaton.state == "YEAR_1":
            if is_digit(symbol):
                automaton.record(symbol, "YEAR_2", "Se registra el primer digito del anio.")
                normalized_symbols.append(symbol)
                year_digits = 1
                continue

            automaton.record(symbol, "REJECT", "El anio debe iniciar con un digito.")
            return _rejected_date_result(
                automaton,
                "El anio de la fecha inicia de forma invalida.",
            )

        if automaton.state == "YEAR_2":
            if is_digit(symbol):
                automaton.record(symbol, "YEAR_3", "Se registra el segundo digito del anio.")
                normalized_symbols.append(symbol)
                year_digits = 2
                continue

            automaton.record(symbol, "REJECT", "El anio debe tener cuatro digitos.")
            return _rejected_date_result(
                automaton,
                "El anio de la fecha esta incompleto.",
            )

        if automaton.state == "YEAR_3":
            if is_digit(symbol):
                automaton.record(symbol, "YEAR_4", "Se registra el tercer digito del anio.")
                normalized_symbols.append(symbol)
                year_digits = 3
                continue

            automaton.record(symbol, "REJECT", "El anio debe tener cuatro digitos.")
            return _rejected_date_result(
                automaton,
                "El anio de la fecha esta incompleto.",
            )

        if automaton.state == "YEAR_4":
            if is_digit(symbol):
                automaton.record(symbol, "DATE_COMPLETE", "Se completa el bloque de cuatro digitos del anio.")
                normalized_symbols.append(symbol)
                year_digits = 4
                continue

            automaton.record(symbol, "REJECT", "El anio debe terminar con un digito.")
            return _rejected_date_result(
                automaton,
                "El anio de la fecha esta incompleto.",
            )

        if automaton.state == "DATE_COMPLETE":
            automaton.record(symbol, "REJECT", "La fecha no debe tener simbolos extra al final.")
            return _rejected_date_result(
                automaton,
                "La fecha contiene simbolos adicionales al final.",
                normalized_symbols,
            )

    if automaton.state != "DATE_COMPLETE":
        automaton.finish("REJECT", "La cadena termina antes de completar DD/MM/YYYY.")
        return _rejected_date_result(
            automaton,
            "La fecha termina antes de completar su estructura.",
            normalized_symbols,
        )

    if day_digits != 2 or month_digits != 2 or year_digits != 4:
        automaton.finish("REJECT", "La estructura de bloques numericos no quedo completa.")
        return _rejected_date_result(
            automaton,
            "La fecha no cumple con la cantidad exacta de digitos requerida.",
            normalized_symbols,
        )

    # A partir de aqui ya no se valida la forma, sino el significado del calendario.
    day = int(text[0:2])
    month = int(text[3:5])
    year = int(text[6:10])

    if month < 1 or month > 12:
        automaton.finish("REJECT", f"El mes {month} esta fuera del rango 1-12.")
        return _rejected_date_result(
            automaton,
            "El mes de la fecha es invalido.",
            normalized_symbols,
        )

    if year < MIN_YEAR or year > MAX_YEAR:
        automaton.finish("REJECT", f"El anio {year} esta fuera del rango {MIN_YEAR}-{MAX_YEAR}.")
        return _rejected_date_result(
            automaton,
            "El anio de la fecha esta fuera del rango permitido.",
            normalized_symbols,
        )

    # El maximo de dias depende del mes y del caso especial de febrero bisiesto.
    max_day = _days_in_month(month, year)
    if day < 1 or day > max_day:
        automaton.finish(
            "REJECT",
            f"El dia {day} excede el maximo permitido {max_day} para el mes {month}.",
        )
        return _rejected_date_result(
            automaton,
            "El dia de la fecha es invalido para el mes dado.",
            normalized_symbols,
        )

    automaton.finish("ACCEPT", "Fecha valida con formato DD/MM/YYYY y rangos correctos.")
    return _accepted_date_result(automaton, normalized_symbols)
