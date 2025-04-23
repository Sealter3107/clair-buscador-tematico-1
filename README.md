# CLAIR Buscador Temático

Este proyecto sirve una tabla filtrable basada en un archivo Excel con más de 160,000 entradas. Utiliza FastAPI para el backend y HTML+JS con DataTables para la vista.

## Cómo ejecutar localmente

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Luego abre tu navegador en http://127.0.0.1:8000
