#!/bin/bash
# Script para monitorear el progreso del generador en tiempo real

echo "📊 Monitor de Progreso del Generador PM2"
echo "========================================="
echo "Presiona Ctrl+C para salir"
echo ""

while true; do
    clear
    echo "📊 Monitor de Progreso del Generador PM2"
    echo "========================================="
    echo ""
    
    # Estado de PM2
    echo "🔧 Estado del Proceso:"
    pm2 list | grep prime-map-generator || echo "  ⚠️  Generador no está corriendo"
    
    echo ""
    echo "📈 Progreso Actual:"
    if [ -f "src/data/generation_progress.json" ]; then
        python3 -c "
import json
try:
    with open('src/data/generation_progress.json', 'r') as f:
        data = json.load(f)
    print(f\"  ✅ Progreso: {data.get('progress_percent', 0):.1f}%\")
    print(f\"  📦 Mapas generados: {data.get('maps_generated', 0)}\")
    print(f\"  ⏭️  Mapas omitidos: {data.get('maps_skipped', 0)}\")
    print(f\"  🕐 Última actualización: {data.get('last_updated', 'N/A')}\")
except:
    print('  ⚠️  No hay datos de progreso')
"
    else
        echo "  ⚠️  Archivo de progreso no encontrado"
    fi
    
    echo ""
    echo "📊 Estadísticas:"
    if [ -f "src/data/generator_stats.json" ]; then
        python3 -c "
import json
try:
    with open('src/data/generator_stats.json', 'r') as f:
        data = json.load(f)
    print(f\"  🎯 Tarea actual: {data.get('current_config', {}).get('num_circulos', 'N/A')}c × {data.get('current_config', {}).get('divisiones_por_circulo', 'N/A')}s\")
    print(f\"  💾 Tamaño total: {data.get('total_size_mb', 0):.2f} MB\")
    print(f\"  ❌ Errores: {data.get('errors', 0)}\")
except:
    print('  ⚠️  No hay estadísticas')
"
    else
        echo "  ⚠️  Archivo de estadísticas no encontrado"
    fi
    
    echo ""
    echo "💾 Almacenamiento:"
    if [ -d "src/data/pregenerated_maps" ]; then
        TOTAL_FILES=$(ls -1 src/data/pregenerated_maps/*.json.gz 2>/dev/null | wc -l)
        TOTAL_SIZE=$(du -sh src/data/pregenerated_maps 2>/dev/null | cut -f1)
        echo "  📁 Archivos: $TOTAL_FILES"
        echo "  💿 Espacio: $TOTAL_SIZE"
    else
        echo "  ⚠️  Directorio no existe"
    fi
    
    echo ""
    echo "🔄 Actualizando en 5 segundos... (Ctrl+C para salir)"
    sleep 5
done
