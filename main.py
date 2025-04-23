from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Cargar el archivo Excel
data_file = "data.xlsx"
df = pd.read_excel(data_file)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/buscar")
async def buscar(request: Request):
    params = await request.query_params
    start = int(params.get("start", 0))
    length = int(params.get("length", 25))
    search_value = params.get("search[value]", "").lower()

    filtrado = df
    if search_value:
        filtrado = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(search_value).any(), axis=1)]

    data = []
    for _, row in filtrado.iloc[start:start+length].iterrows():
        data.append([
            row["Títulos y subtítulos"],
            row["Pág."],
            row["Obra"],
            row["Autor"],
            row["Carpeta"],
            f'<a href="{row["link"]}" target="_blank">Ver</a>'
        ])

    return JSONResponse({
        "draw": int(params.get("draw", 1)),
        "recordsTotal": len(df),
        "recordsFiltered": len(filtrado),
        "data": data
    })