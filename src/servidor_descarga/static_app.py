#!/usr/bin/env python3
"""
Servidor Unificado - Puerto 3000
Mapa Interactivo + Generador de Imágenes en endpoints separados
"""

from flask import Flask, request, jsonify, send_file, Response
import os
import json
import math
import hashlib
from datetime import datetime
from pathlib import Path
import socket
import traceback
import tempfile
import shutil

app = Flask(__name__)

# Configuración
STATIC_MAPS_DIR = Path(__file__).parent.resolve() / "static_maps"
CACHE_INDEX = None

def cargar_indice_mapas():
    """Cargar índice de mapas pre-generados."""
    global CACHE_INDEX
    try:
        index_file = STATIC_MAPS_DIR / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                CACHE_INDEX = json.load(f)
            print(f"✅ Índice cargado: {len(CACHE_INDEX.get('maps', {}))} mapas")
            return True
    except Exception as e:
        print(f"⚠️ Error cargando índice: {e}")
        CACHE_INDEX = {'maps': {}, 'total_count': 0, 'generated_at': datetime.now().isoformat()}
    return False

def es_primo(n):
    """Verifica si un número es primo."""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True

def clasificar_numero_completo(n):
    """Clasifica un número con todos los tipos de primos."""
    tipos = []
    
    if es_primo(n):
        tipos.append('primo')
        
        # Primos gemelos
        if n > 2 and es_primo(n-2): tipos.append('gemelo')
        if n < 1000000 and es_primo(n+2): tipos.append('gemelo')
        
        # Primos primos (diferencia de 4)
        if n > 4 and es_primo(n-4): tipos.append('primo_primo')
        if n < 1000000 and es_primo(n+4): tipos.append('primo_primo')
        
        # Primos sexy (diferencia de 6)
        if n > 6 and es_primo(n-6): tipos.append('sexy')
        if n < 1000000 and es_primo(n+6): tipos.append('sexy')
        
        # Sophie Germain
        if n < 500000 and es_primo(2*n + 1): tipos.append('sophie_germain')
        
        # Palíndromos
        if str(n) == str(n)[::-1] and len(str(n)) > 1:
            tipos.append('palindromico')
        
        # Mersenne (2^p - 1)
        temp = n + 1
        if temp > 1 and (temp & (temp - 1)) == 0:
            p = int(math.log2(temp))
            if es_primo(p): tipos.append('mersenne')
        
        # Fermat (2^(2^n) + 1)  
        if n > 3:
            temp = n - 1
            if temp > 0 and (temp & (temp - 1)) == 0:
                k = int(math.log2(temp))
                if (k & (k - 1)) == 0:
                    tipos.append('fermat')
        
        # Si no tiene tipos especiales, es regular
        if len(tipos) == 1:
            tipos = ['regular']
    else:
        tipos = ['compuesto']
    
    return tipos

def generar_mapa_dinamico(parametros):
    """Genera un mapa dinámico con clasificación completa."""
    num_circulos = parametros.get('num_circulos', 10)
    divisiones = parametros.get('divisiones_por_circulo', 24)
    tipo_mapeo = parametros.get('tipo_mapeo', 'lineal')
    
    limite = num_circulos * divisiones
    elementos = []
    
    print(f"🔄 Generando mapa dinámico: {num_circulos}c x {divisiones}d ({limite} elementos)")
    
    # Funciones de mapeo
    def mapeo_lineal(n):
        circulo = n // divisiones
        segmento = n % divisiones
        return min(circulo, num_circulos - 1), segmento
    
    def mapeo_logaritmico(n):
        if n <= 0: return 0, 0
        log_pos = math.log(n + 1) / math.log(limite + 1)
        pos_total = int(log_pos * num_circulos * divisiones)
        circulo = min(pos_total // divisiones, num_circulos - 1)
        segmento = pos_total % divisiones
        return circulo, segmento
    
    def mapeo_arquimedes(n):
        if n <= 0: return 0, 0
        theta = 2 * math.pi * math.sqrt(n / limite)
        r = math.sqrt(n / limite) * num_circulos
        circulo = min(int(r), num_circulos - 1)
        segmento = int((theta % (2 * math.pi)) / (2 * math.pi) * divisiones)
        return circulo, segmento
    
    def mapeo_fibonacci(n):
        if n <= 0: return 0, 0
        phi = (1 + math.sqrt(5)) / 2
        theta = 2 * math.pi * n / phi
        r = math.sqrt(n) / math.sqrt(limite) * num_circulos
        circulo = min(int(r), num_circulos - 1)
        segmento = int((theta % (2 * math.pi)) / (2 * math.pi) * divisiones)
        return circulo, segmento
    
    # Seleccionar función de mapeo
    mapeos = {
        'lineal': mapeo_lineal,
        'logaritmico': mapeo_logaritmico,
        'arquimedes': mapeo_arquimedes,
        'fibonacci': mapeo_fibonacci
    }
    mapeo_func = mapeos.get(tipo_mapeo, mapeo_lineal)
    
    # Generar elementos
    for n in range(1, limite + 1):
        circulo, segmento = mapeo_func(n)
        
        # Calcular posición
        angulo = (segmento * 360) / divisiones
        radio = circulo + 1
        
        elementos.append({
            'numero': n,
            'circulo': circulo,
            'segmento': segmento,
            'es_primo': es_primo(n),
            'tipos': clasificar_numero_completo(n),
            'posicion': {
                'radio': radio,
                'angulo': angulo,
                'x': radio * math.cos(math.radians(angulo)),
                'y': radio * math.sin(math.radians(angulo))
            }
        })
    
    # Calcular estadísticas
    total_primos = sum(1 for e in elementos if e['es_primo'])
    estadisticas = {
        'total_elementos': len(elementos),
        'total_primos': total_primos,
        'total_compuestos': len(elementos) - total_primos,
        'densidad_primos': (total_primos / len(elementos)) * 100 if elementos else 0
    }
    
    return {
        'elementos': elementos,
        'estadisticas': estadisticas,
        'metadata': {
            'num_circulos': num_circulos,
            'divisiones_por_circulo': divisiones,
            'tipo_mapeo': tipo_mapeo,
            'limite': limite
        }
    }

# ===== RUTAS INTERACTIVAS =====

@app.route('/')
def home():
    """Página principal - Selector de servicios."""
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapas de Números Primos - Servicios</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea, #764ba2);
            margin: 0; padding: 2rem; min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }
        .container { 
            background: white; padding: 3rem; border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); text-align: center;
            max-width: 600px;
        }
        h1 { color: #333; font-size: 2.5rem; margin-bottom: 1rem; }
        .subtitle { color: #666; font-size: 1.2rem; margin-bottom: 3rem; }
        .service { 
            background: #f8f9fa; padding: 2rem; margin: 1rem 0; 
            border-radius: 15px; border: 2px solid #e9ecef;
            transition: all 0.3s ease; cursor: pointer;
        }
        .service:hover { 
            transform: translateY(-5px); 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        .service h3 { color: #667eea; font-size: 1.5rem; margin-bottom: 0.5rem; }
        .service p { color: #666; margin: 0; }
        .btn { 
            background: #667eea; color: white; padding: 1rem 2rem;
            border: none; border-radius: 8px; font-size: 1.1rem;
            text-decoration: none; display: inline-block; margin-top: 1rem;
            transition: background 0.3s ease;
        }
        .btn:hover { background: #5a6fd8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔢 Mapas de Números Primos</h1>
        <p class="subtitle">Selecciona el servicio que deseas usar</p>
        
        <div class="service" onclick="window.location='/interactive'">
            <h3>🗺️ Mapa Interactivo</h3>
            <p>Visualización interactiva con zoom, drag y tooltips</p>
            <a href="/interactive" class="btn">Abrir Mapa Interactivo</a>
        </div>
        
        <div class="service" onclick="window.location='/images'">
            <h3>🎨 Generador de Imágenes</h3>
            <p>Genera imágenes PNG de alta calidad para descarga</p>
            <a href="/images" class="btn">Abrir Generador de Imágenes</a>
        </div>
    </div>
</body>
</html>"""

@app.route('/interactive')
def interactive_creator():
    """Mapa Interactivo."""
    return send_file(Path(__file__).parent / "interactive.html")

@app.route('/images')
def image_generator():
    """Generador de Imágenes."""
    # HTML del generador de imágenes inline
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generador de Imágenes - Mapas de Números Primos</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 2rem;
        }
        .container {
            max-width: 800px; margin: 0 auto; background: rgba(255, 255, 255, 0.95);
            border-radius: 20px; padding: 2rem; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { text-align: center; margin-bottom: 2rem; }
        .title {
            font-size: 2.5rem; font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle { color: #666; font-size: 1.1rem; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
        .form-group { display: flex; flex-direction: column; }
        .form-label { font-weight: 600; color: #333; margin-bottom: 0.5rem; font-size: 0.9rem; }
        .form-input, .form-select {
            padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 8px;
            font-size: 1rem; transition: all 0.3s ease; background: white;
        }
        .form-input:focus, .form-select:focus {
            outline: none; border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .types-section { margin-bottom: 2rem; }
        .types-title { font-size: 1.2rem; font-weight: 600; color: #333; margin-bottom: 1rem; text-align: center; }
        .types-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; }
        .checkbox-group {
            display: flex; align-items: center; padding: 0.5rem; border-radius: 6px;
            background: #f8fafc; transition: background 0.2s ease;
        }
        .checkbox-group:hover { background: #e2e8f0; }
        .checkbox-input { margin-right: 0.5rem; transform: scale(1.2); }
        .checkbox-label { font-weight: 500; color: #374151; cursor: pointer; flex: 1; }
        .generate-btn {
            width: 100%; padding: 1rem 2rem; background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border: none; border-radius: 12px; font-size: 1.1rem; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center;
            justify-content: center; gap: 0.5rem;
        }
        .generate-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        .generate-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .loading-spinner {
            display: none; width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3);
            border-top: 2px solid white; border-radius: 50%; animation: spin 1s linear infinite;
        }
        .loading-spinner.active { display: inline-block; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .result-area { margin-top: 2rem; padding: 1rem; background: #f1f5f9; border-radius: 8px; display: none; }
        .result-area.show { display: block; }
        .error { color: #dc2626; font-weight: 500; }
        .success { color: #16a34a; font-weight: 500; }
        .nav-link {
            position: absolute; top: 1rem; left: 1rem; background: rgba(255,255,255,0.9);
            padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; color: #667eea;
            font-weight: 600; transition: all 0.3s ease;
        }
        .nav-link:hover { background: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        @media (max-width: 768px) {
            .form-grid { grid-template-columns: 1fr; }
            .types-grid { grid-template-columns: 1fr; }
            .title { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <a href="/" class="nav-link"><i class="fas fa-home"></i> Inicio</a>
    
    <div class="container">
        <div class="header">
            <h1 class="title"><i class="fas fa-image"></i> Generador de Imágenes</h1>
            <p class="subtitle">Mapas de Números Primos con Colores y Leyenda</p>
        </div>
        
        <form id="imageForm">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">Número de Círculos</label>
                    <input type="number" class="form-input" id="num_circulos" value="10" min="3" max="10000">
                    <small style="color: #666; font-size: 0.8rem; margin-top: 0.25rem;">
                        Valores grandes (>100) pueden tardar varios minutos
                    </small>
                </div>
                <div class="form-group">
                    <label class="form-label">Divisiones por Círculo</label>
                    <input type="number" class="form-input" id="divisiones" value="24" min="6" max="10000">
                    <small style="color: #666; font-size: 0.8rem; margin-top: 0.25rem;">
                        Total elementos = círculos × divisiones
                    </small>
                </div>
                <div class="form-group">
                    <label class="form-label">Tipo de Mapeo</label>
                    <select class="form-select" id="tipo_mapeo">
                        <option value="lineal">Lineal</option>
                        <option value="logaritmico">Logarítmico</option>
                        <option value="arquimedes">Espiral de Arquímedes</option>
                        <option value="fibonacci">Espiral de Fibonacci</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Resolución (DPI)</label>
                    <select class="form-select" id="dpi">
                        <option value="150">150 DPI (Rápido)</option>
                        <option value="300" selected>300 DPI (Alta Calidad)</option>
                        <option value="600">600 DPI (Máxima Calidad)</option>
                    </select>
                </div>
            </div>
            
            <div class="types-section">
                <h3 class="types-title">Tipos de Números a Incluir</h3>
                <div class="types-grid">
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_regular" class="checkbox-input" checked>
                        <label for="show_regular" class="checkbox-label">Primos Regulares</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_twins" class="checkbox-input" checked>
                        <label for="show_twins" class="checkbox-label">Primos Gemelos</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_cousins" class="checkbox-input" checked>
                        <label for="show_cousins" class="checkbox-label">Primos Primos</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_sexy" class="checkbox-input" checked>
                        <label for="show_sexy" class="checkbox-label">Primos Sexy</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_sophie" class="checkbox-input" checked>
                        <label for="show_sophie" class="checkbox-label">Sophie Germain</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_palindromic" class="checkbox-input" checked>
                        <label for="show_palindromic" class="checkbox-label">Palíndromos</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_mersenne" class="checkbox-input" checked>
                        <label for="show_mersenne" class="checkbox-label">Mersenne</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="show_fermat" class="checkbox-input" checked>
                        <label for="show_fermat" class="checkbox-label">Fermat</label>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="generate-btn" id="generateBtn">
                <div class="loading-spinner" id="loadingSpinner"></div>
                <i class="fas fa-download" id="btnIcon"></i>
                <span id="btnText">Generar y Descargar Imagen</span>
            </button>
        </form>
        
        <div class="result-area" id="resultArea">
            <div id="resultMessage"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('imageForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const btn = document.getElementById('generateBtn');
            const spinner = document.getElementById('loadingSpinner');
            const icon = document.getElementById('btnIcon');
            const text = document.getElementById('btnText');
            const resultArea = document.getElementById('resultArea');
            const resultMessage = document.getElementById('resultMessage');
            
            btn.disabled = true;
            spinner.classList.add('active');
            icon.style.display = 'none';
            text.textContent = 'Generando imagen...';
            resultArea.classList.remove('show');
            
            try {
                const params = {
                    num_circulos: parseInt(document.getElementById('num_circulos').value),
                    divisiones_por_circulo: parseInt(document.getElementById('divisiones').value),
                    tipo_mapeo: document.getElementById('tipo_mapeo').value,
                    dpi: parseInt(document.getElementById('dpi').value),
                    mostrar_regulares: document.getElementById('show_regular').checked,
                    mostrar_gemelos: document.getElementById('show_twins').checked,
                    mostrar_primos: document.getElementById('show_cousins').checked,
                    mostrar_sexy: document.getElementById('show_sexy').checked,
                    mostrar_sophie_germain: document.getElementById('show_sophie').checked,
                    mostrar_palindromicos: document.getElementById('show_palindromic').checked,
                    mostrar_mersenne: document.getElementById('show_mersenne').checked,
                    mostrar_fermat: document.getElementById('show_fermat').checked
                };
                
                // Validación para números grandes
                const total_elementos = params.num_circulos * params.divisiones_por_circulo;
                if (total_elementos > 100000) {
                    const confirmar = confirm(`⚠️ ADVERTENCIA: Vas a generar ${total_elementos.toLocaleString()} elementos.\\n\\nEsto puede tardar varios minutos y usar mucha memoria.\\n\\n¿Continuar?`);
                    if (!confirmar) {
                        return;
                    }
                    text.textContent = 'Generando imagen grande... (puede tardar minutos)';
                } else if (total_elementos > 10000) {
                    text.textContent = 'Generando imagen... (esto puede tardar un poco)';
                }
                
                const response = await fetch('/api/generate-image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `mapa_primos_${params.num_circulos}c_${params.divisiones_por_circulo}d_${params.tipo_mapeo}_${new Date().toISOString().slice(0,19).replace(/[:]/g, '-')}.png`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    resultMessage.innerHTML = '<div class="success"><i class="fas fa-check-circle"></i> ¡Imagen generada y descargada exitosamente!</div>';
                    resultArea.classList.add('show');
                } else {
                    const error = await response.json();
                    throw new Error(error.error || 'Error desconocido');
                }
            } catch (error) {
                resultMessage.innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> Error: ${error.message}</div>`;
                resultArea.classList.add('show');
            } finally {
                btn.disabled = false;
                spinner.classList.remove('active');
                icon.style.display = 'inline';
                text.textContent = 'Generar y Descargar Imagen';
            }
        });
    </script>
</body>
</html>"""

# ===== APIS INTERACTIVAS =====

@app.route('/api/interactive-map', methods=['POST', 'OPTIONS'])
def get_interactive_map():
    """API para el mapa interactivo."""
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        parametros = request.get_json() or {}
        data = generar_mapa_dinamico(parametros)
        
        response = jsonify({
            'elementos': data['elementos'],
            'estadisticas': data['estadisticas'], 
            'metadata': data['metadata'],
            'timestamp': datetime.now().isoformat(),
            'version': '3.4.0-unified',
            'source': 'generated-dynamic',
            'note': 'Mapa interactivo con clasificación completa'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    except Exception as e:
        print(f"❌ Error mapa interactivo: {e}")
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/number/<int:numero>')
def get_number_info(numero):
    """Info detallada de números."""
    info = {
        'numero': numero,
        'es_primo': es_primo(numero),
        'clasificaciones': clasificar_numero_completo(numero),
        'propiedades': {
            'par': numero % 2 == 0,
            'cuadrado_perfecto': int(numero**0.5)**2 == numero,
            'digitos': len(str(numero)),
            'suma_digitos': sum(int(d) for d in str(numero))
        }
    }
    
    response = jsonify(info)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# ===== APIS DE IMÁGENES =====

@app.route('/api/generate-image', methods=['POST', 'OPTIONS'])
def generate_image():
    """Generar imagen PNG optimizada."""
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        parametros = request.get_json() or {}
        
        from image_creator import crear_imagen_mapa
        
        num_circulos = parametros.get('num_circulos', 10)
        divisiones = parametros.get('divisiones_por_circulo', 24)
        tipo_mapeo = parametros.get('tipo_mapeo', 'lineal')
        dpi = parametros.get('dpi', 300)
        
        mostrar_tipos = {
            'primo_regular': parametros.get('mostrar_regulares', True),
            'primo_gemelo': parametros.get('mostrar_gemelos', True),
            'primo_primo': parametros.get('mostrar_primos', True),
            'primo_sexy': parametros.get('mostrar_sexy', True),
            'sophie_germain': parametros.get('mostrar_sophie_germain', True),
            'palindromico': parametros.get('mostrar_palindromicos', True),
            'mersenne': parametros.get('mostrar_mersenne', True),
            'fermat': parametros.get('mostrar_fermat', True)
        }
        
        total_elementos = num_circulos * divisiones
        print(f"🎨 Generando imagen: {num_circulos}c x {divisiones}d ({total_elementos:,} elementos) @ {dpi}DPI")
        
        # Advertencia para números grandes
        if total_elementos > 100000:
            print(f"⚠️ IMAGEN GRANDE: {total_elementos:,} elementos - esto puede tardar varios minutos...")
        elif total_elementos > 10000:
            print(f"⚡ IMAGEN MEDIANA: {total_elementos:,} elementos - procesando...")
        
        fig, filename, stats = crear_imagen_mapa(num_circulos, divisiones, tipo_mapeo, mostrar_tipos)
        
        temp_dir = tempfile.mkdtemp()
        filepath = Path(temp_dir) / filename
        
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
        
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        print(f"✅ Imagen generada: {filename} ({stats['total_elementos']} primos)")
        
        def cleanup():
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        response = send_file(filepath, as_attachment=True, download_name=filename, mimetype='image/png')
        response.headers['Access-Control-Allow-Origin'] = '*'
        
        import threading
        threading.Timer(30.0, cleanup).start()
        
        return response
        
    except Exception as e:
        print(f"❌ Error generando imagen: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Error generando imagen: {str(e)}'}), 500

@app.route('/api/info')
def api_info():
    """Información general de la API."""
    return jsonify({
        'name': 'Servidor Unificado de Mapas Primos',
        'version': '3.4.0-unified',
        'description': 'Mapa interactivo y generador de imágenes en un solo puerto',
        'services': {
            'interactive': {
                'path': '/interactive',
                'description': 'Visualización interactiva con zoom y tooltips',
                'api': '/api/interactive-map'
            },
            'images': {
                'path': '/images', 
                'description': 'Generador de imágenes PNG optimizado',
                'api': '/api/generate-image'
            }
        },
        'port': 3000,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Servidor Unificado (Puerto 3000)...")
    
    cargar_indice_mapas()
    
    import sys
    port = 3000
    host = '0.0.0.0'
    
    for i, arg in enumerate(sys.argv):
        if arg == '--port' and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
        elif arg == '--host' and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
    
    print(f"🌐 Servidor disponible en: http://{host}:{port}/")
    print(f"🗺️ Mapa Interactivo: http://{host}:{port}/interactive")
    print(f"🎨 Generador Imágenes: http://{host}:{port}/images")
    
    app.run(host=host, port=port, debug=False)