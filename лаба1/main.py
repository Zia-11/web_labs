#  вызов unicorh:  uvicorn main:app --reload

from fastapi import FastAPI, HTTPException

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

# Декоратор, указывает FastAPI, что функция под ним, отвечает за обработку запросов, поступающих по адресу


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
