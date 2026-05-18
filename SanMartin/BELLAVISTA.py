# DbscanSanMartin/BELLAVISTA.py
import pandas as pd
from matplotlib.figure import Figure
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def main():
    # 1) Cargar datos limpios (Infracciones_clean.csv con codificacion utf-8)
    path = r"C:\db\Nik_Denilson\Universidad\IntiligenciaArtificial\Martin\Data\Infracciones_clean.csv"
    df = pd.read_csv(path, sep=";", encoding="utf-8")

    # 2) Filtrar por provincia Bellavista (ya estandarizada en mayusculas en el dataset limpio)
    df = df[df['PROVINCIA'] == 'BELLAVISTA']

    # 3) Preprocesar fecha (nuevo formato YYYY/MM/DD) y extraer dia
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%Y/%m/%d', errors='coerce')
    df['DIA'] = df['FECHA'].dt.day

    # 4) Preprocesar hora (formato HH:MM:SS) y calcular segundos
    df['HORA_INFRACCION'] = pd.to_datetime(
        df['HORA_INFRACCION'], format='%H:%M:%S', errors='coerce'
    )
    df['SEGUNDOS'] = (
            df['HORA_INFRACCION'].dt.hour * 3600 +
            df['HORA_INFRACCION'].dt.minute * 60 +
            df['HORA_INFRACCION'].dt.second
    )

    # 5) Eliminar nulos
    df = df.dropna(subset=['DIA', 'SEGUNDOS'])

    # 6) Preparar matriz para DBSCAN
    X = df[['SEGUNDOS', 'DIA']].values
    X_scaled = StandardScaler().fit_transform(X)

    # 7) Ejecutar DBSCAN
    dbscan = DBSCAN(eps=0.5, min_samples=7)
    df['CLUSTER'] = dbscan.fit_predict(X_scaled)

    # 8) Preparar figura
    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()

    # Convertir segundos a horas decimales para graficar
    horas = df['SEGUNDOS'] / 3600
    scatter = ax.scatter(horas, df['DIA'], c=df['CLUSTER'], cmap='tab10', alpha=0.6)

    # Etiquetas y estilo
    ax.set_xlabel('Hora del día (0 – 23)')
    ax.set_ylabel('Día del mes (1 – 31)')
    ax.set_title('Agrupamiento DBSCAN por SEGUNDOS — Bellavista')
    ax.set_xticks(range(0, 24))
    ax.grid(True)

    # Barra de color
    fig.colorbar(scatter, ax=ax, label='Cluster ID')

    return fig
