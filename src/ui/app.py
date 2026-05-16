"""Aplicacion Tkinter con pestanas para Parte A y Parte B.

Arquitectura: FormApp usa un ttk.Notebook con dos pestanas:
  - Pestana "Parte A": ScanSection — busqueda de patrones en texto libre
  - Pestana "Parte B": FormSection — formularios con validacion en tiempo real

Cada componente es autonomo: maneja su propia UI y eventos.
"""

from collections.abc import Callable
from typing import NamedTuple
from tkinter import (
    Canvas,
    Frame,
    Label,
    Scrollbar,
    Text,
    Tk,
    messagebox,
    ttk,
    END,
    NORMAL,
    DISABLED,
    VERTICAL,
    BOTH,
    LEFT,
    RIGHT,
    Y,
    NW,
)

from src.core.result import ValidationResult
from src.ui.forms import ValidatedField
from src.ui.messages import PATTERN_INFO, format_field_message, get_pattern_display
from src.patterns.date_validator import validate_date
from src.patterns.email_validator import validate_email
from src.patterns.nit_validator import validate_nit
from src.patterns.password_validator import validate_password
from src.patterns.phone_validator import validate_phone
from src.patterns.plate_validator import validate_plate
from src.patterns.url_validator import validate_url


class FieldConfig(NamedTuple):
    """Configuracion de un campo del formulario de validacion."""

    label: str
    key: str
    validator: Callable[[str], ValidationResult]
    show: str  # "*" oculta caracteres (para contrasena), "" = visible


# Configuracion de campos del formulario.
FIELDS_CONFIG: list[FieldConfig] = [
    FieldConfig("Telefono:",             "phone",    validate_phone,    ""),
    FieldConfig("Correo:",               "email",    validate_email,    ""),
    FieldConfig("Fecha (DD/MM/AAAA):",   "date",     validate_date,     ""),
    FieldConfig("Placa (ej. ABC123):",   "plate",    validate_plate,    ""),
    FieldConfig("Contrasena:",           "password", validate_password, "*"),
    FieldConfig("NIT (NNN.NNN.NNN-D):", "nit",      validate_nit,      ""),
    FieldConfig("URL:",                  "url",      validate_url,      ""),
]

WINDOW_WIDTH = 760
WINDOW_HEIGHT = 720


# ── Componente 1: Buscador de patrones ───────────────────────────────


class ScanSection:
    """Seccion de busqueda de patrones en texto libre (Parte A)."""

    def __init__(self, parent: ttk.Frame) -> None:
        self.parent = parent
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.parent)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        Label(frame, text="Pega o escribe un texto y presiona Escanear:").pack(anchor="w")

        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="x", pady=4)

        self.scan_input = Text(text_frame, height=4, wrap="word")
        self.scan_input.pack(side=LEFT, fill="x", expand=True)

        scroll = Scrollbar(text_frame, command=self.scan_input.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.scan_input.config(yscrollcommand=scroll.set)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=4)

        ttk.Button(btn_frame, text="Escanear", command=self._on_scan).pack(
            side=LEFT, padx=(0, 6)
        )
        ttk.Button(btn_frame, text="Limpiar texto", command=self._clear).pack(side=LEFT)

        # ── Resultados con formato visual ─────────────────────────
        self.scan_results = Text(frame, height=6, wrap="word", state=DISABLED,
                                 font=("Consolas", 9), bg="#fcfcfc")
        self.scan_results.pack(fill="x", pady=(4, 0))

        # Tags de color para cada tipo de patron
        self._setup_result_tags()

    def _setup_result_tags(self) -> None:
        """Configura tags de color para cada tipo de patron en el Text widget."""
        for _pkey, info in PATTERN_INFO.items():
            tag = _pkey
            self.scan_results.tag_configure(tag, foreground=info.get("color", "#333"))

        # Tags para el texto de posicion y estado
        self.scan_results.tag_configure("pos", foreground="#999999", font=("Consolas", 8))
        self.scan_results.tag_configure("status_ok", foreground="#28a745")
        self.scan_results.tag_configure("status_fail", foreground="#dc3545")

    # ── Eventos ───────────────────────────────────────────────────

    def _on_scan(self) -> None:
        """Ejecuta el escaneo y muestra resultados con formato visual."""

        from src.patterns.text_scanner import scan_text

        text = self.scan_input.get("1.0", END).strip()
        if not text:
            messagebox.showinfo("Sin texto", "Escribe o pega un texto para escanear.")
            return

        matches = scan_text(text)
        self.scan_results.config(state=NORMAL)
        self.scan_results.delete("1.0", END)

        if not matches:
            self.scan_results.insert(END, "No se encontraron patrones en el texto.")
        else:
            for m in matches:
                self._insert_result(m)

        self.scan_results.config(state=DISABLED)

    def _insert_result(self, match: object) -> None:
        """Inserta una linea de resultado formateada con tags de color.

        Formato:
            📧 Correo        user@example.com        ✓ Valido
                              └─ posicion 10-26
        """
        from src.patterns.text_scanner import PatternMatch

        m: PatternMatch = match  # type: ignore[annotation-unchecked]

        emoji, label, color = get_pattern_display(m.pattern)

        estado = "✓" if m.result.accepted else "✗"
        estado_tag = "status_ok" if m.result.accepted else "status_fail"

        # Linea principal: emoji + patron + valor + estado
        self.scan_results.insert(END, f"{emoji} ", ())
        self.scan_results.insert(END, f"{label:12}", m.pattern)
        self.scan_results.insert(END, f"{m.raw:30}", ())
        self.scan_results.insert(END, f"  {estado}", estado_tag)
        self.scan_results.insert(END, "\n", ())

        # Linea secundaria: posicion y normalizado
        norm_display = f"  \u2514 pos={m.start}-{m.end}"
        if m.normalized and m.normalized != m.raw:
            norm_display += f"  norm={m.normalized}"
        self.scan_results.insert(END, f"{'':16}{norm_display}", "pos")
        self.scan_results.insert(END, "\n", ())

    def _clear(self) -> None:
        self.scan_input.delete("1.0", END)
        self.scan_results.config(state=NORMAL)
        self.scan_results.delete("1.0", END)
        self.scan_results.config(state=DISABLED)


# ── Componente 2: Formularios validados ──────────────────────────────


class FormSection:
    """Seccion de formularios con validacion en tiempo real (Parte B)."""

    def __init__(self, parent: ttk.Frame) -> None:
        self.parent = parent
        self.fields: list[ValidatedField] = []
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.parent)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Canvas + Scrollbar para contenido desplazable
        canvas = Canvas(frame, highlightthickness=0)
        scroll = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
        scrollable = Frame(canvas)

        scrollable.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor=NW)
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)

        # Vincular scroll del mouse (SOLO sobre el canvas, no global)
        def _on_mousewheel(event: object) -> None:
            canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")  # type: ignore[union-attr, misc]

        canvas.bind("<MouseWheel>", _on_mousewheel)
        # Soporte para Linux (Tk < 8.7 usa Button-4/Button-5)
        canvas.bind("<Button-4>", lambda _e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda _e: canvas.yview_scroll(1, "units"))

        # ── Barra de progreso ────────────────────────────────────
        self._progress_label = Label(scrollable, text="\u25CB Ningun campo validado aun",
                                     fg="#999999", anchor="w")
        self._progress_label.pack(fill="x", pady=(0, 4))

        # Crear campos validados con key y on_change
        for label, key, validator, show in FIELDS_CONFIG:
            field = ValidatedField(
                scrollable, label, validator, show=show,
                key=key, on_change=self._update_progress,
            )
            self.fields.append(field)

        # Botones
        btn_frame = ttk.Frame(scrollable)
        btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(btn_frame, text="Limpiar todo", command=self._clear).pack(side=LEFT)

    # ── Barra de progreso ─────────────────────────────────────────

    def _update_progress(self) -> None:
        """Actualiza el indicador de progreso 'X de N campos validos'."""
        total = len(self.fields)
        validos = sum(1 for f in self.fields if f.is_valid)
        llenos = sum(1 for f in self.fields if f.value)

        if validos == total:
            self._progress_label.config(
                text=f"\u2713 {validos} de {total} campos validos  \u2014  Todos correctos",
                fg="#28a745",
            )
        elif llenos == 0:
            self._progress_label.config(
                text="\u25CB Ningun campo validado aun",
                fg="#999999",
            )
        else:
            self._progress_label.config(
                text=f"\u26A0 {validos} de {total} campos validos",
                fg="#E67E22",
            )

    # ── Logica de validacion (separada de la presentacion) ────────

    def _collect_results(self) -> list[tuple[str, bool, str]]:
        """Valida todos los campos y retorna [(clave, aceptado, mensaje), ...].

        No toca la UI — solo logica. Ideal para testear sin Tkinter.
        """
        results: list[tuple[str, bool, str]] = []

        for field, config in zip(self.fields, FIELDS_CONFIG):
            is_empty = not field.value
            result = field.last_result
            msg = format_field_message(config.key, result, is_empty)

            if is_empty:
                results.append((config.key, False, msg))
            elif result is None or not result.accepted:
                results.append((config.key, False, msg))
            else:
                results.append((config.key, True, msg))

        return results

    def _on_submit(self) -> None:
        """Toma los resultados de _collect_results y muestra el dialogo apropiado."""
        results = self._collect_results()
        all_valid = all(ok for _key, ok, _msg in results)

        lines = [
            f"{'\u2713' if ok else '\u2717'} {key}: {msg}"
            for key, ok, msg in results
        ]
        summary = "\n".join(lines)

        if all_valid:
            messagebox.showinfo(
                "Envio exitoso",
                "Todos los campos son validos.\n\n" + summary,
            )
        else:
            messagebox.showerror(
                "Errores de validacion",
                "Corrige los campos marcados en rojo.\n\n" + summary,
            )

    def _clear(self) -> None:
        for field in self.fields:
            field.clear()
        self._update_progress()


# ── Ventana principal ────────────────────────────────────────────────


class FormApp:
    """Ventana principal con pestanas para Parte A y Parte B."""

    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("TLF - Busqueda y Validacion de Patrones")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(640, 600)

        # Tema visual
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # ── Pestanas ───────────────────────────────────────────
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=6, pady=6)

        tab_a = ttk.Frame(notebook)
        notebook.add(tab_a, text="Buscador de patrones (Parte A)")
        ScanSection(tab_a)

        tab_b = ttk.Frame(notebook)
        notebook.add(tab_b, text="Validacion de formularios (Parte B)")
        FormSection(tab_b)

    def run(self) -> None:
        self.root.mainloop()


def launch() -> None:
    """Punto de entrada unico para la UI (llamado desde src/main.py)."""
    FormApp().run()
