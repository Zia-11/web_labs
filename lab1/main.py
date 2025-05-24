#  вызов unicorh:  uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Response, Form, Security
from pydantic import BaseModel, Field
from auth import is_authenticated, is_admin_user
from fastapi.security import OAuth2PasswordBearer

# OAuth2PasswordBearer - схема для отображения поля для введения токена в сваггере
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# экземпляр приложения fastapi
app = FastAPI()

# наша бд
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

# get запрос на получение всех книжек


@app.get("/books", tags=["Книги"], summary="Получить все книги")
async def read_books(
    # только авторизованные
    current_user: dict = Security(is_authenticated),
):
    return books

# get запрос на получение книжек с фильтрацией


@app.get("/books/filter", tags=["Книги"], summary="Получение книг с фильтрацией")
async def filter_books(
    title: str | None = None,
    author: str | None = None,
    completed: bool | None = None,
    current_user: dict = Security(is_authenticated),
):
    # применяем фильтры
    filtered = books
    if title:
        filtered = [b for b in filtered if title.lower() in b["title"].lower()]
    if author:
        filtered = [b for b in filtered if author.lower()
                    in b["author"].lower()]
    if completed is not None:
        filtered = [b for b in filtered if b.get("completed") == completed]
    return filtered

# get запрос на получение конкретной книжки


@app.get("/books/{book_id}", tags=["Книги"], summary="Получить конкретную книжку")
async def get_book(
    book_id: int,
    current_user: dict = Security(is_authenticated),
):
    # ищем книжку по айдишнику
    for b in books:
        if b["id"] == book_id:
            return b
    # если нету - ошибка
    raise HTTPException(status_code=404, detail="Книга не найдена")

# модель для валидации данных при создании книжки


class NewBook(BaseModel):
    title: str
    author: str

# post запрос для добавления книжки


@app.post("/books", tags=["Книги"], summary="Добавление книжки",)
async def create_book(
    new_book: NewBook,
    # только для админа
    current_user: dict = Security(is_admin_user),
):
    # добавляем новую книжку
    books.append({
        "id": len(books) + 1,
        "title": new_book.title,
        "author": new_book.author,
    })
    # простой JSON ответ
    return Response(
        content='{"success": true, "message": "Книга добавлена"}',
        media_type="application/json"
    )


# post запрос для получения токена
@app.post("/token", tags=["Авторизация"], summary="Получение токена")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    # проверка учётных данных
    if username == "admin" and password == "admin":
        return {"access_token": "admin_token", "token_type": "bearer"}
    elif username == "user" and password == "user":
        return {"access_token": "user_token", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Неверные данные")

# put запрос для обновления всей книжки


@app.put("/books/{book_id}", tags=["Книги"], summary="Обновление всей книги")
async def update_book(
    book_id: int,
    title: str,
    author: str,
    current_user: dict = Security(is_admin_user),
):
    # обновляем все поля сразу
    for b in books:
        if b["id"] == book_id:
            b.update({"title": title, "author": author})
            return Response(
                content='{"success": true, "message": "Книга обновлена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")

# patch запрос на частичное обновление книжки


@app.patch("/books/{book_id}", tags=["Книги"], summary="Частичное обновление книги")
async def partial_update_book(
    book_id: int,
    title: str | None = None,
    author: str | None = None,
    current_user: dict = Security(is_admin_user),
):
    for b in books:
        if b["id"] == book_id:
            # обновляем только те поля которые переданы
            if title is not None:
                b["title"] = title
            if author is not None:
                b["author"] = author
            return Response(
                content='{"success": true, "message": "Книга частично обновлена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")


# delete запрос
@app.delete("/books/{book_id}", tags=["Книги"], summary="Удаление книги")
async def delete_book(
    book_id: int,
    current_user: dict = Security(is_admin_user),
):
    # удаляем книжку по индексу
    for i, b in enumerate(books):
        if b["id"] == book_id:
            books.pop(i)
            return Response(
                content='{"success": true, "message": "Книга удалена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")

# пример валидации


class UserSchema(BaseModel):
    email: str
    bio: str | None = Field(max_length=1000)
    age: int = Field(ge=0, le=130)


user_data = {"email": "abc@mail.ru", "bio": None, "age": 20}
user = UserSchema(**user_data)
print(user)
