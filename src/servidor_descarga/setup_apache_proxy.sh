#!/bin/bash
# Script para configurar Apache como proxy del puerto 80 al 3000

echo "🌐 Configurando Apache como proxy del puerto 80 al 3000..."

# Verificar si Apache está instalado
if ! command -v apache2 &> /dev/null; then
    echo "❌ Apache no está instalado. Este script requiere Apache."
    exit 1
fi

# Habilitar módulos de proxy
echo "📦 Habilitando módulos de proxy en Apache..."
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_balancer
sudo a2enmod lbmethod_byrequests

# Crear configuración de proxy
echo "📝 Creando configuración de proxy..."
sudo tee /etc/apache2/sites-available/servidor_descarga.conf << EOL
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    # Configuración de proxy para el servidor en puerto 3000
    ProxyPreserveHost On
    ProxyPass / http://localhost:3000/
    ProxyPassReverse / http://localhost:3000/

    ErrorLog \${APACHE_LOG_DIR}/error.log
    CustomLog \${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOL

# Habilitar el sitio
echo "✅ Habilitando el sitio..."
sudo a2ensite servidor_descarga.conf

# Reiniciar Apache
echo "🔄 Reiniciando Apache..."
sudo systemctl restart apache2

# Verificar estado de Apache
echo "🔍 Verificando estado de Apache..."
sudo systemctl status apache2 --no-pager

# Actualizar el servicio para usar el puerto 3000
echo "🔄 Actualizando servicio para usar el puerto 3000..."
sudo systemctl stop dns_persistence.service

# Esperar a que el servicio se detenga
sleep 2

# Iniciar el servicio
echo "🚀 Iniciando servicio en puerto 3000..."
sudo systemctl start dns_persistence.service

# Verificar estado del servicio
echo "🔍 Verificando estado del servicio..."
sudo systemctl status dns_persistence.service --no-pager

# Verificar puertos
echo "🔍 Verificando puertos..."
sudo ss -tlnp | grep -E ':(80|3000)'

# Actualizar archivo de configuración DNS
echo "📝 Actualizando archivo de configuración DNS..."
DNS_PUBLICO="ec2-3-144-134-110.us-east-2.compute.amazonaws.com"
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname -f)

cat > /home/admin/servidor_descarga/dns_ec2_config.json << EOL
{
    "hostname": "$HOSTNAME",
    "ip": "$LOCAL_IP",
    "dns_publico": "$DNS_PUBLICO",
    "port": 80,
    "urls": {
        "dns_publico": "http://$DNS_PUBLICO/",
        "hostname": "http://$HOSTNAME/",
        "ip_publica": "http://$LOCAL_IP/",
        "localhost": "http://localhost/"
    },
    "proxy": {
        "from_port": 80,
        "to_port": 3000,
        "proxy_server": "apache2"
    },
    "configurado_en": "$(date)"
}
EOL

# Actualizar archivo de información DNS
echo "📄 Actualizando archivo de información DNS..."
cat > /home/admin/servidor_descarga/DNS_EC2_INFO.md << EOL
# 🌐 CONFIGURACIÓN DNS PERSISTENTE PARA EC2 CON PROXY APACHE

## ✅ ESTADO: **ACTIVO Y CONFIGURADO**

### 📍 ACCESOS DNS DISPONIBLES:

#### 🔥 **DNS PÚBLICO EC2 (Sin Puerto)**
\`\`\`
http://$DNS_PUBLICO/
\`\`\`

#### 🌍 **HOSTNAME (Sin Puerto)**
\`\`\`  
http://$HOSTNAME/
\`\`\`

#### 📍 **IP PÚBLICA (Sin Puerto)**
\`\`\`  
http://$LOCAL_IP/
\`\`\`

#### 🔗 **LOCALHOST (Sin Puerto)** 
\`\`\`
http://localhost/
\`\`\`

## 🎯 ENDPOINTS DISPONIBLES

### 🏠 Interfaz Principal
- **URL**: \`http://$DNS_PUBLICO/\`
- **Descripción**: Selector de 980 mapas interactivos
- **Acceso**: Público desde cualquier ubicación

### 📊 API Información
- **URL**: \`http://$DNS_PUBLICO/api/info\`
- **Método**: GET
- **Respuesta**: Info del sistema y estadísticas

### 🗺️ Lista de Mapas
- **URL**: \`http://$DNS_PUBLICO/api/maps\`
- **Método**: GET  
- **Respuesta**: Lista completa de 980 mapas disponibles

### 🎲 Mapa Aleatorio
- **URL**: \`http://$DNS_PUBLICO/api/random-map\`
- **Método**: GET
- **Respuesta**: Mapa aleatorio instantáneo

### 🧮 Análisis de Números
- **URL**: \`http://$DNS_PUBLICO/api/number/{numero}\`
- **Método**: GET
- **Ejemplo**: \`http://$DNS_PUBLICO/api/number/97\`

### 🔍 Verificación DNS
- **URL**: \`http://$DNS_PUBLICO/dns-check\`
- **Método**: GET
- **Respuesta**: Estado de la configuración DNS

## ⚡ CARACTERÍSTICAS DE PERSISTENCIA

- ✅ **Inicio automático en arranque** - Servicio systemd
- ✅ **Reinicio automático tras fallos** - Configuración Restart=always
- ✅ **Proxy puerto 80 a 3000** - Apache configurado
- ✅ **Acceso sin especificar puerto** - URLs limpias
- ✅ **Logs persistentes** - Almacenados en /home/admin/servidor_descarga/logs
- ✅ **Acceso DNS persistente** - Configurado para DNS público EC2
- ✅ **Monitorización continua** - Verificación de estado DNS

## 📋 COMANDOS DE CONTROL

### Verificar Estado de Servicios
\`\`\`bash
sudo systemctl status dns_persistence.service
sudo systemctl status apache2
\`\`\`

### Ver Logs en Tiempo Real
\`\`\`bash
tail -f /home/admin/servidor_descarga/dns_persistence.log
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log
\`\`\`

### Detener Servicios
\`\`\`bash
sudo systemctl stop dns_persistence.service
sudo systemctl stop apache2
\`\`\`

### Reiniciar Servicios
\`\`\`bash
sudo systemctl restart dns_persistence.service
sudo systemctl restart apache2
\`\`\`

## 🔥 CONFIGURACIÓN PERSISTENTE COMPLETADA

**Configuración realizada**: $(date)
EOL

# Actualizar script de verificación
echo "📝 Actualizando script de verificación..."
cat > /home/admin/servidor_descarga/check_ec2_dns.sh << EOL
#!/bin/bash
# Script para verificar estado de la configuración DNS EC2 con proxy Apache

echo "🔍 Verificando estado de la configuración DNS EC2 con proxy Apache..."
echo ""
echo "📡 Servidor principal:"
sudo systemctl status dns_persistence.service --no-pager
echo ""
echo "📡 Servidor proxy (Apache):"
sudo systemctl status apache2 --no-pager
echo ""

# Verificar puertos
echo "🔍 Verificando puertos..."
sudo ss -tlnp | grep -E ':(80|3000)'
echo ""

# Verificar acceso DNS
DNS_PUBLICO="$DNS_PUBLICO"

echo "🌐 Verificando acceso DNS..."
curl -s -o /dev/null -w "%{http_code}" http://localhost/dns-check
if [ \$? -eq 0 ]; then
    echo "✅ Acceso local (puerto 80) funcionando correctamente"
else
    echo "❌ Problema con acceso local (puerto 80)"
fi

curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/dns-check
if [ \$? -eq 0 ]; then
    echo "✅ Acceso local (puerto 3000) funcionando correctamente"
else
    echo "❌ Problema con acceso local (puerto 3000)"
fi

echo ""
echo "🔗 URLs disponibles (sin puerto):"
echo "   🌐 DNS Público: http://$DNS_PUBLICO/"
echo "   🏠 Hostname: http://$HOSTNAME/"
echo "   📍 IP: http://$LOCAL_IP/"
echo "   🔗 Localhost: http://localhost/"
EOL

chmod +x /home/admin/servidor_descarga/check_ec2_dns.sh

echo "✅ Configuración de proxy Apache completada"
echo ""
echo "🌐 ACCESOS DNS DISPONIBLES (sin puerto):"
echo "   🌐 DNS Público: http://$DNS_PUBLICO/"
echo "   🏠 Hostname: http://$HOSTNAME/"
echo "   📍 IP: http://$LOCAL_IP/"
echo "   🔗 Localhost: http://localhost/"
echo ""
echo "📋 Para verificar el estado, ejecute:"
echo "   ./check_ec2_dns.sh"
echo ""
echo "📄 Para más información, consulte el archivo DNS_EC2_INFO.md"