# Regresion/MARISCAL.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder


def main():
    # ==========================================
    # 1) CARGAR DATOS LIMPIOS
    # ==========================================
    print("1) Cargando dataset limpio global para MARISCAL CACERES...")
    path = r"C:\db\Nik_Denilson\Universidad\IntiligenciaArtificial\Martin\Data\Infracciones_clean.csv"

    df = pd.read_csv(path, sep=";", encoding="utf-8")

    # ==========================================
    # 2) PROCESAR
    # ==========================================
    # La hora en el dataset limpio viene en formato estricto HH:MM:SS
    df['HORA_INFRACCION'] = pd.to_datetime(
        df['HORA_INFRACCION'], format='%H:%M:%S', errors='coerce'
    )
    df['HORA'] = df['HORA_INFRACCION'].dt.hour

    # ==========================================
    # 3) AGRUPACIÓN GLOBAL
    # ==========================================
    df_group = df.groupby(['PROVINCIA', 'HORA']).size().reset_index(name='CANTIDAD')

    # ==========================================
    # 4) LOG
    # ==========================================
    df_group['LOG'] = np.log1p(df_group['CANTIDAD'])

    # ==========================================
    # 5) ENCODING
    # ==========================================
    le = LabelEncoder()
    df_group['PROVINCIA_ENC'] = le.fit_transform(df_group['PROVINCIA'])

    # ==========================================
    # 6) VARIABLES
    # ==========================================
    X = df_group[['HORA', 'PROVINCIA_ENC']]
    y = df_group['LOG']

    # ==========================================
    # 7) MODELO GLOBAL
    # ==========================================
    print("2) Entrenando modelo global con TODAS las provincias...")
    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(X, y)

    # ==========================================
    # 8) PREDICCIÓN Y GRÁFICO PARA MARISCAL CACERES
    # ==========================================
    prov = 'MARISCAL CACERES'
    print(f"\n[*] Generando prediccion y grafico para {prov}...")

    if prov not in le.classes_:
        print(f"[ERROR] La provincia {prov} no se encuentra en el dataset.")
        return

    cod = le.transform([prov])[0]

    horas = pd.DataFrame({
        'HORA': list(range(24)),
        'PROVINCIA_ENC': [cod]*24
    })

    pred_log = model.predict(horas)
    pred_real = np.expm1(pred_log)

    # Datos reales de la provincia
    df_real = df_group[df_group['PROVINCIA'] == prov]

    fig = plt.figure(figsize=(8, 5))

    # Real
    plt.plot(df_real['HORA'], df_real['CANTIDAD'],
             marker='o', label='Real')

    # Predicción
    plt.plot(horas['HORA'], pred_real,
             linestyle='--', marker='x', label='ML (Modelo Global)')

    plt.title(f"Modelo Global - {prov}")
    plt.xlabel("Hora")
    plt.ylabel("Infracciones")
    plt.xticks(range(24))

    plt.legend()
    plt.grid(True)

    filename = f"mejorado_{prov}.png"
    plt.savefig(filename, dpi=300)
    print(f"[OK] Grafico guardado: {filename}")
    return fig


if __name__ == "__main__":
    fig = main()
    plt.show()
