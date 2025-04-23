
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from typing import List
import uvicorn

app = FastAPI()
df = pd.read_excel("data_fixed.xlsx")

@app.get("/", response_class=HTMLResponse)
def read_index():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/buscar")
def buscar(request: Request):
    args = request.query_params
    filtro = df.copy()

    def aplicar_filtro(col, claves: List[str], cond):
        claves = [k for k in claves if k.strip()]
        if not claves or col not in df.columns:
            return filtro
        if cond == "AND":
            for k in claves:
                filtro = filtro[filtro[col].str.contains(k, case=False, na=False)]
        else:
            filtro = filtro[filtro[col].str.contains("|".join(claves), case=False, na=False)]
        return filtro

    filtro = aplicar_filtro("Título", args.getlist("titulo"), args.get("tituloCond", "AND"))
    filtro = aplicar_filtro("Obra", args.getlist("obra"), args.get("obraCond", "AND"))
    filtro = aplicar_filtro("Autor", args.getlist("autor"), args.get("autorCond", "AND"))

    resultado = []
    for _, row in filtro.iterrows():
        resultado.append({
            "Título": row["Título"],
            "Obra": row["Obra"],
            "Autor": row["Autor"],
            "Editorial": row["Editorial"],
            "Pág.": f'<a href="{row["Pág."]}" target="_blank">Ver</a>' if pd.notna(row["Pág."]) else "",
            "Tema": row["Tema"]
        })
    return resultado
