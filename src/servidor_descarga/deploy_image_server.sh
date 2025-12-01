#!/bin/bash

echo "🎨 DESPLEGANDO GENERADOR DE IMÁGENES EN PUERTO 3002..."
echo "=================================================="

# Detener procesos existentes
echo "🛑 Deteniendo procesos existentes..."
pkill -f "image_server.py" 2>/dev/null || true
sleep 2

# Verificar que matplotlib esté disponible
echo "📦 Verificando dependencias..."
python3 -c "import matplotlib, numpy; print('✅ Dependencias OK')" || {
    echo "❌ Faltan dependencias, instalando..."
    pip3 install matplotlib numpy --break-system-packages
}

# Iniciar servidor
echo "🚀 Iniciando Generador de Imágenes..."
cd /home/admin/servidor_descarga

# Ejecutar con nohup para persistencia
nohup python3 -O image_server.py --port=3002 --host=0.0.0.0 \
    > image_deployment.log 2>&1 &

SERVER_PID=$!
echo "✅ Servidor iniciado con PID: $SERVER_PID"
echo $SERVER_PID > image_server.pid

# Esperar inicialización
echo "⏳ Esperando inicialización del servidor..."
sleep 4

# Verificar que esté funcionando
echo "🔍 Verificando servidor..."
if python3 -c "import requests; r = requests.get('http://localhost:3002/', timeout=5); print('✅ Test OK' if r.status_code == 200 else '❌ Test FAIL')" 2>/dev/null; then
    echo ""
    echo "🔥 GENERADOR DE IMÁGENES DESPLEGADO CON ÉXITO"
    echo "=========================================="
    echo ""
    echo "🌐 ACCESOS DISPONIBLES:"
    echo ""
    echo "   📍 IP PÚBLICA:   http://3.144.134.110:3002/"
    echo "   🌍 DNS/HOSTNAME: http://ec2-3-144-134-110.us-east-2.compute.amazonaws.com:3002/"
    echo "   🔗 LOCALHOST:    http://localhost:3002/"
    echo ""
    echo "🎯 CARACTERÍSTICAS:"
    echo "   • Generación de imágenes PNG de alta calidad"
    echo "   • Colores diferenciados por tipo de número"
    echo "   • Leyenda explicativa completa"
    echo "   • Parámetros personalizables"
    echo "   • Resoluciones: 150, 300, 600 DPI"
    echo "   • Descarga directa de archivos"
    echo ""
    echo "📋 Control del servidor:"
    echo "   Ver logs: tail -f image_deployment.log"
    echo "   Detener:  pkill -f image_server.py"
    echo "   Estado:   ps aux | grep image_server"
    echo ""
    echo "✅ DESPLIEGUE COMPLETADO - PUERTO 3002 ACTIVO"
    echo ""
else
    echo "❌ ERROR: El servidor no está respondiendo"
    echo "📋 Revisando logs..."
    tail -10 image_deployment.log
    exit 1
fi