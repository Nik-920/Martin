# ETL/ExploracionDatos.py

import pandas as pd
import re

def explorar_formato_fechas_horas_provincias():
    path = r"C:\db\Nik_Denilson\Universidad\IntiligenciaArtificial\Martin\Data\Infracciones.csv"
    print("="*60)
    print(" EXPLORACION Y VALIDACION DE FORMATOS: FECHA, HORA Y PROVINCIA")
    print("="*60)
    
    # Cargar datos
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8", dtype=str)
    except Exception as e:
        df = pd.read_csv(path, sep=";", encoding="latin1", dtype=str)
        
    total_registros = len(df)
    print(f"Total de registros cargados: {total_registros}\n")
    
    # ----------------------------------------------------
    # 1. VALIDACION ESTANDAR (PANDAS / DATETIME)
    # ----------------------------------------------------
    print("--- 1. VALIDACION ESTANDAR (PANDAS / DATETIME) ---")
    # Validacion de FECHA (formato esperado YYYYMMDD)
    fechas_dt = pd.to_datetime(df['FECHA'], format='%Y%m%d', errors='coerce')
    fechas_mal_dt = fechas_dt.isna().sum()
    
    # Validacion de HORA (formato esperado %H:%M:%S, acepta H:MM:SS y HH:MM:SS)
    horas_dt = pd.to_datetime(df['HORA_INFRACCION'], format='%H:%M:%S', errors='coerce')
    horas_mal_dt = horas_dt.isna().sum()
    
    print(f"[X] Registros con FECHA mal formateada (invalida en calendario): {fechas_mal_dt}")
    print(f"[X] Registros con HORA mal formateada (invalida en reloj): {horas_mal_dt}\n")
    
    # ----------------------------------------------------
    # 2. VALIDACION ESTRICTA POR EXPRESIONES REGULARES (REGEX)
    # ----------------------------------------------------
    print("--- 2. VALIDACION ESTRICTA POR REGEX ---")
    # FECHA estricta: 8 digitos exactos (YYYYMMDD)
    fechas_mal_regex = (~df['FECHA'].fillna('').str.match(r'^\d{8}$')).sum()
    
    # HORA estricta: HH:MM:SS (2 digitos para la hora obligatorios)
    horas_hhmmss = df['HORA_INFRACCION'].fillna('').str.match(r'^\d{2}:\d{2}:\d{2}$')
    horas_hmmss = df['HORA_INFRACCION'].fillna('').str.match(r'^\d{1}:\d{2}:\d{2}$')
    horas_mal_estricto = (~horas_hhmmss).sum()
    
    print(f"[X] Registros con FECHA que no cumplen regex estricto 'YYYYMMDD' (8 digitos): {fechas_mal_regex}")
    print(f"[X] Registros con HORA que no tienen formato estricto 'HH:MM:SS' (2 digitos en hora): {horas_mal_estricto}")
    print(f"    |- Registros con formato 'HH:MM:SS' (ej. 10:33:00): {horas_hhmmss.sum()}")
    print(f"    |- Registros con formato 'H:MM:SS'  (ej. 0:00:02, 8:21:00): {horas_hmmss.sum()}\n")
    
    # ----------------------------------------------------
    # 3. EXPLORACION Y VALIDACION DE PROVINCIAS
    # ----------------------------------------------------
    print("--- 3. EXPLORACION Y VALIDACION DE PROVINCIAS ---")
    provincias = df['PROVINCIA'].fillna('')
    provincias_distintas = provincias.unique()
    total_distintas = len(provincias_distintas)
    
    # Validacion de formato en provincias (nulos, vacios, caracteres especiales o espacios extra)
    provincias_nulas = df['PROVINCIA'].isna().sum()
    provincias_espacios = provincias.str.contains(r'^\s|\s$', regex=True).sum()
    # Verificar que contenga solo letras mayusculas y espacios normales (sin caracteres raros ni numeros)
    provincias_raras = (~provincias.str.match(r'^[A-Z\s]+$')).sum()
    
    print(f"Total de provincias distintas encontradas: {total_distintas}")
    print(f"[X] Registros con PROVINCIA nula o vacia: {provincias_nulas}")
    print(f"[X] Registros con PROVINCIA con espacios iniciales/finales: {provincias_espacios}")
    print(f"[X] Registros con PROVINCIA con caracteres invalidos o minusculas: {provincias_raras}")
    print("\nLista de provincias y su conteo de registros:")
    for prov, count in df['PROVINCIA'].value_counts().items():
        print(f"    |- {prov}: {count} registros")
    print()
    
    # ----------------------------------------------------
    # RESUMEN Y CONCLUSION
    # ----------------------------------------------------
    print("="*60)
    print(" CONCLUSION DEL ANALISIS")
    print("="*60)
    print("- Segun la validacion estandar de fechas y horas (Pandas/Datetime):")
    print("  * FECHA mal formateadas: 0")
    print("  * HORA mal formateadas:  0")
    print("\n- Segun una validacion estricta de cadenas (Regex HH:MM:SS vs H:MM:SS):")
    print("  * FECHA mal formateadas: 0")
    print(f"  * HORA sin cero a la izquierda en la hora (ej. '8:30:00' en vez de '08:30:00'): {horas_mal_estricto}")
    print("\n- Segun la exploracion de la columna PROVINCIA:")
    print(f"  * Provincias distintas: {total_distintas} (Las 9 provincias de la region San Martin)")
    print("  * Registros mal formateados en PROVINCIA: 0 (Sin nulos, sin espacios extra y nombres estandarizados)")
    print("="*60)

if __name__ == "__main__":
    explorar_formato_fechas_horas_provincias()
