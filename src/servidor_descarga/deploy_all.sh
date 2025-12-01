#!/bin/bash

echo "🚀 DESPLEGANDO SISTEMA COMPLETO DE MAPAS PRIMOS"
echo "=============================================="
echo ""

# Función para verificar puertos
check_port() {
    python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', $1))
sock.close()
exit(0 if result == 0 else 1)
"
}

echo "🧹 Limpiando procesos existentes..."
pkill -f "interactive_server.py" 2>/dev/null || true
pkill -f "image_server.py" 2>/dev/null || true
pkill -f "static_app.py" 2>/dev/null || true
sleep 3

echo ""
echo "📍 Desplegando servicios separados..."
echo ""

# Desplegar servidor interactivo (puerto 3000)
echo "1️⃣ Desplegando Servidor Interactivo..."
./deploy_interactive.sh > /dev/null 2>&1 &
sleep 6

# Verificar servidor interactivo
if check_port 3000; then
    echo "   ✅ Servidor Interactivo: ACTIVO en puerto 3000"
else
    echo "   ❌ Servidor Interactivo: FALLO"
fi

echo ""

# Desplegar generador de imágenes (puerto 3002)
echo "2️⃣ Desplegando Generador de Imágenes..."
./deploy_images.sh > /dev/null 2>&1 &
sleep 6

# Verificar generador de imágenes
if check_port 3002; then
    echo "   ✅ Generador de Imágenes: ACTIVO en puerto 3002"
else
    echo "   ❌ Generador de Imágenes: FALLO"
fi

echo ""
echo "🌐 SISTEMA COMPLETO DESPLEGADO"
echo "============================="
echo ""
echo "🗺️ MAPA INTERACTIVO:"
echo "   📍 http://3.144.134.110:3000/"
echo "   🎮 Zoom, drag, tooltips, tipos de primos completos"
echo ""
echo "🎨 GENERADOR DE IMÁGENES:"
echo "   📍 http://localhost:3002/ (solo local)"
echo "   📥 Descarga PNG optimizada (solo primos)"
echo ""
echo "📊 ESTADO DE SERVICIOS:"
ps aux | grep -E "(interactive_server|image_server)" | grep -v grep | awk '{printf "   🟢 %s (PID: %s)\n", $11, $2}'

echo ""
echo "📋 COMANDOS DE CONTROL:"
echo "   Parar todo:       pkill -f 'interactive_server\\|image_server'"
echo "   Solo interactivo: pkill -f interactive_server"
echo "   Solo imágenes:    pkill -f image_server"
echo "   Ver logs:         tail -f *_deployment.log"
echo ""
echo "✅ DESPLIEGUE COMPLETO FINALIZADO"