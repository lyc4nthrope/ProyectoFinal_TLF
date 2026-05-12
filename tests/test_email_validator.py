"""Pruebas para el validador de correos."""

import unittest

from src.patterns.email_validator import validate_email


class EmailValidatorTests(unittest.TestCase):
    def test_accepts_basic_email(self) -> None:
        result = validate_email("usuario@example.com")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "usuario@example.com")
        self.assertIn("ACCEPT", result.trace[-1])

    def test_accepts_email_with_local_separators(self) -> None:
        result = validate_email("user.name-test_1@sub.domain.com")

        self.assertTrue(result.accepted)

    def test_rejects_missing_at_symbol(self) -> None:
        result = validate_email("usuario.example.com")

        self.assertFalse(result.accepted)
        self.assertIn("simbolo '@'", result.message.lower())

    def test_rejects_repeated_local_separators(self) -> None:
        result = validate_email("user..name@example.com")

        self.assertFalse(result.accepted)
        self.assertIn("separadores mal ubicados", result.message.lower())

    def test_rejects_invalid_domain_suffix(self) -> None:
        result = validate_email("usuario@example.c1")

        self.assertFalse(result.accepted)
        self.assertIn("terminacion del dominio", result.message.lower())

    def test_rejects_local_part_starting_with_separator(self) -> None:
        result = validate_email(".usuario@example.com")

        self.assertFalse(result.accepted)
        self.assertIn("inicia de forma invalida", result.message.lower())

    def test_rejects_domain_label_ending_in_hyphen(self) -> None:
        result = validate_email("usuario@example-.com")

        self.assertFalse(result.accepted)
        self.assertIn("guion mal ubicado", result.message.lower())

    # -- Nuevas reglas (Fase 5) --

    def test_accepts_plus_subaddressing(self) -> None:
        """+ en parte local (subaddressing RFC 5233) debe ser aceptado."""
        result = validate_email("user+tag@example.com")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "user+tag@example.com")

    def test_rejects_email_too_long(self) -> None:
        """Correo que excede MAX_EMAIL_LENGTH debe ser rechazado."""
        local = "a" * 200
        domain = "b" * 50
        result = validate_email(f"{local}@{domain}.com")

        self.assertFalse(result.accepted)
        self.assertIn("longitud maxima", result.message.lower())

    def test_rejects_local_part_too_long(self) -> None:
        """Parte local que excede MAX_LOCAL_LENGTH debe ser rechazada."""
        local = "a" * 65
        result = validate_email(f"{local}@example.com")

        self.assertFalse(result.accepted)
        self.assertIn("parte local", result.message.lower())

    def test_rejects_domain_label_too_long(self) -> None:
        """Etiqueta de dominio que excede MAX_LABEL_LENGTH debe ser rechazada."""
        label = "a" * 64
        result = validate_email(f"user@{label}.com")

        self.assertFalse(result.accepted)
        self.assertIn("dominio", result.message.lower())


if __name__ == "__main__":
    unittest.main()
