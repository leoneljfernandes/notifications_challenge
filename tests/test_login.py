import pytest

@pytest.fixture
def registered_user(client):
    """Fixture que crea un usuario de prueba para los tests de login"""
    payload = {
        "email": "login@example.com",
        "name": "Login User",
        "password": "Password123"
    }
    client.post("/api/users/", json=payload)
    return payload

# Pruebas 2a: Login exitoso
def test_login_success(client, registered_user):
    payload = {
        "username": registered_user["email"], # OAuth2 usa 'username' por defecto en form-data
        "password": registered_user["password"]
    }
    # NOTA: OAuth2PasswordRequestForm usa data, no json
    response = client.post("/api/users/token", data=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# Pruebas 2b: Login fallido (contraseña incorrecta)
def test_login_wrong_password(client, registered_user):
    payload = {
        "username": registered_user["email"],
        "password": "WrongPassword123"
    }
    response = client.post("/api/users/token", data=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.headers["WWW-Authenticate"] == "Bearer"

# Pruebas 2c: Login fallido (usuario no registrado)
def test_login_unregistered_user(client):
    payload = {
        "username": "noexisto@example.com",
        "password": "Password123"
    }
    response = client.post("/api/users/token", data=payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

