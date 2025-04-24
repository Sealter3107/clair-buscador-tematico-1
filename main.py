
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_excel("data.xlsx")

@app.get("/", response_class=HTMLResponse)
def read_index():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

def aplicar_filtro(columna, valores, logica):
    if not valores:
        return pd.Series([True] * len(df))
    condiciones = [df[columna].str.contains(v, case=False, na=False) for v in valores]
    return condiciones[0] if len(condiciones) == 1 else (
        condiciones[0] & condiciones[1] if logica == "AND" else condiciones[0] | condiciones[1]
    )

@app.get("/buscar")
def buscar(request: Request):
    args = request.query_params

    filtro_titulo = aplicar_filtro("Títulos y subtítulos", args.getlist("titulo"), args.get("logica_titulo", "AND"))
    filtro_obra = aplicar_filtro("Obra", args.getlist("obra"), args.get("logica_obra", "AND"))
    filtro_autor = aplicar_filtro("Autor", args.getlist("autor"), args.get("logica_autor", "AND"))

    resultados = df[filtro_titulo & filtro_obra & filtro_autor]
    start = int(args.get("start", 0))
    length = int(args.get("length", 10))
    page = resultados.iloc[start:start+length]

    data = []
    for _, row in page.iterrows():
        data.append({
            "Títulos y subtítulos": row["Títulos y subtítulos"],
            "Obra": row["Obra"],
            "Autor": row["Autor"],
            "Editorial": row.get("Editorial", ""),
            "Pág.": f'<a href="{row["Pág."]}" target="_blank">Ver</a>' if pd.notna(row["Pág."]) else ""
        })

    return {
        "data": data,
        "recordsTotal": len(df),
        "recordsFiltered": len(resultados)
    }
