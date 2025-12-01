#!/usr/bin/env python3
"""
Creador de Imágenes de Mapas de Números Primos
Versión simplificada que solo genera imágenes PNG con colores y leyenda.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
from datetime import datetime
from pathlib import Path
import hashlib
import json

def es_primo(n):
    """Verifica si un número es primo."""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

def generar_primos(limite):
    """Genera lista de números primos hasta el límite usando criba optimizada."""
    if limite < 2: return []
    
    # Para límites grandes, usar estrategia optimizada
    if limite > 100000:
        print(f"⚡ Generando primos hasta {limite:,} (optimizado para memoria)...")
        # Usar generador para no cargar todo en memoria
        primos = []
        chunk_size = 100000
        
        for start in range(2, limite + 1, chunk_size):
            end = min(start + chunk_size - 1, limite)
            chunk_primos = generar_primos_chunk(start, end)
            primos.extend(chunk_primos)
            
        return primos
    else:
        # Criba normal para números pequeños
        criba = [True] * (limite + 1)
        criba[0] = criba[1] = False
        
        for i in range(2, int(math.sqrt(limite)) + 1):
            if criba[i]:
                for j in range(i * i, limite + 1, i):
                    criba[j] = False
        
        return [i for i in range(2, limite + 1) if criba[i]]

def generar_primos_chunk(start, end):
    """Genera primos en un rango específico."""
    if start < 2: start = 2
    primos_chunk = []
    
    for n in range(start, end + 1):
        if es_primo(n):
            primos_chunk.append(n)
    
    return primos_chunk

def clasificar_numero(n, primos_set):
    """Clasifica un número según su tipo."""
    if n in primos_set:
        # Verificar tipos especiales de primos
        if n > 2 and (n-2) in primos_set: return 'primo_gemelo'
        if n > 4 and (n-4) in primos_set: return 'primo_primo'  
        if n > 6 and (n-6) in primos_set: return 'primo_sexy'
        if n > 2 and (2*n + 1) in primos_set: return 'sophie_germain'
        
        # Verificar si es palíndromo
        if str(n) == str(n)[::-1] and len(str(n)) > 1: return 'palindromico'
        
        # Verificar Mersenne (2^p - 1)
        temp = n + 1
        if temp > 1 and (temp & (temp - 1)) == 0:  # es potencia de 2
            p = int(math.log2(temp))
            if es_primo(p): return 'mersenne'
        
        # Verificar Fermat (2^(2^n) + 1)  
        if n > 3:
            temp = n - 1
            if temp > 0 and (temp & (temp - 1)) == 0:  # es potencia de 2
                k = int(math.log2(temp))
                if (k & (k - 1)) == 0:  # k es potencia de 2
                    return 'fermat'
        
        return 'primo_regular'
    else:
        return 'compuesto'

def mapeo_lineal(n, total, num_circulos, divisiones):
    """Mapeo lineal estándar."""
    circulo = n // divisiones
    segmento = n % divisiones
    return min(circulo, num_circulos - 1), segmento

def mapeo_logaritmico(n, total, num_circulos, divisiones):
    """Mapeo logarítmico."""
    if n <= 0: return 0, 0
    log_pos = math.log(n + 1) / math.log(total + 1) if total > 0 else 0
    pos_total = int(log_pos * num_circulos * divisiones)
    circulo = min(pos_total // divisiones, num_circulos - 1)
    segmento = pos_total % divisiones
    return circulo, segmento

def mapeo_espiral_arquimedes(n, total, num_circulos, divisiones):
    """Espiral de Arquímedes."""
    if n <= 0: return 0, 0
    theta = 2 * math.pi * math.sqrt(n / total) if total > 0 else 0
    r = math.sqrt(n / total) * num_circulos if total > 0 else 0
    circulo = min(int(r), num_circulos - 1)
    segmento = int((theta % (2 * math.pi)) / (2 * math.pi) * divisiones)
    return circulo, segmento

def mapeo_espiral_fibonacci(n, total, num_circulos, divisiones):
    """Espiral de Fibonacci."""
    if n <= 0: return 0, 0
    phi = (1 + math.sqrt(5)) / 2
    theta = 2 * math.pi * n / phi
    r = math.sqrt(n) / math.sqrt(total) * num_circulos if total > 0 else 0
    circulo = min(int(r), num_circulos - 1)
    segmento = int((theta % (2 * math.pi)) / (2 * math.pi) * divisiones)
    return circulo, segmento

def obtener_colores():
    """Define los colores para cada tipo de número."""
    return {
        'primo_regular': '#4D96FF',     # Azul
        'primo_gemelo': '#FF0000',      # Rojo
        'primo_primo': '#FF8C00',       # Naranja
        'primo_sexy': '#FF1493',        # Rosa
        'sophie_germain': '#9400D3',    # Violeta
        'palindromico': '#FFD700',      # Oro
        'mersenne': '#00FFFF',          # Cyan
        'fermat': '#ADFF2F',            # Verde lima

    }

def crear_imagen_mapa(num_circulos, divisiones_por_circulo, tipo_mapeo, mostrar_tipos=None):
    """Crea una imagen del mapa de números primos con leyenda y parámetros."""
    
    # Configurar parámetros por defecto
    if mostrar_tipos is None:
        mostrar_tipos = {
            'primo_regular': True,
            'primo_gemelo': True, 
            'primo_primo': True,
            'primo_sexy': True,
            'sophie_germain': True,
            'palindromico': True,
            'mersenne': True,
            'fermat': True,
            'compuesto': True
        }
    
    # Calcular límite basado en parámetros
    limite = num_circulos * divisiones_por_circulo
    
    # Generar primos
    primos = generar_primos(limite)
    primos_set = set(primos)
    
    # Configurar mapeo
    mapeos = {
        'lineal': mapeo_lineal,
        'logaritmico': mapeo_logaritmico, 
        'arquimedes': mapeo_espiral_arquimedes,
        'fibonacci': mapeo_espiral_fibonacci
    }
    
    mapeo_func = mapeos.get(tipo_mapeo, mapeo_lineal)
    colores = obtener_colores()
    
    # Crear figura con espacio para leyenda
    fig, (ax_main, ax_legend) = plt.subplots(1, 2, figsize=(16, 10), 
                                           gridspec_kw={'width_ratios': [3, 1]})
    
    # Configurar título con parámetros
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    titulo = f"Mapa de Números Primos - {fecha_hora}\n"
    titulo += f"Círculos: {num_circulos} | Divisiones: {divisiones_por_circulo} | "
    titulo += f"Mapeo: {tipo_mapeo.title()} | Límite: {limite:,}"
    
    fig.suptitle(titulo, fontsize=14, fontweight='bold', y=0.95)
    
    # Generar puntos (solo números primos, optimizado)
    elementos = []
    for n in range(1, limite + 1):
        tipo = clasificar_numero(n, primos_set)
        
        # Solo renderizar números primos, saltar compuestos para optimizar
        if tipo == 'compuesto':
            continue
            
        if mostrar_tipos.get(tipo, True):
            circulo, segmento = mapeo_func(n, limite, num_circulos, divisiones_por_circulo)
            
            # Calcular posición polar
            angulo = (segmento * 2 * math.pi) / divisiones_por_circulo
            radio = circulo + 1
            
            x = radio * math.cos(angulo)
            y = radio * math.sin(angulo)
            
            elementos.append({
                'x': x, 'y': y, 'tipo': tipo, 'numero': n,
                'circulo': circulo, 'segmento': segmento
            })
    
    # Dibujar puntos por tipo
    for tipo, color in colores.items():
        if not mostrar_tipos.get(tipo, True):
            continue
            
        puntos = [e for e in elementos if e['tipo'] == tipo]
        if puntos:
            xs = [p['x'] for p in puntos]
            ys = [p['y'] for p in puntos]
            
            # Tamaño de punto según tipo y número de círculos
            # Reducir tamaño cuando hay más círculos para mejor visualización
            if num_circulos <= 10:
                size = 3 if tipo == 'compuesto' else 5
            elif num_circulos <= 50:
                size = 2 if tipo == 'compuesto' else 3
            elif num_circulos <= 100:
                size = 1.5 if tipo == 'compuesto' else 2
            elif num_circulos <= 500:
                size = 0.8 if tipo == 'compuesto' else 1.2
            elif num_circulos <= 1000:
                size = 0.5 if tipo == 'compuesto' else 0.8
            else:
                # Para más de 1000 círculos, puntos muy pequeños
                size = 0.3 if tipo == 'compuesto' else 0.5
            
            alpha = 0.6 if tipo == 'compuesto' else 0.8
            
            ax_main.scatter(xs, ys, c=color, s=size, alpha=alpha, edgecolors='none')
    
    # Configurar ejes principales
    ax_main.set_aspect('equal')
    ax_main.grid(True, alpha=0.3)
    ax_main.set_facecolor('#f8f9fa')
    
    # Calcular límites
    max_radio = num_circulos + 1
    ax_main.set_xlim(-max_radio * 1.1, max_radio * 1.1)
    ax_main.set_ylim(-max_radio * 1.1, max_radio * 1.1)
    
    # Dibujar círculos guía
    for i in range(1, num_circulos + 1):
        circle = plt.Circle((0, 0), i, fill=False, color='lightgray', alpha=0.5, linewidth=0.5)
        ax_main.add_patch(circle)
    
    # Crear leyenda
    ax_legend.set_xlim(0, 1)
    ax_legend.set_ylim(0, 1)
    ax_legend.axis('off')
    
    # Títulos de leyenda
    nombres_tipos = {
        'primo_regular': 'Primos Regulares',
        'primo_gemelo': 'Primos Gemelos', 
        'primo_primo': 'Primos Primos',
        'primo_sexy': 'Primos Sexy',
        'sophie_germain': 'Sophie Germain',
        'palindromico': 'Palíndromos',
        'mersenne': 'Mersenne',
        'fermat': 'Fermat'
    }
    
    ax_legend.text(0.1, 0.95, 'LEYENDA DE COLORES', fontweight='bold', fontsize=12)
    
    y_pos = 0.88
    contadores = {}
    
    # Contar elementos por tipo
    for elemento in elementos:
        tipo = elemento['tipo']
        contadores[tipo] = contadores.get(tipo, 0) + 1
    
    # Mostrar leyenda con contadores
    for tipo, color in colores.items():
        if mostrar_tipos.get(tipo, True) and contadores.get(tipo, 0) > 0:
            count = contadores[tipo]
            nombre = nombres_tipos.get(tipo, tipo)
            
            # Dibujar muestra de color
            ax_legend.scatter(0.1, y_pos, c=color, s=80, alpha=0.8, edgecolors='black', linewidth=0.5)
            
            # Texto con nombre y contador
            ax_legend.text(0.2, y_pos, f'{nombre}: {count:,}', 
                          fontsize=10, verticalalignment='center')
            
            y_pos -= 0.08
    
    # Estadísticas generales (solo primos renderizados)
    total_primos = len(elementos)  # Todos los elementos son primos
    total_posibles = limite  # Total de números en el rango
    
    y_pos -= 0.05
    ax_legend.text(0.1, y_pos, 'ESTADÍSTICAS:', fontweight='bold', fontsize=11)
    y_pos -= 0.06
    ax_legend.text(0.1, y_pos, f'Primos renderizados: {total_primos:,}', fontsize=10)
    y_pos -= 0.04
    ax_legend.text(0.1, y_pos, f'Rango analizado: 1-{limite:,}', fontsize=10)
    y_pos -= 0.04
    
    if total_posibles > 0:
        densidad = (total_primos / total_posibles) * 100
        ax_legend.text(0.1, y_pos, f'Densidad primos: {densidad:.1f}%', fontsize=10)
    
    plt.tight_layout()
    
    # Generar nombre de archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mapa_primos_{num_circulos}c_{divisiones_por_circulo}d_{tipo_mapeo}_{timestamp}.png"
    
    return fig, filename, {
        'total_elementos': total_primos,  # Solo primos renderizados
        'total_primos': total_primos,
        'contadores': contadores,
        'parametros': {
            'num_circulos': num_circulos,
            'divisiones_por_circulo': divisiones_por_circulo,
            'tipo_mapeo': tipo_mapeo,
            'limite': limite
        }
    }

def guardar_imagen(fig, filename, directorio="imagenes"):
    """Guarda la imagen en el directorio especificado."""
    Path(directorio).mkdir(exist_ok=True)
    filepath = Path(directorio) / filename
    
    fig.savefig(filepath, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    
    return filepath

if __name__ == "__main__":
    # Ejemplo de uso
    print("🎨 Generando imagen de mapa de números primos...")
    
    # Parámetros de ejemplo
    num_circulos = 10
    divisiones = 24
    tipo_mapeo = "lineal"
    
    # Crear imagen
    fig, filename, stats = crear_imagen_mapa(num_circulos, divisiones, tipo_mapeo)
    
    # Guardar
    filepath = guardar_imagen(fig, filename)
    
    print(f"✅ Imagen guardada: {filepath}")
    print(f"📊 Estadísticas: {stats['total_primos']} primos de {stats['total_elementos']} elementos")