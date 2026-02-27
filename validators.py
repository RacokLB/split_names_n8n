"""
Data validation and cleaning module for XLSX processing.

Column-specific rules:
  - Cedula: numeric, 6-8 digits
  - Nacionalidad: 'V' or 'E'
  - NOMBRE_COMPLETO: non-empty, stripped of invalid characters
  - N°: non-empty row number
"""
import re
from typing import Optional


# ── Character cleaning ─────────────────────────────────────────────

# Keep: letters (including accented), hyphens, apostrophes, spaces
_NAME_CLEAN_PATTERN = re.compile(r"[^a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s\-\']")
_MULTI_SPACE = re.compile(r"\s{2,}")


def clean_name(raw: Optional[str]) -> str:
    """Remove invalid characters from a name field and normalize whitespace."""
    if not raw or not isinstance(raw, str):
        return ""
    text = _NAME_CLEAN_PATTERN.sub("", str(raw))
    text = _MULTI_SPACE.sub(" ", text)
    return text.strip().upper()


# ── Column validators ──────────────────────────────────────────────

_CEDULA_PATTERN = re.compile(r"^\d{6,8}$")
_NACIONALIDAD_VALID = {"V", "E"}


def validate_cedula(value) -> tuple[bool, str]:
    """Validate that Cedula is a 6-8 digit number."""
    raw = str(value).strip() if value is not None else ""
    # Handle floats from Excel (e.g., 12345678.0)
    if "." in raw:
        try:
            raw = str(int(float(raw)))
        except (ValueError, OverflowError):
            return False, f"Invalid Cedula (not numeric): '{value}'"
    if not raw:
        return False, "Cedula is empty"
    if not _CEDULA_PATTERN.match(raw):
        return False, f"Invalid Cedula (must be 6-8 digits): '{raw}'"
    return True, raw


def validate_nacionalidad(value) -> tuple[bool, str]:
    """Validate that Nacionalidad is 'V' or 'E'."""
    raw = str(value).strip().upper() if value is not None else ""
    if not raw:
        return False, "Nacionalidad is empty"
    if raw not in _NACIONALIDAD_VALID:
        return False, f"Invalid Nacionalidad (must be V or E): '{raw}'"
    return True, raw


def validate_nombre(value) -> tuple[bool, str]:
    """Validate that the name is non-empty after cleaning."""
    cleaned = clean_name(value)
    if not cleaned:
        return False, f"Name is empty after cleaning: '{value}'"
    return True, cleaned


def is_row_empty(row_values: list) -> bool:
    """Check if all values in a row are None/empty."""
    return all(
        v is None or (isinstance(v, str) and not v.strip())
        for v in row_values
    )


def validate_row(row_dict: dict) -> tuple[bool, dict, list[str]]:
    """
    Validate and clean a single row.

    Returns:
        (is_valid, cleaned_dict, list_of_errors)
    """
    errors = []
    cleaned = {}

    # N° (row number) — convert Excel float to int
    n_value = row_dict.get("N°", "")
    if n_value is not None and n_value != "":
        try:
            cleaned["N°"] = str(int(float(str(n_value).strip())))
        except (ValueError, OverflowError):
            cleaned["N°"] = str(n_value).strip()
    else:
        cleaned["N°"] = ""

    # Nacionalidad
    nac_valid, nac_result = validate_nacionalidad(row_dict.get("Nacionalidad"))
    if nac_valid:
        cleaned["Nacionalidad"] = nac_result
    else:
        errors.append(nac_result)
        cleaned["Nacionalidad"] = str(row_dict.get("Nacionalidad", ""))

    # Cedula
    ced_valid, ced_result = validate_cedula(row_dict.get("Cedula"))
    if ced_valid:
        cleaned["Cedula"] = ced_result
    else:
        errors.append(ced_result)
        cleaned["Cedula"] = str(row_dict.get("Cedula", ""))

    # NOMBRE_COMPLETO
    nom_valid, nom_result = validate_nombre(row_dict.get("NOMBRE_COMPLETO"))
    if nom_valid:
        cleaned["NOMBRE_COMPLETO"] = nom_result
    else:
        errors.append(nom_result)
        cleaned["NOMBRE_COMPLETO"] = str(row_dict.get("NOMBRE_COMPLETO", ""))

    is_valid = len(errors) == 0
    return is_valid, cleaned, errors
