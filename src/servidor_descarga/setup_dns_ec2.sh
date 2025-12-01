#!/bin/bash
# Script para configurar persistencia DNS para EC2

echo "🌐 Configurando persistencia DNS para EC2..."

# DNS público configurado
DNS_PUBLICO="ec2-3-144-134-110.us-east-2.compute.amazonaws.com"
PUERTO=3001

# Obtener información de red
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname -f)

echo "📍 Configuración de red detectada:"
echo "   🔸 IP Local: $LOCAL_IP"
echo "   🔸 Hostname: $HOSTNAME"
echo "   🔸 DNS Público: $DNS_PUBLICO"

# Crear directorio para logs si no existe
mkdir -p /home/admin/servidor_descarga/logs

# Verificar si systemd está disponible
if ! command -v systemctl &> /dev/null; then
    echo "❌ ERROR: systemd no está disponible en este sistema"
    exit 1
fi

# Copiar archivos de servicio a systemd
echo "📋 Instalando servicios systemd..."
sudo cp /home/admin/servidor_descarga/dns_persistence.service /etc/systemd/system/

# Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar servicios para inicio automático
echo "✅ Habilitando servicios para inicio automático..."
sudo systemctl enable dns_persistence.service

# Detener servicios existentes
echo "🛑 Deteniendo servicios existentes..."
sudo systemctl stop servidor_descarga.service 2>/dev/null || true
sudo systemctl stop autodeploy.service 2>/dev/null || true
sudo fuser -k 3000/tcp 2>/dev/null || true
sudo fuser -k 3001/tcp 2>/dev/null || true

# Iniciar servicios
echo "🚀 Iniciando servicios..."
sudo systemctl start dns_persistence.service

# Esperar a que el servicio se inicie
echo "⏳ Esperando a que el servicio se inicie..."
sleep 5

# Verificar estado de los servicios
echo "🔍 Verificando estado de los servicios..."
sudo systemctl status dns_persistence.service --no-pager

# Crear archivo de configuración DNS
echo "📝 Creando archivo de configuración DNS..."
cat > /home/admin/servidor_descarga/dns_ec2_config.json << EOL
{
    "hostname": "$HOSTNAME",
    "ip": "$LOCAL_IP",
    "dns_publico": "$DNS_PUBLICO",
    "port": $PUERTO,
    "urls": {
        "dns_publico": "http://$DNS_PUBLICO:$PUERTO/",
        "hostname": "http://$HOSTNAME:$PUERTO/",
        "ip_publica": "http://$LOCAL_IP:$PUERTO/",
        "localhost": "http://localhost:$PUERTO/"
    },
    "configurado_en": "$(date)"
}
EOL

# Crear archivo de información DNS
echo "📄 Creando archivo de información DNS..."
cat > /home/admin/servidor_descarga/DNS_EC2_INFO.md << EOL
# 🌐 CONFIGURACIÓN DNS PERSISTENTE PARA EC2

## ✅ ESTADO: **ACTIVO Y CONFIGURADO**

### 📍 ACCESOS DNS DISPONIBLES:

#### 🔥 **DNS PÚBLICO EC2**
\`\`\`
http://$DNS_PUBLICO:$PUERTO/
\`\`\`

#### 🌍 **HOSTNAME**
\`\`\`  
http://$HOSTNAME:$PUERTO/
\`\`\`

#### 📍 **IP PÚBLICA**
\`\`\`  
http://$LOCAL_IP:$PUERTO/
\`\`\`

#### 🔗 **LOCALHOST** 
\`\`\`
http://localhost:$PUERTO/
\`\`\`

## 🎯 ENDPOINTS DISPONIBLES

### 🏠 Interfaz Principal
- **URL**: \`http://$DNS_PUBLICO:$PUERTO/\`
- **Descripción**: Selector de 980 mapas interactivos
- **Acceso**: Público desde cualquier ubicación

### 📊 API Información
- **URL**: \`http://$DNS_PUBLICO:$PUERTO/api/info\`
- **Método**: GET
- **Respuesta**: Info del sistema y estadísticas

### 🗺️ Lista de Mapas
- **URL**: \`http://$DNS_PUBLICO:$PUERTO/api/maps\`
- **Método**: GET  
- **Respuesta**: Lista completa de 980 mapas disponibles

### 🎲 Mapa Aleatorio
- **URL**: \`http://$DNS_PUBLICO:$PUERTO/api/random-map\`
- **Método**: GET
- **Respuesta**: Mapa aleatorio instantáneo

### 🧮 Análisis de Números
- **URL**: \`http://$DNS_PUBLICO:$PUERTO/api/number/{numero}\`
- **Método**: GET
- **Ejemplo**: \`http://$DNS_PUBLICO:$PUERTO/api/number/97\`

### 🔍 Verificación DNS
- **URL**: \`http://$DNS_PUBLICO:$PUERTO/dns-check\`
- **Método**: GET
- **Respuesta**: Estado de la configuración DNS

## ⚡ CARACTERÍSTICAS DE PERSISTENCIA

- ✅ **Inicio automático en arranque** - Servicio systemd
- ✅ **Reinicio automático tras fallos** - Configuración Restart=always
- ✅ **Logs persistentes** - Almacenados en /home/admin/servidor_descarga/logs
- ✅ **Acceso DNS persistente** - Configurado para DNS público EC2
- ✅ **Monitorización continua** - Verificación de estado DNS

## 📋 COMANDOS DE CONTROL

### Verificar Estado de Servicios
\`\`\`bash
sudo systemctl status dns_persistence.service
\`\`\`

### Ver Logs en Tiempo Real
\`\`\`bash
tail -f /home/admin/servidor_descarga/dns_persistence.log
\`\`\`

### Detener Servicios
\`\`\`bash
sudo systemctl stop dns_persistence.service
\`\`\`

### Reiniciar Servicios
\`\`\`bash
sudo systemctl restart dns_persistence.service
\`\`\`

## 🔥 CONFIGURACIÓN PERSISTENTE COMPLETADA

**Configuración realizada**: $(date)
EOL

# Crear script para verificar estado DNS
echo "📝 Creando script para verificar estado DNS..."
cat > /home/admin/servidor_descarga/check_ec2_dns.sh << EOL
#!/bin/bash
# Script para verificar estado de la configuración DNS EC2

echo "🔍 Verificando estado de la configuración DNS EC2..."
echo ""
echo "📡 Servidor principal:"
sudo systemctl status dns_persistence.service --no-pager
echo ""

# Verificar acceso DNS
DNS_PUBLICO="$DNS_PUBLICO"
PUERTO=$PUERTO

echo "🌐 Verificando acceso DNS..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:$PUERTO/dns-check
if [ \$? -eq 0 ]; then
    echo "✅ Acceso local funcionando correctamente"
else
    echo "❌ Problema con acceso local"
fi

echo ""
echo "🔗 URLs disponibles:"
echo "   🌐 DNS Público: http://$DNS_PUBLICO:$PUERTO/"
echo "   🏠 Hostname: http://$HOSTNAME:$PUERTO/"
echo "   📍 IP: http://$LOCAL_IP:$PUERTO/"
echo "   🔗 Localhost: http://localhost:$PUERTO/"
EOL

# Hacer ejecutable el script de verificación
chmod +x /home/admin/servidor_descarga/check_ec2_dns.sh

echo "✅ Configuración de persistencia DNS para EC2 completada"
echo ""
echo "🌐 ACCESOS DNS DISPONIBLES:"
echo "   🌐 DNS Público: http://$DNS_PUBLICO:$PUERTO/"
echo "   🏠 Hostname: http://$HOSTNAME:$PUERTO/"
echo "   📍 IP: http://$LOCAL_IP:$PUERTO/"
echo "   🔗 Localhost: http://localhost:$PUERTO/"
echo ""
echo "📋 Para verificar el estado, ejecute:"
echo "   ./check_ec2_dns.sh"
echo ""
echo "📄 Para más información, consulte el archivo DNS_EC2_INFO.md"