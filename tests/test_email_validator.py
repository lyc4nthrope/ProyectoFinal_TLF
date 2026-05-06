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


if __name__ == "__main__":
    unittest.main()
