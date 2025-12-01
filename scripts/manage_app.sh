#!/bin/bash

# Script para gestionar la aplicación de visualización de primos
# Proporciona comandos simples para iniciar, detener, reiniciar y verificar el estado

# Colores para la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar el uso
show_usage() {
  echo -e "${BLUE}Gestión de la Aplicación de Visualización de Primos${NC}"
  echo ""
  echo "Uso: $0 [comando]"
  echo ""
  echo "Comandos disponibles:"
  echo "  start      - Inicia la aplicación"
  echo "  stop       - Detiene la aplicación"
  echo "  restart    - Reinicia la aplicación"
  echo "  status     - Muestra el estado actual de la aplicación"
  echo "  logs       - Muestra los logs de la aplicación (últimas 50 líneas)"
  echo "  logs-live  - Muestra los logs en tiempo real (Ctrl+C para salir)"
  echo "  deploy     - Ejecuta el script de despliegue persistente (requiere sudo)"
  echo "  help       - Muestra esta ayuda"
  echo ""
  echo -e "${YELLOW}Nota:${NC} Los comandos start, stop, restart y status requieren privilegios de administrador (sudo)"
}

# Verificar si se proporcionó un comando
if [ $# -eq 0 ]; then
  show_usage
  exit 1
fi

# Procesar el comando
case "$1" in
  start)
    echo -e "${GREEN}Iniciando la aplicación...${NC}"
    sudo systemctl start prime-visualization.service
    echo "Para verificar el estado, ejecute: $0 status"
    ;;
  stop)
    echo -e "${RED}Deteniendo la aplicación...${NC}"
    sudo systemctl stop prime-visualization.service
    ;;
  restart)
    echo -e "${YELLOW}Reiniciando la aplicación...${NC}"
    sudo systemctl restart prime-visualization.service
    echo "Para verificar el estado, ejecute: $0 status"
    ;;
  status)
    echo -e "${BLUE}Estado de la aplicación:${NC}"
    sudo systemctl status prime-visualization.service
    ;;
  logs)
    echo -e "${BLUE}Últimas 50 líneas de logs:${NC}"
    tail -n 50 /home/admin/enhanced_app.log
    ;;
  logs-live)
    echo -e "${BLUE}Mostrando logs en tiempo real (Ctrl+C para salir):${NC}"
    tail -f /home/admin/enhanced_app.log
    ;;
  deploy)
    echo -e "${GREEN}Ejecutando script de despliegue persistente...${NC}"
    sudo bash /home/admin/deploy_persistent.sh
    ;;
  help)
    show_usage
    ;;
  *)
    echo -e "${RED}Comando desconocido: $1${NC}"
    show_usage
    exit 1
    ;;
esac