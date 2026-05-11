"""Punto de entrada principal del proyecto TLF.

Expone tres subcomandos:
  scan     -- busca patrones en un texto libre
  validate -- valida una cadena contra un patron especifico
  ui       -- lanza la interfaz grafica (Tkinter)
"""

import argparse
import sys

from src.patterns.date_validator import validate_date
from src.patterns.email_validator import validate_email
from src.patterns.nit_validator import validate_nit
from src.patterns.password_validator import validate_password
from src.patterns.phone_validator import validate_phone
from src.patterns.plate_validator import validate_plate
from src.patterns.url_validator import validate_url

VALIDATORS = {
    "date": validate_date,
    "email": validate_email,
    "nit": validate_nit,
    "phone": validate_phone,
    "plate": validate_plate,
    "password": validate_password,
    "url": validate_url,
}


def cmd_scan(args: argparse.Namespace) -> None:
    """Escanea texto libre e imprime cada coincidencia encontrada."""

    from src.patterns.text_scanner import scan_text

    matches = scan_text(args.text)

    if not matches:
        print("No se encontraron patrones en el texto.")
        return

    for match in matches:
        print(
            f"[{match.pattern}] "
            f"start={match.start} end={match.end} "
            f"raw={match.raw!r} normalized={match.normalized!r} "
            f"msg={match.result.message!r}"
        )


def cmd_validate(args: argparse.Namespace) -> None:
    """Valida una cadena contra el patron indicado e imprime el resultado."""

    validator = VALIDATORS.get(args.type)

    if validator is None:
        tipos = ", ".join(VALIDATORS)
        print(f"Tipo desconocido: {args.type!r}. Tipos validos: {tipos}.")
        sys.exit(1)

    result = validator(args.value)

    print(f"aceptado: {result.accepted}")
    print(f"mensaje:  {result.message}")
    print("traza:")
    for step in result.trace:
        print(f"  {step}")


def cmd_ui(args: argparse.Namespace) -> None:
    """Lanza la ventana grafica Tkinter."""

    from src.ui.app import launch

    launch()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Herramienta de busqueda y validacion de patrones (TLF)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Busca patrones en texto libre.")
    scan_parser.add_argument("text", help="Texto a escanear.")
    scan_parser.set_defaults(func=cmd_scan)

    validate_parser = subparsers.add_parser("validate", help="Valida una cadena contra un patron.")
    validate_parser.add_argument(
        "type",
        choices=list(VALIDATORS),
        help="Tipo de patron a validar.",
    )
    validate_parser.add_argument("value", help="Cadena a validar.")
    validate_parser.set_defaults(func=cmd_validate)

    ui_parser = subparsers.add_parser("ui", help="Lanza la interfaz grafica Tkinter.")
    ui_parser.set_defaults(func=cmd_ui)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
