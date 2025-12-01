#!/bin/bash

echo "🎨 DESPLEGANDO GENERADOR DE IMÁGENES EN PUERTO 3002..."
echo "====================================================="

# Detener procesos existentes
echo "🛑 Deteniendo procesos existentes..."
pkill -f "image_server.py" 2>/dev/null || true
sleep 2

# Verificar dependencias
echo "📦 Verificando dependencias..."
python3 -c "import matplotlib, numpy; print('✅ Dependencias OK')" || {
    echo "❌ Faltan dependencias, instalando..."
    pip3 install matplotlib numpy --break-system-packages
}

# Configuración de red
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)

echo "📍 Configuración de red detectada:"
echo "   🔸 IP Local: $LOCAL_IP"
echo "   🔸 Hostname: $HOSTNAME"

# Iniciar servidor de imágenes
echo "🚀 Iniciando Generador de Imágenes..."
cd /home/admin/servidor_descarga

# Ejecutar con nohup para persistencia
nohup python3 -O image_server.py --port=3002 --host=0.0.0.0 \
    > images_deployment.log 2>&1 &

SERVER_PID=$!
echo "✅ Servidor iniciado con PID: $SERVER_PID"
echo $SERVER_PID > image_server.pid

# Esperar inicialización
echo "⏳ Esperando inicialización del servidor..."
sleep 4

# Verificar que esté funcionando
echo "🔍 Verificando generador de imágenes..."
if python3 -c "import requests; r = requests.get('http://localhost:3002/', timeout=5); print('✅ Test OK' if r.status_code == 200 else '❌ Test FAIL')" 2>/dev/null; then
    echo ""
    echo "🔥 GENERADOR DE IMÁGENES DESPLEGADO CON ÉXITO"
    echo "============================================"
    echo ""
    echo "🌐 ACCESOS DISPONIBLES:"
    echo ""
    echo "   📍 IP LOCAL:     http://$LOCAL_IP:3002/"
    echo "   🌍 HOSTNAME:     http://$HOSTNAME:3002/"
    echo "   🔗 LOCALHOST:    http://localhost:3002/"
    echo ""
    echo "🎯 FUNCIONALIDADES:"
    echo "   • Generación de imágenes PNG optimizada"
    echo "   • Solo números primos (sin compuestos)"
    echo "   • Colores diferenciados por tipo de primo"
    echo "   • Leyenda explicativa automática"
    echo "   • Parámetros en el encabezado de la imagen"
    echo "   • Múltiples resoluciones DPI"
    echo "   • Descarga automática de archivos"
    echo ""
    echo "⚙️ CONFIGURACIÓN:"
    echo "   • Círculos: 3-25"
    echo "   • Divisiones: 6-60"
    echo "   • Mapeos: lineal, logarítmico, arquímedes, fibonacci"
    echo "   • DPI: 150, 300, 600"
    echo ""
    echo "📋 Control del servidor:"
    echo "   Ver logs: tail -f images_deployment.log"
    echo "   Detener:  pkill -f image_server.py"
    echo "   Estado:   ps aux | grep image_server"
    echo ""
    echo "✅ DESPLIEGUE DE IMÁGENES COMPLETADO - PUERTO 3002 ACTIVO"
    echo ""
else
    echo "❌ ERROR: El servidor no está respondiendo"
    echo "📋 Revisando logs..."
    tail -10 images_deployment.log
    exit 1
fi