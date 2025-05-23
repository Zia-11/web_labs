#  вызов unicorh:  uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, EmailStr

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

# Декоратор, указывает FastAPI, что функция под ним, отвечает за обработку запросов, поступающих по адресу
# получение всех книжек


@app.get("/books", tags=["Книги"], summary="Получить все книги")
async def read_books():  # вызывается каждый раз когда поступает запрос get
    return books

# фильтрация


@app.get("/books/filter", tags=["Книги"], summary="Получение книг с фильтрацией")
async def filter_books(title: str | None = None, author: str | None = None, completed: bool | None = None):
    filtered_books = books
    if title:
        filtered_books = [
            book for book in filtered_books if title.lower() in book["title"].lower()]
    if author:
        filtered_books = [
            book for book in filtered_books if author.lower() in book["author"].lower()]
    if completed is not None:
        filtered_books = [book for book in filtered_books if book.get(
            "completed") == completed]
    return filtered_books

# получение id книжек


@app.get("/books/{book_id}", tags=["Книги"], summary="Получить конкретную книжку")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:  # если найдено - круто
            return book
    # не найдено - ошибка
    # обработка ошибок
    raise HTTPException(status_code=404, detail='Книга не найдена')

# POST запрос


class NewBook(BaseModel):  # наследуемся от BaseModel (сериализация)
    title: str
    author: str


@app.post("/books", tags=["Книги"], summary="Добавление книжки")
def create_book(new_book: NewBook):  # функция на добавление книжек
    books.append(
        {
            # возврат кастомных json данных, базовая валидация
            "id": len(books) + 1,
            "title": new_book.title,
            "author": new_book.author,
        }
    )
    # отправляем сообщение если все успешно
    return Response(
        # Возврат простого JSON-ответа через Response
        content='{"success": true, "message": "Книга добавлена"}',
        media_type="application/json"
    )

# валидация данных


# входные данные
data = {
    "email": "abc@mail.ru",
    "bio": None,
    "age": 20
}

# класс для валидации данных


class UserSchema(BaseModel):
    email: str
    bio: str | None = Field(max_lenght=1000)
    age: int = Field(ge=0, le=130)


# выводим данные пользователя
user = UserSchema(**data)
print(user)


# PUT, PATCH запросы

# описание структуры книги
class BookResponse(BaseModel):
    id: int
    title: str
    author: str


@app.put("/books/{book_id}",  tags=["Книги"], summary="Обновление всей книги")
async def update_book(book_id: int, title: str, author: str):
    for b in books:
        if b["id"] == book_id:
            b.update({"title": title, "author": author})
            return Response(
                content='{"success": true, "message": "Книга обновлена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.patch("/books/{book_id}", tags=["Книги"], summary="Частичное обновление книги")
async def partial_update_book(book_id: int, title: str | None = None, author: str | None = None):
    for b in books:
        if b["id"] == book_id:
            if title is not None:
                b["title"] = title
            if author is not None:
                b["author"] = author
            return Response(
                content='{"success": true, "message": "Книга частично обновлена", "data": }',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")

# DELETE запрос


@app.delete("/books/{book_id}", tags=["Книги"], summary="Удаление книги")
async def delete_book(book_id: int):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(i)
            return Response(
                content='{"success": true, "message": "Книга удалена"}',
                media_type="application/json"
            )
    raise HTTPException(status_code=404, detail="Книга не найдена")
