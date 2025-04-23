
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

df = pd.read_excel("data.xlsx").fillna("")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/buscar")
async def buscar(request: Request):
    draw = int(request.query_params.get("draw", 1))
    start = int(request.query_params.get("start", 0))
    length = int(request.query_params.get("length", 20))

    search_value = request.query_params.get("search[value]", "").lower()

    def search_filter(row):
        return (
            search_value in row["Títulos y subtítulos"].lower()
            or search_value in row["Pág."].lower()
            or search_value in row["Autor"].lower()
        )

    filtered_df = df[df.apply(search_filter, axis=1)] if search_value else df
    total_records = len(filtered_df)

    data = []
    for _, row in filtered_df.iloc[start:start+length].iterrows():
        data.append([
            row["Títulos y subtítulos"],
            f'<a href="{row["link"]}" target="_blank">{row["Pág."]}</a>',
            row["Obra"],
            row["Autor"],
            row["Carpeta"],
            row["Etiquetas relacionadas"],
        ])

    return {
        "draw": draw,
        "recordsTotal": len(df),
        "recordsFiltered": total_records,
        "data": data,
    }
