#!/bin/bash
# 🔍 VERIFICADOR DEL SISTEMA DE MAPAS PRIMOS
# Verifica que todos los componentes estén instalados y configurados correctamente

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🔍 VERIFICADOR DEL SISTEMA DE MAPAS PRIMOS           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0
WARNINGS=0

# Función para check
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

check_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Verificar archivos principales
echo "📁 Verificando archivos del sistema..."
echo ""

FILES=(
    "background_map_generator.py"
    "ecosystem.config.js"
    "pm2_manager.sh"
    "static_maps_server.py"
    "index_pregenerated.html"
    "setup_pm2_system.sh"
    "README_PM2_MAPS.md"
    "QUICK_START.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "Archivo encontrado: $file"
    else
        check_fail "Archivo NO encontrado: $file"
    fi
done

echo ""

# 2. Verificar permisos de ejecución
echo "🔒 Verificando permisos de ejecución..."
echo ""

EXEC_FILES=(
    "pm2_manager.sh"
    "background_map_generator.py"
    "static_maps_server.py"
    "setup_pm2_system.sh"
)

for file in "${EXEC_FILES[@]}"; do
    if [ -x "$file" ]; then
        check_pass "Ejecutable: $file"
    else
        check_warn "No ejecutable: $file (ejecuta: chmod +x $file)"
    fi
done

echo ""

# 3. Verificar Node.js y npm
echo "📦 Verificando dependencias de Node.js..."
echo ""

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js instalado: $NODE_VERSION"
else
    check_fail "Node.js NO instalado"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    check_pass "npm instalado: $NPM_VERSION"
else
    check_fail "npm NO instalado"
fi

echo ""

# 4. Verificar PM2
echo "🎯 Verificando PM2..."
echo ""

if command -v pm2 &> /dev/null; then
    PM2_VERSION=$(pm2 --version)
    check_pass "PM2 instalado: $PM2_VERSION"
else
    check_fail "PM2 NO instalado (ejecuta: npm install -g pm2)"
fi

echo ""

# 5. Verificar Python
echo "🐍 Verificando Python..."
echo ""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "Python 3 instalado: $PYTHON_VERSION"
else
    check_fail "Python 3 NO instalado"
fi

if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | awk '{print $2}')
    check_pass "pip3 instalado: $PIP_VERSION"
else
    check_fail "pip3 NO instalado"
fi

echo ""

# 6. Verificar módulos de Python
echo "📚 Verificando módulos de Python..."
echo ""

python3 -c "import flask" 2>/dev/null
if [ $? -eq 0 ]; then
    check_pass "Flask instalado"
else
    check_fail "Flask NO instalado (ejecuta: pip3 install flask)"
fi

python3 -c "import flask_cors" 2>/dev/null
if [ $? -eq 0 ]; then
    check_pass "Flask-CORS instalado"
else
    check_warn "Flask-CORS NO instalado (ejecuta: pip3 install flask-cors)"
fi

echo ""

# 7. Verificar directorios
echo "📂 Verificando directorios..."
echo ""

DIRS=(
    "static_maps"
    "logs"
    "cache_primes"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directorio existe: $dir"
    else
        check_warn "Directorio NO existe: $dir (se creará automáticamente)"
        mkdir -p "$dir" 2>/dev/null && check_info "Directorio creado: $dir"
    fi
done

echo ""

# 8. Verificar proceso PM2 (si está corriendo)
echo "🔄 Verificando procesos PM2..."
echo ""

if command -v pm2 &> /dev/null; then
    if pm2 describe map-generator &> /dev/null; then
        PM2_STATUS=$(pm2 describe map-generator | grep "status" | head -1 | awk '{print $4}')
        check_pass "Proceso PM2 'map-generator': $PM2_STATUS"
    else
        check_info "Proceso PM2 'map-generator' no está corriendo (normal si no se ha iniciado)"
    fi
else
    check_info "PM2 no instalado, saltando verificación de procesos"
fi

echo ""

# 9. Verificar archivos generados
echo "🗺️ Verificando mapas generados..."
echo ""

if [ -d "static_maps" ]; then
    MAP_COUNT=$(find static_maps -name "data_*.json" 2>/dev/null | wc -l)
    if [ $MAP_COUNT -gt 0 ]; then
        check_pass "$MAP_COUNT mapas generados"
        TOTAL_SIZE=$(du -sh static_maps 2>/dev/null | cut -f1)
        check_info "Tamaño total: $TOTAL_SIZE"
    else
        check_info "No hay mapas generados aún (normal si no se ha iniciado la generación)"
    fi
else
    check_warn "Directorio static_maps no existe"
fi

echo ""

# 10. Verificar espacio en disco
echo "💾 Verificando espacio en disco..."
echo ""

DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')
DISK_PERCENT=$(df -h . | awk 'NR==2 {print $5}' | tr -d '%')

check_info "Espacio disponible: $DISK_SPACE (usado: ${DISK_PERCENT}%)"

if [ "$DISK_PERCENT" -gt 90 ]; then
    check_warn "Espacio en disco bajo (más del 90% usado)"
elif [ "$DISK_PERCENT" -gt 80 ]; then
    check_info "Espacio en disco: Advertencia (más del 80% usado)"
else
    check_pass "Espacio en disco: OK"
fi

echo ""

# 11. Verificar puerto 3000
echo "🌐 Verificando puerto 3000..."
echo ""

if command -v netstat &> /dev/null; then
    if netstat -tuln 2>/dev/null | grep -q ":3000 "; then
        check_info "Puerto 3000 en uso (servidor probablemente corriendo)"
    else
        check_info "Puerto 3000 libre (normal si servidor no está corriendo)"
    fi
else
    check_info "netstat no disponible, saltando verificación de puerto"
fi

echo ""

# RESUMEN
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                      RESUMEN                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ SISTEMA COMPLETAMENTE VERIFICADO${NC}"
    echo -e "${GREEN}✅ Todos los componentes están listos${NC}"
    echo ""
    echo "🚀 Próximos pasos:"
    echo "   1. ./pm2_manager.sh start    # Iniciar generador"
    echo "   2. python3 static_maps_server.py  # Iniciar servidor"
    echo "   3. Abrir http://localhost:3000 en el navegador"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  SISTEMA VERIFICADO CON ADVERTENCIAS${NC}"
    echo -e "${YELLOW}   Advertencias: $WARNINGS${NC}"
    echo ""
    echo "El sistema puede funcionar, pero revisa las advertencias arriba."
else
    echo -e "${RED}❌ SISTEMA CON ERRORES${NC}"
    echo -e "${RED}   Errores: $ERRORS${NC}"
    echo -e "${YELLOW}   Advertencias: $WARNINGS${NC}"
    echo ""
    echo "Por favor, corrige los errores antes de continuar."
    echo "Ejecuta: ./setup_pm2_system.sh para instalar dependencias faltantes"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   📚 Documentación: cat README_PM2_MAPS.md                ║"
echo "║   🚀 Inicio rápido: cat QUICK_START.md                    ║"
echo "╚════════════════════════════════════════════════════════════╝"

exit $ERRORS
