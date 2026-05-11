"""Tipo uniforme de resultado para todos los validadores del proyecto.

Responsabilidad unica: exponer ValidationResult con factory methods
accept() y reject(). Ningun validador construye el resultado manualmente.

Incluye helpers compartidos (build_accept, build_reject, reject_empty)
para evitar duplicar wrappers identicos en cada validador.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationResult:
    """Representa el resultado de un recorrido formal sobre una cadena."""

    accepted: bool
    consumed: int
    message: str
    # Guarda las transiciones para sustentar por que se acepto o rechazo.
    trace: list[str] = field(default_factory=list)
    # Version limpia del patron, util para comparar o reportar resultados.
    normalized: str = ""

    @classmethod
    def accept(
        cls,
        *,
        consumed: int,
        message: str,
        trace: list[str],
        normalized: str = "",
    ) -> "ValidationResult":
        """Construye un resultado aceptado con una estructura uniforme."""

        return cls(
            accepted=True,
            consumed=consumed,
            message=message,
            trace=trace,
            normalized=normalized,
        )

    @classmethod
    def reject(
        cls,
        *,
        consumed: int,
        message: str,
        trace: list[str],
        normalized: str = "",
    ) -> "ValidationResult":
        """Construye un resultado rechazado con una estructura uniforme."""

        return cls(
            accepted=False,
            consumed=consumed,
            message=message,
            trace=trace,
            normalized=normalized,
        )


# ── Helpers compartidos entre validadores ─────────────────────────────


def build_accept(
    *,
    consumed: int,
    message: str,
    trace: list[str],
    normalized: str = "",
) -> ValidationResult:
    """Construye un resultado de aceptacion (wrapper conciso para los validadores)."""
    return ValidationResult.accept(
        consumed=consumed,
        message=message,
        trace=trace,
        normalized=normalized,
    )


def build_reject(
    *,
    consumed: int,
    message: str,
    trace: list[str],
    normalized: str = "",
) -> ValidationResult:
    """Construye un resultado de rechazo (wrapper conciso para los validadores)."""
    return ValidationResult.reject(
        consumed=consumed,
        message=message,
        trace=trace,
        normalized=normalized,
    )


def reject_empty(state_name: str = "START") -> ValidationResult:
    """Construye un resultado de rechazo para cadena vacia.

    Args:
        state_name: nombre del estado inicial del automata (para la traza).
    """
    return ValidationResult.reject(
        consumed=0,
        message="La cadena esta vacia.",
        trace=[f"{state_name}: no hay simbolos para procesar."],
    )
