from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

df = pd.read_excel("data_fixed.xlsx")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/buscar")
async def buscar(request: Request):
    params = dict(request.query_params)
    terms_titulo = [params.get("titulo1", ""), params.get("titulo2", ""), params.get("titulo3", "")]
    terms_obra = [params.get("obra1", ""), params.get("obra2", ""), params.get("obra3", "")]
    terms_autor = [params.get("autor1", ""), params.get("autor2", ""), params.get("autor3", "")]
    modo_titulo = params.get("modoTitulo", "or")
    modo_obra = params.get("modoObra", "or")
    modo_autor = params.get("modoAutor", "or")

    def matches(cell_value, terms, mode):
        if mode == "and":
            return all(term.lower() in str(cell_value).lower() for term in terms if term)
        else:
            return any(term.lower() in str(cell_value).lower() for term in terms if term)

    resultados = []
    for _, row in df.iterrows():
        if not (matches(row["Títulos y subtítulos"], terms_titulo, modo_titulo) and
                matches(row["Obra"], terms_obra, modo_obra) and
                matches(row["Autor"], terms_autor, modo_autor)):
            continue
        resultados.append([
            row["Títulos y subtítulos"],
            row["Obra"],
            row["Autor"],
            f'<a href="{row["Pág."]}" target="_blank">{row["Pág."]}</a>'
        ])
    return JSONResponse({"data": resultados})
