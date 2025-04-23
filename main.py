from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Cargar DataFrame global
df = pd.read_excel("data.xlsx")
df = df.fillna("")

# HTML principal
@app.get("/", response_class=HTMLResponse)
async def get_home():
    return FileResponse("static/index.html")

# Endpoint para los datos en formato JSON
@app.get("/data")
async def get_data():
    return df.to_dict(orient="records")