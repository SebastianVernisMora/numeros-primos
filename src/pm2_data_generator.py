#!/usr/bin/env python3
"""
Generador de Datos de Mapas de Números Primos - PM2 Background Task
Genera y almacena localmente datos para configuraciones de 10,000 círculos × 1,300 segmentos
"""

import os
import sys
import json
import time
import math
import signal
import gzip
from datetime import datetime
from pathlib import Path
import hashlib
import gc
import traceback

# Configuración
DATA_DIR = Path(__file__).parent / "data" / "pregenerated_maps"
INDEX_FILE = Path(__file__).parent / "data" / "index.json"
PROGRESS_FILE = Path(__file__).parent / "data" / "generation_progress.json"
STATS_FILE = Path(__file__).parent / "data" / "generator_stats.json"

# Crear directorios
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.parent.mkdir(parents=True, exist_ok=True)

# Estado global
RUNNING = True
STATS = {
    'started_at': datetime.now().isoformat(),
    'maps_generated': 0,
    'maps_skipped': 0,
    'errors': 0,
    'current_config': None,
    'last_activity': datetime.now().isoformat(),
    'total_size_mb': 0,
    'estimated_completion': None
}

def signal_handler(signum, frame):
    """Manejar señales de terminación."""
    global RUNNING
    print(f"\n🛑 Señal {signum} recibida. Guardando progreso y cerrando...")
    RUNNING = False
    save_stats()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def log(message):
    """Log con timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    STATS['last_activity'] = datetime.now().isoformat()

def es_primo(n):
    """Verifica si un número es primo."""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0: return False
    return True

def criba_eratostenes_optimizada(limite):
    """Criba de Eratóstenes optimizada para grandes números."""
    if limite < 2:
        return []
    
    log(f"🔢 Generando primos hasta {limite:,}...")
    
    # Para números muy grandes, usar estrategia por chunks
    if limite > 1000000:
        return criba_por_chunks(limite)
    
    # Criba normal para números menores
    criba = [True] * (limite + 1)
    criba[0] = criba[1] = False
    
    for i in range(2, int(limite**0.5) + 1):
        if criba[i]:
            for j in range(i * i, limite + 1, i):
                criba[j] = False
    
    primos = [i for i in range(2, limite + 1) if criba[i]]
    del criba
    gc.collect()
    
    return primos

def criba_por_chunks(limite, chunk_size=1000000):
    """Generar primos por chunks para optimizar memoria."""
    primos = []
    
    for start in range(2, limite + 1, chunk_size):
        end = min(start + chunk_size - 1, limite)
        
        # Generar primos en este chunk
        for n in range(start, end + 1):
            if es_primo(n):
                primos.append(n)
        
        if len(primos) % 10000 == 0:
            log(f"  ⚡ {len(primos):,} primos encontrados hasta {end:,}")
    
    return primos

def clasificar_numero(n, primos_set):
    """Clasifica un número según su tipo."""
    if n not in primos_set:
        return ['compuesto']
    
    tipos = []
    
    # Primos gemelos (diferencia de 2)
    if (n-2) in primos_set or (n+2) in primos_set:
        tipos.append('gemelo')
    
    # Primos primos (diferencia de 4)
    if (n-4) in primos_set or (n+4) in primos_set:
        tipos.append('primo_primo')
    
    # Primos sexy (diferencia de 6)
    if (n-6) in primos_set or (n+6) in primos_set:
        tipos.append('sexy')
    
    # Sophie Germain
    if (2*n + 1) in primos_set:
        tipos.append('sophie_germain')
    
    # Palíndromo
    if str(n) == str(n)[::-1] and len(str(n)) > 1:
        tipos.append('palindromico')
    
    # Mersenne (2^p - 1)
    temp = n + 1
    if temp > 1 and (temp & (temp - 1)) == 0:
        p = int(math.log2(temp))
        if p in primos_set:
            tipos.append('mersenne')
    
    # Fermat (2^(2^n) + 1)
    if n > 3:
        temp = n - 1
        if temp > 0 and (temp & (temp - 1)) == 0:
            k = int(math.log2(temp))
            if (k & (k - 1)) == 0:
                tipos.append('fermat')
    
    # Si no tiene tipos especiales, es regular
    if not tipos:
        tipos = ['regular']
    
    return tipos

def generar_configuraciones():
    """Generar configuraciones para 10,000 círculos × 1,300 segmentos."""
    configuraciones = []
    
    # SOLO generar para la configuración específica solicitada
    # 10,000 círculos × 1,300 segmentos
    configuraciones.append({
        'num_circulos': 10000,
        'divisiones_por_circulo': 1300,
        'tipo_mapeo': 'lineal',
        'total_elementos': 13000000
    })
    
    log(f"✅ Configuración objetivo: 10,000 círculos × 1,300 segmentos = 13,000,000 números")
    
    return configuraciones

def generar_hash_config(config):
    """Generar hash único para configuración."""
    config_str = f"{config['num_circulos']}_{config['divisiones_por_circulo']}_{config['tipo_mapeo']}"
    return hashlib.md5(config_str.encode()).hexdigest()[:12]

def verificar_existe(hash_config):
    """Verificar si ya existe un mapa con este hash."""
    json_path = DATA_DIR / f"data_{hash_config}.json.gz"
    return json_path.exists()

def generar_datos_mapa(config):
    """Generar datos completos para un mapa."""
    num_circulos = config['num_circulos']
    divisiones = config['divisiones_por_circulo']
    tipo_mapeo = config['tipo_mapeo']
    total_numeros = num_circulos * divisiones
    
    log(f"🎨 Generando mapa: {num_circulos:,} círculos × {divisiones:,} segmentos = {total_numeros:,} números")
    
    start_time = time.time()
    
    # Generar primos hasta el límite
    primos = criba_eratostenes_optimizada(total_numeros)
    primos_set = set(primos)
    
    log(f"✅ {len(primos):,} primos encontrados ({len(primos)/total_numeros*100:.2f}%)")
    
    # Generar elementos (optimizado para memoria)
    elementos = []
    batch_size = 100000  # Procesar en lotes de 100k
    
    for batch_start in range(1, total_numeros + 1, batch_size):
        if not RUNNING:
            break
        
        batch_end = min(batch_start + batch_size - 1, total_numeros)
        
        for n in range(batch_start, batch_end + 1):
            # Calcular posición (mapeo lineal)
            circulo = (n - 1) // divisiones
            segmento = (n - 1) % divisiones
            
            # Clasificar número
            es_primo_val = n in primos_set
            tipos = clasificar_numero(n, primos_set) if es_primo_val else ['compuesto']
            
            # Calcular ángulo y radio
            angulo = (segmento * 360) / divisiones
            radio = circulo + 1
            
            elementos.append({
                'numero': n,
                'circulo': circulo,
                'segmento': segmento,
                'es_primo': es_primo_val,
                'tipos': tipos,
                'posicion': {
                    'radio': radio,
                    'angulo': angulo,
                    'x': radio * math.cos(math.radians(angulo)),
                    'y': radio * math.sin(math.radians(angulo))
                }
            })
        
        # Log de progreso
        progress = (batch_end / total_numeros) * 100
        log(f"  📊 Progreso: {progress:.1f}% ({batch_end:,}/{total_numeros:,})")
        
        # Liberar memoria periódicamente
        if batch_end % 500000 == 0:
            gc.collect()
    
    # Calcular estadísticas
    total_primos = sum(1 for e in elementos if e['es_primo'])
    
    elapsed = time.time() - start_time
    log(f"⏱️  Tiempo de generación: {elapsed:.2f}s")
    
    # Liberar memoria
    del primos
    del primos_set
    gc.collect()
    
    return {
        'metadata': {
            'num_circulos': num_circulos,
            'divisiones_por_circulo': divisiones,
            'tipo_mapeo': tipo_mapeo,
            'total_numeros': total_numeros,
            'generated_at': datetime.now().isoformat(),
            'generation_time_seconds': elapsed,
            'version': '2.0-pm2'
        },
        'elementos': elementos,
        'estadisticas': {
            'total_elementos': len(elementos),
            'total_primos': total_primos,
            'total_compuestos': len(elementos) - total_primos,
            'densidad_primos': (total_primos / len(elementos)) * 100 if elementos else 0
        }
    }

def guardar_mapa(hash_config, datos):
    """Guardar mapa en formato JSON comprimido."""
    json_path = DATA_DIR / f"data_{hash_config}.json.gz"
    
    try:
        # Guardar con compresión gzip
        with gzip.open(json_path, 'wt', encoding='utf-8') as f:
            json.dump(datos, f, separators=(',', ':'))
        
        # Obtener tamaño del archivo
        file_size_mb = json_path.stat().st_size / (1024 * 1024)
        
        log(f"💾 Guardado: {json_path.name} ({file_size_mb:.2f} MB)")
        
        return file_size_mb
    except Exception as e:
        log(f"❌ Error guardando mapa: {e}")
        traceback.print_exc()
        return 0

def actualizar_indice(hash_config, config, file_size_mb):
    """Actualizar índice de mapas generados."""
    try:
        # Cargar índice existente
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r') as f:
                indice = json.load(f)
        else:
            indice = {
                'maps': {},
                'total_count': 0,
                'total_size_mb': 0,
                'generated_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        
        # Agregar nuevo mapa
        indice['maps'][hash_config] = {
            'num_circulos': config['num_circulos'],
            'divisiones_por_circulo': config['divisiones_por_circulo'],
            'tipo_mapeo': config['tipo_mapeo'],
            'total_elementos': config['total_elementos'],
            'file_size_mb': file_size_mb,
            'generated_at': datetime.now().isoformat()
        }
        
        indice['total_count'] = len(indice['maps'])
        indice['total_size_mb'] = sum(m['file_size_mb'] for m in indice['maps'].values())
        indice['last_updated'] = datetime.now().isoformat()
        
        # Guardar índice
        with open(INDEX_FILE, 'w') as f:
            json.dump(indice, f, indent=2)
        
        log(f"📇 Índice actualizado: {indice['total_count']} mapas, {indice['total_size_mb']:.2f} MB total")
        
    except Exception as e:
        log(f"⚠️ Error actualizando índice: {e}")

def save_stats():
    """Guardar estadísticas del generador."""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(STATS, f, indent=2)
    except Exception as e:
        log(f"⚠️ Error guardando estadísticas: {e}")

def save_progress(current_index, total_configs):
    """Guardar progreso de generación."""
    try:
        progress = {
            'current_index': current_index,
            'total_configs': total_configs,
            'progress_percent': (current_index / total_configs) * 100 if total_configs > 0 else 0,
            'maps_generated': STATS['maps_generated'],
            'maps_skipped': STATS['maps_skipped'],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        log(f"⚠️ Error guardando progreso: {e}")

def main():
    """Función principal del generador."""
    log("🚀 Iniciando Generador de Datos PM2")
    log(f"📁 Directorio de datos: {DATA_DIR}")
    log(f"🎯 Objetivo: 10,000 círculos × 1,300 segmentos")
    
    # Generar configuraciones
    configuraciones = generar_configuraciones()
    total_configs = len(configuraciones)
    
    log(f"📋 Total de configuraciones a generar: {total_configs}")
    
    # Procesar cada configuración
    for idx, config in enumerate(configuraciones, 1):
        if not RUNNING:
            log("🛑 Deteniendo generador...")
            break
        
        hash_config = generar_hash_config(config)
        
        # Verificar si ya existe
        if verificar_existe(hash_config):
            log(f"⏭️  [{idx}/{total_configs}] Ya existe: {config['num_circulos']}c × {config['divisiones_por_circulo']}s")
            STATS['maps_skipped'] += 1
            save_progress(idx, total_configs)
            continue
        
        # Actualizar estado
        STATS['current_config'] = config
        
        try:
            log(f"🔄 [{idx}/{total_configs}] Generando: {config['num_circulos']:,}c × {config['divisiones_por_circulo']:,}s")
            
            # Generar datos
            datos = generar_datos_mapa(config)
            
            # Guardar mapa
            file_size_mb = guardar_mapa(hash_config, datos)
            
            # Actualizar índice
            actualizar_indice(hash_config, config, file_size_mb)
            
            # Actualizar estadísticas
            STATS['maps_generated'] += 1
            STATS['total_size_mb'] += file_size_mb
            
            # Guardar progreso
            save_progress(idx, total_configs)
            save_stats()
            
            # Liberar memoria
            del datos
            gc.collect()
            
            log(f"✅ [{idx}/{total_configs}] Completado: {hash_config}")
            
        except Exception as e:
            log(f"❌ Error generando mapa: {e}")
            traceback.print_exc()
            STATS['errors'] += 1
            save_stats()
            continue
    
    # Finalización
    STATS['finished_at'] = datetime.now().isoformat()
    STATS['current_config'] = 'completado'
    save_stats()
    
    log("🎉 Generación completada!")
    log(f"📊 Resumen:")
    log(f"   - Mapas generados: {STATS['maps_generated']}")
    log(f"   - Mapas omitidos: {STATS['maps_skipped']}")
    log(f"   - Errores: {STATS['errors']}")
    log(f"   - Tamaño total: {STATS['total_size_mb']:.2f} MB")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log("\n🛑 Interrumpido por usuario")
        save_stats()
    except Exception as e:
        log(f"❌ Error fatal: {e}")
        traceback.print_exc()
        STATS['errors'] += 1
        save_stats()
        sys.exit(1)
