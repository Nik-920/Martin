# 🚗 Sistema para el Análisis y Predicción de Infracciones de Tránsito en San Martín

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black?style=for-the-badge&logo=flask&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-orange?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Data%20Visualization-3178C6?style=for-the-badge)
DATASET : https://www.datosabiertos.gob.pe/dataset/registro-de-infracciones-tr%C3%A1nsito-de-la-regi%C3%B3n-san-mart%C3%ADn-%E2%80%93-gore-san-mart%C3%ADn-%E2%80%93-grsm/resource#{view-graph:{graphOptions:{hooks:{processOffset:{},bindEvents:{}}}},graphOptions:{hooks:{processOffset:{},bindEvents:{}}}}

Este proyecto es un ecosistema integral de Inteligencia Artificial y Ciencia de Datos diseñado para analizar, agrupar y predecir patrones de infracciones de tránsito en las **9 provincias de la región de San Martín, Perú** (Bellavista, Huallaga, Lamas, Mariscal Cáceres, Moyobamba, Picota, Rioja, San Martín y Tocache).

El sistema integra un pipeline completo de **ETL (Extracción, Transformación y Carga)**, algoritmos de clustering no supervisado (**DBSCAN**), modelado predictivo supervisado (**Random Forest Regressor**) y un **Dashboard Web Interactivo** construido en Flask.

---

## 🏗️ Arquitectura del Proyecto

```text
C:\db\Nik_Denilson\Universidad\IntiligenciaArtificial\Martin\
├── Data/
│   ├── Infracciones.csv             # Dataset original bruto
│   └── Infracciones_clean.csv       # Dataset normalizado y limpio (Salida del ETL)
├── ETL/
│   ├── ExploracionDatos.py          # Auditoría de calidad y diagnóstico por Regex
│   └── Transformacion.py            # Pipeline de limpieza y estandarización de datos
├── SanMartin/                       # Módulos de Clustering no supervisado (DBSCAN)
│   ├── BELLAVISTA.py
│   ├── HUALLAGA.py
│   ├── LAMAS.py
│   ├── MARISCAL.py
│   ├── MOYOBAMBA.py
│   ├── PICOTA.py
│   ├── RIOJA.py
│   ├── SAN_MARTIN.py
│   └── TOCACHE.py
├── Regresion/                       # Módulos de Modelado Predictivo (Random Forest)
│   ├── Regresion.py                 # Controlador general de regresión
│   ├── PROVINCIA.py                 # Modelos globales por provincia
│   └── PROVINCIA_SEMANA.py          # Modelos de análisis diario/semanal por provincia
├── INTERFAX.py                      # Aplicación Web Flask (Dashboard Interactivo)
├── .gitignore                       # Reglas de exclusión de Git (Caché, IDEs, imágenes gen.)
└── README.md                        # Documentación técnica del proyecto
```

---

## 🧠 Técnicas de Machine Learning Utilizadas y Justificación

La selección de algoritmos en este proyecto no es arbitraria; responde directamente a la naturaleza espaciotemporal y no lineal de los datos de tráfico vehicular. A continuación se detallan los dos enfoques clave implementados:

### 1. DBSCAN (Clustering No Supervisado)

**DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** es un algoritmo de agrupamiento basado en la densidad espacial. En este proyecto se utiliza para analizar la relación entre la hora del día (convertida a segundos) y el día del mes.

* **¿Por qué se eligió sobre K-Means?**
  * **Formas Arbitrarias:** `K-Means` asume que los clústeres son esféricos y de tamaño similar. En el tráfico real, las infracciones ocurren en "franjas horarias" o flujos continuos (ej. horas pico de la mañana o la salida del trabajo) que tienen formas alargadas e irregulares. DBSCAN agrupa perfectamente estas densidades continuas.
  * **Detección de Ruido (Anomalías):** `K-Means` fuerza a todos los puntos a pertenecer a un clúster, lo que distorsiona el análisis si hay infracciones aisladas en la madrugada. DBSCAN identifica automáticamente estos eventos esporádicos como ruido (`clúster -1`), permitiendo a las autoridades centrarse exclusivamente en las zonas y horarios de alta concentración sistemática.
  * **Sin K Predefinido:** No requiere adivinar cuántos clústeres existen de antemano; el algoritmo los descubre de forma natural según la cercanía (`eps`) y cantidad mínima de incidentes (`min_samples`) de cada provincia.

### 2. Random Forest Regressor (Modelado Predictivo Supervisado)

**Random Forest** es un método de ensamble (ensemble learning) que construye múltiples árboles de decisión independientes y promedia sus predicciones para estimar la cantidad de infracciones que ocurrirán en una hora y día específicos.

* **¿Por qué se eligió sobre Regresión Lineal o Polinómica?**
  * **Relaciones No Lineales Complejas:** El comportamiento del tráfico vehicular es altamente cíclico y dependiente de múltiples factores (ej. un Lunes a las 8:00 AM es completamente distinto a un Domingo a las 8:00 AM). Una regresión lineal no puede capturar estos cambios bruscos. Random Forest divide el espacio de datos en nodos de decisión, capturando interacciones multidimensionales complejas de forma nativa.
  * **Robustez ante Valores Atípicos:** Al promediar la predicción de 150 árboles de decisión (`n_estimators=150`), el modelo es sumamente resistente al sobreajuste (overfitting) y no se deja sesgar por días feriados o eventos atípicos con picos inusuales.
  * **Sinergia con Transformación Logarítmica:** Al predecir sobre el logaritmo de las infracciones (`np.log1p(CANTIDAD)`), el modelo maneja sin problemas la asimetría de los datos (distribución típica en conteos de incidentes de tráfico), logrando curvas de predicción suaves y altamente precisas para la planificación de patrullajes.

---

## 🚀 Componentes Principales

### 1. 🧹 Pipeline ETL (`ETL/`)

Garantiza la calidad e integridad de los datos antes de alimentar los modelos de Machine Learning.

* **`ExploracionDatos.py`**: Realiza auditorías avanzadas utilizando expresiones regulares (Regex) para identificar inconsistencias sutiles (como horas sin ceros a la izquierda) y validar la consistencia geográfica de las 9 provincias.
* **`Transformacion.py`**: Estandariza las fechas al formato estricto `YYYY/MM/DD`, normaliza las horas a `HH:MM:SS`, corrige separadores decimales en coordenadas de latitud/longitud, convierte textos a mayúsculas eliminando espacios redundantes y exporta el archivo `Infracciones_clean.csv` con codificación `utf-8-sig` para compatibilidad universal.

### 2. 🎯 Clustering No Supervisado (`SanMartin/`)

Utiliza el algoritmo **DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** para encontrar agrupaciones naturales y patrones de concentración de infracciones.

* Convierte la hora exacta de la infracción en segundos acumulados del día (`0 - 86400`).
* Relaciona la hora del día con el día del mes (`1 - 31`).
* Cada provincia cuenta con hiperparámetros minuciosamente optimizados (`eps` y `min_samples`) para reflejar la densidad vehicular y demográfica particular de su zona.

### 3. 📈 Modelado Predictivo (`Regresion/`)

Implementa modelos de **Random Forest Regressor** para predecir la cantidad de infracciones esperadas.

* **Transformación Logarítmica:** Aplica `np.log1p` a la variable objetivo (conteo de infracciones) para estabilizar la varianza y manejar picos asimétricos, revirtiendo la predicción con `np.expm1`.
* **Análisis Global (`PROVINCIA.py`):** Evalúa y grafica el comportamiento general de las infracciones a lo largo de las 24 horas del día.
* **Análisis Semanal (`PROVINCIA_SEMANA.py`):** Desglosa las predicciones en 7 gráficos independientes (uno por cada día de la semana, de Lunes a Domingo), permitiendo identificar si los picos de infracciones ocurren en fines de semana o días laborales.

### 4. 🌐 Dashboard Web Interactivo (`INTERFAX.py`)

Una aplicación web desarrollada en **Flask** que unifica todos los modelos de Inteligencia Artificial en una interfaz elegante y fácil de usar.

* **Selección Dinámica:** El usuario elige una provincia desde un menú desplegable.
* **Ejecución en Tiempo Real:** Al seleccionar una provincia, el servidor ejecuta en segundo plano los modelos de DBSCAN y Random Forest correspondientes.
* **Visualización Integrada:** Muestra de forma simultánea el gráfico de clústeres (DBSCAN), la curva de regresión global, las 7 curvas de predicción diaria y una tabla de datos limpios, además de enlazar con paneles de analítica BI.

---

## 🛠️ Instalación y Configuración

### 1. Prerrequisitos

Asegúrate de tener instalado **Python 3.12 o superior** en tu sistema operativo Windows.

### 2. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Martin
```

### 3. Crear y activar un entorno virtual (Recomendado)

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 4. Instalar dependencias

Asegúrate de instalar las librerías requeridas para el análisis de datos y la web app:

```bash
pip install pandas numpy scikit-learn matplotlib flask
```

---

## 🖥️ Guía de Uso y Ejecución

### Opción A: Ejecutar el Dashboard Web (Recomendado)

Para interactuar con todo el sistema de forma visual a través del navegador:

```bash
python INTERFAX.py
```

1. Abre tu navegador web e ingresa a: `http://127.0.0.1:5000/`.
2. Selecciona una provincia en el menú desplegable y haz clic en **"Generar Análisis"**.
3. Explora los gráficos interactivos generados en tiempo real por la Inteligencia Artificial.

### Opción B: Ejecutar Módulos Individuales por Consola

Si deseas probar o auditar partes específicas del pipeline desde la terminal:

* **Ejecutar la Limpieza y ETL:**

  ```bash
  python ETL/Transformacion.py
  ```

  *(Generará el archivo `Data/Infracciones_clean.csv` y mostrará una comparativa en consola).*

* **Ejecutar Clustering (DBSCAN) de una provincia:**

  ```bash
  python -c "from SanMartin.BELLAVISTA import main; main()"
  ```

* **Ejecutar Regresión Semanal de una provincia:**

  ```bash
  python Regresion/BELLAVISTA_SEMANA.py
  ```

---

## 📊 Estructura del Dataset Limpio (`Infracciones_clean.csv`)

El dataset procesado contiene las siguientes columnas principales listas para el modelado:

| Columna | Descripción | Formato / Ejemplo |
| :--- | :--- | :--- |
| **ID_REGISTRO** | Identificador único de la fila | Numérico (`18799`) |
| **ACTA** | Código del acta de infracción | Texto (`C002485`) |
| **FECHA** | Fecha estandarizada de la infracción | `YYYY/MM/DD` (`2017/10/10`) |
| **HORA_INFRACCION** | Hora estricta de la infracción | `HH:MM:SS` (`00:00:02`) |
| **D_INFRACCION** | Descripción normalizada de la falta | Texto en mayúsculas (`NO CUENTA CON EXTINTOR`) |
| **PROVINCIA** | Nombre de la provincia de San Martín | Texto en mayúsculas (`BELLAVISTA`) |
| **LATITUD / LONGITUD**| Coordenadas geográficas validadas | Decimal con punto (`-7.1017`) |

---

## 📓 Notebook Jupyter (Flujo Completo)

Se ha desarrollado un Notebook estructurado que documenta todo el ciclo de vida del análisis de datos de forma interactiva. Este flujo de trabajo incluye:

1. **Carga de Datos:** Importación de los datasets originales y estructuración inicial.
2. **Análisis Exploratorio de Datos (EDA):** Visualización de distribuciones, identificación de valores nulos o atípicos, y análisis de correlación entre variables clave (horas, días, ubicaciones).
3. **Modelo de Machine Learning:** Entrenamiento y ajuste de hiperparámetros de los algoritmos (Random Forest y DBSCAN).
4. **Métricas de Evaluación:** Validación de la precisión del modelo utilizando métricas estándar (como RMSE, MAE, R², y visualización real vs. predicho) para garantizar la fiabilidad y robustez de las predicciones en cada provincia.

---

## 🎯 Conclusiones y Toma de Decisiones

### ¿Qué patrones se encontraron?
* **Picos Temporales Específicos:** A través del análisis temporal y el algoritmo Random Forest, se detectó que existen "ventanas de tiempo" críticas donde las infracciones se disparan, y que estas varían de forma consistente según el día de la semana (por ejemplo, diferencias marcadas entre los viernes por la noche y los lunes por la mañana).
* **Concentraciones Densas (Hotspots):** El algoritmo DBSCAN identificó agrupaciones naturales y continuas de infracciones (zonas calientes temporales), demostrando que las faltas de tránsito no son eventos aislados, sino que responden a dinámicas poblacionales repetitivas.
* **Comportamiento por Provincia:** Cada provincia muestra una "huella digital" única en cuanto a infracciones, influenciada por su densidad poblacional y sus dinámicas de transporte local, lo que descarta una solución única para toda la región.

### ¿Cómo apoya a la toma de decisiones?
* **Optimización de Patrullajes:** Permite a las autoridades de tránsito abandonar el modelo de patrullaje aleatorio o reactivo, pasando a un modelo proactivo. Pueden desplegar personal y recursos operativos exactamente en los días, horas y provincias donde el modelo predice una alta probabilidad de infracciones.
* **Gestión de Recursos Eficiente:** Reduce los costos operativos al evitar la sobrevigilancia en horarios de "ruido" (baja probabilidad de incidentes detectados por DBSCAN) y focalizando esfuerzos en los clústeres principales.
* **Políticas Preventivas:** Facilita el diseño de campañas de concientización vial focalizadas, sabiendo de antemano cuándo y dónde los conductores son más propensos a cometer infracciones específicas.
