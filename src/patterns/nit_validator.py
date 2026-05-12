"""AFD para Numeros de Identificacion Tributaria (NIT) colombianos.

Responsabilidad unica: recorrer char-by-char y decidir si la cadena es
un NIT valido con formato NNN.NNN.NNN-D (9 digitos) o N.NNN.NNN.NNN-D
(10 digitos), mas verificacion de digito de control modulo 11 (DIAN).

Formatos aceptados:
  - 9 digitos:  NNN.NNN.NNN-D   (personas juridicas)
  - 10 digitos: N.NNN.NNN.NNN-D (personas naturales)
"""

from src.core.automaton import TraceableAutomaton
from src.core.result import ValidationResult, build_accept, build_reject, reject_empty
from src.core.symbol_classifier import is_digit

# Pesos para el calculo del digito verificador modulo 11 (DIAN).
# Se aplican de derecha a izquierda sobre los digitos base.
_CHECK_WEIGHTS = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]

# Estructuras de bloques validas.
_VALID_STRUCTURES = [
    [3, 3, 3],        # 9 digitos (personas juridicas)
    [1, 3, 3, 3],     # 10 digitos (personas naturales)
]


def _calc_check_digit(base_digits: str) -> str:
    """Calcula el digito verificador modulo 11 segun algoritmo DIAN.

    Los pesos se aplican de derecha a izquierda sobre los digitos base.
    Mapeo de residuo a digito: 0→0, 1→1, 2→9, 3→8, ..., 10→1.
    """
    s = sum(
        w * int(d)
        for w, d in zip(_CHECK_WEIGHTS, reversed(base_digits))
    ) % 11
    return "01987654321"[s]


def validate_nit(text: str) -> ValidationResult:
    """Valida NITs colombianos con formato NNN.NNN.NNN-D o N.NNN.NNN.NNN-D.

    Reglas implementadas:
    - Grupos de digitos separados por punto.
    - Digito verificador separado por guion al final.
    - Estructura valida: [3,3,3] (9 digitos) o [1,3,3,3] (10 digitos).
    - Digito verificador validado con algoritmo modulo 11 (DIAN).
    - Sin caracteres extra al final.
    """

    automaton = TraceableAutomaton(state="START")
    digits: list[str] = []
    digit_groups: list[int] = []
    current_count = 0

    if not text:
        return reject_empty("START")

    for symbol in text:
        if automaton.state == "START":
            if is_digit(symbol):
                automaton.record(symbol, "IN_BLOCK", "Inicia el primer grupo de digitos.")
                digits.append(symbol)
                current_count = 1
                continue
            automaton.record(symbol, "REJECT", "El NIT debe iniciar con un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT no inicia con digito.",
                trace=automaton.trace,
            )

        if automaton.state == "IN_BLOCK":
            if is_digit(symbol):
                automaton.stay(symbol, "Continua el grupo actual de digitos.")
                digits.append(symbol)
                current_count += 1
                continue
            if symbol == ".":
                if current_count == 0:
                    automaton.record(symbol, "REJECT", "Bloque vacio antes del punto.")
                    return build_reject(
                        consumed=automaton.consumed,
                        message="El NIT tiene un grupo vacio.",
                        trace=automaton.trace,
                    )
                digit_groups.append(current_count)
                current_count = 0
                automaton.record(symbol, "AFTER_DOT", "Separador de grupos.")
                continue
            if symbol == "-":
                if current_count == 0:
                    automaton.record(symbol, "REJECT", "Bloque vacio antes del guion.")
                    return build_reject(
                        consumed=automaton.consumed,
                        message="El NIT tiene un grupo vacio antes del digito verificador.",
                        trace=automaton.trace,
                    )
                digit_groups.append(current_count)
                current_count = 0
                automaton.record(symbol, "HYPHEN", "Separador antes del digito verificador.")
                continue
            automaton.record(symbol, "REJECT", "Simbolo no permitido en el NIT.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT contiene simbolos invalidos.",
                trace=automaton.trace,
            )

        if automaton.state == "AFTER_DOT":
            if is_digit(symbol):
                automaton.record(symbol, "IN_BLOCK", "Inicia un nuevo grupo de digitos.")
                digits.append(symbol)
                current_count = 1
                continue
            automaton.record(symbol, "REJECT", "Despues del punto debe venir un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT tiene un grupo vacio despues de punto.",
                trace=automaton.trace,
            )

        if automaton.state == "HYPHEN":
            if is_digit(symbol):
                automaton.record(symbol, "CHECK", "Digito verificador del NIT.")
                digits.append(symbol)
                continue
            automaton.record(symbol, "REJECT", "El digito verificador debe ser un digito.")
            return build_reject(
                consumed=automaton.consumed,
                message="El digito verificador del NIT es invalido.",
                trace=automaton.trace,
            )

        if automaton.state == "CHECK":
            automaton.record(symbol, "REJECT", "El NIT no puede tener caracteres extra al final.")
            return build_reject(
                consumed=automaton.consumed,
                message="El NIT tiene caracteres extra al final.",
                trace=automaton.trace,
                normalized="".join(digits),
            )

    # ── Validacion al cierre ────────────────────────────────────────

    if automaton.state != "CHECK":
        automaton.finish("REJECT", f"La cadena termina en estado incompleto: {automaton.state}.")
        return build_reject(
            consumed=automaton.consumed,
            message="El NIT esta incompleto.",
            trace=automaton.trace,
            normalized="".join(digits),
        )

    # Validar estructura de bloques.
    if digit_groups not in _VALID_STRUCTURES:
        automaton.finish(
            "REJECT",
            f"Estructura de grupos invalida: {digit_groups}.",
        )
        return build_reject(
            consumed=automaton.consumed,
            message="El formato del NIT es invalido.",
            trace=automaton.trace,
            normalized="".join(digits),
        )

    # Validar digito verificador modulo 11.
    base_digits = "".join(digits[:-1])
    provided_check = digits[-1]
    expected_check = _calc_check_digit(base_digits)

    if provided_check != expected_check:
        automaton.finish(
            "REJECT",
            f"Digito verificador {provided_check} no coincide con el esperado {expected_check}.",
        )
        return build_reject(
            consumed=automaton.consumed,
            message="El NIT tiene un digito verificador invalido.",
            trace=automaton.trace,
            normalized="".join(digits),
        )

    automaton.finish(
        "ACCEPT",
        f"NIT valido con {len(digits)-1} digitos y digito verificador correcto.",
    )
    return build_accept(
        consumed=automaton.consumed,
        message="NIT valido.",
        trace=automaton.trace,
        normalized="".join(digits),
    )
