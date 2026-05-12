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

    def test_rejects_too_many_digits(self) -> None:
        """11 digitos sin prefijo deben ser rechazados."""
        result = validate_phone("31438080440")

        self.assertFalse(result.accepted)
        self.assertIn("cantidad de digitos", result.message.lower())

    def test_rejects_international_with_too_many_local_digits(self) -> None:
        """+57 con 11 digitos locales debe ser rechazado."""
        result = validate_phone("+57 314-380-80440")

        self.assertFalse(result.accepted)
        self.assertIn("cantidad de digitos", result.message.lower())

    def test_accepts_other_country_code(self) -> None:
        """Codigo de pais diferente a 57 debe funcionar."""
        result = validate_phone("+1 300-123-4567")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "13001234567")

    def test_rejects_international_without_local_digits(self) -> None:
        """+ solo con codigo de pais y sin digitos locales."""
        result = validate_phone("+57")

        self.assertFalse(result.accepted)
        self.assertIn("cantidad de digitos", result.message.lower())

    def test_rejects_international_leading_zero_local(self) -> None:
        """+57 con 0 adelantado al numero local (11 locales) debe rechazar."""
        result = validate_phone("+57 03143808044")

        self.assertFalse(result.accepted)
        self.assertIn("cantidad de digitos", result.message.lower())

    def test_rejects_eleven_digits_with_plus_prefix(self) -> None:
        """11 digitos totales con prefijo + (solo 1 de pais + 10 locales)."""
        result = validate_phone("+1 2345678901")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "12345678901")


if __name__ == "__main__":
    unittest.main()
