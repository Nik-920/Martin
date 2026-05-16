import base64
import importlib
import io
import os
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request

# Añadir ruta de los módulos de análisis
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

EXCEL_PATH = os.path.join(BASE_DIR, "PROVINCIAS.xlsx")

app = Flask(__name__, template_folder='static')

# Lista de provincias y mapeo a nombres de módulos
PROVINCIAS = [
    'HUALLAGA', 'BELLAVISTA', 'PICOTA', 'TOCACHE', 'LAMAS',
    'MARISCAL', 'MOYOBAMBA', 'SAN_MARTIN', 'RIOJA'
]

TEMPLATE = "index.html"


@app.route('/', methods=['GET', 'POST'])
def index():
    """Ruta principal que maneja tanto GET como POST"""
    if request.method == 'POST':
        # Verificar si se solicitó Power BI
        if request.form.get('powerbi'):
            return render_template(
                TEMPLATE,
                provincias=PROVINCIAS,
                image=None,
                image_regresion=None,
                image_regresion_general=None,
                selected=None,
                tabla=None,
                powerbi=True
            )

        # Obtener provincia del formulario POST
        prov = request.form.get('provincia')

        if prov and prov in PROVINCIAS:
            # 1) Generar gráfico via módulo DBSCAN
            try:
                module_dbscan = importlib.import_module(f"SanMartin.{prov}")
                fig_dbscan = module_dbscan.main()
                buf = io.BytesIO()
                fig_dbscan.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                buf.seek(0)
                img_dbscan_b64 = base64.b64encode(buf.read()).decode('ascii')
            except Exception as e:
                img_dbscan_b64 = None
                print(f"Error DBSCAN {prov}: {e}")

            # 2) Generar gráfico via módulo Regresión Semanal
            try:
                module_reg = importlib.import_module(f"Regresion.{prov}_SEMANA")
                fig_reg = module_reg.main()
                buf2 = io.BytesIO()
                fig_reg.savefig(buf2, format='png', bbox_inches='tight', dpi=150)
                buf2.seek(0)
                img_reg_b64 = base64.b64encode(buf2.read()).decode('ascii')
            except Exception as e:
                img_reg_b64 = None
                print(f"Error Regresion Semana {prov}: {e}")

            # 3) Generar gráfico via módulo Regresión General (24h)
            try:
                module_reg_gen = importlib.import_module(f"Regresion.{prov}")
                fig_reg_gen = module_reg_gen.main()
                buf3 = io.BytesIO()
                fig_reg_gen.savefig(buf3, format='png', bbox_inches='tight', dpi=150)
                buf3.seek(0)
                img_reg_gen_b64 = base64.b64encode(buf3.read()).decode('ascii')
            except Exception as e:
                img_reg_gen_b64 = None
                print(f"Error Regresion General {prov}: {e}")

            # 4) Leer la hoja correspondiente desde el Excel
            try:
                hoja = prov.replace('_', ' ')
                df = pd.read_excel(EXCEL_PATH, sheet_name=hoja)
                tabla_html = df.to_html(classes='tabla-provincia', index=False)
            except Exception as e:
                tabla_html = f"<p>Error al leer la tabla: {e}</p>"

            return render_template(
                TEMPLATE,
                provincias=PROVINCIAS,
                image=img_dbscan_b64,
                image_regresion=img_reg_b64,
                image_regresion_general=img_reg_gen_b64,
                selected=prov,
                tabla=tabla_html,
                powerbi=False
            )

    # GET request o POST sin provincia válida
    return render_template(
        TEMPLATE,
        provincias=PROVINCIAS,
        image=None,
        image_regresion=None,
        image_regresion_general=None,
        selected=None,
        tabla=None,
        powerbi=False
    )


if __name__ == '__main__':
    app.run(debug=True)
