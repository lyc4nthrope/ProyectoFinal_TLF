"""AFD base — registra transiciones y traza; no decide aceptacion.

Responsabilidad unica: mantener estado, contador de consumidos y lista
de transiciones. Cada validador instancia TraceableAutomaton y es el
unico responsable de las reglas de aceptacion o rechazo.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class TraceableAutomaton:
    """Automata simple que registra cada cambio de estado.

    Esta estructura no decide por si sola si una cadena es valida.
    Su trabajo es dejar trazabilidad clara para que cada validador
    implemente sus propias reglas sobre estados y simbolos.
    """

    state: str
    consumed: int = 0
    trace: list[str] = field(default_factory=list)

    def record(self, symbol: str, next_state: str, note: str) -> None:
        """Registra la transicion actual y actualiza el estado."""

        self.trace.append(
            f"{self.state} --[{symbol!r}]--> {next_state}: {note}"
        )
        self.state = next_state
        self.consumed += 1

    def stay(self, symbol: str, note: str) -> None:
        """Registra que el automata permanece en el mismo estado."""

        self.record(symbol, self.state, note)

    def finish(self, next_state: str, note: str) -> None:
        """Registra el cierre del recorrido sin consumir un nuevo simbolo."""

        self.trace.append(f"{self.state} --[END]--> {next_state}: {note}")
        self.state = next_state
