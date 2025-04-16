
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import openpyxl

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    df = pd.read_excel("data.xlsx", engine="openpyxl")
    columnas = ["Títulos y subtítulos", "Pág.", "Obra", "Autor", "Tema"]

    wb = openpyxl.load_workbook("data.xlsx")
    sheet = wb.active
    links = []
    for row in sheet.iter_rows(min_row=2):
        cell = row[1]
        valor = cell.value
        link = cell.hyperlink.target if cell.hyperlink else ""
        if link:
            links.append(f'<a href="{link}" target="_blank">{valor}</a>')
        else:
            links.append(valor)
    df["Pág."] = links

    rows_html = ""
    for _, row in df.iterrows():
        rows_html += "<tr>" + "".join(f"<td>{{row[col]}}</td>" for col in columnas) + "</tr>"

    filters_html = ""
    for col in columnas[:3]:
        filters_html += f'''
        <div class="filter-group">
            <label>{col}</label>
            <input type="text" placeholder="Filtro 1" class="filter-input" data-column="{col}">
            <input type="text" placeholder="Filtro 2" class="filter-input" data-column="{col}">
            <input type="text" placeholder="Filtro 3" class="filter-input" data-column="{col}">
            <select class="logic" data-column="{col}">
                <option value="AND">Y (AND)</option>
                <option value="OR">O (OR)</option>
            </select>
        </div>
        '''

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8' />
        <title>CLAIR Buscador Temático</title>
        <link href='https://fonts.googleapis.com/css2?family=Montserrat&display=swap' rel='stylesheet'>
        <style>
            body {{
                font-family: 'Montserrat', sans-serif;
                padding: 20px;
            }}
            .filters {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .filter-group {{
                display: flex;
                flex-direction: column;
            }}
            .filter-input {{
                margin: 2px 0;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }}
            select {{
                margin-top: 5px;
                padding: 5px;
                border-radius: 4px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th {{
                background-color: #1AB5D9;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #ccc;
            }}
            td {{
                padding: 8px;
                border: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <div class="filters">
            {filters_html}
        </div>
        <table id="data-table">
            <thead>
                <tr>
                    <th>Título</th>
                    <th>Página</th>
                    <th>Obra</th>
                    <th>Autor</th>
                    <th>Tema</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <script>
        function applyFilters() {{
            const rows = document.querySelectorAll("tbody tr");
            const inputs = document.querySelectorAll(".filter-input");
            const logicMap = {{}};

            document.querySelectorAll(".logic").forEach(select => {{
                logicMap[select.dataset.column] = select.value;
            }});

            const filterMap = {{}};
            inputs.forEach(input => {{
                const col = input.dataset.column;
                if (!filterMap[col]) filterMap[col] = [];
                if (input.value.trim() !== "") {{
                    filterMap[col].push(input.value.trim().toLowerCase());
                }}
            }});

            rows.forEach(row => {{
                let visible = true;
                for (let col in filterMap) {{
                    const logic = logicMap[col];
                    const colIndex = ["Títulos y subtítulos", "Pág.", "Obra", "Autor", "Tema"].indexOf(col);
                    const td = row.children[colIndex];
                    const text = td.innerText.toLowerCase();
                    const matches = filterMap[col].map(f => text.includes(f));
                    if (logic === "AND" && !matches.every(Boolean)) visible = false;
                    if (logic === "OR" && !matches.some(Boolean)) visible = false;
                }}
                row.style.display = visible ? "" : "none";
            }});
        }}

        document.querySelectorAll(".filter-input, .logic").forEach(el => {{
            el.addEventListener("input", applyFilters);
            el.addEventListener("change", applyFilters);
        }});
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html)
