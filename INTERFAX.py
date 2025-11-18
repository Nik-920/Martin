import base64
import importlib
import io
import sys
import pandas as pd
from flask import Flask, render_template, request

# Añadir ruta de los módulos de análisis
BASE_DIR = r"/"
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

EXCEL_PATH = r"C:\db\Nik Denilson\Universidad\IntiligenciaArtificial\Proyecto\Scrip\Martin\PROVINCIAS.xlsx"

app = Flask(__name__, template_folder='static')
# Lista de provincias y mapeo a nombres de módulos
PROVINCIAS = [
    'BELLAVISTA', 'HUALLAGA', 'LAMAS', 'MARISCAL','MOYOBAMBA', 'PICOTA', 'RIOJA', 'SAN_MARTIN', 'TOCACHE'
]

TEMPLATE = "index.html"

@app.route('/')
def index():
    return render_template(TEMPLATE, provincias=PROVINCIAS, image=None, selected=None)


@app.route('/provincia')
def show_provincia():
    prov = request.args.get('prov')
    if prov not in PROVINCIAS:
        return "Provincia no válida", 400

    # 1) Generar gráfico via módulo DBSCAN
    try:
        module = importlib.import_module(f"SanMartin.{prov}")
        fig = module.main()
    except ImportError:
        return f"No se encontró el módulo para {prov}", 500
    except Exception as e:
        return f"Error al ejecutar el módulo {prov}: {e}", 500

    # Convertir figura a base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('ascii')

    # 2) Leer la hoja correspondiente desde el Excel
    try:
        hoja = prov.replace('_', ' ')
        df = pd.read_excel(EXCEL_PATH, sheet_name=hoja)
        tabla_html = df.to_html(classes='tabla-provincia', index=False)
    except Exception as e:
        tabla_html = f"<p><strong>Error al leer la tabla:</strong> {e}</p>"

    return render_template(
        TEMPLATE,
        provincias=PROVINCIAS,
        image=img_b64,
        selected=prov,
        tabla=tabla_html
    )


if __name__ == '__main__':
    app.run(debug=True)