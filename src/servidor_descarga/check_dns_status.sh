#!/bin/bash
# Script para verificar estado de los servicios DNS

echo "🔍 Verificando estado de los servicios DNS..."
echo ""
echo "📡 Servidor principal:"
sudo systemctl status servidor_descarga.service --no-pager
echo ""
echo "🔄 Auto-deploy webhook:"
sudo systemctl status autodeploy.service --no-pager
echo ""
echo "🌐 Verificando acceso DNS..."
curl -s -o /dev/null -w "%{http_code}" http://ip-172-31-40-57:3000/api/info
if [ $? -eq 0 ]; then
    echo "✅ Acceso DNS funcionando correctamente"
else
    echo "❌ Problema con acceso DNS"
fi
echo ""
echo "🔗 URLs disponibles:"
echo "   🏠 Principal: http://ip-172-31-40-57:3000/"
echo "   🌍 IP: http://172.31.40.57:3000/"
echo "   🔄 Webhook: http://ip-172-31-40-57:9000/webhook"
