
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_excel("data.xlsx")

@app.get("/")
def root():
    return FileResponse("index.html")

@app.get("/buscar")
def buscar(request: Request):
    params = request.query_params
    draw = int(params.get("draw", 1))
    start = int(params.get("start", 0))
    length = int(params.get("length", 10))

    filtered_df = df.copy()

    data = []
    for index, row in filtered_df.iloc[start:start+length].iterrows():
        data.append([
            row["Títulos y subtítulos"],
            f'<a href="{row["link"]}" target="_blank">{row["Pág."]}</a>',
            row["Obra"],
            row["Autor"],
            row["Carpeta"],
            row["Tema"],
        ])

    return JSONResponse({
        "draw": draw,
        "recordsTotal": len(df),
        "recordsFiltered": len(filtered_df),
        "data": data
    })
