#!/bin/bash

# Script de gestión para la aplicación de visualización de primos (versión 3000)
# Actualizado para soportar hasta 3000 números con círculos adaptativos

APP_NAME="Enhanced Prime Visualization v3.2"
SCRIPT_PATH="/home/admin/deploy_enhanced.py"
PORT=3000
LOG_FILE="/home/admin/enhanced_app.log"

show_status() {
    echo "=== Estado de $APP_NAME ==="
    
    # Verificar si el proceso está corriendo
    if pgrep -f "python.*deploy_enhanced.py" > /dev/null; then
        PID=$(pgrep -f "python.*deploy_enhanced.py")
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
    print(f\"Características principales:\")
    for feature in data.get('features', []):
        print(f\"  • {feature}\")
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
    echo "🌐 Interfaz Principal: http://localhost:$PORT/"
    echo "🎯 Interfaz Mejorada: http://localhost:$PORT/enhanced"
    echo "🔧 API Info: http://localhost:$PORT/api/info"
    echo "📊 API Mapa Interactivo: http://localhost:$PORT/api/interactive-map (POST)"
    echo ""
}

start_app() {
    echo "🚀 Iniciando $APP_NAME..."
    
    # Verificar si ya está corriendo
    if pgrep -f "python.*deploy_enhanced.py" > /dev/null; then
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
    if pgrep -f "python.*deploy_enhanced.py" > /dev/null; then
        echo "✅ Aplicación iniciada correctamente"
        
        # Probar API
        if curl -s http://localhost:$PORT/api/info > /dev/null; then
            echo "✅ API funcionando correctamente"
            echo ""
            echo "=== Prueba de Funcionalidad (3000 números) ==="
            
            # Probar con configuración de 3000 números
            TEST_RESULT=$(curl -s -X POST http://localhost:$PORT/api/interactive-map \
              -H "Content-Type: application/json" \
              -d '{
                "num_circulos": 100,
                "divisiones_por_circulo": 30,
                "tipo_mapeo": "lineal",
                "mostrar_regulares": true,
                "mostrar_gemelos": true,
                "mostrar_compuestos": false
              }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    stats = data['estadisticas']
    print(f\"✅ Procesados {stats['total_numeros']} números\")
    print(f\"✅ Encontrados {stats['total_primos']} primos\")
    print(f\"✅ Densidad: {stats['densidad_primos']:.2f}%\")
    print(f\"✅ Primos gemelos: {stats['patrones']['gemelos']}\")
    print(f\"✅ Configuración: {stats['configuracion']['circulos']} círculos × {stats['configuracion']['segmentos']} segmentos\")
except Exception as e:
    print(f'❌ Error en prueba: {e}')
")
            echo "$TEST_RESULT"
        else
            echo "❌ API no responde después del inicio"
        fi
    else
        echo "❌ Error iniciando la aplicación"
        echo "📋 Últimas líneas del log:"
        tail -10 $LOG_FILE 2>/dev/null || echo "No se pudo leer el log"
    fi
    
    echo ""
    show_status
}

stop_app() {
    echo "🛑 Deteniendo $APP_NAME..."
    
    # Buscar y terminar procesos
    PIDS=$(pgrep -f "python.*deploy_enhanced.py" || true)
    
    if [ -z "$PIDS" ]; then
        echo "ℹ️  No hay procesos corriendo"
    else
        echo "🔧 Terminando procesos: $PIDS"
        echo "$PIDS" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        
        # Verificar si siguen corriendo
        REMAINING=$(pgrep -f "python.*deploy_enhanced.py" || true)
        if [ ! -z "$REMAINING" ]; then
            echo "🔨 Forzando terminación: $REMAINING"
            echo "$REMAINING" | xargs kill -9 2>/dev/null || true
        fi
    fi
    
    # Liberar puerto
    if ss -tlnp | grep ":$PORT" > /dev/null 2>&1; then
        echo "🔧 Liberando puerto $PORT..."
        PID_PORT=$(ss -tlnp | grep ":$PORT" | grep -o 'pid=[0-9]*' | cut -d= -f2 | head -1)
        if [ ! -z "$PID_PORT" ]; then
            kill -9 $PID_PORT 2>/dev/null || true
        fi
    fi
    
    sleep 1
    echo "✅ Aplicación detenida"
}

restart_app() {
    echo "🔄 Reiniciando $APP_NAME..."
    stop_app
    sleep 2
    start_app
}

show_logs() {
    echo "📋 Últimas líneas del log ($LOG_FILE):"
    echo "================================================"
    tail -50 $LOG_FILE 2>/dev/null || echo "No se pudo leer el archivo de log"
    echo "================================================"
}

test_api() {
    echo "🧪 Probando API con diferentes configuraciones..."
    
    if ! curl -s http://localhost:$PORT/api/info > /dev/null; then
        echo "❌ API no disponible"
        return 1
    fi
    
    echo ""
    echo "=== Prueba 1: Configuración pequeña (300 números) ==="
    curl -s -X POST http://localhost:$PORT/api/interactive-map \
      -H "Content-Type: application/json" \
      -d '{
        "num_circulos": 10,
        "divisiones_por_circulo": 30,
        "tipo_mapeo": "lineal",
        "mostrar_regulares": true,
        "mostrar_gemelos": true
      }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    stats = data['estadisticas']
    print(f\"✅ {stats['total_numeros']} números, {stats['total_primos']} primos ({stats['densidad_primos']:.2f}%)\")
    print(f\"✅ Elementos generados: {len(data['elementos'])}\")
except Exception as e:
    print(f'❌ Error: {e}')
"
    
    echo ""
    echo "=== Prueba 2: Configuración máxima (3000 números) ==="
    curl -s -X POST http://localhost:$PORT/api/interactive-map \
      -H "Content-Type: application/json" \
      -d '{
        "num_circulos": 100,
        "divisiones_por_circulo": 30,
        "tipo_mapeo": "fibonacci",
        "mostrar_regulares": true,
        "mostrar_gemelos": true,
        "mostrar_sophie_germain": true,
        "mostrar_mersenne": true
      }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    stats = data['estadisticas']
    print(f\"✅ {stats['total_numeros']} números, {stats['total_primos']} primos ({stats['densidad_primos']:.2f}%)\")
    print(f\"✅ Elementos generados: {len(data['elementos'])}\")
    print(f\"✅ Patrones encontrados:\")
    for tipo, cantidad in stats['patrones'].items():
        if cantidad > 0:
            print(f\"   • {tipo}: {cantidad}\")
except Exception as e:
    print(f'❌ Error: {e}')
"
    
    echo ""
    echo "=== Prueba 3: Análisis de número específico ==="
    curl -s http://localhost:$PORT/api/number/2999 | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"✅ Número {data['numero']}: {'PRIMO' if data['es_primo'] else 'COMPUESTO'}\")
    if data['tipos_primo']:
        print(f\"✅ Tipos especiales: {', '.join(data['tipos_primo'])}\")
    print(f\"✅ Propiedades: {len(data['propiedades'])} encontradas\")
    print(f\"✅ Fórmulas: {len(data['formulas'])} generadas\")
except Exception as e:
    print(f'❌ Error: {e}')
"
}

show_help() {
    echo "=== Gestor de $APP_NAME ==="
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Iniciar la aplicación"
    echo "  stop      - Detener la aplicación"
    echo "  restart   - Reiniciar la aplicación"
    echo "  status    - Mostrar estado actual"
    echo "  logs      - Mostrar logs recientes"
    echo "  test      - Probar funcionalidad de la API"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "Características de esta versión:"
    echo "  • Soporte hasta 3000 números primos"
    echo "  • Círculos adaptativos (más pequeños con más círculos)"
    echo "  • Múltiples tipos de mapeo geométrico"
    echo "  • Análisis matemático en tiempo real"
    echo "  • Interfaz web responsiva"
    echo ""
    echo "URLs de acceso:"
    echo "  http://localhost:$PORT/           - Interfaz principal"
    echo "  http://localhost:$PORT/enhanced   - Interfaz mejorada"
    echo "  http://localhost:$PORT/api/info   - Información de la API"
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
    "logs")
        show_logs
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