
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

df = pd.read_excel("data.xlsx").fillna("")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/buscar")
async def buscar(
    start: int = 0,
    length: int = 25,
    filtro_titulo1: str = "",
    filtro_titulo2: str = "",
    filtro_titulo3: str = "",
    filtro_obra1: str = "",
    filtro_obra2: str = "",
    filtro_obra3: str = "",
    filtro_autor1: str = "",
    filtro_autor2: str = "",
    filtro_autor3: str = "",
    logica_titulo: str = "AND",
    logica_obra: str = "AND",
    logica_autor: str = "AND"
):
    def aplicar_filtros(columnas, filtros, logica):
        condiciones = []
        for columna in columnas:
            for f in filtros:
                if f:
                    condiciones.append(df[columna].str.contains(f, case=False, na=False))
        if condiciones:
            if logica == "AND":
                return pd.concat(condiciones, axis=1).all(axis=1)
            else:
                return pd.concat(condiciones, axis=1).any(axis=1)
        else:
            return pd.Series([True] * len(df))

    condiciones_titulo = aplicar_filtros(["Título"], [filtro_titulo1, filtro_titulo2, filtro_titulo3], logica_titulo)
    condiciones_obra = aplicar_filtros(["Obra"], [filtro_obra1, filtro_obra2, filtro_obra3], logica_obra)
    condiciones_autor = aplicar_filtros(["Autor"], [filtro_autor1, filtro_autor2, filtro_autor3], logica_autor)

    resultado = df[condiciones_titulo & condiciones_obra & condiciones_autor]

    datos = []
    for _, row in resultado.iloc[start:start+length].iterrows():
        pag_value = str(row["Pág"])
        link = f'<a href="{pag_value}" target="_blank">{pag_value}</a>' if pag_value.startswith("http") else pag_value
        datos.append([
            row["Título"],
            row["Obra"],
            row["Autor"],
            row["Tema"],
            row["Etiqueta relacionada"],
            link
        ])

    return JSONResponse({
        "recordsTotal": len(df),
        "recordsFiltered": len(resultado),
        "data": datos
    })
