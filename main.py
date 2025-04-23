
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Leer el Excel
df = pd.read_excel("data.xlsx")
df = df.fillna("")

@app.get("/buscar")
def buscar(
    titulo: List[str] = Query([]),
    logica_titulo: str = Query("AND"),
    obra: List[str] = Query([]),
    logica_obra: str = Query("AND"),
    autor: List[str] = Query([]),
    logica_autor: str = Query("AND"),
    start: int = Query(0),
    length: int = Query(25)
):
    def aplicar_filtros(valor: str, filtros: List[str], logica: str) -> bool:
        if not filtros:
            return True
        valor = valor.lower()
        checks = [f.lower() in valor for f in filtros]
        return all(checks) if logica == "AND" else any(checks)

    resultados = []
    for _, row in df.iterrows():
        if (
            aplicar_filtros(str(row["Títulos y subtítulos"]), titulo, logica_titulo)
            and aplicar_filtros(str(row["Obra"]), obra, logica_obra)
            and aplicar_filtros(str(row["Autor"]), autor, logica_autor)
        ):
            resultados.append(dict(row))

    total = len(resultados)
    paginados = resultados[start:start + length]

    return {
        "total": total,
        "data": paginados
    }
