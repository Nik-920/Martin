# Regresion/MOYOBAMBA_SEMANA.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from matplotlib.ticker import MaxNLocator


def main():
    provincia = "MOYOBAMBA"
    print(f"1) Cargando dataset para análisis semanal de {provincia}...")
    path = r"C:\db\Dataset\Infracciones.csv"

    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8")
    except:
        df = pd.read_csv(path, sep=";", encoding="latin1")

    # ==========================================
    # 2) PROCESAR
    # ==========================================
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%Y%m%d', errors='coerce')

    df['HORA_INFRACCION'] = pd.to_datetime(
        df['HORA_INFRACCION'], format='%H:%M:%S', errors='coerce'
    )

    df['HORA'] = df['HORA_INFRACCION'].dt.hour
    df['DIA_SEMANA'] = df['FECHA'].dt.dayofweek

    dias_nombre = {
        0: "Lunes", 1: "Martes", 2: "Miércoles",
        3: "Jueves", 4: "Viernes",
        5: "Sábado", 6: "Domingo"
    }

    # ==========================================
    # 3) AGRUPACIÓN
    # ==========================================
    df_group = df.groupby(
        ['PROVINCIA', 'HORA', 'DIA_SEMANA']
    ).size().reset_index(name='CANTIDAD')

    df_group['LOG'] = np.log1p(df_group['CANTIDAD'])

    # ==========================================
    # 4) MODELO GLOBAL
    # ==========================================
    le = LabelEncoder()
    df_group['PROVINCIA_ENC'] = le.fit_transform(df_group['PROVINCIA'])

    X = df_group[['HORA', 'PROVINCIA_ENC', 'DIA_SEMANA']]
    y = df_group['LOG']

    print("2) Entrenando modelo global con TODAS las provincias...")
    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(X, y)

    print("✅ Modelo entrenado")

    # ==========================================
    # ✅ 5) GRAFICO POR DÍA (7 IMÁGENES INDEPENDIENTES)
    # ==========================================
    print(f"\n🔹 Generando predicción y gráfico por día de la semana para {provincia}...")
    if provincia not in le.classes_:
        print(f"❌ Error: La provincia {provincia} no se encuentra en el dataset.")
        return {}

    cod = le.transform([provincia])[0]

    figs = {}

    for dia in range(7):
        fig, ax = plt.subplots(figsize=(8, 5))

        # Datos reales
        df_real = df_group[
            (df_group['PROVINCIA'] == provincia) &
            (df_group['DIA_SEMANA'] == dia)
        ]

        # Predicción
        horas = pd.DataFrame({
            'HORA': list(range(24)),
            'PROVINCIA_ENC': [cod]*24,
            'DIA_SEMANA': [dia]*24
        })

        pred_log = model.predict(horas)
        pred_real = np.expm1(pred_log)

        # Graficar
        ax.plot(df_real['HORA'], df_real['CANTIDAD'],
                marker='o', label='Real')

        ax.plot(horas['HORA'], pred_real,
                linestyle='--', marker='x', label='ML')

        nombre_dia = dias_nombre[dia]
        ax.set_title(f"{nombre_dia} - {provincia}", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Hora del día (0 - 23 hrs)", fontsize=11, fontweight='bold')
        ax.set_ylabel("Infracciones", fontsize=11, fontweight='bold')
        ax.set_xticks(range(24))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
        ax.grid(True)
        ax.legend(loc='upper right')

        plt.tight_layout()

        filename = f"semana_{provincia.replace(' ', '_')}_{nombre_dia}.png"
        plt.savefig(filename, dpi=300)
        print(f"✅ Gráfico guardado: {filename}")

        figs[nombre_dia] = fig

    return figs


if __name__ == "__main__":
    figs = main()
    for dia, fig in figs.items():
        plt.show()
