"""Grafo visual del automata AFD a partir de una traza de validacion.

Dibuja nodos (estados) y aristas (transiciones) en un Canvas de Tkinter,
con flechas etiquetadas por simbolo, bucles de auto-transicion y
coloreado del estado final (verde = ACCEPT, rojo = REJECT).
Responsabilidad unica: dibujar; no decide logica de validacion.
"""

from __future__ import annotations

import re
from tkinter import Canvas, Frame, Scrollbar, Widget, BOTH, HORIZONTAL, LEFT, BOTTOM, X
from typing import Any


# Configuracion visual del grafo
NODE_W = 110
NODE_H = 36
H_GAP = 80
CANVAS_H = 240
TOP_PAD = 32
BTM_PAD = 16
BOW_HEIGHT = 36  # altura del arco de bucle
MIN_CANVAS_W = 500

COLOR_BG = "#fafafa"
COLOR_NODE_FILL = "#ffffff"
COLOR_NODE_STROKE = "#444444"
COLOR_TEXT = "#222222"
COLOR_EDGE = "#666666"
COLOR_ACCEPT_FILL = "#d4edda"
COLOR_ACCEPT_STROKE = "#28a745"
COLOR_REJECT_FILL = "#f8d7da"
COLOR_REJECT_STROKE = "#dc3545"
FONT_NODE = ("Segoe UI", 9, "bold")
FONT_LABEL = ("Segoe UI", 8)
FONT_LOOP = ("Segoe UI", 7)

TRACE_PATTERN = re.compile(r"^(.+?) --\[(.+?)\]--> (.+?):")


def _parse_trace(trace: list[str]) -> tuple[list[str], list[tuple[int, int, str]], dict[int, list[str]]]:
    """Convierte traza en nodos, aristas y bucles.

    Returns:
        nodes:  lista ordenada de nombres de estado (indice = id)
        edges:  lista de (src_idx, tgt_idx, simbolo)
        loops:  {node_idx: [simbolos]} para auto-transiciones
    """
    raw: list[tuple[str, str, str]] = []
    for line in trace:
        m = TRACE_PATTERN.match(line)
        if m:
            raw.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))

    nodes: list[str] = []
    edges: list[tuple[int, int, str]] = []
    loops: dict[int, list[str]] = {}
    idx_of: dict[str, int] = {}

    for src, sym, tgt in raw:
        if src not in idx_of:
            idx_of[src] = len(nodes)
            nodes.append(src)

        si = idx_of[src]

        if src == tgt and sym != "END":
            loops.setdefault(si, []).append(sym)
        else:
            if tgt not in idx_of:
                idx_of[tgt] = len(nodes)
                nodes.append(tgt)
            ti = idx_of[tgt]
            edges.append((si, ti, sym))

    return nodes, edges, loops


class AutomatonGraph(Frame):
    """Panel que dibuja un grafo de estados AFD en un lienzo desplazable.

    Uso:
        graph = AutomatonGraph(parent, trace, accepted=True, message="valido")
        graph.pack(fill="both", expand=True)
    """

    def __init__(
        self,
        parent: Widget,
        trace: list[str],
        accepted: bool,
        message: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._trace = trace
        self._accepted = accepted
        self._message = message

        self._nodes, self._edges, self._loops = _parse_trace(trace)
        self._build_ui()

    # ── Construccion del lienzo ────────────────────────────────────

    def _build_ui(self) -> None:
        n = len(self._nodes)
        cw = max(MIN_CANVAS_W, n * (NODE_W + H_GAP) + H_GAP)

        self._canvas = Canvas(self, width=cw, height=CANVAS_H,
                              bg=COLOR_BG, highlightthickness=0)

        if cw > MIN_CANVAS_W:
            scroll = Scrollbar(self, orient=HORIZONTAL, command=self._canvas.xview)
            scroll.pack(side=BOTTOM, fill=X)
            self._canvas.config(xscrollcommand=scroll.set,
                                scrollregion=(0, 0, cw, CANVAS_H))

        self._canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self._draw(cw)

    # ── Dibujado ───────────────────────────────────────────────────

    def _draw(self, canvas_w: int) -> None:
        cx0 = H_GAP // 2 + NODE_W // 2
        step = NODE_W + H_GAP
        # Centrar considerando espacio extra para bucles arriba del nodo
        has_loops = any(self._loops.values())
        cy = CANVAS_H // 2 + (BOW_HEIGHT // 2 if has_loops else 0)
        last_node_idx = len(self._nodes) - 1

        # Dibujar aristas (detras de los nodos)
        for src_idx, tgt_idx, sym in self._edges:
            x1 = cx0 + src_idx * step + NODE_W // 2
            y1 = cy
            x2 = cx0 + tgt_idx * step - NODE_W // 2
            y2 = cy

            # Flecha
            self._canvas.create_line(
                x1, y1, x2, y2,
                arrow="last", arrowshape=(8, 10, 4),
                fill=COLOR_EDGE, width=1.5,
            )
            # Etiqueta del simbolo sobre la flecha
            mx = (x1 + x2) // 2
            self._canvas.create_text(mx, cy - 14, text=sym,
                                     font=FONT_LABEL, fill=COLOR_EDGE)

        # Dibujar bucles (auto-transiciones)
        for node_idx, symbols in self._loops.items():
            x = cx0 + node_idx * step
            y_top = cy - NODE_H // 2 - BOW_HEIGHT

            # Arco semicircular sobre el nodo
            self._canvas.create_arc(
                x - NODE_W // 2, y_top,
                x + NODE_W // 2, cy - NODE_H // 2,
                start=180, extent=180,
                style="arc", outline=COLOR_EDGE, width=1.5,
            )

            # Etiqueta con los simbolos del bucle
            label = _format_loop_label(symbols)
            self._canvas.create_text(x, y_top - 4, text=label,
                                     font=FONT_LOOP, fill=COLOR_EDGE)

        # Dibujar nodos (sobre las aristas)
        for i, name in enumerate(self._nodes):
            x = cx0 + i * step
            is_last = (i == last_node_idx)

            fill = COLOR_NODE_FILL
            stroke = COLOR_NODE_STROKE

            # Colorear el ultimo estado segun aceptacion
            if is_last:
                if self._accepted:
                    fill = COLOR_ACCEPT_FILL
                    stroke = COLOR_ACCEPT_STROKE
                else:
                    fill = COLOR_REJECT_FILL
                    stroke = COLOR_REJECT_STROKE

            # Rectangulo redondeado (simulado con polygon)
            r = 8  # radio de esquinas
            x1, y1, x2, y2 = x - NODE_W // 2, cy - NODE_H // 2, x + NODE_W // 2, cy + NODE_H // 2
            pts = [
                x1 + r, y1,
                x2 - r, y1,
                x2, y1 + r,
                x2, y2 - r,
                x2 - r, y2,
                x1 + r, y2,
                x1, y2 - r,
                x1, y1 + r,
            ]
            self._canvas.create_polygon(pts, fill=fill, outline=stroke,
                                        width=2, smooth=True)

            # Doble borde para estado final (estilo de aceptacion clasico)
            if is_last:
                self._canvas.create_rectangle(
                    x1 - 3, y1 - 3, x2 + 3, y2 + 3,
                    outline=stroke, width=1.5,
                )

            # Nombre del estado
            self._canvas.create_text(x, cy, text=name,
                                     font=FONT_NODE, fill=COLOR_TEXT)

        # Pie con el mensaje de resultado
        summary = f"{'✓ ACEPTADO' if self._accepted else '✗ RECHAZADO'}: {self._message}"
        color = COLOR_ACCEPT_STROKE if self._accepted else COLOR_REJECT_STROKE
        self._canvas.create_text(canvas_w // 2, CANVAS_H - 6,
                                 text=summary, font=("Segoe UI", 9, "bold"),
                                 fill=color)


def _format_loop_label(symbols: list[str]) -> str:
    """Abreviar lista de simbolos para mostrar en un bucle."""
    if len(symbols) <= 4:
        return ", ".join(symbols)
    return f"{len(symbols)}x"
