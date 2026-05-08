"""Pruebas para el validador de placas vehiculares colombianas."""

import unittest

from src.patterns.plate_validator import validate_plate


class PlateValidatorTests(unittest.TestCase):

    # --- Validos ---

    def test_accepts_car_plate_without_hyphen(self) -> None:
        result = validate_plate("ABC123")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "ABC123")
        self.assertIn("ACCEPT", result.trace[-1])

    def test_accepts_car_plate_with_hyphen(self) -> None:
        result = validate_plate("ABC-123")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "ABC123")

    def test_accepts_moto_plate_without_hyphen(self) -> None:
        result = validate_plate("XYZ456A")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "XYZ456A")
        self.assertIn("moto", result.message.lower())

    def test_accepts_moto_plate_with_hyphen(self) -> None:
        result = validate_plate("XYZ-456A")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "XYZ456A")

    def test_message_distinguishes_car_from_moto(self) -> None:
        car = validate_plate("AAA000")
        moto = validate_plate("AAA000A")

        self.assertIn("carro", car.message.lower())
        self.assertIn("moto", moto.message.lower())

    # --- Invalidos ---

    def test_rejects_lowercase_letters(self) -> None:
        result = validate_plate("abc123")

        self.assertFalse(result.accepted)

    def test_rejects_only_two_initial_letters(self) -> None:
        result = validate_plate("AB123")

        self.assertFalse(result.accepted)
        self.assertIn("tres letras", result.message.lower())

    def test_rejects_only_two_digits(self) -> None:
        result = validate_plate("ABC12")

        self.assertFalse(result.accepted)
        self.assertIn("tres digitos", result.message.lower())

    def test_rejects_extra_characters_after_car_plate(self) -> None:
        result = validate_plate("ABC123X9")

        self.assertFalse(result.accepted)
        self.assertIn("extra", result.message.lower())

    def test_rejects_empty_string(self) -> None:
        result = validate_plate("")

        self.assertFalse(result.accepted)
        self.assertIn("vacia", result.message.lower())

    def test_rejects_digit_in_first_position(self) -> None:
        result = validate_plate("1BC123")

        self.assertFalse(result.accepted)

    def test_rejects_invalid_symbol(self) -> None:
        result = validate_plate("ABC.123")

        self.assertFalse(result.accepted)

    def test_rejects_double_hyphen(self) -> None:
        result = validate_plate("ABC--123")

        self.assertFalse(result.accepted)

    def test_rejects_trailing_hyphen_on_car(self) -> None:
        result = validate_plate("ABC123-")

        self.assertFalse(result.accepted)
        self.assertIn("extra", result.message.lower())

    # --- Borde ---

    def test_normalized_strips_hyphen(self) -> None:
        result = validate_plate("ZZZ-999")

        self.assertEqual(result.normalized, "ZZZ999")

    def test_moto_normalized_strips_hyphen(self) -> None:
        result = validate_plate("ZZZ-999Z")

        self.assertEqual(result.normalized, "ZZZ999Z")

    def test_rejects_incomplete_plate_three_letters_only(self) -> None:
        result = validate_plate("ABC")

        self.assertFalse(result.accepted)
        self.assertIn("incompleta", result.message.lower())


if __name__ == "__main__":
    unittest.main()
