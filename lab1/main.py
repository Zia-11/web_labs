#  вызов unicorh:  uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Response, Form, Security
from pydantic import BaseModel, Field
from auth import is_authenticated, is_admin_user
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token")  # схема OAuth2 для Swagger UI

app = FastAPI()  # объект класса FastAPI() созданный внутри файла main

books = [
    {
        "id": 1,
        "title": "Асинхронность на Python",
        "author": "Вася",
        "completed": True
    },
    {
        "id": 2,
        "title": "Backend разработка на Python",
        "author": "Петя",
        "completed": True
    }
]

# GET запросы

# чтение всех книг — доступно авторизованным пользователям


@app.get(
    "/books",
    tags=["Книги"],
    summary="Получить все книги",
)
async def read_books(
    # проверка токена и прав доступа
    current_user: dict = Security(is_authenticated),
):
    return books

# фильтрация — доступно авторизованным


@app.get(
    "/books/filter",
    tags=["Книги"],
    summary="Получение книг с фильтрацией",
)
async def filter_books(
    title: str | None = None,
    author: str | None = None,
    completed: bool | None = None,
    current_user: dict = Security(is_authenticated),
):
    filtered = books
    if title:
        filtered = [b for b in filtered if title.lower() in b["title"].lower()]
    if author:
        filtered = [b for b in filtered if author.lower()
                    in b["author"].lower()]
    if completed is not None:
        filtered = [b for b in filtered if b.get("completed") == completed]
    return filtered

# получение конкретной книги — доступно авторизованным


@app.get(
    "/books/{book_id}",
    tags=["Книги"],
    summary="Получить конкретную книжку",
)
async def get_book(
    book_id: int,
    current_user: dict = Security(is_authenticated),
):
    for b in books:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="Книга не найдена")

# Тестовый эндпоинт для проверки Swagger Authorize


@app.get(
    "/auth-test",
    summary="Проверка отображения поля Authorize",
)
async def auth_test(
    token: str = Security(oauth2_scheme),
):
    return {"token": token}

# POST запрос — добавление книги (только админ)


class NewBook(BaseModel):  # структура данных для создания книги
    title: str
    author: str


@app.post(
    "/books",
    tags=["Книги"],
    summary="Добавление книжки",
)
async def create_book(
    new_book: NewBook,
    current_user: dict = Security(is_admin_user),  # только админ
):
    books.append({
        "id": len(books) + 1,
        "title": new_book.title,
        "author": new_book.author,
    })
    return Response(
        content='{"success": true, "message": "Книга добавлена"}',
        media_type="application/json"
    )

# аутентификация — получение токена по login/password


@app.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        return {"access_token": "admin_token", "token_type": "bearer"}
    elif username == "user" and password == "user":
        return {"access_token": "user_token", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Неверные данные")

# валидация данных пользователя — для примера


class UserSchema(BaseModel):
    email: str
    bio: str | None = Field(max_length=1000)
    age: int = Field(ge=0, le=130)


# демонстрация работы Pydantic
user_data = {"email": "abc@mail.ru", "bio": None, "age": 20}
user = UserSchema(**user_data)
print(user)

# PUT запрос — обновление всей книги (только админ)


@app.put(
    "/books/{book_id}",
    tags=["Книги"],
    summary="Обновление всей книги",
)
async def update_book(
    book_id: int,
    title: str,
    author: str,
    current_user: dict = Security(is_admin_user),
):
    for b in books:
        if b["id"] == book_id:
            b.update({"title": title, "author": author})
            return Response(
                content='{"success": true, "message": "Книга обновлена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")

# PATCH запрос — частичное обновление книги (только админ)


@app.patch(
    "/books/{book_id}",
    tags=["Книги"],
    summary="Частичное обновление книги",
)
async def partial_update_book(
    book_id: int,
    title: str | None = None,
    author: str | None = None,
    current_user: dict = Security(is_admin_user),
):
    for b in books:
        if b["id"] == book_id:
            if title is not None:
                b["title"] = title
            if author is not None:
                b["author"] = author
            return Response(
                content='{"success": true, "message": "Книга частично обновлена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")

# DELETE запрос — удаление книги (только админ)


@app.delete(
    "/books/{book_id}",
    tags=["Книги"],
    summary="Удаление книги",
)
async def delete_book(
    book_id: int,
    current_user: dict = Security(is_admin_user),
):
    for i, b in enumerate(books):
        if b["id"] == book_id:
            books.pop(i)
            return Response(
                content='{"success": true, "message": "Книга удалена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")
