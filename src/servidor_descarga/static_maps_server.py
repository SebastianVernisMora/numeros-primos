#!/usr/bin/env python3
"""
Servidor Optimizado para Mapas Pregenerados
Soporta hasta 10,000 círculos × 1,300 segmentos
Sirve datos pregenerados desde static_maps/
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
import gzip
import io

app = Flask(__name__)
CORS(app)

# Configuración
STATIC_MAPS_DIR = Path(__file__).parent.resolve() / "static_maps"
CACHE_INDEX = {}
COMPRESSION_ENABLED = True

def cargar_indice_mapas():
    """Cargar índice de mapas pregenerados."""
    global CACHE_INDEX
    try:
        index_file = STATIC_MAPS_DIR / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                data = json.load(f)
                CACHE_INDEX = data.get('maps', {}) if isinstance(data, dict) else {}
            print(f"✅ Índice cargado: {len(CACHE_INDEX)} mapas disponibles")
            return True
        else:
            print(f"⚠️ Archivo de índice no encontrado: {index_file}")
    except Exception as e:
        print(f"❌ Error cargando índice: {e}")
        import traceback
        traceback.print_exc()

    CACHE_INDEX = {}
    return False

def generar_hash_parametros(parametros):
    """Generar hash único para parámetros."""
    param_hash = {
        'num_circulos': parametros.get('num_circulos'),
        'divisiones_por_circulo': parametros.get('divisiones_por_circulo'),
        'tipo_mapeo': parametros.get('tipo_mapeo', 'lineal'),
        'filtros': parametros.get('filtros', {})
    }
    param_str = json.dumps(param_hash, sort_keys=True)
    return hashlib.md5(param_str.encode()).hexdigest()[:12]

def comprimir_respuesta(data):
    """Comprimir respuesta JSON con gzip si está habilitado."""
    if not COMPRESSION_ENABLED:
        return data

    json_str = json.dumps(data, separators=(',', ':'))
    compressed = gzip.compress(json_str.encode('utf-8'))
    return compressed

@app.route('/')
def index():
    """Página de inicio con estadísticas."""
    total_maps = len(CACHE_INDEX)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Servidor de Mapas Pregenerados</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                margin: 0;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 2rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }}
            h1 {{
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }}
            .stat-card {{
                background: rgba(255, 255, 255, 0.2);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 3rem;
                font-weight: bold;
                color: #FFD700;
            }}
            .stat-label {{
                font-size: 1.1rem;
                margin-top: 0.5rem;
                opacity: 0.9;
            }}
            .endpoints {{
                margin-top: 2rem;
            }}
            .endpoint {{
                background: rgba(0, 0, 0, 0.3);
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
            }}
            .method {{
                display: inline-block;
                padding: 0.3rem 0.8rem;
                border-radius: 5px;
                font-weight: bold;
                margin-right: 1rem;
            }}
            .get {{ background: #28a745; }}
            .post {{ background: #007bff; }}
            code {{
                background: rgba(0, 0, 0, 0.5);
                padding: 0.2rem 0.5rem;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ Servidor de Mapas Pregenerados</h1>
            <p style="text-align: center; font-size: 1.2rem;">
                Capacidad: <strong>10,000 círculos × 1,300 segmentos</strong>
            </p>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_maps:,}</div>
                    <div class="stat-label">Mapas Disponibles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">13M</div>
                    <div class="stat-label">Elementos Máximos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">10K</div>
                    <div class="stat-label">Círculos Máx</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">1.3K</div>
                    <div class="stat-label">Segmentos Máx</div>
                </div>
            </div>

            <div class="endpoints">
                <h2>📡 API Endpoints</h2>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/api/maps</code>
                    <p>Listar todos los mapas disponibles con sus parámetros</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/api/map/&lt;hash&gt;</code>
                    <p>Obtener datos de un mapa específico por su hash</p>
                </div>

                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/api/get-map</code>
                    <p>Obtener mapa por parámetros específicos</p>
                    <pre style="margin-top: 0.5rem;">{{
  "num_circulos": 10000,
  "divisiones_por_circulo": 1300,
  "tipo_mapeo": "lineal",
  "filtros": {{"primos": true, "compuestos": true}}
}}</pre>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/api/stats</code>
                    <p>Obtener estadísticas del servidor y generación</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/static_maps/&lt;filename&gt;</code>
                    <p>Acceso directo a archivos de mapas pregenerados</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/api/maps')
def listar_mapas():
    """Listar todos los mapas disponibles."""
    try:
        # Escanear directorio de mapas
        mapas = []
        for json_file in STATIC_MAPS_DIR.glob("data_*.json"):
            hash_id = json_file.stem.replace("data_", "")
            file_size = json_file.stat().st_size

            # Buscar info en índice
            info = CACHE_INDEX.get(hash_id, {})

            mapas.append({
                'hash': hash_id,
                'file': json_file.name,
                'size_bytes': file_size,
                'size_kb': round(file_size / 1024, 2),
                'parametros': info.get('parametros', {}),
                'elementos_count': info.get('elementos_count', 0),
                'primos_count': info.get('primos_count', 0)
            })

        # Ordenar por tamaño de mapa (círculos × segmentos)
        mapas.sort(key=lambda x: (
            x['parametros'].get('num_circulos', 0) *
            x['parametros'].get('divisiones_por_circulo', 0)
        ))

        return jsonify({
            'success': True,
            'total': len(mapas),
            'maps': mapas,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/map/<hash_id>')
def obtener_mapa_por_hash(hash_id):
    """Obtener datos de un mapa específico por hash."""
    try:
        json_file = STATIC_MAPS_DIR / f"data_{hash_id}.json"

        if not json_file.exists():
            return jsonify({
                'success': False,
                'error': 'Mapa no encontrado'
            }), 404

        with open(json_file, 'r') as f:
            data = json.load(f)

        # Agregar metadata
        data['hash'] = hash_id
        data['file_size'] = json_file.stat().st_size
        data['served_at'] = datetime.now().isoformat()

        # Comprimir si es necesario
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding and COMPRESSION_ENABLED:
            compressed = comprimir_respuesta(data)
            response = app.make_response(compressed)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Type'] = 'application/json'
            return response

        return jsonify(data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-map', methods=['POST'])
def obtener_mapa_por_parametros():
    """Obtener mapa por parámetros específicos."""
    try:
        parametros = request.json

        # Generar hash
        hash_id = generar_hash_parametros(parametros)

        json_file = STATIC_MAPS_DIR / f"data_{hash_id}.json"

        if not json_file.exists():
            # Buscar alternativas similares
            alternativas = []
            num_circulos = parametros.get('num_circulos')
            divisiones = parametros.get('divisiones_por_circulo')

            for mapa_hash, mapa_info in CACHE_INDEX.items():
                params = mapa_info.get('parametros', {})
                if (params.get('num_circulos') == num_circulos and
                    params.get('divisiones_por_circulo') == divisiones):
                    alternativas.append({
                        'hash': mapa_hash,
                        'parametros': params
                    })

            return jsonify({
                'success': False,
                'error': 'Mapa no encontrado',
                'requested_hash': hash_id,
                'requested_params': parametros,
                'alternatives': alternativas[:5]  # Máximo 5 alternativas
            }), 404

        with open(json_file, 'r') as f:
            data = json.load(f)

        data['hash'] = hash_id
        data['matched_params'] = parametros

        return jsonify(data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def obtener_estadisticas():
    """Obtener estadísticas del servidor."""
    try:
        # Contar archivos
        total_files = len(list(STATIC_MAPS_DIR.glob("data_*.json")))
        total_size = sum(f.stat().st_size for f in STATIC_MAPS_DIR.glob("data_*.json"))

        # Estadísticas del generador
        stats_file = Path("background_generator_stats.json")
        generator_stats = {}
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                generator_stats = json.load(f)

        # Rangos disponibles
        rangos = {
            'min_circulos': None,
            'max_circulos': None,
            'min_segmentos': None,
            'max_segmentos': None
        }

        for mapa_info in CACHE_INDEX.values():
            params = mapa_info.get('parametros', {})
            circulos = params.get('num_circulos', 0)
            segmentos = params.get('divisiones_por_circulo', 0)

            if rangos['min_circulos'] is None or circulos < rangos['min_circulos']:
                rangos['min_circulos'] = circulos
            if rangos['max_circulos'] is None or circulos > rangos['max_circulos']:
                rangos['max_circulos'] = circulos
            if rangos['min_segmentos'] is None or segmentos < rangos['min_segmentos']:
                rangos['min_segmentos'] = segmentos
            if rangos['max_segmentos'] is None or segmentos > rangos['max_segmentos']:
                rangos['max_segmentos'] = segmentos

        return jsonify({
            'success': True,
            'maps': {
                'total': total_files,
                'indexed': len(CACHE_INDEX),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            },
            'ranges': rangos,
            'generator': generator_stats,
            'capabilities': {
                'max_circulos': 10000,
                'max_segmentos': 1300,
                'max_elements': 13000000
            },
            'server': {
                'compression_enabled': COMPRESSION_ENABLED,
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static_maps/<path:filename>')
def servir_archivo_estatico(filename):
    """Servir archivos estáticos directamente."""
    try:
        return send_from_directory(STATIC_MAPS_DIR, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/health')
def health_check():
    """Health check para monitoreo."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'maps_loaded': len(CACHE_INDEX)
    })

if __name__ == '__main__':
    print("🚀 Iniciando Servidor de Mapas Pregenerados")
    print("=" * 60)
    print(f"📁 Directorio de mapas: {STATIC_MAPS_DIR}")
    print(f"🗺️ Capacidad: 10,000 círculos × 1,300 segmentos")
    print("=" * 60)

    # Crear directorio si no existe
    STATIC_MAPS_DIR.mkdir(exist_ok=True)

    # Cargar índice
    cargar_indice_mapas()

    print(f"✅ Servidor listo - {len(CACHE_INDEX)} mapas cargados")
    print("🌐 Escuchando en http://0.0.0.0:3000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=3000, debug=False)
