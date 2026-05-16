# ML_Regresion/regresion_por_dia_semana.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from matplotlib.ticker import MaxNLocator


def main():

    # ==========================================
    # 1) CARGAR DATOS
    # ==========================================
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

    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(X, y)

    print("✅ Modelo entrenado")

    # ==========================================
    # ✅ 5) GRAFICO POR DÍA (SUBPLOTS)
    # ==========================================
    provincia = "TOCACHE"  # puedes cambiar
    cod = le.transform([provincia])[0]

    fig, axes = plt.subplots(4, 2, figsize=(12, 14))
    axes = axes.flatten()

    for dia in range(7):

        ax = axes[dia]

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

        ax.set_title(dias_nombre[dia], fontsize=13, fontweight='bold', pad=12)
        ax.set_ylabel("Infracciones")
        ax.set_xticks(range(24))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
        ax.grid(True)

    # quitar último subplot vacío
    axes[-1].axis('off')

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    fig.supxlabel("Hora del día (0 - 23 hrs)", fontsize=14, fontweight='bold')
    plt.suptitle(f"Infracciones por Día - {provincia}", fontsize=16, fontweight='bold', y=0.98)

    plt.tight_layout(h_pad=4.0, w_pad=2.0, rect=[0, 0.05, 1, 0.95])
    plt.show()


if __name__ == "__main__":
    main()