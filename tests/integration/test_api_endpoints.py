"""
Integration tests simulating the n8n → FastAPI request flow.
Tests authentication, input validation, and batch processing.
"""
import pytest


class TestAuthentication:
    """Verify API key enforcement."""

    def test_missing_api_key_returns_403(self, client):
        response = client.post("/split_names", json=[{"NOMBRE_COMPLETO": "TEST"}])
        assert response.status_code == 403

    def test_wrong_api_key_returns_403(self, client):
        response = client.post(
            "/split_names",
            json=[{"NOMBRE_COMPLETO": "TEST"}],
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 403

    def test_correct_api_key_returns_200(self, client, auth_headers):
        response = client.post(
            "/split_names",
            json=[{"NOMBRE_COMPLETO": "JUAN PEREZ"}],
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_root_endpoint_no_auth_required(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Name Splitter API is Online"


class TestInputValidation:
    """Verify Pydantic model and constraints."""

    def test_name_too_long_returns_422(self, client, auth_headers):
        long_name = "A" * 201  # exceeds max_length=200
        response = client.post(
            "/split_names",
            json=[{"NOMBRE_COMPLETO": long_name}],
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_missing_nombre_completo_uses_default(self, client, auth_headers):
        """If NOMBRE_COMPLETO is missing, it defaults to empty string."""
        response = client.post(
            "/split_names",
            json=[{"Cedula": 12345}],
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data[0]["p_nombre"] == ""

    def test_extra_fields_are_preserved(self, client, auth_headers):
        """Passthrough fields like Cedula and Nacionalidad survive processing."""
        payload = [
            {"NOMBRE_COMPLETO": "JUAN PEREZ", "Cedula": 12345678, "Nacionalidad": "V"}
        ]
        response = client.post("/split_names", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data[0]["Cedula"] == 12345678
        assert data[0]["Nacionalidad"] == "V"
        assert data[0]["p_nombre"] == "Juan"


class TestN8nBatchSimulation:
    """Simulate the exact request n8n sends after the Aggregate node."""

    def test_batch_of_names(self, client, auth_headers):
        payload = [
            {"N°": "1", "Nacionalidad": "V", "Cedula": 12345678, "NOMBRE_COMPLETO": "CARLOS ANDRES PEREZ GOMEZ"},
            {"N°": "2", "Nacionalidad": "E", "Cedula": 87654321, "NOMBRE_COMPLETO": "MARIA DEL PILAR RUIZ"},
            {"N°": "3", "Nacionalidad": "V", "Cedula": 11111111, "NOMBRE_COMPLETO": "JOSE MARIA DE LOS ANGELES TORRES"},
        ]
        response = client.post("/split_names", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Verify batch size
        assert len(data) == 3

        # Row 1: CARLOS ANDRES PEREZ GOMEZ → 4 groups
        assert data[0]["p_nombre"] == "Carlos"
        assert data[0]["s_nombre"] == "Andres"
        assert data[0]["p_apellido"] == "Perez"
        assert data[0]["s_apellido"] == "Gomez"
        assert data[0]["Cedula"] == 12345678  # passthrough preserved

        # Row 2: MARIA DEL PILAR RUIZ → 3 groups
        assert data[1]["p_nombre"] == "Maria"
        assert data[1]["p_apellido"] == "Del Pilar"
        assert data[1]["s_apellido"] == "Ruiz"

        # Row 3: JOSE MARIA DE LOS ANGELES TORRES → 4 groups
        assert data[2]["p_nombre"] == "Jose"
        assert data[2]["s_nombre"] == "Maria"
        assert data[2]["p_apellido"] == "De Los Angeles"
        assert data[2]["s_apellido"] == "Torres"

    def test_empty_batch(self, client, auth_headers):
        response = client.post("/split_names", json=[], headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
