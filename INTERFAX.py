import base64
import importlib
import io
import sys
import openpyxl
import pandas as pd
from flask import Flask, render_template_string, request

# Añadir ruta de los módulos de análisis
BASE_DIR = r"/"
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

EXCEL_PATH = r"C:\db\Nik Denilson\Universidad\IntiligenciaArtificial\Proyecto\Scrip\Martin\PROVINCIAS.xlsx"

app = Flask(__name__)
# Lista de provincias y mapeo a nombres de módulos
PROVINCIAS = [
    'BELLAVISTA', 'HUALLAGA', 'LAMAS', 'MARISCAL','MOYOBAMBA', 'PICOTA', 'RIOJA', 'SAN_MARTIN', 'TOCACHE'
]

TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sistema de Análisis DBSCAN - San Martín</title>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      color: #333;
    }
    
    /* Partículas de fondo animadas */
    .particles {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 0;
    }
    
    .particle {
      position: absolute;
      background: rgba(255, 255, 255, 0.5);
      border-radius: 50%;
      animation: float 6s infinite;
    }
    
    @keyframes float {
      0%, 100% { transform: translateY(0) translateX(0); }
      25% { transform: translateY(-20px) translateX(10px); }
      50% { transform: translateY(-40px) translateX(-10px); }
      75% { transform: translateY(-20px) translateX(5px); }
    }
    
    .container {
      max-width: 1400px;
      margin: 0 auto;
      background: white;
      min-height: 100vh;
      box-shadow: 0 0 50px rgba(0,0,0,0.3);
      position: relative;
      z-index: 1;
    }
    
    header {
      background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
      color: white;
      padding: 3rem 1rem;
      text-align: center;
      position: relative;
      overflow: hidden;
    }
    
    header::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
      background-size: 50px 50px;
      animation: moveGrid 20s linear infinite;
    }
    
    @keyframes moveGrid {
      0% { transform: translate(0, 0); }
      100% { transform: translate(50px, 50px); }
    }
    
    .header-content {
      position: relative;
      z-index: 1;
    }
    
    .header-title {
      font-size: 2.8rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
      animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
      from { text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
      to { text-shadow: 2px 2px 20px rgba(255,255,255,0.5); }
    }
    
    .header-subtitle {
      font-size: 1.2rem;
      opacity: 0.9;
      font-weight: 300;
    }
    
    /* Botón moderno estilo uiverse.io */
    .nav-button {
      position: relative;
      overflow: hidden;
      border: 1px solid #667eea;
      color: #667eea;
      background: white;
      padding: 1.2rem 2rem;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      border-radius: 12px;
      transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
      box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .nav-button::before {
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      transform: translateX(-100%);
      transition: transform 0.3s cubic-bezier(0.23, 1, 0.320, 1);
      z-index: -1;
    }
    
    .nav-button:hover {
      color: white;
      transform: translateY(-5px) scale(1.02);
      box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    .nav-button:hover::before {
      transform: translateX(0);
    }
    
    .nav-button:active {
      transform: scale(0.98);
    }
    
    .nav-button i {
      margin-right: 0.5rem;
      transition: transform 0.3s ease;
    }
    
    .nav-button:hover i {
      transform: rotate(360deg);
    }
    
    .nav-section {
      background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
      padding: 2.5rem 1.5rem;
      border-bottom: 3px solid #667eea;
      position: relative;
    }
    
    .nav-title {
      text-align: center;
      margin-bottom: 2rem;
      color: #2c3e50;
      font-weight: 700;
      font-size: 1.5rem;
      position: relative;
      display: inline-block;
      left: 50%;
      transform: translateX(-50%);
    }
    
    .nav-title::after {
      content: '';
      position: absolute;
      bottom: -10px;
      left: 0;
      width: 100%;
      height: 3px;
      background: linear-gradient(90deg, #667eea, #764ba2);
      border-radius: 2px;
    }
    
    .nav-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
    }
    
    main {
      padding: 2rem;
      min-height: 60vh;
    }
    
    /* Cards con efecto glassmorphism */
    .analysis-card {
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      padding: 2rem;
      box-shadow: 0 15px 35px rgba(0,0,0,0.1);
      border: 1px solid rgba(255, 255, 255, 0.5);
      transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
      position: relative;
      overflow: hidden;
    }
    
    .analysis-card::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
      opacity: 0;
      transition: opacity 0.4s ease;
    }
    
    .analysis-card:hover::before {
      opacity: 1;
      animation: rotate 4s linear infinite;
    }
    
    @keyframes rotate {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    .analysis-card:hover {
      transform: translateY(-10px);
      box-shadow: 0 20px 50px rgba(102, 126, 234, 0.3);
    }
    
    .analysis-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      margin-top: 2rem;
    }
    
    .card-header {
      display: flex;
      align-items: center;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 2px solid #f8f9fa;
      position: relative;
      z-index: 1;
    }
    
    .card-icon {
      font-size: 2.5rem;
      margin-right: 1rem;
      background: linear-gradient(135deg, #667eea, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); }
    }
    
    .card-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #2c3e50;
    }
    
    /* Contenedor de gráfico mejorado */
    .chart-container {
      text-align: center;
      background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
      border-radius: 15px;
      padding: 1.5rem;
      margin-bottom: 1rem;
      position: relative;
      z-index: 1;
      box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .chart-container img {
      max-width: 100%;
      height: auto;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.15);
      transition: transform 0.3s ease;
    }
    
    .chart-container:hover img {
      transform: scale(1.02);
    }
    
    /* Tabla mejorada */
    .table-container {
      max-height: 500px;
      overflow-y: auto;
      border-radius: 12px;
      border: 1px solid #e9ecef;
      position: relative;
      z-index: 1;
      box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .table-container::-webkit-scrollbar {
      width: 8px;
    }
    
    .table-container::-webkit-scrollbar-track {
      background: #f8f9fa;
      border-radius: 4px;
    }
    
    .table-container::-webkit-scrollbar-thumb {
      background: linear-gradient(135deg, #667eea, #764ba2);
      border-radius: 4px;
    }
    
    .tabla-provincia {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }
    
    .tabla-provincia th {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-weight: 600;
      padding: 1rem 0.8rem;
      text-align: center;
      position: sticky;
      top: 0;
      z-index: 10;
    }
    
    .tabla-provincia td {
      padding: 0.8rem;
      text-align: center;
      border-bottom: 1px solid #e9ecef;
      transition: all 0.2s ease;
    }
    
    .tabla-provincia tr:hover td {
      background-color: rgba(102, 126, 234, 0.1);
      transform: scale(1.01);
    }
    
    .tabla-provincia tr:nth-child(even) {
      background-color: #fafafa;
    }
    
    /* Welcome section mejorada */
    .welcome-section {
      text-align: center;
      padding: 4rem 2rem;
      background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,250,0.9) 100%);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      margin: 2rem 0;
      box-shadow: 0 15px 35px rgba(0,0,0,0.1);
      position: relative;
      overflow: hidden;
    }
    
    .welcome-section::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
      animation: rotate 10s linear infinite;
    }
    
    .welcome-icon {
      font-size: 5rem;
      background: linear-gradient(135deg, #667eea, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 2rem;
      animation: bounce 2s ease-in-out infinite;
      position: relative;
      z-index: 1;
    }
    
    @keyframes bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-20px); }
    }
    
    .welcome-title {
      font-size: 2.2rem;
      color: #2c3e50;
      margin-bottom: 1rem;
      font-weight: 700;
      position: relative;
      z-index: 1;
    }
    
    .welcome-text {
      font-size: 1.2rem;
      color: #6c757d;
      line-height: 1.8;
      max-width: 700px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
    }
    
    /* Stats cards mejoradas */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
      margin-top: 3rem;
      position: relative;
      z-index: 1;
    }
    
    .stat-card {
      background: white;
      padding: 2rem 1.5rem;
      border-radius: 15px;
      text-align: center;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
      border: 2px solid transparent;
      transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
      position: relative;
      overflow: hidden;
    }
    
    .stat-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #667eea, #764ba2);
      transform: scaleX(0);
      transition: transform 0.3s ease;
    }
    
    .stat-card:hover::before {
      transform: scaleX(1);
    }
    
    .stat-card:hover {
      transform: translateY(-10px) scale(1.02);
      box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
      border-color: #667eea;
    }
    
    .stat-number {
      font-size: 2.5rem;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }
    
    .stat-label {
      color: #6c757d;
      font-weight: 500;
      font-size: 0.95rem;
    }
    
    /* Loading spinner mejorado */
    .loading {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(255, 255, 255, 0.95);
      z-index: 9999;
      justify-content: center;
      align-items: center;
      flex-direction: column;
    }
    
    .loading.active {
      display: flex;
    }
    
    .spinner {
      width: 60px;
      height: 60px;
      border: 5px solid #f3f3f3;
      border-top: 5px solid #667eea;
      border-radius: 50%;
      animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
      margin-bottom: 1.5rem;
      box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .loading p {
      font-size: 1.2rem;
      color: #667eea;
      font-weight: 600;
      animation: fade 1.5s ease-in-out infinite;
    }
    
    @keyframes fade {
      0%, 100% { opacity: 0.5; }
      50% { opacity: 1; }
    }
    
    footer {
      background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
      color: white;
      text-align: center;
      padding: 3rem 2rem;
      margin-top: 4rem;
      position: relative;
      overflow: hidden;
    }
    
    footer::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .footer-content {
      max-width: 1200px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
    }
    
    .footer-title {
      font-size: 1.3rem;
      margin-bottom: 1rem;
      font-weight: 600;
    }
    
    .footer-text {
      opacity: 0.85;
      line-height: 1.8;
      font-size: 0.95rem;
    }
    
    @media (max-width: 768px) {
      .header-title {
        font-size: 2rem;
      }
      
      .analysis-container {
        grid-template-columns: 1fr;
      }
      
      .nav-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      }
      
      .stats-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      }
    }
  </style>
</head>
<body>
  <!-- Partículas de fondo -->
  <div class="particles" id="particles"></div>
  
  <div class="container">
    <header>
      <div class="header-content">
        <h1 class="header-title">Sistema de Análisis DBSCAN - IA</h1>
        <p class="header-subtitle">Análisis de Densidades Horarias de Infracciones - Región San Martín</p>
      </div>
    </header>
    
    <div class="nav-section">
      <h2 class="nav-title">
        <i class="fas fa-map-marker-alt"></i>
        Seleccionar Provincia para Análisis
      </h2>
      <div class="nav-grid">
        {% for prov in provincias %}
          <form style="display:inline;" method="get" action="/provincia">
            <input type="hidden" name="prov" value="{{ prov }}">
            <button type="submit" class="nav-button">
              <i class="fas fa-chart-bar"></i>
              {{ prov.replace('_',' ') }}
            </button>
          </form>
        {% endfor %}
      </div>
    </div>
    
    <main>
      {% if image %}
        <div class="analysis-container">
          <div class="analysis-card">
            <div class="card-header">
              <i class="fas fa-chart-line card-icon"></i>
              <h2 class="card-title">Análisis de Clusters</h2>
            </div>
            <div class="chart-container">
              <img src="data:image/png;base64,{{ image }}" alt="Gráfico DBSCAN de {{ selected }}">
            </div>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-number">{{ selected.replace('_',' ') }}</div>
                <div class="stat-label">Provincia Analizada</div>
              </div>
            </div>
          </div>
          
          <div class="analysis-card">
            <div class="card-header">
              <i class="fas fa-table card-icon"></i>
              <h2 class="card-title">Datos de Infracciones</h2>
            </div>
            <div class="table-container">
              {{ tabla | safe }}
            </div>
          </div>
        </div>
      {% else %}
        <div class="welcome-section">
          <i class="fas fa-rocket welcome-icon"></i>
          <h2 class="welcome-title">Sistema de Análisis Avanzado</h2>
          <p class="welcome-text">
            Bienvenido al sistema de análisis de infracciones utilizando algoritmos de clustering DBSCAN. 
            Seleccione una provincia para visualizar los patrones de densidad horaria y análisis estadístico detallado.
          </p>
          
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-number">{{ provincias|length }}</div>
              <div class="stat-label">Provincias Disponibles</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">DBSCAN</div>
              <div class="stat-label">Algoritmo de Clustering</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">24h</div>
              <div class="stat-label">Análisis Horario</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">Real-time</div>
              <div class="stat-label">Generación de Datos</div>
            </div>
          </div>
        </div>
      {% endif %}
    </main>
    
    <footer>
      <div class="footer-content">
        <h3 class="footer-title">
          <i class="fas fa-university"></i>
          Sistema de Análisis de Infracciones
        </h3>
        <p class="footer-text">
          Desarrollado para el análisis de patrones de infracciones mediante clustering DBSCAN.
          Ingeniería de Sistemas - Universidad Nacional de Cañete
        </p>
      </div>
    </footer>
  </div>
  
  <div class="loading" id="loading">
    <div class="spinner"></div>
    <p>Procesando análisis DBSCAN...</p>
  </div>
  
  <script>
    // Crear partículas de fondo
    function createParticles() {
      const particlesContainer = document.getElementById('particles');
      const particleCount = 30;
      
      for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        const size = Math.random() * 5 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 6}s`;
        particle.style.animationDuration = `${Math.random() * 4 + 4}s`;
        
        particlesContainer.appendChild(particle);
      }
    }
    
    // Mostrar loading al enviar formulario
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function() {
        document.getElementById('loading').classList.add('active');
      });
    });
    
    // Animaciones de entrada
    document.addEventListener('DOMContentLoaded', function() {
      createParticles();
      
      const cards = document.querySelectorAll('.analysis-card, .stat-card, .nav-button');
      cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
          card.style.transition = 'opacity 0.8s cubic-bezier(0.23, 1, 0.320, 1), transform 0.8s cubic-bezier(0.23, 1, 0.320, 1)';
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, index * 50);
      });
      
      // Efecto parallax en el header
      window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const header = document.querySelector('header');
        if (header) {
          header.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
      });
      
      // Contador animado para stats
      const animateCounter = (element) => {
        const target = parseInt(element.textContent);
        if (isNaN(target)) return;
        
        const duration = 2000;
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
          current += increment;
          if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
          } else {
            element.textContent = Math.floor(current);
          }
        }, 16);
      };
      
      // Observer para animar contadores cuando son visibles
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const number = entry.target.querySelector('.stat-number');
            if (number && !number.classList.contains('animated')) {
              number.classList.add('animated');
              animateCounter(number);
            }
          }
        });
      }, { threshold: 0.5 });
      
      document.querySelectorAll('.stat-card').forEach(card => {
        observer.observe(card);
      });
      
      // Efecto hover en tabla
      const tableRows = document.querySelectorAll('.tabla-provincia tr');
      tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
          this.style.transition = 'all 0.3s ease';
        });
      });
    });
    
    // Efecto de ripple en botones
    document.querySelectorAll('.nav-button').forEach(button => {
      button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255,255,255,0.6)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s ease-out';
        ripple.style.pointerEvents = 'none';
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
      });
    });
    
    // Agregar animación ripple
    const style = document.createElement('style');
    style.textContent = `
      @keyframes ripple {
        to {
          transform: scale(2);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(TEMPLATE, provincias=PROVINCIAS, image=None, selected=None)


@app.route('/provincia')
def show_provincia():
    prov = request.args.get('prov')
    if prov not in PROVINCIAS:
        return "Provincia no válida", 400

    # 1) Generar gráfico via módulo DBSCAN
    try:
        module = importlib.import_module(f"SanMartin.{prov}")
        fig = module.main()
    except ImportError:
        return f"No se encontró el módulo para {prov}", 500
    except Exception as e:
        return f"Error al ejecutar el módulo {prov}: {e}", 500

    # Convertir figura a base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('ascii')

    # 2) Leer la hoja correspondiente desde el Excel
    try:
        hoja = prov.replace('_', ' ')
        df = pd.read_excel(EXCEL_PATH, sheet_name=hoja)
        tabla_html = df.to_html(classes='tabla-provincia', index=False)
    except Exception as e:
        tabla_html = f"<p><strong>Error al leer la tabla:</strong> {e}</p>"

    return render_template_string(
        TEMPLATE,
        provincias=PROVINCIAS,
        image=img_b64,
        selected=prov,
        tabla=tabla_html
    )


if __name__ == '__main__':
    app.run(debug=True)