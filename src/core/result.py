"""Estructuras de resultado para validaciones y escaneos."""

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
