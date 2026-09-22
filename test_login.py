import asyncio
from app.api.users import login_for_access_token
from fastapi.security import OAuth2PasswordRequestForm

async def test():
    class DummyDB:
        pass
    class DummyForm:
        username = "prueba2@example.com"
        password = "Prueba1234"
        scopes = []
        client_id = None
        client_secret = None
    form = DummyForm()
    # We can't easily mock DB here without real setup. Let's trace it differently.
