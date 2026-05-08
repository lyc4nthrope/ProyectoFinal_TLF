"""Pruebas para el escaneo de patrones en texto."""

import unittest

from src.patterns.text_scanner import scan_text


class TextScannerTests(unittest.TestCase):
    def test_finds_date_in_text(self) -> None:
        matches = scan_text("La reunion es el 15/08/2024 a las 10am.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "date")
        self.assertEqual(matches[0].raw, "15/08/2024")
        self.assertEqual(matches[0].start, 17)

    def test_finds_email_in_text(self) -> None:
        matches = scan_text("Escribe a usuario@example.com para mas info.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "email")
        self.assertEqual(matches[0].normalized, "usuario@example.com")

    def test_finds_phone_in_text(self) -> None:
        matches = scan_text("Llama al 3001234567 hoy mismo.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "phone")
        self.assertEqual(matches[0].normalized, "3001234567")

    def test_finds_international_phone(self) -> None:
        matches = scan_text("Contacto: +57 300-123-4567.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "phone")
        self.assertEqual(matches[0].normalized, "573001234567")

    def test_finds_multiple_patterns_in_text(self) -> None:
        text = "Fecha: 29/02/2024. Correo: admin@test.org. Tel: 3001234567."
        matches = scan_text(text)

        patterns = [m.pattern for m in matches]
        self.assertIn("date", patterns)
        self.assertIn("email", patterns)
        self.assertIn("phone", patterns)
        self.assertEqual(len(matches), 3)

    def test_returns_empty_for_no_matches(self) -> None:
        matches = scan_text("Este texto no tiene patrones reconocibles.")

        self.assertEqual(matches, [])

    def test_returns_empty_for_empty_string(self) -> None:
        matches = scan_text("")

        self.assertEqual(matches, [])

    def test_date_has_correct_position(self) -> None:
        matches = scan_text("HOY: 01/01/2000 fin.")

        self.assertEqual(matches[0].start, 5)
        self.assertEqual(matches[0].end, 15)

    def test_invalid_date_not_reported(self) -> None:
        matches = scan_text("La fecha 31/04/2024 no existe en el calendario.")

        self.assertEqual(matches, [])

    def test_invalid_email_not_reported(self) -> None:
        matches = scan_text("El correo usuario@ no esta completo.")

        self.assertEqual(matches, [])

    def test_phone_too_short_not_reported(self) -> None:
        matches = scan_text("El numero 12345 es muy corto.")

        self.assertEqual(matches, [])

    def test_date_found_before_adjacent_text(self) -> None:
        matches = scan_text("15/08/2024texto")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "date")
        self.assertEqual(matches[0].end, 10)

    def test_consecutive_matches(self) -> None:
        matches = scan_text("3001234567 usuario@example.com")

        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].pattern, "phone")
        self.assertEqual(matches[1].pattern, "email")


if __name__ == "__main__":
    unittest.main()
