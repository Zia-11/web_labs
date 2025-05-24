import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app


@pytest_asyncio.fixture
async def client():
    # используем ASGITransport и тестовый базовый URL
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_read_books_unauthenticated(client):
    # без токена — теперь HTTPBearer отдаёт 403, а не 401
    response = await client.get("/books")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_read_books_authenticated(client):
    # логинимся как обычный пользователь
    token_res = await client.post("/token", data={"username": "user", "password": "user"})
    assert token_res.status_code == 200
    token = token_res.json()["access_token"]

    # с токеном — получаем 200
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.get("/books", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_delete_book_forbidden(client):
    # обычный user не может удалять — 403
    token_res = await client.post("/token", data={"username": "user", "password": "user"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.delete("/books/1", headers=headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_delete_book_as_admin(client):
    # админ успешно удаляет — 200 + проверяем тело
    token_res = await client.post("/token", data={"username": "admin", "password": "admin"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.delete("/books/2", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body.get("success") is True
    assert "message" in body
