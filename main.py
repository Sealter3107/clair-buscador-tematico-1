
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# CORS para permitir peticiones desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_excel("data.xlsx")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/buscar")
async def buscar(request: Request):
    draw = int(request.query_params.get("draw", "1"))
    start = int(request.query_params.get("start", "0"))
    length = int(request.query_params.get("length", "10"))
    search_value = request.query_params.get("search[value]", "")

    filtered_df = df.copy()

    if search_value:
        filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1)]

    total_count = len(df)
    filtered_count = len(filtered_df)

    data = []
    for _, row in filtered_df.iloc[start:start+length].iterrows():
        data.append([
            row["Títulos y subtítulos"],
            row["Autor"],
            row["Tema"],
            row["Editorial"],
            f'<a href="{row["Pág."]}" target="_blank">Ver</a>'
        ])

    return JSONResponse({
        "draw": draw,
        "recordsTotal": total_count,
        "recordsFiltered": filtered_count,
        "data": data
    })
