"""
Unit tests for the split_names function.
10 complex Spanish name edge cases covering particles, apostrophes,
single names, empty strings, compound surnames, and whitespace.
"""
import pytest
import os

os.environ.setdefault("API_KEY", "test-key")
from main import split_names


class TestSplitNamesBasic:
    """Standard two-word, three-word, and four-word names."""

    def test_two_words(self):
        result = split_names("DIEGO VELAZQUEZ")
        assert result["p_nombre"] == "Diego"
        assert result["p_apellido"] == "Velazquez"
        assert result["s_apellido"] == ""

    def test_three_words(self):
        result = split_names("JUAN PEREZ GARCIA")
        assert result["p_nombre"] == "Juan"
        assert result["p_apellido"] == "Perez"
        assert result["s_apellido"] == "Garcia"

    def test_four_words(self):
        result = split_names("CARLOS ANDRES PEREZ GOMEZ")
        assert result["p_nombre"] == "Carlos"
        assert result["s_nombre"] == "Andres"
        assert result["p_apellido"] == "Perez"
        assert result["s_apellido"] == "Gomez"


class TestSplitNamesEdgeCases:
    """10 complex Spanish name edge cases from the audit report."""

    def test_compound_first_name_with_del(self):
        """María del Pilar de la Rosa García"""
        result = split_names("MARIA DEL PILAR DE LA ROSA GARCIA")
        assert result["p_nombre"] == "Maria"
        assert result["p_apellido"] == "De La Rosa"
        assert result["s_apellido"] == "Garcia"

    def test_apostrophe_name(self):
        """Juan O'Brian Pérez — apostrophe in name."""
        result = split_names("JUAN O'BRIAN PEREZ")
        assert result["p_nombre"] == "Juan"
        assert result["p_apellido"] == "O'Brian"
        assert result["s_apellido"] == "Perez"

    def test_compound_de_los(self):
        """José María de los Ángeles Torres"""
        result = split_names("JOSE MARIA DE LOS ANGELES TORRES")
        assert result["p_nombre"] == "Jose"
        assert result["s_nombre"] == "Maria"
        assert result["p_apellido"] == "De Los Angeles"
        assert result["s_apellido"] == "Torres"

    def test_single_word(self):
        """Single name — should leave all fields empty (edge case)."""
        result = split_names("LUIS")
        # With only 1 group, the current logic produces all-empty
        assert result["p_nombre"] == ""
        assert result["p_apellido"] == ""

    def test_empty_string(self):
        """Empty string input."""
        result = split_names("")
        assert result["p_nombre"] == ""
        assert result["p_apellido"] == ""
        assert result["s_apellido"] == ""

    def test_only_particles(self):
        """Only particles with a single real word — 'DE LA CRUZ'."""
        result = split_names("DE LA CRUZ")
        # Grouping: 'de la cruz' → 1 group → all empty (edge case)
        assert result["p_nombre"] == ""

    def test_compound_surnames(self):
        """CARLOS ANDRÉS DE LA VEGA DEL CAMPO"""
        result = split_names("CARLOS ANDRES DE LA VEGA DEL CAMPO")
        assert result["p_nombre"] == "Carlos"
        assert result["s_nombre"] == "Andres"
        assert result["p_apellido"] == "De La Vega"
        assert result["s_apellido"] == "Del Campo"

    def test_extra_whitespace(self):
        """Leading/trailing and multiple inner spaces."""
        result = split_names("  MARIA   LUISA  ")
        assert result["p_nombre"] == "Maria"
        assert result["p_apellido"] == "Luisa"

    def test_hyphenated_name(self):
        """Rosa-María del Carmen López Fernández"""
        result = split_names("ROSA-MARIA DEL CARMEN LOPEZ FERNANDEZ")
        assert result["p_nombre"] == "Rosa-Maria"
        assert result["s_nombre"] == "Del Carmen"
        assert result["p_apellido"] == "Lopez"
        assert result["s_apellido"] == "Fernandez"

    def test_y_particle(self):
        """Ana Y Martínez — Y as particle groups with next word."""
        result = split_names("ANA Y MARTINEZ")
        # 'y' is a particle → groups with 'martinez' → 2 groups total
        assert result["p_nombre"] == "Ana"
        assert result["p_apellido"] == "Y Martinez"


class TestSplitNamesOutputFormat:
    """Verify output format: title case, all five keys present."""

    def test_all_keys_present(self):
        result = split_names("JUAN PEREZ")
        expected_keys = {"p_nombre", "s_nombre", "t_nombre", "p_apellido", "s_apellido"}
        assert set(result.keys()) == expected_keys

    def test_title_case_output(self):
        result = split_names("JUAN PEREZ GARCIA")
        for value in result.values():
            if value:  # skip empty strings
                assert value == value.title()
