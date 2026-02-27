"""
Tests for the validators module — data cleaning and column validation.
"""
import pytest
import os

os.environ.setdefault("API_KEY", "test-key")
from validators import (
    clean_name,
    validate_cedula,
    validate_nacionalidad,
    validate_nombre,
    validate_row,
    is_row_empty,
)


class TestCleanName:
    """Test character cleaning for name fields."""

    def test_removes_digits(self):
        assert clean_name("JUAN 123 PEREZ") == "JUAN PEREZ"

    def test_removes_special_chars(self):
        assert clean_name("MARIA@DEL #PILAR") == "MARIADEL PILAR"

    def test_keeps_hyphens(self):
        assert clean_name("ROSA-MARIA LOPEZ") == "ROSA-MARIA LOPEZ"

    def test_keeps_apostrophes(self):
        assert clean_name("O'BRIAN PEREZ") == "O'BRIAN PEREZ"

    def test_keeps_accented_chars(self):
        assert clean_name("JOSÉ ÁNGELES") == "JOSÉ ÁNGELES"

    def test_collapses_spaces(self):
        assert clean_name("MARIA   LUISA") == "MARIA LUISA"

    def test_strips_edges(self):
        assert clean_name("  JUAN PEREZ  ") == "JUAN PEREZ"

    def test_empty_string(self):
        assert clean_name("") == ""

    def test_none_input(self):
        assert clean_name(None) == ""

    def test_numeric_input(self):
        assert clean_name(12345) == ""


class TestValidateCedula:
    """Cédula must be 7-8 digits."""

    def test_valid_7_digits(self):
        ok, val = validate_cedula("1234567")
        assert ok is True
        assert val == "1234567"

    def test_valid_8_digits(self):
        ok, val = validate_cedula("12345678")
        assert ok is True
        assert val == "12345678"

    def test_too_short(self):
        ok, msg = validate_cedula("12345")
        assert ok is False

    def test_too_long(self):
        ok, msg = validate_cedula("123456789")
        assert ok is False

    def test_float_from_excel(self):
        """Excel sometimes stores numbers as floats."""
        ok, val = validate_cedula(12345678.0)
        assert ok is True
        assert val == "12345678"

    def test_empty(self):
        ok, msg = validate_cedula("")
        assert ok is False

    def test_none(self):
        ok, msg = validate_cedula(None)
        assert ok is False

    def test_letters(self):
        ok, msg = validate_cedula("ABC1234")
        assert ok is False


class TestValidateNacionalidad:
    """Nacionalidad must be V or E."""

    def test_v(self):
        ok, val = validate_nacionalidad("V")
        assert ok is True and val == "V"

    def test_e(self):
        ok, val = validate_nacionalidad("E")
        assert ok is True and val == "E"

    def test_lowercase(self):
        ok, val = validate_nacionalidad("v")
        assert ok is True and val == "V"

    def test_invalid(self):
        ok, msg = validate_nacionalidad("X")
        assert ok is False

    def test_empty(self):
        ok, msg = validate_nacionalidad("")
        assert ok is False


class TestValidateNombre:

    def test_valid_name(self):
        ok, val = validate_nombre("JUAN PEREZ")
        assert ok is True
        assert val == "JUAN PEREZ"

    def test_empty_after_cleaning(self):
        ok, msg = validate_nombre("@#$%")
        assert ok is False

    def test_none(self):
        ok, msg = validate_nombre(None)
        assert ok is False


class TestValidateRow:

    def test_valid_row(self):
        row = {"N°": "1", "Nacionalidad": "V", "Cedula": "12345678", "NOMBRE_COMPLETO": "JUAN PEREZ"}
        is_valid, cleaned, errors = validate_row(row)
        assert is_valid is True
        assert len(errors) == 0
        assert cleaned["Cedula"] == "12345678"
        assert cleaned["NOMBRE_COMPLETO"] == "JUAN PEREZ"

    def test_invalid_cedula_and_name(self):
        row = {"N°": "1", "Nacionalidad": "V", "Cedula": "123", "NOMBRE_COMPLETO": ""}
        is_valid, cleaned, errors = validate_row(row)
        assert is_valid is False
        assert len(errors) == 2

    def test_is_row_empty_true(self):
        assert is_row_empty([None, "", "  ", None]) is True

    def test_is_row_empty_false(self):
        assert is_row_empty([None, "V", None, None]) is False
