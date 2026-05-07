"""Pruebas para el validador de fechas."""

import unittest

from src.patterns.date_validator import validate_date


class DateValidatorTests(unittest.TestCase):
    def test_accepts_regular_date(self) -> None:
        result = validate_date("15/08/2024")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "15/08/2024")
        self.assertIn("ACCEPT", result.trace[-1])

    def test_accepts_leap_day(self) -> None:
        result = validate_date("29/02/2024")

        self.assertTrue(result.accepted)

    def test_rejects_invalid_day_for_month(self) -> None:
        result = validate_date("31/04/2024")

        self.assertFalse(result.accepted)
        self.assertIn("dia de la fecha es invalido", result.message.lower())

    def test_rejects_non_leap_february(self) -> None:
        result = validate_date("29/02/2023")

        self.assertFalse(result.accepted)
        self.assertIn("dia de la fecha es invalido", result.message.lower())

    def test_rejects_missing_zero_padding(self) -> None:
        result = validate_date("1/08/2024")

        self.assertFalse(result.accepted)
        self.assertIn("dia de la fecha esta incompleto", result.message.lower())

    def test_rejects_invalid_separator(self) -> None:
        result = validate_date("15-08-2024")

        self.assertFalse(result.accepted)
        self.assertIn("separador correcto", result.message.lower())

    def test_rejects_year_out_of_range(self) -> None:
        result = validate_date("15/08/2201")

        self.assertFalse(result.accepted)
        self.assertIn("anio de la fecha esta fuera del rango", result.message.lower())

    def test_rejects_month_zero(self) -> None:
        result = validate_date("15/00/2024")

        self.assertFalse(result.accepted)
        self.assertIn("mes de la fecha es invalido", result.message.lower())

    def test_rejects_extra_trailing_symbols(self) -> None:
        result = validate_date("15/08/2024x")

        self.assertFalse(result.accepted)
        self.assertIn("simbolos adicionales", result.message.lower())


if __name__ == "__main__":
    unittest.main()
