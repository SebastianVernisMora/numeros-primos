#!/bin/bash
# 🎯 INSTALACIÓN Y CONFIGURACIÓN DEL SISTEMA PM2
# Para generación de mapas hasta 10,000 × 1,300

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🎯 INSTALACIÓN DEL SISTEMA DE GENERACIÓN DE MAPAS      ║"
echo "║   Capacidad: 10,000 círculos × 1,300 segmentos           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Función para imprimir con color
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "background_map_generator.py" ]; then
    print_error "Este script debe ejecutarse desde el directorio servidor_descarga"
    exit 1
fi

print_info "Directorio actual: $(pwd)"
echo ""

# 1. Verificar Node.js y npm
print_info "Verificando Node.js y npm..."
if ! command -v node &> /dev/null; then
    print_warning "Node.js no está instalado"
    print_info "Instalando Node.js..."

    # Detectar sistema operativo
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS/Amazon Linux
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo yum install -y nodejs
    else
        print_error "Sistema operativo no soportado automáticamente"
        print_info "Por favor instala Node.js manualmente desde https://nodejs.org/"
        exit 1
    fi
else
    print_status "Node.js ya está instalado: $(node --version)"
fi

if ! command -v npm &> /dev/null; then
    print_error "npm no está instalado"
    exit 1
else
    print_status "npm está instalado: $(npm --version)"
fi
echo ""

# 2. Instalar PM2
print_info "Verificando PM2..."
if ! command -v pm2 &> /dev/null; then
    print_warning "PM2 no está instalado"
    print_info "Instalando PM2..."
    sudo npm install -g pm2
    print_status "PM2 instalado exitosamente"
else
    print_status "PM2 ya está instalado: $(pm2 --version)"
fi
echo ""

# 3. Verificar Python3
print_info "Verificando Python 3..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    print_info "Instalando Python 3..."

    if [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y python3 python3-pip
    fi
else
    print_status "Python 3 está instalado: $(python3 --version)"
fi
echo ""

# 4. Instalar dependencias de Python
print_info "Instalando dependencias de Python..."
pip3 install --user flask flask-cors || pip install flask flask-cors
print_status "Dependencias de Python instaladas"
echo ""

# 5. Crear directorios necesarios
print_info "Creando directorios..."
mkdir -p logs
mkdir -p static_maps
mkdir -p cache_primes
print_status "Directorios creados"
echo ""

# 6. Dar permisos de ejecución
print_info "Configurando permisos de ejecución..."
chmod +x pm2_manager.sh
chmod +x background_map_generator.py
chmod +x static_maps_server.py
print_status "Permisos configurados"
echo ""

# 7. Verificar/crear archivo ecosystem.config.js
print_info "Verificando configuración de PM2..."
if [ ! -f "ecosystem.config.js" ]; then
    print_warning "ecosystem.config.js no encontrado"
    print_info "El archivo debería existir. Verifica la instalación."
else
    print_status "ecosystem.config.js encontrado"
fi
echo ""

# 8. Configurar PM2 startup (opcional)
print_info "¿Deseas configurar PM2 para iniciar automáticamente al arrancar el sistema?"
read -p "Esto requiere privilegios de administrador (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_info "Configurando PM2 startup..."
    pm2 startup
    print_warning "Ejecuta el comando que PM2 sugiere arriba (requiere sudo)"
    print_info "Después de iniciar el generador, ejecuta: pm2 save"
fi
echo ""

# 9. Verificar espacio en disco
print_info "Verificando espacio en disco..."
DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')
print_status "Espacio disponible: $DISK_SPACE"
print_warning "Se recomienda tener al menos 100GB libres para la generación completa"
echo ""

# 10. Resumen final
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ INSTALACIÓN COMPLETADA                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
print_status "El sistema está listo para usar"
echo ""
echo -e "${BLUE}🚀 Próximos pasos:${NC}"
echo ""
echo "1. Iniciar el generador de mapas:"
echo -e "   ${GREEN}./pm2_manager.sh start${NC}"
echo ""
echo "2. Ver el progreso:"
echo -e "   ${GREEN}./pm2_manager.sh logs${NC}"
echo ""
echo "3. Verificar estadísticas:"
echo -e "   ${GREEN}./pm2_manager.sh stats${NC}"
echo ""
echo "4. Iniciar el servidor web:"
echo -e "   ${GREEN}python3 static_maps_server.py${NC}"
echo ""
echo -e "${BLUE}📚 Documentación completa:${NC}"
echo -e "   ${GREEN}cat README_PM2_MAPS.md${NC}"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      🎯 Sistema listo para generar hasta 13M elementos    ║"
echo "╚════════════════════════════════════════════════════════════╝"
