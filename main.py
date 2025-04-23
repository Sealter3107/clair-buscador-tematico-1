
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cargar el Excel con las columnas correctas
df = pd.read_excel("data.xlsx").fillna("")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/buscar")
async def buscar(request: Request):
    params = request.query_params
    start = int(params.get("start", 0))
    length = int(params.get("length", 25))

    filtro_titulo = params.get("search[value]", "").lower()

    resultados = []
    for _, row in df.iterrows():
        if filtro_titulo in str(row["Títulos y subtítulos"]).lower():
            resultados.append([
                row["Títulos y subtítulos"],
                row["Pág."],
                row["Obra"],
                row["Autor"],
                row["Tema"],
                f'<a href="{row["link"]}" target="_blank">Ver</a>'
            ])

    return {
        "draw": int(params.get("draw", 1)),
        "recordsTotal": len(df),
        "recordsFiltered": len(resultados),
        "data": resultados[start:start + length]
    }
