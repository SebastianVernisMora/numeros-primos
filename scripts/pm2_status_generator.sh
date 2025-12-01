#!/bin/bash
# Script para ver el estado del generador PM2

echo "📊 Estado del Generador de Datos PM2"
echo "======================================"
echo ""

# Estado de PM2
echo "🔧 Proceso PM2:"
pm2 list | grep prime-map-generator || echo "  ⚠️  Generador no está corriendo"

echo ""
echo "📈 Estadísticas del Generador:"
if [ -f "src/data/generator_stats.json" ]; then
    cat src/data/generator_stats.json | python3 -m json.tool
else
    echo "  ⚠️  No hay estadísticas disponibles"
fi

echo ""
echo "📊 Progreso de Generación:"
if [ -f "src/data/generation_progress.json" ]; then
    cat src/data/generation_progress.json | python3 -m json.tool
else
    echo "  ⚠️  No hay datos de progreso"
fi

echo ""
echo "💾 Almacenamiento:"
if [ -d "src/data/pregenerated_maps" ]; then
    TOTAL_FILES=$(ls -1 src/data/pregenerated_maps/*.json.gz 2>/dev/null | wc -l)
    TOTAL_SIZE=$(du -sh src/data/pregenerated_maps 2>/dev/null | cut -f1)
    echo "  📁 Mapas generados: $TOTAL_FILES"
    echo "  💿 Espacio usado: $TOTAL_SIZE"
else
    echo "  ⚠️  Directorio de datos no existe"
fi

echo ""
echo "📋 Comandos útiles:"
echo "  Ver logs: pm2 logs prime-map-generator"
echo "  Reiniciar: pm2 restart prime-map-generator"
echo "  Detener: ./scripts/pm2_stop_generator.sh"
