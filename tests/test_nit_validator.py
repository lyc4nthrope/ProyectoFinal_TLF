"""Pruebas para el validador de NITs colombianos."""

import unittest

from src.patterns.nit_validator import validate_nit


class NitValidatorTests(unittest.TestCase):

    # -- Validos --

    def test_nit_basico(self) -> None:
        result = validate_nit("900.123.456-7")
        self.assertTrue(result.accepted)

    def test_nit_ceros(self) -> None:
        result = validate_nit("000.000.000-0")
        self.assertTrue(result.accepted)

    def test_nit_noves(self) -> None:
        result = validate_nit("999.999.999-9")
        self.assertTrue(result.accepted)

    def test_nit_verificador_cero(self) -> None:
        result = validate_nit("800.100.200-0")
        self.assertTrue(result.accepted)

    def test_normalized_solo_digitos(self) -> None:
        result = validate_nit("900.123.456-7")
        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "9001234567")

    # -- Invalidos --

    def test_sin_puntos_rechazado(self) -> None:
        result = validate_nit("900123456-7")
        self.assertFalse(result.accepted)

    def test_sin_guion_rechazado(self) -> None:
        result = validate_nit("900.123.4567")
        self.assertFalse(result.accepted)

    def test_un_grupo_rechazado(self) -> None:
        result = validate_nit("900")
        self.assertFalse(result.accepted)

    def test_dos_grupos_rechazado(self) -> None:
        result = validate_nit("900.123")
        self.assertFalse(result.accepted)

    def test_letras_en_grupo_rechazado(self) -> None:
        result = validate_nit("9AB.123.456-7")
        self.assertFalse(result.accepted)

    def test_separador_incorrecto_rechazado(self) -> None:
        result = validate_nit("900-123-456-7")
        self.assertFalse(result.accepted)

    def test_caracteres_extra_rechazado(self) -> None:
        result = validate_nit("900.123.456-7X")
        self.assertFalse(result.accepted)

    def test_cadena_vacia_rechazada(self) -> None:
        result = validate_nit("")
        self.assertFalse(result.accepted)

    # -- Borde --

    def test_digito_verificador_es_unico(self) -> None:
        result = validate_nit("900.123.456-77")
        self.assertFalse(result.accepted)

    def test_grupo_con_dos_digitos_rechazado(self) -> None:
        result = validate_nit("90.123.456-7")
        self.assertFalse(result.accepted)

    def test_grupo_con_cuatro_digitos_rechazado(self) -> None:
        result = validate_nit("9000.123.456-7")
        self.assertFalse(result.accepted)


if __name__ == "__main__":
    unittest.main()
