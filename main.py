
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (por si abres desde otros dominios, como Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

df = pd.read_excel("data_fixed.xlsx")
df = df.fillna("")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/buscar")
async def buscar():
    data = []
    for _, row in df.iterrows():
        data.append([
            row["Títulos y subtítulos"],
            f'<a href="{row["link"]}" target="_blank">{row["Pág."]}</a>',
            row["Obra"],
            row["Autor"]
        ])
    return {"data": data}
