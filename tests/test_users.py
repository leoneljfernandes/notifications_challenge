import pytest

# Pruebas 1a: Registro exitoso
def test_register_user_success(client):
    payload = {
        "email": "nuevo@example.com",
        "name": "Usuario Nuevo",
        "password": "SuperSecretPassword123"
    }
    response = client.post("/api/users/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo@example.com"
    assert data["name"] == "Usuario Nuevo"
    assert "password" not in data
    assert "password_hash" not in data

# Pruebas 1b: Faltantes de datos (Parametrizado para probar cada campo omitido)
@pytest.mark.parametrize("missing_field", ["email", "name", "password"])
def test_register_user_missing_fields(client, missing_field):
    payload = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123"
    }
    # Quitamos el campo que queremos probar como faltante
    payload.pop(missing_field)
    
    response = client.post("/api/users/", json=payload)
    
    # 422 es Unprocessable Entity (el error típico de Pydantic cuando falta un required)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", missing_field]
    assert response.json()["detail"][0]["type"] == "missing"

# Pruebas 1c: Datos erróneos
@pytest.mark.parametrize("bad_payload, expected_error_type, expected_field", [
    (
        {"email": "no-es-un-email", "name": "Test", "password": "123"},
        "value_error", # Pydantic v2 a veces arroja value_error para correos inválidos
        "email"
    ),
    (
        {"email": "test@example.com", "name": "Test", "password": "1"}, # Password muy corta
        "string_too_short",
        "password"
    ),
])
def test_register_user_invalid_data(client, bad_payload, expected_error_type, expected_field):
    response = client.post("/api/users/", json=bad_payload)
    
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", expected_field]
    assert response.json()["detail"][0]["type"] == expected_error_type
