"""Campos de formulario con validacion en tiempo real y grafo del automata.

Cada ValidatedField envuelve un Entry de tkinter con su StringVar,
valida automaticamente en cada cambio de tecla, muestra el resultado
inline (check/equis + mensaje) y permite expandir el grafo del
automata (nodos = estados, flechas = transiciones).

Mejoras de usabilidad:
  - Placeholder: texto gris de ejemplo cuando el campo esta vacio
  - Tooltip: burbuja de ayuda al hacer hover sobre el campo
  - Mensajes traducidos a lenguaje natural (via messages.py)
  - Callback on_change: notifica al contenedor para actualizar progreso
"""

from __future__ import annotations

from collections.abc import Callable
from tkinter import Entry, Frame, Label, StringVar, ttk

from src.core.result import ValidationResult
from src.ui.automaton_graph import AutomatonGraph
from src.ui.messages import FIELD_INFO, format_field_message
from src.ui.widgets import ToolTip

GREEN = "#28a745"
RED = "#dc3545"
GRAY = "#6c757d"
PLACEHOLDER_FG = "#b0b0b0"
NORMAL_FG = "#222222"


class ValidatedField:
    """Campo de formulario que se valida automaticamente al escribir.

    Args:
        parent: contenedor del campo
        label: texto de la etiqueta
        validator: funcion validadora (recibe str, retorna ValidationResult)
        show: caracter de mascara (ej. "*" para contrasena)
        width: ancho del Entry en caracteres
        key: clave del campo en FIELD_INFO (para mensajes y metadatos)
        on_change: callback disparado en cada cambio de validacion
    """

    def __init__(
        self,
        parent: Frame,
        label: str,
        validator: Callable[[str], ValidationResult],
        *,
        show: str = "",
        width: int = 40,
        key: str = "",
        on_change: Callable[[], None] | None = None,
    ) -> None:
        self.validator = validator
        self.var = StringVar()
        self._last_result: ValidationResult | None = None
        self._trace_visible = False
        self._graph_widget: AutomatonGraph | None = None
        self._on_change_cb = on_change
        self.key = key

        # ── Metadatos del campo ───────────────────────────────────
        info = FIELD_INFO.get(key, {})
        self._placeholder = info.get("placeholder", "")
        self._placeholder_active = False

        # ── Contenedor principal del campo (fila + area del grafo) ─
        self.field_box = ttk.Frame(parent)
        self.field_box.pack(fill="x", pady=4)

        # ── Fila superior: label + entrada + indicadores ──────────

        row = ttk.Frame(self.field_box)
        row.pack(fill="x")

        self.label_widget = Label(row, text=label, width=20, anchor="w")
        self.label_widget.pack(side="left", padx=(0, 6))

        self.entry = Entry(row, textvariable=self.var, show=show, width=width)
        self.entry.pack(side="left")

        # ── Placeholder ──────────────────────────────────────────
        if self._placeholder:
            self._setup_placeholder()

        # ── Tooltip sobre la entrada ─────────────────────────────
        tooltip_text = info.get("tooltip", "")
        if tooltip_text:
            self._tooltip = ToolTip(self.entry, tooltip_text)
        else:
            self._tooltip = None

        # Boton ojito para campos con mascara (ej. contrasena)
        self._visible = False
        if show:
            self.toggle_btn = ttk.Button(
                row, text="\U0001F441", width=3,
                command=self._toggle_visibility,
            )
            self.toggle_btn.pack(side="left", padx=(2, 0))

        # Indicador ✓/✗
        self.indicator = Label(row, text="", width=2)
        self.indicator.pack(side="left", padx=(2, 0))

        # Mensaje de resultado
        self.msg = Label(row, text="", anchor="w", wraplength=300)
        self.msg.pack(side="left", padx=(4, 0))

        # Boton para expandir/ocultar grafo del automata
        self.trace_btn = ttk.Button(row, text="\u25B8", width=3, command=self._toggle_trace)
        self.trace_btn.pack(side="left", padx=(4, 0))

        # ── Contenedor del grafo (oculto por defecto) ─────────────
        self.graph_container = ttk.Frame(self.field_box)

        self.var.trace_add("write", self._on_change)

    # ── Placeholder ───────────────────────────────────────────────

    def _setup_placeholder(self) -> None:
        """Configura el comportamiento de placeholder en el Entry."""
        self._show_placeholder()
        self.entry.bind("<FocusIn>", self._on_focus_in, add=True)
        self.entry.bind("<FocusOut>", self._on_focus_out, add=True)

    def _show_placeholder(self) -> None:
        """Muestra el placeholder si el Entry esta vacio."""
        if not self.var.get():
            self._placeholder_active = True
            self.entry.config(fg=PLACEHOLDER_FG)
            # Insertar placeholder sin tocar StringVar
            self.entry.delete(0, "end")
            self.entry.insert(0, self._placeholder)

    def _clear_placeholder(self) -> None:
        """Quita el placeholder y restaura el color normal."""
        if self._placeholder_active:
            self._placeholder_active = False
            self.entry.delete(0, "end")
            self.entry.config(fg=NORMAL_FG)
            # Forzar actualizacion del StringVar
            self.var.set("")

    def _on_focus_in(self, _event: object) -> None:
        """Al recibir foco: quita el placeholder."""
        if self._placeholder_active:
            self._clear_placeholder()
            # Si hay placeholder tooltip, ocultarlo
            if self._tooltip:
                self._tooltip._on_leave(None)

    def _on_focus_out(self, _event: object) -> None:
        """Al perder foco: restaura placeholder si esta vacio."""
        if not self.var.get() and self._placeholder:
            self._show_placeholder()

    # ── Validacion ───────────────────────────────────────────────

    def _on_change(self, *_args: object) -> None:
        text = self.var.get()

        # No validar cuando el placeholder esta activo
        if self._placeholder_active and text == self._placeholder:
            return

        if not text:
            self._last_result = None
            self.indicator.config(text="")
            self.msg.config(text="", fg=GRAY)
            self._rebuild_graph()
            self._notify_change()
            return

        try:
            self._last_result = self.validator(text)
        except Exception as exc:
            self._last_result = ValidationResult.reject(
                consumed=0,
                message=f"Error en validador: {exc}",
                trace=[],
            )

        result = self._last_result
        if result is None:
            self._notify_change()
            return

        # Usar mensaje traducido de la capa de presentacion
        display_msg = format_field_message(self.key, result, is_empty=False)
        if result.accepted:
            self.indicator.config(text="\u2713", fg=GREEN)
            self.msg.config(text=display_msg, fg=GREEN)
        else:
            self.indicator.config(text="\u2717", fg=RED)
            self.msg.config(text=display_msg, fg=RED)

        self._rebuild_graph()
        self._notify_change()

    def _notify_change(self) -> None:
        """Dispara el callback on_change si existe."""
        if self._on_change_cb is not None:
            self._on_change_cb()

    # ── Grafo del automata ───────────────────────────────────────

    def _toggle_trace(self) -> None:
        """Expande o colapsa el grafo del automata."""
        self._trace_visible = not self._trace_visible
        self.trace_btn.config(text="\u25BE" if self._trace_visible else "\u25B8")

        if self._trace_visible:
            self.graph_container.pack(fill="x", pady=(4, 0))
        else:
            self.graph_container.pack_forget()

        self._rebuild_graph()

    def _rebuild_graph(self) -> None:
        """Destruye el grafo anterior y crea uno nuevo con la traza actual."""
        if self._graph_widget is not None:
            self._graph_widget.destroy()
            self._graph_widget = None

        if not self._trace_visible or self._last_result is None:
            return

        result = self._last_result
        if not result.trace:
            return

        self._graph_widget = AutomatonGraph(
            self.graph_container,
            trace=result.trace,
            accepted=result.accepted,
            message=result.message,
        )
        self._graph_widget.pack(fill="x")

    # ── Ojito ────────────────────────────────────────────────────

    def _toggle_visibility(self) -> None:
        """Muestra u oculta los caracteres del campo."""
        self._visible = not self._visible
        self.entry.config(show="" if self._visible else "*")
        self.toggle_btn.config(text="\U0001F512" if self._visible else "\U0001F441")

    # ── Properties publicas ──────────────────────────────────────

    @property
    def value(self) -> str:
        if self._placeholder_active:
            return ""
        return self.var.get()

    @property
    def is_valid(self) -> bool:
        if self._placeholder_active:
            return False
        return self._last_result is not None and self._last_result.accepted

    @property
    def last_result(self) -> ValidationResult | None:
        if self._placeholder_active:
            return None
        return self._last_result

    def clear(self) -> None:
        self.var.set("")
        self.indicator.config(text="")
        self.msg.config(text="", fg=GRAY)
        # _last_result se pone en None via _on_change (disparado por var.set)
        # Restaurar placeholder si aplica
        if self._placeholder:
            self._show_placeholder()

        if self._trace_visible:
            self._toggle_trace()

    def destroy(self) -> None:
        """Limpieza completa."""
        if self._tooltip is not None:
            self._tooltip.destroy()
        if self._graph_widget is not None:
            self._graph_widget.destroy()
