#!/bin/bash

# Script de gestión para el Servidor Unificado de Mapas de Números Primos
# Versión con círculos adaptativos y soporte hasta 3000 números

APP_NAME="Servidor Unificado de Mapas Primos v3.4.0"
SCRIPT_PATH="/home/admin/unified_server_updated.py"
PORT=3000
LOG_FILE="/home/admin/unified_server.log"

show_status() {
    echo "=== Estado de $APP_NAME ==="
    
    # Verificar si el proceso está corriendo
    if pgrep -f "python.*unified_server_updated.py" > /dev/null; then
        PID=$(pgrep -f "python.*unified_server_updated.py")
        echo "✅ Aplicación CORRIENDO (PID: $PID)"
        
        # Verificar puerto
        if ss -tlnp | grep ":$PORT" > /dev/null 2>&1; then
            echo "✅ Puerto $PORT ACTIVO"
        else
            echo "❌ Puerto $PORT NO DISPONIBLE"
        fi
        
        # Probar conectividad
        if curl -s http://localhost:$PORT/api/info > /dev/null; then
            echo "✅ API RESPONDIENDO"
            
            # Mostrar información de la API
            echo ""
            echo "=== Información de la API ==="
            curl -s http://localhost:$PORT/api/info | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"Versión: {data.get('version', 'N/A')}\")
    print(f\"Nombre: {data.get('name', 'N/A')}\")
    print(f\"Puerto: {data.get('port', 'N/A')}\")
    print(f\"Servicios disponibles:\")
    services = data.get('services', {})
    for name, info in services.items():
        print(f\"  • {name.title()}: {info.get('path', 'N/A')} - {info.get('description', 'N/A')}\")
    print(f\"Timestamp: {data.get('timestamp', 'N/A')}\")
except:
    print('Error parseando respuesta de la API')
"
        else
            echo "❌ API NO RESPONDE"
        fi
        
    else
        echo "❌ Aplicación NO CORRIENDO"
    fi
    
    echo ""
    echo "=== URLs de Acceso ==="
    echo "🏠 Página Principal: http://localhost:$PORT/"
    echo "🗺️ Mapa Interactivo: http://localhost:$PORT/interactive"
    echo "🎨 Generador Imágenes: http://localhost:$PORT/images"
    echo "🔧 API Info: http://localhost:$PORT/api/info"
    echo "📊 API Mapa: http://localhost:$PORT/api/interactive-map (POST)"
    echo "🖼️ API Imágenes: http://localhost:$PORT/api/generate-image (POST)"
    echo ""
}

start_app() {
    echo "🚀 Iniciando $APP_NAME..."
    
    # Verificar si ya está corriendo
    if pgrep -f "python.*unified_server_updated.py" > /dev/null; then
        echo "⚠️  La aplicación ya está corriendo"
        show_status
        return
    fi
    
    # Liberar puerto si está ocupado
    if ss -tlnp | grep ":$PORT" > /dev/null 2>&1; then
        echo "🔧 Liberando puerto $PORT..."
        PID_PORT=$(ss -tlnp | grep ":$PORT" | grep -o 'pid=[0-9]*' | cut -d= -f2 | head -1)
        if [ ! -z "$PID_PORT" ]; then
            kill -9 $PID_PORT 2>/dev/null || true
            sleep 2
        fi
    fi
    
    # Iniciar aplicación
    echo "📦 Ejecutando: python3 $SCRIPT_PATH --port=$PORT"
    nohup python3 $SCRIPT_PATH --port=$PORT > $LOG_FILE 2>&1 &
    
    # Esperar un momento para que inicie
    sleep 3
    
    # Verificar inicio
    if pgrep -f "python.*unified_server_updated.py" > /dev/null; then
        echo "✅ Aplicación iniciada correctamente"
        
        # Probar API
        if curl -s http://localhost:$PORT/api/info > /dev/null; then
            echo "✅ API funcionando correctamente"
            echo ""
            echo "=== Prueba de Funcionalidad ==="
            
            # Probar mapa interactivo
            echo "🗺️ Probando mapa interactivo (3000 números)..."
            INTERACTIVE_RESULT=$(curl -s -X POST http://localhost:$PORT/api/interactive-map \
              -H "Content-Type: application/json" \
              -d '{\n                \"num_circulos\": 100,\n                \"divisiones_por_circulo\": 30,\n                \"tipo_mapeo\": \"lineal\",\n                \"mostrar_regulares\": true,\n                \"mostrar_gemelos\": true\n              }' | python3 -c "\nimport sys, json\ntry:\n    data = json.load(sys.stdin)\n    stats = data['estadisticas']\n    meta = data['metadata']\n    print(f\"✅ Procesados {len(data['elementos'])} elementos\")\n    print(f\"✅ Encontrados {stats['total_primos']} primos\")\n    print(f\"✅ Densidad: {stats['densidad_primos']:.2f}%\")\n    print(f\"✅ Límite: {meta['limite']} números\")\n    print(f\"✅ Configuración: {meta['num_circulos']} círculos × {meta['divisiones_por_circulo']} segmentos\")\nexcept Exception as e:\n    print(f'❌ Error en prueba interactiva: {e}')\n")\n            echo "$INTERACTIVE_RESULT"\n            \n            # Probar generador de imágenes\n            echo "🎨 Probando generador de imágenes..."\n            if curl -s -X POST http://localhost:$PORT/api/generate-image \\\n              -H "Content-Type: application/json" \\\n              -d '{\n                \"num_circulos\": 5,\n                \"divisiones_por_circulo\": 12,\n                \"tipo_mapeo\": \"lineal\",\n                \"dpi\": 150\n              }' --output /tmp/test_unified.png > /dev/null 2>&1; then\n                echo "✅ Generador de imágenes funcionando"\n                echo "✅ Imagen de prueba guardada en /tmp/test_unified.png"\n                rm -f /tmp/test_unified.png 2>/dev/null\n            else\n                echo "❌ Error en generador de imágenes"\n            fi\n        else\n            echo "❌ API no responde después del inicio"\n        fi\n    else\n        echo "❌ Error iniciando la aplicación"\n        echo "📋 Últimas líneas del log:"\n        tail -10 $LOG_FILE 2>/dev/null || echo "No se pudo leer el log"\n    fi\n    \n    echo ""\n    show_status\n}\n\nstop_app() {\n    echo "🛑 Deteniendo $APP_NAME..."\n    \n    # Buscar y terminar procesos\n    PIDS=$(pgrep -f "python.*unified_server_updated.py" || true)\n    \n    if [ -z "$PIDS" ]; then\n        echo "ℹ️  No hay procesos corriendo"\n    else\n        echo "🔧 Terminando procesos: $PIDS"\n        echo "$PIDS" | xargs kill -TERM 2>/dev/null || true\n        sleep 2\n        \n        # Verificar si siguen corriendo\n        REMAINING=$(pgrep -f "python.*unified_server_updated.py" || true)\n        if [ ! -z "$REMAINING" ]; then\n            echo "🔨 Forzando terminación: $REMAINING"\n            echo "$REMAINING" | xargs kill -9 2>/dev/null || true\n        fi\n    fi\n    \n    # Liberar puerto\n    if ss -tlnp | grep ":$PORT" > /dev/null 2>&1; then\n        echo "🔧 Liberando puerto $PORT..."\n        PID_PORT=$(ss -tlnp | grep ":$PORT" | grep -o 'pid=[0-9]*' | cut -d= -f2 | head -1)\n        if [ ! -z "$PID_PORT" ]; then\n            kill -9 $PID_PORT 2>/dev/null || true\n        fi\n    fi\n    \n    sleep 1\n    echo "✅ Aplicación detenida"\n}\n\nrestart_app() {\n    echo "🔄 Reiniciando $APP_NAME..."\n    stop_app\n    sleep 2\n    start_app\n}\n\nshow_logs() {\n    echo "📋 Últimas líneas del log ($LOG_FILE):"\n    echo "================================================"\n    tail -50 $LOG_FILE 2>/dev/null || echo "No se pudo leer el archivo de log"\n    echo "================================================"\n}\n\ntest_api() {\n    echo "🧪 Probando APIs del servidor unificado..."\n    \n    if ! curl -s http://localhost:$PORT/api/info > /dev/null; then\n        echo "❌ Servidor no disponible"\n        return 1\n    fi\n    \n    echo ""\n    echo "=== Prueba 1: Mapa Interactivo Pequeño (240 números) ==="\n    curl -s -X POST http://localhost:$PORT/api/interactive-map \\\n      -H "Content-Type: application/json" \\\n      -d '{\n        \"num_circulos\": 10,\n        \"divisiones_por_circulo\": 24,\n        \"tipo_mapeo\": \"lineal\",\n        \"mostrar_regulares\": true,\n        \"mostrar_gemelos\": true\n      }' | python3 -c "\nimport sys, json\ntry:\n    data = json.load(sys.stdin)\n    stats = data['estadisticas']\n    meta = data['metadata']\n    print(f\"✅ {len(data['elementos'])} elementos, {stats['total_primos']} primos ({stats['densidad_primos']:.2f}%)\")\n    print(f\"✅ Límite: {meta['limite']}, Mapeo: {meta['tipo_mapeo']}\")\nexcept Exception as e:\n    print(f'❌ Error: {e}')\n"\n    \n    echo ""\n    echo "=== Prueba 2: Mapa Interactivo Máximo (3000 números) ==="\n    curl -s -X POST http://localhost:$PORT/api/interactive-map \\\n      -H "Content-Type: application/json" \\\n      -d '{\n        \"num_circulos\": 100,\n        \"divisiones_por_circulo\": 30,\n        \"tipo_mapeo\": \"fibonacci\",\n        \"mostrar_regulares\": true,\n        \"mostrar_gemelos\": true,\n        \"mostrar_sophie_germain\": true,\n        \"mostrar_mersenne\": true\n      }' | python3 -c "\nimport sys, json\ntry:\n    data = json.load(sys.stdin)\n    stats = data['estadisticas']\n    meta = data['metadata']\n    print(f\"✅ {len(data['elementos'])} elementos, {stats['total_primos']} primos ({stats['densidad_primos']:.2f}%)\")\n    print(f\"✅ Límite: {meta['limite']}, Mapeo: {meta['tipo_mapeo']}\")\n    print(f\"✅ Configuración: {meta['num_circulos']} círculos × {meta['divisiones_por_circulo']} segmentos\")\nexcept Exception as e:\n    print(f'❌ Error: {e}')\n"\n    \n    echo ""\n    echo "=== Prueba 3: Generador de Imágenes ==="\n    if curl -s -X POST http://localhost:$PORT/api/generate-image \\\n      -H "Content-Type: application/json" \\\n      -d '{\n        \"num_circulos\": 8,\n        \"divisiones_por_circulo\": 16,\n        \"tipo_mapeo\": \"arquimedes\",\n        \"dpi\": 150,\n        \"mostrar_regulares\": true,\n        \"mostrar_gemelos\": true\n      }' --output /tmp/test_unified_api.png > /dev/null 2>&1; then\n        SIZE=$(ls -lh /tmp/test_unified_api.png | awk '{print $5}')\n        echo "✅ Imagen generada correctamente (${SIZE})"\n        rm -f /tmp/test_unified_api.png 2>/dev/null\n    else\n        echo "❌ Error generando imagen"\n    fi\n    \n    echo ""\n    echo "=== Prueba 4: Análisis de Número Específico ==="\n    curl -s http://localhost:$PORT/api/number/2999 | python3 -c "\nimport sys, json\ntry:\n    data = json.load(sys.stdin)\n    print(f\"✅ Número {data['numero']}: {'PRIMO' if data['es_primo'] else 'COMPUESTO'}\")\n    if data['clasificaciones']:\n        print(f\"✅ Clasificaciones: {', '.join(data['clasificaciones'])}\")\n    props = data['propiedades']\n    print(f\"✅ Propiedades: {len(props)} encontradas\")\n    print(f\"   • Par: {props['par']}, Dígitos: {props['digitos']}, Suma dígitos: {props['suma_digitos']}\")\nexcept Exception as e:\n    print(f'❌ Error: {e}')\n"\n}\n\nshow_help() {\n    echo "=== Gestor de $APP_NAME ==="\n    echo ""\n    echo "Uso: $0 [comando]"\n    echo ""\n    echo "Comandos disponibles:"\n    echo "  start     - Iniciar el servidor unificado"\n    echo "  stop      - Detener el servidor"\n    echo "  restart   - Reiniciar el servidor"\n    echo "  status    - Mostrar estado actual"\n    echo "  logs      - Mostrar logs recientes"\n    echo "  test      - Probar funcionalidad completa"\n    echo "  help      - Mostrar esta ayuda"\n    echo ""\n    echo "Características de esta versión:"\n    echo "  • Servidor unificado en puerto 3000"\n    echo "  • Mapa interactivo con círculos adaptativos"\n    echo "  • Generador de imágenes PNG con leyenda"\n    echo "  • Soporte hasta 3000 números primos"\n    echo "  • Múltiples tipos de mapeo geométrico"\n    echo "  • Análisis matemático en tiempo real"\n    echo ""\n    echo "Servicios disponibles:"\n    echo "  🏠 Página principal: http://localhost:$PORT/"\n    echo "  🗺️ Mapa interactivo: http://localhost:$PORT/interactive"\n    echo "  🎨 Generador imágenes: http://localhost:$PORT/images"\n    echo "  🔧 API información: http://localhost:$PORT/api/info"\n    echo ""\n}\n\n# Procesamiento de comandos\ncase "${1:-help}" in\n    "start")\n        start_app\n        ;;\n    "stop")\n        stop_app\n        ;;\n    "restart")\n        restart_app\n        ;;\n    "status")\n        show_status\n        ;;\n    "logs")\n        show_logs\n        ;;\n    "test")\n        test_api\n        ;;\n    "help"|"--help"|"-h")\n        show_help\n        ;;\n    *)\n        echo "❌ Comando desconocido: $1"\n        echo ""\n        show_help\n        exit 1\n        ;;\nesac