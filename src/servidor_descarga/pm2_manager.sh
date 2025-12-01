#!/bin/bash
# 🎯 GESTOR UNIFICADO DE PM2 PARA GENERADOR DE MAPAS
# Soporta generación de hasta 10,000 círculos x 1,300 segmentos

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
APP_NAME="map-generator"
ECOSYSTEM_FILE="ecosystem.config.js"
STATS_FILE="background_generator_stats.json"
LOGS_DIR="logs"

# Banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     🎯 GESTOR PM2 - GENERADOR DE MAPAS PRIMOS            ║"
    echo "║     Capacidad: 10,000 círculos × 1,300 segmentos         ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar si PM2 está instalado
check_pm2() {
    if ! command -v pm2 &> /dev/null; then
        echo -e "${RED}❌ PM2 no está instalado${NC}"
        echo -e "${YELLOW}📦 Instalando PM2...${NC}"
        npm install -g pm2
        echo -e "${GREEN}✅ PM2 instalado exitosamente${NC}"
    fi
}

# Crear directorios necesarios
setup_directories() {
    mkdir -p "$LOGS_DIR"
    mkdir -p static_maps
    mkdir -p cache_primes
}

# Iniciar el proceso
start_process() {
    print_banner
    check_pm2
    setup_directories

    echo -e "${BLUE}🚀 Iniciando generador de mapas...${NC}"

    if pm2 describe "$APP_NAME" &> /dev/null; then
        echo -e "${YELLOW}⚠️  El proceso ya está corriendo${NC}"
        echo -e "${CYAN}📊 Estado actual:${NC}"
        pm2 describe "$APP_NAME"
        echo ""
        read -p "¿Deseas reiniciar el proceso? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            pm2 restart "$APP_NAME"
            echo -e "${GREEN}✅ Proceso reiniciado${NC}"
        fi
    else
        pm2 start "$ECOSYSTEM_FILE"
        pm2 save
        echo -e "${GREEN}✅ Generador iniciado exitosamente${NC}"
    fi

    show_status
}

# Detener el proceso
stop_process() {
    print_banner
    echo -e "${YELLOW}🛑 Deteniendo generador de mapas...${NC}"

    if pm2 describe "$APP_NAME" &> /dev/null; then
        pm2 stop "$APP_NAME"
        echo -e "${GREEN}✅ Proceso detenido${NC}"
    else
        echo -e "${YELLOW}⚠️  El proceso no está corriendo${NC}"
    fi
}

# Eliminar el proceso
delete_process() {
    print_banner
    echo -e "${RED}🗑️  Eliminando proceso de PM2...${NC}"

    if pm2 describe "$APP_NAME" &> /dev/null; then
        pm2 delete "$APP_NAME"
        pm2 save
        echo -e "${GREEN}✅ Proceso eliminado de PM2${NC}"
    else
        echo -e "${YELLOW}⚠️  El proceso no existe en PM2${NC}"
    fi
}

# Reiniciar el proceso
restart_process() {
    print_banner
    echo -e "${CYAN}🔄 Reiniciando generador de mapas...${NC}"

    if pm2 describe "$APP_NAME" &> /dev/null; then
        pm2 restart "$APP_NAME"
        echo -e "${GREEN}✅ Proceso reiniciado${NC}"
        show_status
    else
        echo -e "${YELLOW}⚠️  El proceso no está corriendo. Iniciando...${NC}"
        start_process
    fi
}

# Ver estado del proceso
show_status() {
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}📊 ESTADO DEL GENERADOR${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}"

    if pm2 describe "$APP_NAME" &> /dev/null; then
        pm2 describe "$APP_NAME"
        echo ""

        # Mostrar estadísticas del archivo JSON si existe
        if [ -f "$STATS_FILE" ]; then
            echo -e "${CYAN}📈 Estadísticas de generación:${NC}"
            if command -v jq &> /dev/null; then
                cat "$STATS_FILE" | jq '.'
            else
                cat "$STATS_FILE"
            fi
        fi

        # Contar mapas generados
        TOTAL_MAPS=$(find static_maps -name "data_*.json" 2>/dev/null | wc -l)
        echo ""
        echo -e "${GREEN}📁 Mapas generados: ${TOTAL_MAPS}${NC}"
    else
        echo -e "${YELLOW}⚠️  El proceso no está corriendo${NC}"
    fi

    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}"
}

# Ver logs en tiempo real
show_logs() {
    print_banner
    echo -e "${CYAN}📋 Logs del generador (Ctrl+C para salir)${NC}"
    echo ""
    pm2 logs "$APP_NAME" --lines 50
}

# Ver métricas y monitoreo
show_monitor() {
    print_banner
    echo -e "${CYAN}📊 Monitor en tiempo real${NC}"
    pm2 monit
}

# Ver estadísticas detalladas
show_stats() {
    print_banner
    echo -e "${CYAN}📊 ESTADÍSTICAS DETALLADAS${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}"

    # Estadísticas de PM2
    if pm2 describe "$APP_NAME" &> /dev/null; then
        pm2 show "$APP_NAME"
    fi

    echo ""
    echo -e "${CYAN}📁 Análisis de archivos generados:${NC}"

    # Contar archivos por rango
    TOTAL_FILES=$(find static_maps -name "data_*.json" 2>/dev/null | wc -l)
    TOTAL_SIZE=$(du -sh static_maps 2>/dev/null | cut -f1)

    echo -e "${GREEN}  Total de mapas: ${TOTAL_FILES}${NC}"
    echo -e "${GREEN}  Tamaño total: ${TOTAL_SIZE}${NC}"

    # Estadísticas del generador
    if [ -f "$STATS_FILE" ]; then
        echo ""
        echo -e "${CYAN}📈 Estado del generador:${NC}"
        cat "$STATS_FILE"
    fi

    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}"
}

# Limpiar logs antiguos
clean_logs() {
    print_banner
    echo -e "${YELLOW}🧹 Limpiando logs antiguos...${NC}"

    pm2 flush "$APP_NAME" 2>/dev/null || true

    # Limpiar logs antiguos (más de 7 días)
    find "$LOGS_DIR" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

    echo -e "${GREEN}✅ Logs limpiados${NC}"
}

# Mostrar ayuda
show_help() {
    print_banner
    echo -e "${CYAN}Uso: $0 [comando]${NC}"
    echo ""
    echo -e "${YELLOW}Comandos disponibles:${NC}"
    echo ""
    echo -e "  ${GREEN}start${NC}      - Iniciar el generador de mapas"
    echo -e "  ${GREEN}stop${NC}       - Detener el generador"
    echo -e "  ${GREEN}restart${NC}    - Reiniciar el generador"
    echo -e "  ${GREEN}delete${NC}     - Eliminar el proceso de PM2"
    echo -e "  ${GREEN}status${NC}     - Ver estado actual"
    echo -e "  ${GREEN}logs${NC}       - Ver logs en tiempo real"
    echo -e "  ${GREEN}monitor${NC}    - Monitor interactivo de PM2"
    echo -e "  ${GREEN}stats${NC}      - Ver estadísticas detalladas"
    echo -e "  ${GREEN}clean${NC}      - Limpiar logs antiguos"
    echo -e "  ${GREEN}help${NC}       - Mostrar esta ayuda"
    echo ""
    echo -e "${CYAN}Ejemplos:${NC}"
    echo -e "  $0 start       # Iniciar generador"
    echo -e "  $0 logs        # Ver logs en vivo"
    echo -e "  $0 stats       # Ver estadísticas"
    echo ""
}

# Main
case "${1:-help}" in
    start)
        start_process
        ;;
    stop)
        stop_process
        ;;
    restart)
        restart_process
        ;;
    delete)
        delete_process
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    monitor)
        show_monitor
        ;;
    stats)
        show_stats
        ;;
    clean)
        clean_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconocido: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
