#!/bin/bash

echo "🗺️ DESPLEGANDO MAPA INTERACTIVO EN PUERTO 3000..."
echo "================================================"

# Detener procesos existentes
echo "🛑 Deteniendo procesos existentes..."
pkill -f "interactive_server.py" 2>/dev/null || true
pkill -f "static_app.py.*port.*3000" 2>/dev/null || true
sleep 2

# Configuración de red
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)

echo "📍 Configuración de red detectada:"
echo "   🔸 IP Local: $LOCAL_IP"
echo "   🔸 Hostname: $HOSTNAME"

# Iniciar servidor interactivo
echo "🚀 Iniciando Mapa Interactivo..."
cd /home/admin/servidor_descarga

# Ejecutar con nohup para persistencia
nohup python3 -O interactive_server.py --port=3000 --host=0.0.0.0 \
    > interactive_deployment.log 2>&1 &

SERVER_PID=$!
echo "✅ Servidor iniciado con PID: $SERVER_PID"
echo $SERVER_PID > interactive_server.pid

# Esperar inicialización
echo "⏳ Esperando inicialización del servidor..."
sleep 4

# Verificar que esté funcionando
echo "🔍 Verificando mapa interactivo..."
if python3 -c "import requests; r = requests.get('http://localhost:3000/', timeout=5); print('✅ Test OK' if r.status_code == 200 else '❌ Test FAIL')" 2>/dev/null; then
    echo ""
    echo "🔥 MAPA INTERACTIVO DESPLEGADO CON ÉXITO"
    echo "======================================="
    echo ""
    echo "🌐 ACCESOS PÚBLICOS DISPONIBLES:"
    echo ""
    echo "   📍 IP PÚBLICA:   http://$LOCAL_IP:3000/"
    echo "   🌍 DNS/HOSTNAME: http://$HOSTNAME:3000/"
    echo "   🔗 LOCALHOST:    http://localhost:3000/"
    echo ""
    echo "🎯 FUNCIONALIDADES:"
    echo "   • Visualización interactiva en tiempo real"
    echo "   • Zoom y navegación (rueda del mouse + drag)"
    echo "   • Tooltips informativos al hacer hover"
    echo "   • Clasificación completa de tipos de primos"
    echo "   • Múltiples mapeos geométricos"
    echo "   • Controles de pantalla completa"
    echo ""
    echo "🎮 CONTROLES:"
    echo "   • Zoom: Botones +/- o rueda del mouse"
    echo "   • Mover: Click y arrastrar"
    echo "   • Reset: Botón de reset de zoom"
    echo "   • Info: Hover sobre números"
    echo ""
    echo "📋 Control del servidor:"
    echo "   Ver logs: tail -f interactive_deployment.log"
    echo "   Detener:  pkill -f interactive_server.py"
    echo "   Estado:   ps aux | grep interactive_server"
    echo ""
    echo "✅ DESPLIEGUE INTERACTIVO COMPLETADO - PUERTO 3000 ACTIVO"
    echo ""
else
    echo "❌ ERROR: El servidor no está respondiendo"
    echo "📋 Revisando logs..."
    tail -10 interactive_deployment.log
    exit 1
fi