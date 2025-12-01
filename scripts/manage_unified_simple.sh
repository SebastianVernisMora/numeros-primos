#!/bin/bash

# Script de gestión simple para el Servidor Unificado
APP_NAME="Servidor Unificado de Mapas Primos v3.4.0"
SCRIPT_PATH="/home/admin/unified_server_updated.py"
PORT=3000

show_status() {
    echo "=== Estado de $APP_NAME ==="
    
    if pgrep -f "python.*unified_server_updated.py" > /dev/null; then
        PID=$(pgrep -f "python.*unified_server_updated.py")
        echo "✅ Aplicación CORRIENDO (PID: $PID)"
        
        if ss -tlnp | grep ":$PORT" > /dev/null 2>&1; then
            echo "✅ Puerto $PORT ACTIVO"
        else
            echo "❌ Puerto $PORT NO DISPONIBLE"
        fi
        
        if curl -s http://localhost:$PORT/api/info > /dev/null; then
            echo "✅ API RESPONDIENDO"
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
    echo ""
}

start_app() {
    echo "🚀 Iniciando $APP_NAME..."
    
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
    
    echo "📦 Ejecutando: python3 $SCRIPT_PATH --port=$PORT"
    nohup python3 $SCRIPT_PATH --port=$PORT > /dev/null 2>&1 &
    
    sleep 3
    
    if pgrep -f "python.*unified_server_updated.py" > /dev/null; then
        echo "✅ Aplicación iniciada correctamente"
        
        if curl -s http://localhost:$PORT/api/info > /dev/null; then
            echo "✅ API funcionando correctamente"
        else
            echo "❌ API no responde"
        fi
    else
        echo "❌ Error iniciando la aplicación"
    fi
    
    show_status
}

stop_app() {
    echo "🛑 Deteniendo $APP_NAME..."
    
    PIDS=$(pgrep -f "python.*unified_server_updated.py" || true)
    
    if [ -z "$PIDS" ]; then
        echo "ℹ️  No hay procesos corriendo"
    else
        echo "🔧 Terminando procesos: $PIDS"
        echo "$PIDS" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        
        REMAINING=$(pgrep -f "python.*unified_server_updated.py" || true)
        if [ ! -z "$REMAINING" ]; then
            echo "🔨 Forzando terminación: $REMAINING"
            echo "$REMAINING" | xargs kill -9 2>/dev/null || true
        fi
    fi
    
    echo "✅ Aplicación detenida"
}

restart_app() {
    echo "🔄 Reiniciando $APP_NAME..."
    stop_app
    sleep 2
    start_app
}

test_api() {
    echo "🧪 Probando APIs del servidor unificado..."
    
    if ! curl -s http://localhost:$PORT/api/info > /dev/null; then
        echo "❌ Servidor no disponible"
        return 1
    fi
    
    echo "✅ Servidor disponible"
    
    # Probar mapa interactivo
    echo "🗺️ Probando mapa interactivo..."
    if curl -s -X POST http://localhost:$PORT/api/interactive-map \
      -H "Content-Type: application/json" \
      -d '{"num_circulos": 10, "divisiones_por_circulo": 24}' > /dev/null; then
        echo "✅ Mapa interactivo funcionando"
    else
        echo "❌ Error en mapa interactivo"
    fi
    
    # Probar generador de imágenes
    echo "🎨 Probando generador de imágenes..."
    if curl -s -X POST http://localhost:$PORT/api/generate-image \
      -H "Content-Type: application/json" \
      -d '{"num_circulos": 5, "divisiones_por_circulo": 12}' \
      --output /tmp/test.png > /dev/null 2>&1; then
        echo "✅ Generador de imágenes funcionando"
        rm -f /tmp/test.png 2>/dev/null
    else
        echo "❌ Error en generador de imágenes"
    fi
}

show_help() {
    echo "=== Gestor de $APP_NAME ==="
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Iniciar el servidor"
    echo "  stop      - Detener el servidor"
    echo "  restart   - Reiniciar el servidor"
    echo "  status    - Mostrar estado actual"
    echo "  test      - Probar funcionalidad"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "URLs de acceso:"
    echo "  http://localhost:$PORT/           - Página principal"
    echo "  http://localhost:$PORT/interactive - Mapa interactivo"
    echo "  http://localhost:$PORT/images     - Generador de imágenes"
    echo ""
}

# Procesamiento de comandos
case "${1:-help}" in
    "start")
        start_app
        ;;
    "stop")
        stop_app
        ;;
    "restart")
        restart_app
        ;;
    "status")
        show_status
        ;;
    "test")
        test_api
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ Comando desconocido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac