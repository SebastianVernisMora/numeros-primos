#!/bin/bash

echo "🌐 Configurando proxy para Generador de Imágenes..."

# Verificar que Apache esté corriendo
if ! pgrep apache2 > /dev/null; then
    echo "❌ Apache no está corriendo"
    exit 1
fi

# Crear configuración para el proxy de imágenes
sudo tee /etc/apache2/sites-available/image-proxy.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName image.localhost
    DocumentRoot /var/www/html
    
    # Proxy para generador de imágenes
    ProxyPreserveHost On
    ProxyPass /images/ http://localhost:3002/
    ProxyPassReverse /images/ http://localhost:3002/
    
    # Logs
    ErrorLog ${APACHE_LOG_DIR}/image_proxy_error.log
    CustomLog ${APACHE_LOG_DIR}/image_proxy_access.log combined
</VirtualHost>
EOF

# Habilitar módulos necesarios
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite

# Habilitar el sitio
sudo a2ensite image-proxy

# Recargar Apache
sudo systemctl reload apache2

echo "✅ Proxy configurado. Acceso disponible en:"
echo "   http://3.144.134.110/images/"
echo "   http://ec2-3-144-134-110.us-east-2.compute.amazonaws.com/images/"