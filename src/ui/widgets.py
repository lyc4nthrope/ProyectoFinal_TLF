"""Widgets reutilizables para la interfaz Tkinter.

ToolTip: popup flotante tipo burbuja que aparece al hacer hover
sobre un widget y muestra texto de ayuda.
"""

from __future__ import annotations

from tkinter import Label, Toplevel, Widget

TOOLTIP_BG = "#FFFFDD"
TOOLTIP_FG = "#333333"
TOOLTIP_FONT = ("Segoe UI", 9)
TOOLTIP_DELAY_MS = 400


class ToolTip:
    """Burbuja de ayuda que aparece al posar el mouse sobre un widget.

    Uso:
        ToolTip(widget, "Texto de ayuda")
    """

    def __init__(self, widget: Widget, text: str, *, delay_ms: int = TOOLTIP_DELAY_MS) -> None:
        self._widget = widget
        self._text = text
        self._delay_ms = delay_ms
        self._tip_window: Toplevel | None = None
        self._after_id: str | None = None

        widget.bind("<Enter>", self._on_enter, add=True)
        widget.bind("<Leave>", self._on_leave, add=True)
        widget.bind("<ButtonPress>", self._on_leave, add=True)

    # ── Eventos ───────────────────────────────────────────────────

    def _on_enter(self, _event: object) -> None:
        """Inicia el temporizador para mostrar el tooltip."""
        self._schedule()

    def _on_leave(self, _event: object) -> None:
        """Cancela el temporizador y cierra el tooltip si esta abierto."""
        self._unschedule()
        self._hide()

    # ── Temporizador ──────────────────────────────────────────────

    def _schedule(self) -> None:
        self._unschedule()
        self._after_id = self._widget.after(self._delay_ms, self._show)

    def _unschedule(self) -> None:
        if self._after_id is not None:
            try:
                self._widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    # ── Mostrar / Ocultar ─────────────────────────────────────────

    def _show(self) -> None:
        """Crea la ventana flotante del tooltip."""
        if self._tip_window is not None:
            return

        x = self._widget.winfo_pointerx() + 12
        y = self._widget.winfo_pointery() + 8

        self._tip_window = Toplevel(self._widget)
        self._tip_window.wm_overrideredirect(True)
        self._tip_window.wm_geometry(f"+{x}+{y}")
        self._tip_window.wm_attributes("-topmost", True)

        label = Label(
            self._tip_window,
            text=self._text,
            justify="left",
            background=TOOLTIP_BG,
            foreground=TOOLTIP_FG,
            font=TOOLTIP_FONT,
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3,
        )
        label.pack()

    def _hide(self) -> None:
        """Destruye la ventana flotante."""
        if self._tip_window is not None:
            try:
                self._tip_window.destroy()
            except Exception:
                pass
            self._tip_window = None

    def destroy(self) -> None:
        """Limpieza final."""
        self._unschedule()
        self._hide()
