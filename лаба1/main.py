#  вызов unicorh:  uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()  # объект класса FastAPI() созданный внутри файла main

books = [
    {
        "id": 1,
        "title": "Асинхронность на Python",
        "author": "Вася",
    },
    {
        "id": 2,
        "title": "Backend разработка на Python",
        "author": "Петя",
    }
]

# GET запросы

# Декоратор, указывает FastAPI, что функция под ним, отвечает за обработку запросов, поступающих по адресу
# получение всех книжек


@app.get("/books", tags=["Книги"], summary="Получить все книги")
async def read_books():  # вызывается каждый раз когда поступает запрос get
    return books


# получение id книжек
@app.get("/books/{book_id}", tags=["Книги"], summary="Получить конкретную книжку")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:  # если найдено - круто
            return book
    # не найдено - ошибка
    raise HTTPException(status_code=404, detail='Книга не найдена')

# POST запрос


class NewBook(BaseModel):  # наследуемся от BaseModel
    title: str
    author: str


@app.post("/books", tags=["Книги"], summary="Добавление книжки")
def create_book(new_book: NewBook):  # функция на добавление книжек
    books.append(
        {
            "id": len(books) + 1,  # возврат кастомных json данных
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
