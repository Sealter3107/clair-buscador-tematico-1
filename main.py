
import os
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Verificar existencia del archivo
file_path = "data_fixed.xlsx"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Archivo no encontrado: {file_path} en {os.getcwd()}")

df = pd.read_excel(file_path)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/buscar")
async def buscar():
    resultados = []
    for _, row in df.iterrows():
        resultados.append([
            row["Títulos y subtítulos"],
            row["Obra"],
            row["Autor"],
            f'<a href="{row["Pág."]}" target="_blank">{row["Pág."]}</a>'
        ])
    return JSONResponse(content={"data": resultados})
