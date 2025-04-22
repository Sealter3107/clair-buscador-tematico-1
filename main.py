
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os

app = FastAPI()

# Cargar el archivo Excel
file_path = os.path.join(os.path.dirname(__file__), "data.xlsx")
df = pd.read_excel(file_path)

# Servir archivos estáticos (como index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/buscar")
async def buscar(request: Request):
    params = request.query_params
    start = int(params.get("start", 0))
    length = int(params.get("length", 10))

    filtro_titulo = [params.get(f"filtro_titulo{i}", "") for i in range(1, 4)]
    filtro_obra = [params.get(f"filtro_obra{i}", "") for i in range(1, 4)]
    filtro_autor = [params.get(f"filtro_autor{i}", "") for i in range(1, 4)]

    def contiene_todo(valor, filtros):
        return all(f.lower() in str(valor).lower() for f in filtros if f)

    filtrado = df[
        df["Títulos y subtítulos"].apply(lambda x: contiene_todo(x, filtro_titulo))
        & df["Obra"].apply(lambda x: contiene_todo(x, filtro_obra))
        & df["Autor"].apply(lambda x: contiene_todo(x, filtro_autor))
    ]

    data = []
    for _, row in filtrado.iloc[start:start + length].iterrows():
        pag_value = str(row["Pág."])
        pagina = (
            f'<a href="{pag_value}" target="_blank">Ver</a>'
            if pag_value.startswith("http") else pag_value
        )
        data.append([
            row["Títulos y subtítulos"],
            pagina,
            row["Obra"],
            row["Autor"],
            row["Carpeta"],
            row["Etiquetas relacionadas"]
        ])

    return JSONResponse(content={
        "draw": int(params.get("draw", 1)),
        "recordsTotal": len(df),
        "recordsFiltered": len(filtrado),
        "data": data,
    })
