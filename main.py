
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from functools import reduce
import operator
import json
from starlette.responses import Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar los datos
df = pd.read_excel("data.xlsx")
if "Pág." in df.columns:
    df["Pág."] = df["Pág."].astype("Int64")  # <- Esto convierte a enteros pero permite valores vacíos


@app.get("/", response_class=HTMLResponse)
def read_index():
    with open("index_with_ajax.html", encoding="utf-8") as f:
        return f.read()

def aplicar_filtro(columna, valores, logica):
    if not valores:
        return pd.Series([True] * len(df))
    condiciones = [df[columna].astype(str).str.contains(valor, case=False, na=False) for valor in valores]
    return reduce(operator.or_, condiciones) if logica == "OR" else reduce(operator.and_, condiciones)

@app.get("/buscar")
def buscar(request: Request):
    args = request.query_params

    draw = int(args.get("draw", 1))
    start = int(args.get("start", 0))
    length = int(args.get("length", 10))

    titulo_vals = [args.get(f"titulo{i}", "") for i in range(1, 6)]
    obra_vals   = [args.get(f"obra{i}", "") for i in range(1, 6)]
    autor_vals  = [args.get(f"autor{i}", "") for i in range(1, 6)]

    logica_titulo = args.get("logica_titulo", "AND")
    logica_obra = args.get("logica_obra", "AND")
    logica_autor = args.get("logica_autor", "AND")

    f1 = aplicar_filtro("Capítulo (tema)", [v for v in titulo_vals if v], logica_titulo)
    f2 = aplicar_filtro("Obra", [v for v in obra_vals if v], logica_obra)
    f3 = aplicar_filtro("Autor", [v for v in autor_vals if v], logica_autor)

    filtrado = df[f1 & f2 & f3].copy()

    if "Pág." in filtrado.columns and "link" in filtrado.columns:
        filtrado["Pág."] = filtrado.apply(
            lambda row: f'<a href="{row["link"]}" target="_blank">{row["Pág."]}</a>' if pd.notna(row["Pág."]) and pd.notna(row["link"]) else "",
            axis=1
        )

    filtrado = filtrado.replace([float("inf"), float("-inf")], None)
    filtrado = filtrado.fillna("")

    total = len(df)
    total_filtrado = len(filtrado)

    paginado = filtrado.iloc[start:start + length]
    data = paginado.to_dict(orient="records")

    json_data = json.dumps({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": total_filtrado,
        "data": data
    }, allow_nan=False)

    return Response(content=json_data, media_type="application/json")
