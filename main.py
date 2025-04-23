
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_excel("data_fixed.xlsx")

def aplicar_filtro(columna, valores, condicion):
    filtro = pd.Series([True] * len(df))  # por defecto no filtra nada
    if valores:
        if condicion == "OR":
            filtro = df[columna].apply(lambda x: any(v.lower() in str(x).lower() for v in valores))
        else:
            for v in valores:
                filtro &= df[columna].apply(lambda x: v.lower() in str(x).lower())
    return filtro

@app.get("/", response_class=HTMLResponse)
def read_index():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/buscar")
def buscar(request: Request):
    args = request.query_params
    start = int(args.get("start", 0))
    length = int(args.get("length", 10))

    filtro_titulo = aplicar_filtro("Títulos y subtítulos", args.getlist("titulo"), args.get("tituloCond", "AND"))
    filtro_obra = aplicar_filtro("Obra", args.getlist("obra"), args.get("obraCond", "AND"))
    filtro_autor = aplicar_filtro("Autor", args.getlist("autor"), args.get("autorCond", "AND"))

    df_filtrado = df[filtro_titulo & filtro_obra & filtro_autor]

    data = []
    for _, row in df_filtrado.iloc[start:start + length].iterrows():
        data.append([
            row["Títulos y subtítulos"],
            row["Obra"],
            row["Autor"],
            row["Pág."]
        ])

    return {
        "data": data,
        "recordsTotal": len(df),
        "recordsFiltered": len(df_filtrado),
        "draw": int(args.get("draw", 1))
    }
