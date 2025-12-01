#!/bin/bash

case "$1" in
    start)
        echo "🚀 Iniciando servicio..."
        sudo systemctl start mapas-primos
        ;;
    stop)
        echo "🛑 Deteniendo servicio..."
        sudo systemctl stop mapas-primos
        ;;
    restart)
        echo "🔄 Reiniciando servicio..."
        sudo systemctl restart mapas-primos
        ;;
    status)
        echo "📊 Estado del servicio:"
        sudo systemctl status mapas-primos --no-pager
        ;;
    logs)
        echo "📋 Logs del servicio (Ctrl+C para salir):"
        sudo journalctl -u mapas-primos -f
        ;;
    test)
        echo "🧪 Probando conectividad..."
        python3 -c "
import requests
try:
    r = requests.get('http://localhost:3000/', timeout=5)
    print(f'✅ Servicio funcionando: {r.status_code}')
    
    r = requests.get('http://localhost:3000/api/info', timeout=5)
    if r.status_code == 200:
        info = r.json()
        print(f'📊 Version: {info[\"version\"]}')
        print(f'🎯 Servicios: {list(info[\"services\"].keys())}')
except Exception as e:
    print(f'❌ Error: {e}')
"
        ;;
    *)
        echo "🔧 Control del Servicio de Mapas de Números Primos"
        echo "================================================="
        echo ""
        echo "Uso: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Comandos disponibles:"
        echo "  start    - Iniciar servicio"
        echo "  stop     - Detener servicio" 
        echo "  restart  - Reiniciar servicio"
        echo "  status   - Ver estado del servicio"
        echo "  logs     - Ver logs en tiempo real"
        echo "  test     - Probar conectividad"
        echo ""
        echo "URLs del servicio:"
        echo "  📍 http://3.144.134.110:3000/ (selector)"
        echo "  🗺️ http://3.144.134.110:3000/interactive"
        echo "  🎨 http://3.144.134.110:3000/images"
        ;;
esac