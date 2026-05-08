"""Pruebas para el validador de URLs."""

import unittest

from src.patterns.url_validator import validate_url


class UrlValidatorTests(unittest.TestCase):

    # -- Validos --

    def test_http_basic(self) -> None:
        result = validate_url("http://example.com")
        self.assertTrue(result.accepted)

    def test_https_basic(self) -> None:
        result = validate_url("https://example.com")
        self.assertTrue(result.accepted)

    def test_https_with_www(self) -> None:
        result = validate_url("https://www.google.com")
        self.assertTrue(result.accepted)

    def test_url_with_path(self) -> None:
        result = validate_url("https://example.com/path/to/page")
        self.assertTrue(result.accepted)

    def test_url_with_query(self) -> None:
        result = validate_url("https://example.com/search?q=hola&lang=es")
        self.assertTrue(result.accepted)

    def test_url_with_subdomain(self) -> None:
        result = validate_url("https://api.sub.example.org")
        self.assertTrue(result.accepted)

    def test_url_country_tld(self) -> None:
        result = validate_url("https://example.co.uk")
        self.assertTrue(result.accepted)

    def test_url_with_trailing_slash(self) -> None:
        result = validate_url("http://example.com/")
        self.assertTrue(result.accepted)

    def test_url_with_fragment(self) -> None:
        result = validate_url("https://example.com/page#section")
        self.assertTrue(result.accepted)

    def test_url_query_without_path(self) -> None:
        result = validate_url("https://example.com?q=test")
        self.assertTrue(result.accepted)

    # -- Invalidos --

    def test_ftp_protocol_rejected(self) -> None:
        result = validate_url("ftp://example.com")
        self.assertFalse(result.accepted)

    def test_no_dot_in_domain_rejected(self) -> None:
        result = validate_url("http://example")
        self.assertFalse(result.accepted)

    def test_missing_slash_rejected(self) -> None:
        result = validate_url("http:/example.com")
        self.assertFalse(result.accepted)

    def test_empty_domain_rejected(self) -> None:
        result = validate_url("http://")
        self.assertFalse(result.accepted)

    def test_empty_string_rejected(self) -> None:
        result = validate_url("")
        self.assertFalse(result.accepted)

    def test_domain_trailing_hyphen_rejected(self) -> None:
        result = validate_url("http://example-.com")
        self.assertFalse(result.accepted)

    def test_domain_leading_dot_rejected(self) -> None:
        result = validate_url("http://.example.com")
        self.assertFalse(result.accepted)

    def test_no_protocol_rejected(self) -> None:
        result = validate_url("example.com")
        self.assertFalse(result.accepted)

    # -- Borde --

    def test_minimum_valid_url(self) -> None:
        result = validate_url("http://a.bc")
        self.assertTrue(result.accepted)

    def test_normalized_equals_raw(self) -> None:
        result = validate_url("https://example.com/path")
        self.assertEqual(result.normalized, "https://example.com/path")

    def test_http_uppercase_protocol_accepted(self) -> None:
        result = validate_url("HTTP://example.com")
        self.assertTrue(result.accepted)

    def test_url_with_port_like_path(self) -> None:
        result = validate_url("https://example.com/page?a=1&b=2")
        self.assertTrue(result.accepted)


if __name__ == "__main__":
    unittest.main()
