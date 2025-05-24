import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app


# функция чтобы тестировать приложение без запуска сервера
@pytest_asyncio.fixture
async def client():
    # настраиваем транспорт с нашим приложением
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac  # возвращаем клиент в тестовые функции

# функция для авторизации админа


@pytest_asyncio.fixture
async def admin_auth_headers(client):
    # логинимся под админом
    res = await client.post("/token", data={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    token = res.json()["access_token"]  # извлекаем токен
    # вставляем токен в окно авторизации
    return {"Authorization": f"Bearer {token}"}

# фунция для авторизации пользователя


@pytest_asyncio.fixture
async def user_auth_headers(client):
    res = await client.post("/token", data={"username": "user", "password": "user"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# наши тесты

# попытка получить книги без авторизации


@pytest.mark.asyncio
async def test_read_books_unauthenticated(client):
    res = await client.get("/books")
    assert res.status_code == 403

# получение книг с авторизацией обычного пользователя


@pytest.mark.asyncio
async def test_read_books_authenticated(client, user_auth_headers):
    res = await client.get("/books", headers=user_auth_headers)
    assert res.status_code == 200
    books = res.json()
    assert isinstance(books, list)
    assert len(books) >= 1
    assert all(
        "id" in b and "title" in b and "author" in b
        for b in books
    )

# получение книги по  конкретному айдишнику


@pytest.mark.asyncio
async def test_get_book_detail(client, user_auth_headers):
    res = await client.get("/books/1", headers=user_auth_headers)
    assert res.status_code == 200
    book = res.json()
    assert book["id"] == 1
    assert "title" in book and "author" in book

# запрашиваем книгу которой нет в базе


@pytest.mark.asyncio
async def test_get_book_not_found(client, user_auth_headers):
    res = await client.get("/books/9999", headers=user_auth_headers)
    assert res.status_code == 404

# фильтруем книги по слову Python


@pytest.mark.asyncio
async def test_filter_books(client, user_auth_headers):
    params = {"title": "Python"}
    res = await client.get("/books/filter", params=params, headers=user_auth_headers)
    assert res.status_code == 200
    books = res.json()
    assert all(
        "python" in b["title"].lower()
        for b in books
    )

# создание книги от лица обычного пользователя


@pytest.mark.asyncio
async def test_create_book_unauthorized(client, user_auth_headers):
    payload = {"title": "Unauthorized", "author": "User"}
    res = await client.post("/books", json=payload, headers=user_auth_headers
                            )
    assert res.status_code == 403

# создание книги от лица админа


@pytest.mark.asyncio
async def test_create_book_as_admin(client, admin_auth_headers):
    payload = {"title": "New Book", "author": "New Author"}
    res = await client.post("/books", json=payload, headers=admin_auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body.get("success") is True
    assert "message" in body

# создаем книгу с неполным заполнением полей


@pytest.mark.asyncio
async def test_create_book_validation_error(client, admin_auth_headers):
    res = await client.post("/books", json={"title": "NoAuthor"}, headers=admin_auth_headers)
    assert res.status_code == 422

# попытка обновить книгу от имени обычного пользователя


@pytest.mark.asyncio
async def test_update_book_unauthorized(client, user_auth_headers):
    res = await client.put("/books/1", params={"title": "X", "author": "Y"}, headers=user_auth_headers)
    assert res.status_code == 403

# проверка обновления данных книги


@pytest.mark.asyncio
async def test_update_book_as_admin(client, admin_auth_headers):
    # создаем книгу от имени админа
    payload = {"title": "Temp", "author": "Author"}
    await client.post("/books", json=payload, headers=admin_auth_headers)
    # получаем список книг и находим созданную
    res_list = await client.get("/books", headers=admin_auth_headers)
    new_book = next(
        b for b in res_list.json()
        if b["title"] == "Temp" and b["author"] == "Author"
    )
    book_id = new_book["id"]
    # put запрос
    update_params = {"title": "Updated Title", "author": "Updated Author"}
    res = await client.put(
        f"/books/{book_id}",
        params=update_params,
        headers=admin_auth_headers
    )
    assert res.status_code == 200
    body = res.json()
    assert body.get("success") is True
    # проверка что данные действительно обновились
    res2 = await client.get(f"/books/{book_id}", headers=admin_auth_headers)
    b2 = res2.json()
    assert b2["title"] == "Updated Title"
    assert b2["author"] == "Updated Author"

#  проверка обновления книги которой нет


@pytest.mark.asyncio
async def test_update_book_not_found(client, admin_auth_headers):
    res = await client.put("/books/9999", params={"title": "X", "author": "Y"}, headers=admin_auth_headers)
    assert res.status_code == 404

# частичное обновление книги


@pytest.mark.asyncio
async def test_partial_update_book_as_admin(client, admin_auth_headers):
    # cоздаём новую книгу
    payload = {"title": "PatchMe", "author": "Author"}
    await client.post("/books", json=payload, headers=admin_auth_headers)
    # находим её айдишник
    res_list = await client.get("/books", headers=admin_auth_headers)
    book = next(b for b in res_list.json() if b["title"] == "PatchMe")
    book_id = book["id"]
    # patch запрос для тайтла
    res = await client.patch(
        f"/books/{book_id}",
        params={"title": "PatchDone"},
        headers=admin_auth_headers
    )
    assert res.status_code == 200
    body = res.json()
    assert body.get("success") is True
    # проверяем что тайтл обновился
    res2 = await client.get(f"/books/{book_id}", headers=admin_auth_headers)
    b2 = res2.json()
    assert b2["title"] == "PatchDone"

# частичное обновление книги которой нет


@pytest.mark.asyncio
async def test_partial_update_book_not_found(client, admin_auth_headers):
    res = await client.patch("/books/9999", params={"title": "Nope"}, headers=admin_auth_headers)
    assert res.status_code == 404

# удаление книги от имени пользователя


@pytest.mark.asyncio
async def test_delete_book_forbidden(client, user_auth_headers):
    res = await client.delete("/books/1", headers=user_auth_headers)
    assert res.status_code == 403

# удаление книги от имени админа


@pytest.mark.asyncio
async def test_delete_book_as_admin(client, admin_auth_headers):
    # создаём книгу для удаления
    payload = {"title": "DeleteMe", "author": "Author"}
    await client.post("/books", json=payload, headers=admin_auth_headers)
    # находим её айдишник
    res_list = await client.get("/books", headers=admin_auth_headers)
    book = next(b for b in res_list.json() if b["title"] == "DeleteMe")
    book_id = book["id"]
    # удаляем книгу
    res = await client.delete(f"/books/{book_id}", headers=admin_auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body.get("success") is True
    # проверяем, что книга удалена
    res2 = await client.get(f"/books/{book_id}", headers=admin_auth_headers)
    assert res2.status_code == 404
