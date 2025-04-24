
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar los datos
df = pd.read_excel("data.xlsx")

@app.get("/", response_class=HTMLResponse)
def read_index():
    with open("index_with_ajax.html", encoding="utf-8") as f:
        return f.read()

def aplicar_filtro(columna, valores, logica):
    if not valores:
        return pd.Series([True] * len(df))
    condiciones = [df[columna].astype(str).str.contains(valor, case=False, na=False) for valor in valores]
    if logica == "OR":
        return condiciones[0] if len(condiciones) == 1 else condiciones[0] | condiciones[1] | condiciones[2]
    else:
        return condiciones[0] & condiciones[1] & condiciones[2] if len(condiciones) > 2 else condiciones[0] & condiciones[1] if len(condiciones) > 1 else condiciones[0]

@app.get("/buscar")
def buscar(request: Request):
    args = request.query_params

    draw = int(args.get("draw", 1))
    start = int(args.get("start", 0))
    length = int(args.get("length", 10))

    titulo_vals = [args.get("titulo1", ""), args.get("titulo2", ""), args.get("titulo3", "")]
    obra_vals = [args.get("obra1", ""), args.get("obra2", ""), args.get("obra3", "")]
    autor_vals = [args.get("autor1", ""), args.get("autor2", ""), args.get("autor3", "")]

    logica_titulo = args.get("logica_titulo", "AND")
    logica_obra = args.get("logica_obra", "AND")
    logica_autor = args.get("logica_autor", "AND")

    f1 = aplicar_filtro("Títulos y subtítulos", [v for v in titulo_vals if v], logica_titulo)
    f2 = aplicar_filtro("Obra", [v for v in obra_vals if v], logica_obra)
    f3 = aplicar_filtro("Autor", [v for v in autor_vals if v], logica_autor)

    filtrado = df[f1 & f2 & f3].copy()

    if "Pág." in filtrado.columns:
        filtrado["Pág."] = filtrado["Pág."].apply(lambda x: f'<a href="{x}" target="_blank">Ver</a>' if pd.notna(x) else "")

    # 🔧 Limpiar datos problemáticos para JSON
    filtrado = filtrado.replace([float("inf"), float("-inf")], None)
    filtrado = filtrado.fillna("")

    total = len(df)
    total_filtrado = len(filtrado)

    paginado = filtrado.iloc[start:start + length]
    data = paginado.to_dict(orient="records")

    return JSONResponse(content={
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": total_filtrado,
        "data": data
    }, dumps_kwargs={"allow_nan": False})
