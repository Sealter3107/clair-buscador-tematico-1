
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd
from math import ceil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_excel("data.xlsx")
df.fillna("", inplace=True)

@app.get("/buscar")
def buscar(
    start: int = 0,
    length: int = 25,
    filtro_titulo: str = "",
    logica_titulo: str = "AND",
    filtro_obra: str = "",
    logica_obra: str = "AND",
    filtro_autor: str = "",
    logica_autor: str = "AND",
):
    def filtrar(columna, texto, logica):
        palabras = texto.lower().split()
        if not palabras:
            return pd.Series([True] * len(df))
        if logica == "OR":
            return df[columna].str.lower().apply(lambda x: any(p in x for p in palabras))
        else:
            return df[columna].str.lower().apply(lambda x: all(p in x for p in palabras))

    mask = (
        filtrar("Título", filtro_titulo, logica_titulo)
        & filtrar("Obra", filtro_obra, logica_obra)
        & filtrar("Autor", filtro_autor, logica_autor)
    )
    filtrado = df[mask]
    total = len(filtrado)

    datos = []
    for _, row in filtrado.iloc[start:start+length].iterrows():
        pagina = row["Página"]
        if pd.notna(pagina) and "http" in str(pagina):
            enlace = f'<a href="{pagina}" target="_blank">{row["Pág"]}</a>'
        else:
            enlace = row["Pág"]
        datos.append([
            row["Título"],
            row["Obra"],
            row["Autor"],
            row["Tema"],
            row["Etiqueta"],
            enlace
        ])

    return {
        "data": datos,
        "recordsTotal": total,
        "recordsFiltered": total
    }

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()
