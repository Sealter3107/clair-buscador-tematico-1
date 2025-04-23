from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_excel("data_fixed.xlsx")

@app.get("/", response_class=FileResponse)
def home():
    return FileResponse("static/index.html")

@app.get("/buscar")
async def buscar(request: Request):
    params = request.query_params
    draw = int(params.get("draw", 1))
    start = int(params.get("start", 0))
    length = int(params.get("length", 10))
    search_value = params.get("search[value]", "")

    filtered = df
    if search_value:
        filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1)]

    data = []
    for _, row in filtered.iloc[start:start+length].iterrows():
        data.append([
            row["Título"],
            row["Subtítulo"],
            row["Autor"],
            row["Año"],
            row["Tema"],
            f'<a href="{row["link"]}" target="_blank">Ver</a>',
        ])

    return {
        "draw": draw,
        "recordsTotal": len(df),
        "recordsFiltered": len(filtered),
        "data": data
    }