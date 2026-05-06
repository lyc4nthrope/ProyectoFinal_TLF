"""Pruebas para el validador de telefonos."""

import unittest

from src.patterns.phone_validator import validate_phone


class PhoneValidatorTests(unittest.TestCase):
    def test_accepts_plain_local_phone(self) -> None:
        result = validate_phone("3001234567")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "3001234567")
        self.assertIn("ACCEPT", result.trace[-1])

    def test_accepts_international_phone_with_separators(self) -> None:
        result = validate_phone("+57 300-123-4567")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "573001234567")

    def test_rejects_consecutive_separators(self) -> None:
        result = validate_phone("300--1234567")

        self.assertFalse(result.accepted)
        self.assertIn("separadores consecutivos", result.message.lower())

    def test_rejects_invalid_symbols(self) -> None:
        result = validate_phone("30012A4567")

        self.assertFalse(result.accepted)
        self.assertIn("simbolos no permitidos", result.message.lower())

    def test_rejects_too_few_digits(self) -> None:
        result = validate_phone("12345")

        self.assertFalse(result.accepted)
        self.assertIn("cantidad de digitos", result.message.lower())


if __name__ == "__main__":
    unittest.main()
