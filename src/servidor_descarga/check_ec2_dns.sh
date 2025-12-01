#!/bin/bash
# Script para verificar estado de la configuración DNS EC2 con proxy

echo "🔍 Verificando estado de la configuración DNS EC2 con proxy..."
echo ""
echo "📡 Servidor principal:"
sudo systemctl status dns_persistence.service --no-pager
echo ""
echo "📡 Servidor proxy (nginx):"
sudo systemctl status nginx --no-pager
echo ""

# Verificar puertos
echo "🔍 Verificando puertos..."
sudo ss -tlnp | grep -E ':(80|3000)'
echo ""

# Verificar acceso DNS
DNS_PUBLICO="ec2-3-144-134-110.us-east-2.compute.amazonaws.com"

echo "🌐 Verificando acceso DNS..."
curl -s -o /dev/null -w "%{http_code}" http://localhost/dns-check
if [ $? -eq 0 ]; then
    echo "✅ Acceso local (puerto 80) funcionando correctamente"
else
    echo "❌ Problema con acceso local (puerto 80)"
fi

curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/dns-check
if [ $? -eq 0 ]; then
    echo "✅ Acceso local (puerto 3000) funcionando correctamente"
else
    echo "❌ Problema con acceso local (puerto 3000)"
fi

echo ""
echo "🔗 URLs disponibles (sin puerto):"
echo "   🌐 DNS Público: http://ec2-3-144-134-110.us-east-2.compute.amazonaws.com/"
echo "   🏠 Hostname: http://ip-172-31-40-57/"
echo "   📍 IP: http://172.31.40.57/"
echo "   🔗 Localhost: http://localhost/"
