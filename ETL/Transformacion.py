# EDA_Infracciones/eda_infracciones_validado.py

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def main():

    # ==========================================
    # 1) CARGAR DATOS (🔧 FIX ENCODING)
    # ==========================================
    print("1) Cargando dataset...")
    path = r"C:\db\Dataset\Infracciones.csv"

    # 👉 Prueba UTF-8 primero (mejor)
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8")
    except:
        df = pd.read_csv(path, sep=";", encoding="latin1")

    print("\n📌 Dimensiones:", df.shape)

    # ==========================================
    # 2) VALIDACIÓN DE FECHA
    # ==========================================
    print("\n2) Validando FECHA...")

    df['FECHA_ORIGINAL'] = df['FECHA']

    df['FECHA'] = pd.to_datetime(
        df['FECHA'], format='%Y%m%d', errors='coerce'
    )

    fechas_invalidas = df['FECHA'].isnull().sum()
    print(f"❌ Fechas inválidas: {fechas_invalidas}")

    if fechas_invalidas > 0:
        print(df[df['FECHA'].isnull()][['FECHA_ORIGINAL']].head())

    df['DIA'] = df['FECHA'].dt.day
    df['MES'] = df['FECHA'].dt.month
    df['AÑO'] = df['FECHA'].dt.year

    # ==========================================
    # 3) VALIDACIÓN DE HORA
    # ==========================================
    print("\n3) Validando HORA...")

    df['HORA_ORIGINAL'] = df['HORA_INFRACCION']

    df['HORA_INFRACCION'] = pd.to_datetime(
        df['HORA_INFRACCION'],
        format='%H:%M:%S',
        errors='coerce'
    )

    horas_invalidas = df['HORA_INFRACCION'].isnull().sum()
    print(f"❌ Horas inválidas: {horas_invalidas}")

    df['HORA'] = df['HORA_INFRACCION'].dt.hour

    # ==========================================
    # 4) VALIDACIÓN DE COORDENADAS
    # ==========================================
    print("\n4) Validando COORDENADAS...")

    df['LAT_ORIGINAL'] = df['LATITUD']
    df['LON_ORIGINAL'] = df['LONGITUD']

    df['LATITUD'] = df['LATITUD'].astype(str).str.replace(',', '.')
    df['LONGITUD'] = df['LONGITUD'].astype(str).str.replace(',', '.')

    df['LATITUD'] = pd.to_numeric(df['LATITUD'], errors='coerce')
    df['LONGITUD'] = pd.to_numeric(df['LONGITUD'], errors='coerce')

    print("❌ Lat inválidas:", df['LATITUD'].isnull().sum())
    print("❌ Lon inválidas:", df['LONGITUD'].isnull().sum())

    # ==========================================
    # 🔥 5) LIMPIEZA DE TEXTO (LO MÁS IMPORTANTE)
    # ==========================================
    print("\n5) Limpiando texto de infracciones...")

    # Quitar espacios extras
    df['D_INFRACCION'] = df['D_INFRACCION'].astype(str).str.strip()

    # Pasar a mayúscula
    df['D_INFRACCION'] = df['D_INFRACCION'].str.upper()

    # Reemplazar caracteres raros
    df['D_INFRACCION'] = df['D_INFRACCION'] \
        .str.replace('Ã', 'A', regex=False) \
        .str.replace('É', 'E', regex=False)

    # ==========================================
    # 🔥 6) CATEGORIZACIÓN INTELIGENTE
    # ==========================================
    df['TIPO_LIMPIO'] = df['D_INFRACCION'].apply(
        lambda x:
        'LUCES' if 'LUZ' in x or 'LUCES' in x else
        'EXTINTOR' if 'EXTINTOR' in x else
        'BOTIQUIN' if 'BOTIQUIN' in x else
        'LICENCIA' if 'LICENCIA' in x else
        'AUTORIZACION' if 'AUTORIZ' in x else
        'PRONTO PAGO' if 'PRONTO PAGO' in x else
        'OTROS'
    )

    print("\n📌 Distribución limpia:")
    print(df['TIPO_LIMPIO'].value_counts())

    # ==========================================
    # 7) TOP ORIGINAL VS LIMPIO
    # ==========================================
    print("\n📌 Top original:")
    print(df['D_INFRACCION'].value_counts().head(10))

    print("\n📌 Top limpio:")
    print(df['TIPO_LIMPIO'].value_counts())

    # ==========================================
    # 8) GRÁFICOS
    # ==========================================
    fig = Figure(figsize=(14, 10))
    axs = fig.subplots(2, 2)

    # TOP limpio (MEJOR)
    limpio_counts = df['TIPO_LIMPIO'].value_counts()
    axs[0, 0].bar(limpio_counts.index, limpio_counts.values)
    axs[0, 0].set_title('Tipos de Infracción (LIMPIO)')
    axs[0, 0].tick_params(axis='x', rotation=45)

    # Hora
    axs[0, 1].hist(df['HORA'].dropna(), bins=24, edgecolor='black')
    axs[0, 1].set_title('Distribución por Hora')

    # Mes
    mes_counts = df['MES'].value_counts().sort_index()
    axs[1, 0].bar(mes_counts.index.astype(str), mes_counts.values)
    axs[1, 0].set_title('Distribución por Mes')

    # Mapa
    axs[1, 1].scatter(df['LONGITUD'], df['LATITUD'], s=10, alpha=0.3)
    axs[1, 1].set_title("Mapa de Infracciones")

    print("\n✅ Exploración completa + limpieza avanzada")

    return fig


# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig = main()

    fig.savefig("eda_limpio.png", dpi=300, bbox_inches='tight')
    print("\n✅ Gráfico guardado: eda_limpio.png")

    plt.show()