#!/usr/bin/env python3
"""
Aplicación Flask que sirve mapas pre-generados estáticos para máximo rendimiento.
No hace cálculos en tiempo real - usa archivos HTML/JSON pre-calculados.
"""

from flask import Flask, request, jsonify, send_from_directory, send_file, Response
import os
import json
import hashlib
import math
from datetime import datetime
import traceback
from pathlib import Path
import socket

app = Flask(__name__)

# Configuración
STATIC_MAPS_DIR = Path("/home/admin/servidor_descarga/static_maps")
CACHE_INDEX = None

def cargar_indice_mapas():
    """Cargar índice de mapas pre-generados."""
    global CACHE_INDEX
    try:
        with open(STATIC_MAPS_DIR / "index.json", 'r') as f:
            CACHE_INDEX = json.load(f)
        print(f"✅ Índice cargado: {len(CACHE_INDEX['maps'])} mapas disponibles")
        return True
    except Exception as e:
        print(f"❌ Error cargando índice: {e}")
        return False

def generar_hash_parametros(parametros):
    """Generar hash para combinación de parámetros."""
    # Normalizar parámetros para matching consistente
    normalized = {
        'num_circulos': int(parametros.get('num_circulos', 10)),
        'divisiones_por_circulo': int(parametros.get('divisiones_por_circulo', 24)),
        'tipo_mapeo': parametros.get('tipo_mapeo', 'lineal'),
        'filtros': {
            'regulares': parametros.get('mostrar_regulares', True),
            'gemelos': parametros.get('mostrar_gemelos', True),
            'primos': parametros.get('mostrar_primos', True),
            'sexy': parametros.get('mostrar_sexy', False),
            'sophie_germain': parametros.get('mostrar_sophie_germain', False),
            'palindromicos': parametros.get('mostrar_palindromicos', False),
            'mersenne': parametros.get('mostrar_mersenne', False),
            'fermat': parametros.get('mostrar_fermat', False),
            'compuestos': parametros.get('mostrar_compuestos', True)
        }
    }
    
    param_str = json.dumps(normalized, sort_keys=True)
    return hashlib.md5(param_str.encode()).hexdigest()[:12]

def encontrar_mapa_similar(parametros):
    """Encontrar el mapa pre-generado más similar a los parámetros solicitados."""
    if not CACHE_INDEX:
        return None
    
    target_circulos = int(parametros.get('num_circulos', 10))
    target_divisiones = int(parametros.get('divisiones_por_circulo', 24))
    target_mapeo = parametros.get('tipo_mapeo', 'lineal')
    
    mejores_matches = []
    
    # Verificar si maps es dict o list
    maps_data = CACHE_INDEX['maps']
    if isinstance(maps_data, list):
        # Si es lista vacía, usar archivos estáticos disponibles
        archivos_json = list(STATIC_MAPS_DIR.glob("data_*.json"))
        if archivos_json:
            archivo_aleatorio = archivos_json[0]
            return {'archivo': archivo_aleatorio.name, 'score': 0.5}
        return None
    
    for map_hash, info in maps_data.items():
        param_map = info['parametros']
        
        # Calcular score de similitud
        score = 0
        
        # Exactitud en mapeo (más importante)
        if param_map['tipo_mapeo'] == target_mapeo:
            score += 50
        
        # Proximidad en círculos
        diff_circulos = abs(param_map['num_circulos'] - target_circulos)
        score += max(0, 25 - diff_circulos * 5)
        
        # Proximidad en divisiones  
        diff_divisiones = abs(param_map['divisiones_por_circulo'] - target_divisiones)
        score += max(0, 25 - diff_divisiones * 2)
        
        mejores_matches.append({
            'hash': map_hash,
            'info': info,
            'score': score
        })
    
    # Ordenar por score y retornar el mejor
    mejores_matches.sort(key=lambda x: x['score'], reverse=True)
    
    if mejores_matches and mejores_matches[0]['score'] > 30:
        return mejores_matches[0]
    
    return None

@app.route('/')
def home():
    """Página principal - interfaz mejorada interactiva."""
    return send_file(STATIC_MAPS_DIR / "index.html")

@app.route('/interactive')
def interactive_creator():
    """Creador interactivo de mapas."""
    return send_file(Path(__file__).parent / "interactive.html")

@app.route('/enhanced')
def enhanced_interface():
    """Interfaz mejorada - redirigir a selector."""
    return send_file(STATIC_MAPS_DIR / "index.html")

@app.route('/api/interactive-map', methods=['POST', 'OPTIONS'])
def get_pregenerated_map():
    """API que retorna datos de mapas pre-generados."""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        parametros = request.get_json() or {}
        
        # Intentar encontrar mapa exacto
        param_hash = generar_hash_parametros(parametros)
        
        # Buscar en archivos JSON pre-generados
        json_file = STATIC_MAPS_DIR / f"data_{param_hash}.json"
        
        if json_file.exists():
            # Mapa exacto encontrado
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Mapa exacto servido: {param_hash}")
            return jsonify({
                'elementos': data['elementos'],
                'estadisticas': data['estadisticas'],
                'timestamp': datetime.now().isoformat(),
                'version': '3.3.0-enhanced',
                'source': 'pre-generated-exact',
                'hash': param_hash
            })
        
        else:
            # Buscar mapa similar
            match = encontrar_mapa_similar(parametros)
            
            if match:
                # Usar archivo directo si no hay estructura completa
                if 'archivo' in match:
                    json_file = STATIC_MAPS_DIR / match['archivo']
                else:
                    json_file = STATIC_MAPS_DIR / match['info']['json_file']
                
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Transformar elementos para compatibilidad con frontend
                elementos_transformados = []
                metadata = data.get('metadata', {})
                divisiones = metadata.get('divisiones_por_circulo', 420)
                
                for elemento in data['elementos']:
                    # Calcular posición polar para compatibilidad
                    circulo = elemento.get('circulo', 0)
                    segmento = elemento.get('segmento', 0)
                    angulo = (segmento * 360) / divisiones
                    radio = circulo + 1
                    
                    elemento_transformado = elemento.copy()
                    elemento_transformado['posicion'] = {
                        'radio': radio,
                        'angulo': angulo,
                        'x': radio * math.cos(math.radians(angulo)),
                        'y': radio * math.sin(math.radians(angulo))
                    }
                    elementos_transformados.append(elemento_transformado)
                
                score = match.get('score', 0.5)
                print(f"✅ Mapa servido: {json_file.name} (score: {score})")
                response = jsonify({
                    'elementos': elementos_transformados,
                    'estadisticas': data.get('estadisticas', {}),
                    'metadata': metadata,
                    'timestamp': datetime.now().isoformat(),
                    'version': '3.3.0-enhanced',
                    'source': 'pre-generated-similar',
                    'hash': match.get('hash', json_file.stem),
                    'similarity_score': match.get('score', 0.5),
                    'note': 'Mapa similar al solicitado - pre-calculado para máximo rendimiento'
                })
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            
            else:
                # Fallback: usar el mapa más cercano disponible
                if CACHE_INDEX and CACHE_INDEX['maps']:
                    # Tomar cualquier mapa disponible como fallback
                    fallback_hash = list(CACHE_INDEX['maps'].keys())[0]
                    fallback_info = CACHE_INDEX['maps'][fallback_hash]
                    
                    json_file = STATIC_MAPS_DIR / fallback_info['json_file']
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    # Transformar elementos para compatibilidad
                    elementos_transformados = []
                    metadata = data.get('metadata', {})
                    divisiones = metadata.get('divisiones_por_circulo', 420)
                    
                    for elemento in data['elementos']:
                        circulo = elemento.get('circulo', 0)
                        segmento = elemento.get('segmento', 0)
                        angulo = (segmento * 360) / divisiones
                        radio = circulo + 1
                        
                        elemento_transformado = elemento.copy()
                        elemento_transformado['posicion'] = {
                            'radio': radio,
                            'angulo': angulo,
                            'x': radio * math.cos(math.radians(angulo)),
                            'y': radio * math.sin(math.radians(angulo))
                        }
                        elementos_transformados.append(elemento_transformado)
                    
                    print(f"⚠️ Usando mapa fallback: {json_file.name}")
                    response = jsonify({
                        'elementos': elementos_transformados,
                        'estadisticas': data.get('estadisticas', {}),
                        'metadata': metadata,
                        'timestamp': datetime.now().isoformat(),
                        'version': '3.3.0-fallback',
                        'source': 'pre-generated-fallback',
                        'hash': fallback_hash,
                        'note': 'Mapa alternativo - parámetros solicitados no disponibles',
                        'requested_params': parametros,
                        'actual_params': fallback_info['parametros']
                    })
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                    return response
                else:
                    return jsonify({
                        'error': 'No hay mapas disponibles en el sistema',
                        'suggestion': 'Ejecuta python3 pregenerate_static_maps.py',
                        'timestamp': datetime.now().isoformat()
                    }), 503
    
    except Exception as e:
        print(f"❌ Error sirviendo mapa: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'Error del servidor: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/maps')
def list_available_maps():
    """Listar mapas pre-generados disponibles."""
    if not CACHE_INDEX:
        return jsonify({'error': 'Índice de mapas no disponible'}), 500
    
    # Preparar resumen de mapas disponibles
    resumen = {
        'total_maps': len(CACHE_INDEX['maps']),
        'generated': CACHE_INDEX['generated'],
        'combinations': {},
        'mapeos_disponibles': set(),
        'rangos_circulos': {'min': float('inf'), 'max': 0},
        'rangos_segmentos': {'min': float('inf'), 'max': 0}
    }
    
    for map_hash, info in CACHE_INDEX['maps'].items():
        param = info['parametros']
        
        # Recopilar estadísticas
        resumen['mapeos_disponibles'].add(param['tipo_mapeo'])
        resumen['rangos_circulos']['min'] = min(resumen['rangos_circulos']['min'], param['num_circulos'])
        resumen['rangos_circulos']['max'] = max(resumen['rangos_circulos']['max'], param['num_circulos'])
        resumen['rangos_segmentos']['min'] = min(resumen['rangos_segmentos']['min'], param['divisiones_por_circulo'])
        resumen['rangos_segmentos']['max'] = max(resumen['rangos_segmentos']['max'], param['divisiones_por_circulo'])
        
        # Agrupar por configuración base
        config_key = f"{param['num_circulos']}x{param['divisiones_por_circulo']}-{param['tipo_mapeo']}"
        if config_key not in resumen['combinations']:
            resumen['combinations'][config_key] = {
                'parametros': param,
                'elementos_count': info['elementos_count'],
                'primos_count': info['primos_count'],
                'densidad': info['densidad'],
                'file_size_kb': info['file_size_kb'],
                'html_url': f"/static_map/{info['html_file']}",
                'json_url': f"/api/map-data/{map_hash}",
                'hash': map_hash
            }
    
    resumen['mapeos_disponibles'] = list(resumen['mapeos_disponibles'])
    
    return jsonify(resumen)



@app.route('/api/number/<int:numero>')
def get_number_info(numero):
    """Obtener información detallada de un número específico."""
    def es_primo(n):
        if n < 2: return False
        if n == 2: return True
        if n % 2 == 0: return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0: return False
        return True
    
    def clasificar_numero(n):
        clasificaciones = []
        
        if es_primo(n):
            clasificaciones.append('primo')
            
            # Verificar gemelos
            if n > 2 and es_primo(n-2): clasificaciones.append('gemelo_mayor')
            if es_primo(n+2): clasificaciones.append('gemelo_menor')
            
            # Verificar primos
            if n > 4 and es_primo(n-4): clasificaciones.append('primo_mayor')  
            if es_primo(n+4): clasificaciones.append('primo_menor')
            
            # Verificar sexy
            if n > 6 and es_primo(n-6): clasificaciones.append('sexy_mayor')
            if es_primo(n+6): clasificaciones.append('sexy_menor')
            
            # Sophie Germain
            if es_primo(2*n + 1): clasificaciones.append('sophie_germain')
            
            # Palíndromo
            if str(n) == str(n)[::-1] and len(str(n)) > 1:
                clasificaciones.append('palindromico')
        else:
            clasificaciones.append('compuesto')
        
        return clasificaciones
    
    info = {
        'numero': numero,
        'es_primo': es_primo(numero),
        'clasificaciones': clasificar_numero(numero),
        'factores': [],
        'propiedades': {
            'par': numero % 2 == 0,
            'cuadrado_perfecto': int(numero**0.5)**2 == numero,
            'digitos': len(str(numero)),
            'suma_digitos': sum(int(d) for d in str(numero))
        }
    }
    
    # Calcular factores si es compuesto
    if not info['es_primo'] and numero > 1:
        factores = []
        temp = numero
        d = 2
        while d * d <= temp:
            while temp % d == 0:
                factores.append(d)
                temp //= d
            d += 1
        if temp > 1:
            factores.append(temp)
        info['factores'] = factores
    
    response = jsonify(info)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/descargar-imagen', methods=['POST', 'OPTIONS'])
def descargar_imagen():
    """Generar y descargar imagen PNG del mapa."""
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        parametros = request.get_json() or {}
        
        # Importar el creador de imágenes
        from image_creator import crear_imagen_mapa, guardar_imagen
        
        # Extraer parámetros
        num_circulos = parametros.get('num_circulos', 10)
        divisiones = parametros.get('divisiones_por_circulo', 24)
        tipo_mapeo = parametros.get('tipo_mapeo', 'lineal')
        
        # Configurar tipos a mostrar
        mostrar_tipos = {
            'primo_regular': parametros.get('mostrar_regulares', True),
            'primo_gemelo': parametros.get('mostrar_gemelos', True),
            'primo_primo': parametros.get('mostrar_primos', True),
            'primo_sexy': parametros.get('mostrar_sexy', True),
            'sophie_germain': parametros.get('mostrar_sophie_germain', True),
            'palindromico': parametros.get('mostrar_palindromicos', True),
            'mersenne': parametros.get('mostrar_mersenne', True),
            'fermat': parametros.get('mostrar_fermat', True),
            'compuesto': parametros.get('mostrar_compuestos', True)
        }
        
        # Crear imagen
        fig, filename, stats = crear_imagen_mapa(
            num_circulos, divisiones, tipo_mapeo, mostrar_tipos
        )
        
        # Guardar temporalmente
        import tempfile
        temp_dir = tempfile.mkdtemp()
        filepath = Path(temp_dir) / filename
        
        fig.savefig(filepath, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        # Enviar archivo
        def remove_file(response):
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
            return response
        
        response = send_file(filepath, as_attachment=True, 
                           download_name=filename, mimetype='image/png')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.call_on_close(lambda: remove_file(response))
        
        return response
        
    except Exception as e:
        print(f"❌ Error generando imagen: {e}")
        return jsonify({'error': f'Error generando imagen: {str(e)}'}), 500

@app.route('/api/map-data/<map_hash>')
def get_map_data(map_hash):
    """Obtener datos JSON de un mapa específico."""
    try:
        if not CACHE_INDEX or map_hash not in CACHE_INDEX['maps']:
            return jsonify({'error': 'Mapa no encontrado'}), 404
        
        info = CACHE_INDEX['maps'][map_hash]
        json_file = STATIC_MAPS_DIR / info['json_file']
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': f'Error cargando mapa: {str(e)}'}), 500

@app.route('/static_map/<filename>')
def serve_static_map(filename):
    """Servir archivo HTML de mapa estático."""
    try:
        if not filename.endswith('.html'):
            return jsonify({'error': 'Solo archivos HTML'}), 400
        
        file_path = STATIC_MAPS_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'Mapa no encontrado'}), 404
        
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/info')
def api_info():
    """Información de la API estática."""
    # Obtener hostname para DNS
    hostname = socket.gethostname()
    try:
        hostname_fqdn = socket.getfqdn()
    except:
        hostname_fqdn = hostname
    
    # Obtener IP local
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    
    # Obtener puerto actual
    port = request.host.split(':')[-1] if ':' in request.host else '3000'
    
    # DNS público configurado
    dns_publico = "ec2-3-144-134-110.us-east-2.compute.amazonaws.com"
    
    # Detectar si estamos detrás de un proxy
    behind_proxy = 'X-Forwarded-For' in request.headers or 'X-Real-IP' in request.headers
    
    return jsonify({
        'version': '3.3.0-enhanced',
        'name': 'Enhanced Interactive Prime Visualization',
        'features': [
            'Interactive HTML interface with advanced tooltips',
            'Real-time mathematical analysis',
            'Pre-generated maps for maximum performance',
            'Advanced prime pattern visualization',
            'Mobile-responsive design',
            'Zoom and pan controls',
            'Multiple mathematical mappings',
            'Live statistics dashboard',
            'DNS persistence with auto-recovery'
        ],
        'performance': {
            'map_loading': 'Instant (pre-generated)',
            'calculation_time': '0ms (pre-calculated)',
            'memory_usage': 'Minimal (static files)',
            'cache_type': 'Static HTML/JSON files'
        },
        'statistics': {
            'total_maps': len(CACHE_INDEX['maps']) if CACHE_INDEX and isinstance(CACHE_INDEX.get('maps'), dict) else len(list(STATIC_MAPS_DIR.glob("data_*.json"))),
            'total_size_kb': sum(f.stat().st_size for f in STATIC_MAPS_DIR.glob("*") if f.is_file()) // 1024,
            'generated': CACHE_INDEX.get('generated') if CACHE_INDEX else None
        },
        'endpoints': {
            'home': '/ (map selector)',
            'maps_list': '/api/maps',
            'map_data': '/api/map-data/<hash>',
            'static_map': '/static_map/<filename>',
            'interactive_api': '/api/interactive-map (POST)',
            'dns_check': '/dns-check'
        },
        'server_info': {
            'hostname': hostname,
            'hostname_fqdn': hostname_fqdn,
            'ip': local_ip,
            'dns_publico': dns_publico,
            'behind_proxy': behind_proxy,
            'dns_access': f"http://{dns_publico}/",
            'dns_access_con_puerto': f"http://{dns_publico}:{port}/",
            'hostname_access': f"http://{hostname_fqdn}/",
            'hostname_access_con_puerto': f"http://{hostname_fqdn}:{port}/",
            'ip_access': f"http://{local_ip}/",
            'ip_access_con_puerto': f"http://{local_ip}:{port}/"
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/number/<int:number>')
def analyze_number_static(number):
    """Análisis básico de números (sin pre-generación pesada)."""
    try:
        if number < 1 or number > 10000:
            return jsonify({'error': 'Número debe estar entre 1 y 10,000'}), 400
        
        # Análisis básico y rápido
        def es_primo_simple(n):
            if n < 2: return False
            if n == 2: return True
            if n % 2 == 0: return False
            for i in range(3, int(n**0.5) + 1, 2):
                if n % i == 0: return False
            return True
        
        es_primo = es_primo_simple(number)
        
        analisis = {
            'numero': number,
            'es_primo': es_primo,
            'propiedades': [],
            'formulas': [],
            'tipos_primo': []
        }
        
        # Propiedades básicas
        analisis['propiedades'].append("Número primo" if es_primo else "Número compuesto")
        analisis['propiedades'].append("Par" if number % 2 == 0 else "Impar")
        
        # Fórmulas básicas
        analisis['formulas'].extend([
            f"{number} ≡ {number % 6} (mod 6)",
            f"{number} ≡ {number % 10} (mod 10)",
            f"Binario: {bin(number)[2:]}",
            f"Hexadecimal: {hex(number)[2:].upper()}"
        ])
        
        if es_primo and number > 2:
            # Verificar tipos especiales básicos
            if es_primo_simple(number - 2) or es_primo_simple(number + 2):
                twin = (number - 2) if es_primo_simple(number - 2) else (number + 2)
                analisis['tipos_primo'].append(f"Primo gemelo con {twin}")
            
            if es_primo_simple(number - 4) or es_primo_simple(number + 4):
                cousin = (number - 4) if es_primo_simple(number - 4) else (number + 4)
                analisis['tipos_primo'].append(f"Primo primo con {cousin}")
        
        elif not es_primo:
            # Factorización básica
            factors = []
            temp = number
            for i in range(2, int(number**0.5) + 1):
                while temp % i == 0:
                    factors.append(i)
                    temp //= i
            if temp > 1:
                factors.append(temp)
            
            if factors:
                analisis['formulas'].append(f"{number} = {' × '.join(map(str, factors))}")
        
        return jsonify(analisis)
        
    except Exception as e:
        return jsonify({
            'error': f'Error analizando número: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/random-map')
def get_random_map():
    """Obtener un mapa aleatorio de los pre-generados."""
    if not CACHE_INDEX:
        return jsonify({'error': 'Índice no disponible'}), 500
    
    import random
    map_hash = random.choice(list(CACHE_INDEX['maps'].keys()))
    info = CACHE_INDEX['maps'][map_hash]
    
    return jsonify({
        'html_url': f"/static_map/{info['html_file']}",
        'json_url': f"/api/map-data/{map_hash}",
        'parametros': info['parametros'],
        'estadisticas': {
            'elementos': info['elementos_count'],
            'primos': info['primos_count'],
            'densidad': info['densidad'],
            'tamaño_kb': info['file_size_kb']
        },
        'hash': map_hash
    })

# Ruta para verificar DNS
@app.route('/dns-check')
def dns_check():
    """Verificar configuración DNS."""
    hostname = socket.gethostname()
    try:
        hostname_fqdn = socket.getfqdn()
    except:
        hostname_fqdn = hostname
    
    # Obtener IP local
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    
    # DNS público configurado
    dns_publico = "ec2-3-144-134-110.us-east-2.compute.amazonaws.com"
    
    # Obtener puerto actual
    port = request.host.split(':')[-1] if ':' in request.host else '3000'
    
    # Detectar si estamos detrás de un proxy
    behind_proxy = 'X-Forwarded-For' in request.headers or 'X-Real-IP' in request.headers
    
    # Intentar resolver el hostname
    try:
        resolved_ip = socket.gethostbyname(hostname_fqdn)
        dns_local_ok = resolved_ip == local_ip
    except:
        resolved_ip = "No resuelto"
        dns_local_ok = False
    
    # Intentar resolver el DNS público
    try:
        dns_public_ip = socket.gethostbyname(dns_publico)
        dns_public_ok = True
    except:
        dns_public_ip = "No resuelto"
        dns_public_ok = False
    
    return jsonify({
        'dns_check': {
            'hostname': hostname,
            'hostname_fqdn': hostname_fqdn,
            'local_ip': local_ip,
            'resolved_ip': resolved_ip,
            'dns_local_ok': dns_local_ok,
            'dns_publico': dns_publico,
            'dns_public_ip': dns_public_ip,
            'dns_public_ok': dns_public_ok,
            'behind_proxy': behind_proxy,
            'proxy_info': {
                'from_port': 80,
                'to_port': 3000,
                'proxy_server': 'nginx'
            },
            'access_urls': {
                'dns_publico_sin_puerto': f"http://{dns_publico}/",
                'dns_publico_con_puerto': f"http://{dns_publico}:{port}/",
                'hostname_sin_puerto': f"http://{hostname_fqdn}/",
                'hostname_con_puerto': f"http://{hostname_fqdn}:{port}/",
                'ip_sin_puerto': f"http://{local_ip}/",
                'ip_con_puerto': f"http://{local_ip}:{port}/",
                'localhost_sin_puerto': f"http://localhost/",
                'localhost_con_puerto': f"http://localhost:{port}/"
            }
        },
        'timestamp': datetime.now().isoformat()
    })

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Ruta no encontrada',
        'available_routes': [
            '/ (interfaz interactiva mejorada)',
            '/enhanced (selector de mapas estáticos)', 
            '/api/maps (lista de mapas disponibles)',
            '/api/interactive-map (mapa interactivo optimizado)',
            '/api/number/<int> (análisis matemático de número)',
            '/api/random-map (mapa aleatorio)',
            '/static_map/<filename> (mapa HTML pre-generado)',
            '/dns-check (verificar configuración DNS)'
        ],
        'total_maps_available': len(CACHE_INDEX['maps']) if CACHE_INDEX else 0
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Consulta los logs para más información',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 Iniciando servidor MEJORADO con interfaz interactiva avanzada...")
    print("=" * 70)
    
    # Cargar índice de mapas
    if cargar_indice_mapas():
        print(f"📊 {len(CACHE_INDEX['maps'])} mapas pre-generados listos para servir")
        if isinstance(CACHE_INDEX['maps'], dict):
            print(f"💾 Tamaño total: {sum(info.get('file_size_kb', 0) for info in CACHE_INDEX['maps'].values())}KB")
        else:
            print(f"💾 Mapas en formato lista: {len(CACHE_INDEX['maps'])} elementos")
        print("⚡ Rendimiento: MÁXIMO (mapas pre-calculados + interfaz responsiva)")
        print()
        
        # Obtener información de red para DNS
        hostname = socket.gethostname()
        try:
            hostname_fqdn = socket.getfqdn()
        except:
            hostname_fqdn = hostname
        
        # Obtener IP local
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "127.0.0.1"
            
        # DNS público configurado
        dns_publico = "ec2-3-144-134-110.us-east-2.compute.amazonaws.com"
        
        # Obtener puerto de los argumentos o usar 3000 por defecto
        import sys
        port = 3000
        host = '0.0.0.0'
        
        # Procesar argumentos de línea de comandos
        for i, arg in enumerate(sys.argv):
            if arg == '--port' and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
            elif arg.startswith('--port='):
                port = int(arg.split('=')[1])
            elif arg == '--host' and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
            elif arg.startswith('--host='):
                host = arg.split('=')[1]
        
        print("🌐 URLs disponibles:")
        print(f"   🏠 Interfaz Interactiva:   http://localhost:{port}/")
        print(f"   🎯 API Mapas Dinámicos:    POST http://localhost:{port}/api/interactive-map")
        print(f"   📊 Lista de Mapas:         GET http://localhost:{port}/api/maps")
        print(f"   🎲 Mapa Aleatorio:         GET http://localhost:{port}/api/random-map")
        print(f"   📈 Info del Sistema:       GET http://localhost:{port}/api/info")
        print(f"   🧮 Análisis de Números:    GET http://localhost:{port}/api/number/<n>")
        print()
        print("🎨 NUEVAS CARACTERÍSTICAS:")
        print("   ✨ Tooltips matemáticos avanzados con análisis en tiempo real")
        print("   🔍 Controles de zoom y navegación mejorados")
        print("   📱 Diseño completamente responsive para móviles")
        print("   🎯 8 tipos diferentes de primos con visualización especializada")
        print("   ⚡ Carga instantánea usando mapas pre-generados")
        print("   🌈 Animaciones y efectos visuales mejorados")
        print()
        
        # Mostrar información de acceso DNS
        print("🌐 ACCESOS DNS DISPONIBLES:")
        print(f"   📍 IP PÚBLICA:   http://{local_ip}:{port}/")
        print(f"   🌍 DNS/HOSTNAME: http://{hostname_fqdn}:{port}/")
        print(f"   🌐 DNS PÚBLICO:  http://{dns_publico}:{port}/")
        print(f"   🔗 LOCALHOST:    http://localhost:{port}/")
        print()
        
        print(f"🔥 SERVIDOR INTERACTIVO MEJORADO INICIANDO EN PUERTO {port}...")
        
        app.run(host=host, port=port, debug=False, threaded=True)
    else:
        print("❌ No se pudo cargar el índice de mapas pre-generados")
        print("💡 Ejecuta primero: python3 pregenerate_static_maps.py")
        exit(1)