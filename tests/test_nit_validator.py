"""Pruebas para el validador de NITs colombianos."""

import unittest

from src.patterns.nit_validator import validate_nit


class NitValidatorTests(unittest.TestCase):

    # -- Validos: 9 digitos (NNN.NNN.NNN-D) --

    def test_nit_basico(self) -> None:
        result = validate_nit("900.123.456-8")
        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "9001234568")

    def test_nit_ceros(self) -> None:
        result = validate_nit("000.000.000-0")
        self.assertTrue(result.accepted)

    def test_nit_con_dv_cuatro(self) -> None:
        """999.999.999 con DV correcto (modulo 11)."""
        result = validate_nit("999.999.999-4")
        self.assertTrue(result.accepted)

    def test_normalized_solo_digitos(self) -> None:
        result = validate_nit("900.123.456-8")
        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "9001234568")

    # -- Validos: 10 digitos (N.NNN.NNN.NNN-D) --

    def test_nit_10_digitos_basico(self) -> None:
        """NIT de persona natural con 10 digitos."""
        result = validate_nit("1.092.850.782-3")
        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "10928507823")

    def test_nit_10_digitos_ceros(self) -> None:
        result = validate_nit("0.000.000.000-0")
        self.assertTrue(result.accepted)

    # -- Invalidos: estructura --

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
        result = validate_nit("900.123.456-8X")
        self.assertFalse(result.accepted)

    def test_cadena_vacia_rechazada(self) -> None:
        result = validate_nit("")
        self.assertFalse(result.accepted)

    # -- Invalidos: borde --

    def test_digito_verificador_es_unico(self) -> None:
        result = validate_nit("900.123.456-88")
        self.assertFalse(result.accepted)

    def test_grupo_con_dos_digitos_rechazado(self) -> None:
        result = validate_nit("90.123.456-7")
        self.assertFalse(result.accepted)

    def test_grupo_con_cuatro_digitos_rechazado(self) -> None:
        result = validate_nit("9000.123.456-7")
        self.assertFalse(result.accepted)

    # -- Invalidos: digito verificador --

    def test_dv_incorrecto_rechazado(self) -> None:
        """900.123.456-7 debe ser rechazado porque el DV correcto es 8."""
        result = validate_nit("900.123.456-7")
        self.assertFalse(result.accepted)
        self.assertIn("digito verificador", result.message.lower())

    def test_dv_incorrecto_10_digitos_rechazado(self) -> None:
        """1.092.850.782-7 debe ser rechazado porque el DV correcto es 3."""
        result = validate_nit("1.092.850.782-7")
        self.assertFalse(result.accepted)
        self.assertIn("digito verificador", result.message.lower())

    # -- Invalidos: estructura de 10 digitos --

    def test_estructura_10_digitos_invalida(self) -> None:
        """10 digitos con grupos incorrectos."""
        result = validate_nit("10.928.507-8")
        self.assertFalse(result.accepted)

    def test_formato_no_soportado(self) -> None:
        """4 bloques de 3 no es valido."""
        result = validate_nit("123.456.789.012-3")
        self.assertFalse(result.accepted)


if __name__ == "__main__":
    unittest.main()
