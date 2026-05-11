"""Pruebas para el validador de contrasenas seguras."""

import unittest

from src.patterns.password_validator import validate_password


class PasswordValidatorTests(unittest.TestCase):

    # --- Validos ---

    def test_accepts_valid_password(self) -> None:
        result = validate_password("Secure@1")

        self.assertTrue(result.accepted)
        self.assertEqual(result.normalized, "")
        self.assertIn("ACCEPT", result.trace[-1])

    def test_accepts_long_valid_password(self) -> None:
        result = validate_password("MyP@ssw0rd!")

        self.assertTrue(result.accepted)

    def test_accepts_password_at_exact_minimum_length(self) -> None:
        result = validate_password("Abcde@1z")

        self.assertTrue(result.accepted)
        self.assertEqual(len("Abcde@1z"), 8)

    def test_normalized_is_always_empty(self) -> None:
        result = validate_password("Secure@1")

        self.assertEqual(result.normalized, "")

    # --- Invalidos ---

    def test_rejects_too_short(self) -> None:
        result = validate_password("Ab1@")

        self.assertFalse(result.accepted)
        self.assertIn("longitud", result.message.lower())

    def test_rejects_missing_uppercase(self) -> None:
        result = validate_password("secure@1abc")

        self.assertFalse(result.accepted)
        self.assertIn("mayuscula", result.message.lower())

    def test_rejects_missing_lowercase(self) -> None:
        result = validate_password("SECURE@1ABC")

        self.assertFalse(result.accepted)
        self.assertIn("minuscula", result.message.lower())

    def test_rejects_missing_digit(self) -> None:
        result = validate_password("SecurePass@")

        self.assertFalse(result.accepted)
        self.assertIn("digito", result.message.lower())

    def test_rejects_missing_special_symbol(self) -> None:
        result = validate_password("SecurePass1")

        self.assertFalse(result.accepted)
        self.assertIn("simbolo especial", result.message.lower())

    def test_rejects_invalid_symbol(self) -> None:
        result = validate_password("Secure^1ab")

        self.assertFalse(result.accepted)
        self.assertIn("^", result.message)

    def test_rejects_empty_string(self) -> None:
        result = validate_password("")

        self.assertFalse(result.accepted)
        self.assertIn("vacia", result.message.lower())

    # --- Borde ---

    def test_rejects_seven_characters_all_conditions_met_except_length(self) -> None:
        result = validate_password("Abc@1zX")

        self.assertFalse(result.accepted)
        self.assertIn("longitud", result.message.lower())

    def test_message_lists_all_missing_conditions(self) -> None:
        result = validate_password("abcdefgh")

        self.assertFalse(result.accepted)
        self.assertIn("mayuscula", result.message.lower())
        self.assertIn("digito", result.message.lower())
        self.assertIn("simbolo especial", result.message.lower())

    def test_trace_records_flag_activations(self) -> None:
        result = validate_password("Secure@1")

        trace_text = " ".join(result.trace)
        # Verificar que la traza muestra transiciones de estado reales.
        # Cada nueva bandera activada produce un estado compuesto diferente.
        self.assertIn("SEEN_U", trace_text)       # 'S' activa mayuscula
        self.assertIn("SEEN_L_U", trace_text)     # 'e' activa minuscula
        self.assertIn("SEEN_L_U_S", trace_text)   # '@' activa especial
        self.assertIn("SEEN_L_U_D_S", trace_text) # '1' activa digito


if __name__ == "__main__":
    unittest.main()
