"""Traduccion y metadatos para presentar resultados al usuario final.

Separa los mensajes tecnicos del backend (AFDs) de lo que ve el usuario:
- FIELD_INFO: metadatos amigables para cada campo del formulario
- PATTERN_INFO: metadatos para cada patron del scanner
- format_message(): construye el mensaje final segun el contexto
"""

from __future__ import annotations

from src.core.result import ValidationResult


# ── Metadatos de campos del formulario (Parte B) ─────────────────────

FIELD_INFO: dict[str, dict[str, str]] = {
    "phone": {
        "label": "Telefono",
        "emoji": "\U0001F4DE",  # 📞
        "placeholder": "3001234567",
        "tooltip": "10 digitos. Ej: 3001234567 o +57 300 123 4567",
        "color": "#E67E22",  # naranja
        "accepted": "Numero valido",
        "invalid": "Numero invalido. Debe tener 10 digitos.",
        "empty": "Escribe tu numero de telefono",
    },
    "email": {
        "label": "Correo",
        "emoji": "\U0001F4E7",  # 📧
        "placeholder": "usuario@correo.com",
        "tooltip": "usuario@dominio.com. Ej: user@example.com",
        "color": "#27AE60",  # verde
        "accepted": "Correo valido",
        "invalid": "Correo invalido. Revisa el formato.",
        "empty": "Escribe tu correo electronico",
    },
    "date": {
        "label": "Fecha",
        "emoji": "\U0001F4C5",  # 📅
        "placeholder": "DD/MM/AAAA",
        "tooltip": "Formato DD/MM/AAAA. Ej: 15/03/2024",
        "color": "#2980B9",  # azul
        "accepted": "Fecha valida",
        "invalid": "Fecha invalida. Usa el formato DD/MM/AAAA.",
        "empty": "Escribe una fecha en formato DD/MM/AAAA",
    },
    "plate": {
        "label": "Placa",
        "emoji": "\U0001F697",  # 🚗
        "placeholder": "ABC123",
        "tooltip": "3 letras + 3 digitos (carro) o 3+3+1 letra (moto)",
        "color": "#E74C3C",  # rojo
        "accepted": "Placa valida",
        "invalid": "Placa invalida. Formato: ABC123 o ABC12D.",
        "empty": "Escribe la placa del vehiculo",
    },
    "password": {
        "label": "Contrasena",
        "emoji": "\U0001F512",  # 🔒
        "placeholder": "Min. 8 caracteres",
        "tooltip": (
            "Minimo 8 caracteres.\n"
            "Al menos 1 mayuscula, 1 numero y 1 caracter especial."
        ),
        "color": "#8E44AD",  # purpura
        "accepted": "Contrasena segura",
        "invalid": "Contrasena debil. Debe tener 8+ caracteres, mayuscula, numero y especial.",
        "empty": "Escribe una contrasena",
    },
    "nit": {
        "label": "NIT",
        "emoji": "\U0001F4CB",  # 📋
        "placeholder": "123.456.789-5",
        "tooltip": "Formato NNN.NNN.NNN-D. Ej: 123.456.789-5",
        "color": "#2C3E50",  # gris oscuro
        "accepted": "NIT valido",
        "invalid": "NIT invalido. Formato: NNN.NNN.NNN-D.",
        "empty": "Escribe el NIT",
    },
}


# ── Metadatos de patrones del scanner (Parte A) ──────────────────────

PATTERN_INFO: dict[str, dict[str, str]] = {
    "date": {
        "label": "Fecha",
        "emoji": "\U0001F4C5",  # 📅
        "color": "#2980B9",  # azul
    },
    "email": {
        "label": "Correo",
        "emoji": "\U0001F4E7",  # 📧
        "color": "#27AE60",  # verde
    },
    "url": {
        "label": "URL",
        "emoji": "\U0001F310",  # 🌐
        "color": "#8E44AD",  # purpura
    },
    "phone": {
        "label": "Telefono",
        "emoji": "\U0001F4DE",  # 📞
        "color": "#E67E22",  # naranja
    },
    "nit": {
        "label": "NIT",
        "emoji": "\U0001F4CB",  # 📋
        "color": "#2C3E50",  # gris oscuro
    },
    "plate": {
        "label": "Placa",
        "emoji": "\U0001F697",  # 🚗
        "color": "#E74C3C",  # rojo
    },
}


# ── Construccion de mensajes amigables ──────────────────────────────


def format_field_message(key: str, result: ValidationResult | None, is_empty: bool) -> str:
    """Retorna mensaje amigable para un campo del formulario.

    Args:
        key: clave del campo (phone, email, date, ...)
        result: resultado del AFD (None si no se ha validado)
        is_empty: si el campo esta vacio

    Returns:
        str: mensaje listo para mostrar al usuario
    """
    info = FIELD_INFO.get(key, {})
    if is_empty:
        return info.get("empty", "Escribe un valor.")
    if result is None:
        return info.get("invalid", "Valor invalido.")
    if result.accepted:
        # Mensaje amigable de exito
        return info.get("accepted", "Valido")
    # Para rechazos: el mensaje especifico del AFD es mas util
    return result.message


def get_pattern_display(pattern_key: str) -> tuple[str, str, str]:
    """Retorna (emoji, label, color) para un patron del scanner.

    Args:
        pattern_key: clave del patron (date, email, url, ...)

    Returns:
        (emoji, label, color_hex)
    """
    info = PATTERN_INFO.get(pattern_key, {})
    return (
        info.get("emoji", ""),
        info.get("label", pattern_key),
        info.get("color", "#333333"),
    )


def field_tag_name(key: str) -> str:
    """Nombre del tag Tkinter para un campo, usado en tags del Text widget."""
    return f"field_{key}"
