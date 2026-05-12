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

    def test_finds_car_plate_in_text(self) -> None:
        matches = scan_text("El carro ABC123 fue reportado.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "plate")
        self.assertEqual(matches[0].raw, "ABC123")
        self.assertEqual(matches[0].normalized, "ABC123")

    def test_finds_moto_plate_in_text(self) -> None:
        matches = scan_text("Moto XYZ456A circulaba por la via.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "plate")
        self.assertEqual(matches[0].normalized, "XYZ456A")

    def test_finds_plate_with_hyphen_in_text(self) -> None:
        matches = scan_text("Placa ABC-123 registrada.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "plate")
        self.assertEqual(matches[0].normalized, "ABC123")

    def test_finds_url_in_text(self) -> None:
        matches = scan_text("Visita https://example.com para mas info.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "url")
        self.assertEqual(matches[0].raw, "https://example.com")

    def test_finds_url_with_path_in_text(self) -> None:
        matches = scan_text("Descarga en http://example.com/archivo.pdf hoy.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "url")
        self.assertEqual(matches[0].normalized, "http://example.com/archivo.pdf")

    def test_finds_nit_in_text(self) -> None:
        matches = scan_text("La empresa con NIT 900.123.456-8 esta registrada.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].pattern, "nit")
        self.assertEqual(matches[0].raw, "900.123.456-8")

    def test_nit_normalized_only_digits(self) -> None:
        matches = scan_text("NIT: 800.100.200-8.")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].normalized, "8001002008")

    def test_invalid_url_not_reported(self) -> None:
        matches = scan_text("El protocolo ftp://example.com no es valido aqui.")

        self.assertEqual(matches, [])

    def test_invalid_nit_not_reported(self) -> None:
        matches = scan_text("El codigo 900123456 no tiene formato NIT.")

        self.assertNotIn("nit", [m.pattern for m in matches])

    def test_finds_url_and_email_together(self) -> None:
        text = "Web: https://example.com correo: admin@example.com"
        matches = scan_text(text)

        patterns = [m.pattern for m in matches]
        self.assertIn("url", patterns)
        self.assertIn("email", patterns)

    def test_password_not_found_in_scanner(self) -> None:
        matches = scan_text("La clave es Secure@1 segun el sistema.")

        patterns = [m.pattern for m in matches]
        self.assertNotIn("password", patterns)

    def test_finds_plate_email_and_phone_together(self) -> None:
        text = "Placa ABC123 correo user@example.com telefono 3001234567."
        matches = scan_text(text)

        patterns = [m.pattern for m in matches]
        self.assertIn("plate", patterns)
        self.assertIn("email", patterns)
        self.assertIn("phone", patterns)
        self.assertEqual(len(matches), 3)


if __name__ == "__main__":
    unittest.main()
