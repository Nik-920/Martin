# DbscanSanMartin/RIOJA.py

import pandas as pd
from matplotlib.figure import Figure
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


def main():
    # 1) Cargar datos
    path = r"C:\db\Dataset\Infracciones.csv"
    df = pd.read_csv(path, sep=";", encoding="latin1")

    # 2) Filtrar por provincia Rioja
    df = df[df['PROVINCIA'].str.upper().fillna('') == 'RIOJA']

    # 3) Convertir FECHA y extraer día
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%Y%m%d', errors='coerce')
    df['DIA'] = df['FECHA'].dt.day

    # 4) Convertir HORA_INFRACCION y calcular segundos desde medianoche
    df['HORA_INFRACCION'] = pd.to_datetime(
        df['HORA_INFRACCION'], format='%H:%M:%S', errors='coerce'
    )
    df['SEGUNDOS'] = (
            df['HORA_INFRACCION'].dt.hour * 3600 +
            df['HORA_INFRACCION'].dt.minute * 60 +
            df['HORA_INFRACCION'].dt.second
    )

    # 5) Eliminar registros con valores faltantes
    df = df.dropna(subset=['DIA', 'SEGUNDOS'])

    # 6) Preparar matriz y normalizar
    X = df[['SEGUNDOS', 'DIA']].values
    X_scaled = StandardScaler().fit_transform(X)

    dbscan = DBSCAN(eps=0.14, min_samples=25)
    df['CLUSTER'] = dbscan.fit_predict(X_scaled)

    # 8) Preparar figura
    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()

    # Convertir segundos a horas decimales
    df['HORAS_DECIMALES'] = df['SEGUNDOS'] / 3600
    scatter = ax.scatter(
        df['HORAS_DECIMALES'],
        df['DIA'],
        c=df['CLUSTER'],
        cmap='tab10',
        alpha=0.6
    )

    # Etiquetas y estilo
    ax.set_xlabel('Hora del día (0 - 23)')
    ax.set_ylabel('Día del mes (1 - 31)')
    ax.set_title('Agrupamiento DBSCAN por SEGUNDOS (Rioja)')
    ax.set_xticks(range(0, 24))
    ax.grid(True)

    # Barra de color
    fig.colorbar(scatter, ax=ax, label='Cluster ID')

    return fig
