# ETL/Transformacion.py

import pandas as pd

def main():
    # ==========================================
    # 1) CARGAR DATOS
    # ==========================================
    print("1) Cargando dataset original...")
    path = r"C:\db\Nik_Denilson\Universidad\IntiligenciaArtificial\Martin\Data\Infracciones.csv"

    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8")
    except Exception:
        df = pd.read_csv(path, sep=";", encoding="latin1")

    print(f"\n[*] Dimensiones originales: {df.shape}")

    # Guardar copias originales para mostrar el antes y el despues
    df['FECHA_ORIGINAL'] = df['FECHA'].astype(str)
    df['HORA_ORIGINAL'] = df['HORA_INFRACCION'].astype(str)

    # ==========================================
    # 2) TRANSFORMACION DE FECHA (YYYY/MM/DD)
    # ==========================================
    print("\n2) Transformando columna FECHA al formato estandar (YYYY/MM/DD)...")
    df['FECHA_DT'] = pd.to_datetime(df['FECHA'], format='%Y%m%d', errors='coerce')
    df['FECHA'] = df['FECHA_DT'].dt.strftime('%Y/%m/%d')

    # Extraer componentes si se requieren para analisis
    df['DIA'] = df['FECHA_DT'].dt.day
    df['MES'] = df['FECHA_DT'].dt.month
    df['AÑO'] = df['FECHA_DT'].dt.year

    # ==========================================
    # 3) TRANSFORMACION DE HORA (HH:MM:SS)
    # ==========================================
    print("\n3) Transformando columna HORA_INFRACCION al formato estricto (HH:MM:SS)...")
    # Convertir a datetime para estandarizar y luego formatear con 2 digitos en la hora (%H:%M:%S)
    df['HORA_DT'] = pd.to_datetime(df['HORA_INFRACCION'], format='%H:%M:%S', errors='coerce')
    df['HORA_INFRACCION'] = df['HORA_DT'].dt.strftime('%H:%M:%S')

    df['HORA'] = df['HORA_DT'].dt.hour

    # Eliminar columnas temporales de datetime
    df = df.drop(columns=['FECHA_DT', 'HORA_DT'])

    # ==========================================
    # 4) TRANSFORMACION DE PROVINCIA
    # ==========================================
    print("\n4) Estandarizando columna PROVINCIA (mayusculas y sin espacios en los extremos)...")
    df['PROV_ORIGINAL'] = df['PROVINCIA'].astype(str)
    df['PROVINCIA'] = df['PROVINCIA'].astype(str).str.strip().str.upper()

    # ==========================================
    # 5) VALIDACION Y LIMPIEZA DE COORDENADAS
    # ==========================================
    print("\n5) Limpiando y validando COORDENADAS (LATITUD / LONGITUD)...")
    df['LAT_ORIGINAL'] = df['LATITUD']
    df['LON_ORIGINAL'] = df['LONGITUD']

    df['LATITUD'] = df['LATITUD'].astype(str).str.replace(',', '.')
    df['LONGITUD'] = df['LONGITUD'].astype(str).str.replace(',', '.')

    df['LATITUD'] = pd.to_numeric(df['LATITUD'], errors='coerce')
    df['LONGITUD'] = pd.to_numeric(df['LONGITUD'], errors='coerce')

    # ==========================================
    # 6) LIMPIEZA DE TEXTO EN INFRACCIONES
    # ==========================================
    print("\n6) Limpiando texto de la descripcion de infracciones...")
    df['D_INFRACCION'] = df['D_INFRACCION'].astype(str).str.strip().str.upper()
    df['D_INFRACCION'] = df['D_INFRACCION'].str.replace('Ã', 'A', regex=False).str.replace('É', 'E', regex=False)

    # ==========================================
    # 7) MUESTRA DEL ANTES Y DESPUES
    # ==========================================
    print("\n" + "="*60)
    print(" COMPARATIVA DE TRANSFORMACION: ANTES VS DESPUES")
    print("="*60)
    comparativa = df[['FECHA_ORIGINAL', 'FECHA', 'HORA_ORIGINAL', 'HORA_INFRACCION', 'PROV_ORIGINAL', 'PROVINCIA']].head(10)
    print(comparativa.to_string(index=False))
    print("="*60)

    # ==========================================
    # 8) GUARDAR ARCHIVO LIMPIO
    # ==========================================
    out_path = r"C:\db\Nik_Denilson\Universidad\IntiligenciaArtificial\Martin\Data\Infracciones_clean.csv"
    print(f"\n8) Guardando dataset limpio en:\n   {out_path} ...")
    
    # Eliminar columnas de respaldo antes de exportar
    df_clean = df.drop(columns=['FECHA_ORIGINAL', 'HORA_ORIGINAL', 'PROV_ORIGINAL', 'LAT_ORIGINAL', 'LON_ORIGINAL'])
    df_clean.to_csv(out_path, sep=";", index=False, encoding="utf-8-sig")
    print("[OK] Archivo guardado exitosamente.")

    print("\n[OK] Transformacion completa y exitosa.")
    return df_clean

if __name__ == "__main__":
    df_limpio = main()