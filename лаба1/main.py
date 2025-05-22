#  вызов unicorh:  uvicorn main:app --reload

from fastapi import FastAPI

app = FastAPI() #объект класса FastAPI() созданный внутри файла main


@app.get("/items/{item_id}")  #Декоратор, указывает FastAPI, что функция под ним, отвечает за обработку запросов, поступающих по адресу
async def read_item(item_id: int): #вызывается каждый раз когда поступает запрос get
    return {"item_id": item_id}