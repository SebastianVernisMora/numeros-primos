#!/usr/bin/env python3
"""
Servidor del Mapa Interactivo de Números Primos
Puerto 3000 - Solo funcionalidad interactiva
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

# ===== RUTAS =====

@app.route('/')
def home():
    """Página principal - Mapa Interactivo."""
    return send_file(Path(__file__).parent / "interactive.html")

@app.route('/api/interactive-map', methods=['POST', 'OPTIONS'])
def get_interactive_map():
    """API principal para el mapa interactivo."""
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        parametros = request.get_json() or {}
        
        # Siempre generar mapa dinámico con todos los tipos
        print("🔄 Generando mapa dinámico con todos los tipos...")
        data = generar_mapa_dinamico(parametros)
        
        response = jsonify({
            'elementos': data['elementos'],
            'estadisticas': data['estadisticas'], 
            'metadata': data['metadata'],
            'timestamp': datetime.now().isoformat(),
            'version': '3.4.0-interactive',
            'source': 'generated-dynamic',
            'note': 'Mapa interactivo con clasificación completa de primos'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    except Exception as e:
        print(f"❌ Error sirviendo mapa: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'Error del servidor: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/number/<int:numero>')
def get_number_info(numero):
    """Obtener información detallada de un número específico."""
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

@app.route('/api/info')
def api_info():
    """Información de la API."""
    return jsonify({
        'name': 'Mapa Interactivo de Números Primos',
        'version': '3.4.0-interactive',
        'description': 'Visualización interactiva con zoom, drag y tooltips',
        'features': [
            'Visualización interactiva en tiempo real',
            'Clasificación completa de tipos de primos',
            'Controles de zoom y navegación',
            'Tooltips informativos',
            'Múltiples tipos de mapeo geométrico'
        ],
        'endpoints': [
            '/ - Interfaz interactiva',
            '/api/interactive-map - Generar mapa (POST)',
            '/api/number/{n} - Info de números',
            '/api/info - Información de la API'
        ],
        'port': 3000,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🗺️ Iniciando Servidor del Mapa Interactivo...")
    
    # Cargar índice de mapas
    cargar_indice_mapas()
    
    # Configurar argumentos
    import sys
    port = 3000
    host = '0.0.0.0'
    
    for i, arg in enumerate(sys.argv):
        if arg == '--port' and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
        elif arg == '--host' and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
    
    print(f"🌐 Mapa Interactivo disponible en: http://{host}:{port}/")
    print(f"🎮 Funciones: Zoom, Drag, Tooltips, Clasificación completa")
    
    # Iniciar servidor
    app.run(host=host, port=port, debug=False)