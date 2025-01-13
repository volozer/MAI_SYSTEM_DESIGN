#!/usr/bin/env python3

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates 
from routers import predict

app = FastAPI(
    title="tech_sap_prediction"
)

templates = Jinja2Templates(directory="./template")

app.include_router(predict.router)

app = FastAPI()

# Главная страница (HTML форма для ввода текста)
@app.get("/")
async def select_your_permission(request: Request):
    return templates.TemplateResponse("index.html", {"status": 200, "request": request})

if __name__ == '__main__':
    app.run(debug=True)
