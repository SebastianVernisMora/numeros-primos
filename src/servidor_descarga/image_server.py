#!/usr/bin/env python3
"""
Servidor Simple para Generador de Imágenes de Mapas de Números Primos
Solo renderiza y entrega imágenes PNG con colores, leyenda y parámetros.
"""

from flask import Flask, request, jsonify, send_file, Response
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import traceback

app = Flask(__name__)

# Página HTML simple para el generador de imágenes
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generador de Imágenes - Mapas de Números Primos</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
            padding: 2rem;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .title {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-label {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        .form-input, .form-select {
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }
        
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .types-section {
            margin-bottom: 2rem;
        }
        
        .types-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .types-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.75rem;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            padding: 0.5rem;
            border-radius: 6px;
            background: #f8fafc;
            transition: background 0.2s ease;
        }
        
        .checkbox-group:hover {
            background: #e2e8f0;
        }
        
        .checkbox-input {
            margin-right: 0.5rem;
            transform: scale(1.2);
        }
        
        .checkbox-label {
            font-weight: 500;
            color: #374151;
            cursor: pointer;
            flex: 1;
        }
        
        .generate-btn {
            width: 100%;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading-spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        .loading-spinner.active {
            display: inline-block;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result-area {
            margin-top: 2rem;
            padding: 1rem;
            background: #f1f5f9;
            border-radius: 8px;
            display: none;
        }
        
        .result-area.show {
            display: block;
        }
        
        .error {
            color: #dc2626;
            font-weight: 500;
        }
        
        .success {
            color: #16a34a;
            font-weight: 500;
        }
        
        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .types-grid {
                grid-template-columns: 1fr;
            }
            
            .title {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title"><i class="fas fa-image"></i> Generador de Imágenes</h1>
            <p class="subtitle">Mapas de Números Primos con Colores y Leyenda</p>
        </div>
        
        <form id="imageForm">
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">Número de Círculos</label>
                    <input type="number" class="form-input" id="num_circulos" value="10" min="3" max="25">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Divisiones por Círculo</label>
                    <input type="number" class="form-input" id="divisiones" value="24" min="6" max="60">
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
            
            // Mostrar loading
            btn.disabled = true;
            spinner.classList.add('active');
            icon.style.display = 'none';
            text.textContent = 'Generando imagen...';
            resultArea.classList.remove('show');
            
            try {
                // Recopilar parámetros
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
                
                console.log('Generando imagen con parámetros:', params);
                
                // Llamar a la API
                const response = await fetch('/generate-image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(params)
                });
                
                if (response.ok) {
                    // Descargar archivo
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `mapa_primos_${params.num_circulos}c_${params.divisiones_por_circulo}d_${params.tipo_mapeo}_${new Date().toISOString().slice(0,19).replace(/[:]/g, '-')}.png`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    // Mostrar éxito
                    resultMessage.innerHTML = '<div class="success"><i class="fas fa-check-circle"></i> ¡Imagen generada y descargada exitosamente!</div>';
                    resultArea.classList.add('show');
                } else {
                    const error = await response.json();
                    throw new Error(error.error || 'Error desconocido');
                }
                
            } catch (error) {
                console.error('Error:', error);
                resultMessage.innerHTML = `<div class="error"><i class="fas fa-exclamation-triangle"></i> Error: ${error.message}</div>`;
                resultArea.classList.add('show');
            } finally {
                // Ocultar loading
                btn.disabled = false;
                spinner.classList.remove('active');
                icon.style.display = 'inline';
                text.textContent = 'Generar y Descargar Imagen';
            }
        });
        
        console.log('✅ Generador de Imágenes cargado');
    </script>
</body>
</html>"""

@app.route('/')
def home():
    """Página principal del generador de imágenes."""
    return HTML_TEMPLATE

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """Generar y entregar imagen PNG del mapa."""
    try:
        parametros = request.get_json() or {}
        
        # Importar el creador de imágenes
        from image_creator import crear_imagen_mapa
        
        # Extraer parámetros
        num_circulos = parametros.get('num_circulos', 10)
        divisiones = parametros.get('divisiones_por_circulo', 24)
        tipo_mapeo = parametros.get('tipo_mapeo', 'lineal')
        dpi = parametros.get('dpi', 300)
        
        # Configurar tipos a mostrar
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
        
        print(f"🎨 Generando imagen: {num_circulos}c x {divisiones}d ({tipo_mapeo}) @ {dpi}DPI")
        
        # Crear imagen
        fig, filename, stats = crear_imagen_mapa(
            num_circulos, divisiones, tipo_mapeo, mostrar_tipos
        )
        
        # Guardar temporalmente
        temp_dir = tempfile.mkdtemp()
        filepath = Path(temp_dir) / filename
        
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        print(f"✅ Imagen generada: {filename} ({stats['total_elementos']} elementos)")
        
        # Crear función de limpieza
        def cleanup():
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        # Enviar archivo y programar limpieza
        response = send_file(filepath, as_attachment=True, 
                           download_name=filename, mimetype='image/png')
        
        # Limpiar después de enviar (programado)
        import threading
        threading.Timer(30.0, cleanup).start()
        
        return response
        
    except Exception as e:
        print(f"❌ Error generando imagen: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Error generando imagen: {str(e)}'}), 500

@app.route('/api/info')
def api_info():
    """Información de la API."""
    return jsonify({
        'name': 'Generador de Imágenes de Mapas Primos',
        'version': '1.0.0',
        'description': 'Genera imágenes PNG con colores, leyenda y parámetros',
        'endpoints': {
            '/': 'Interfaz web',
            '/generate-image': 'Generar imagen (POST)',
            '/api/info': 'Información de la API'
        },
        'supported_formats': ['PNG'],
        'supported_mappings': ['lineal', 'logaritmico', 'arquimedes', 'fibonacci'],
        'supported_dpi': [150, 300, 600],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🎨 Iniciando Generador de Imágenes de Mapas Primos...")
    
    # Configurar argumentos
    import sys
    port = 3002
    host = '0.0.0.0'
    
    for i, arg in enumerate(sys.argv):
        if arg == '--port' and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
        elif arg == '--host' and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
    
    print(f"🌐 Servidor disponible en: http://{host}:{port}/")
    print(f"🖼️ Interfaz: http://{host}:{port}/")
    print(f"📊 API Info: http://{host}:{port}/api/info")
    
    # Iniciar servidor
    app.run(host=host, port=port, debug=False)