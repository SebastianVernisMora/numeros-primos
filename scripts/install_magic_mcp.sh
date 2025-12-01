#!/bin/bash

# Script para instalar Magic MCP con permisos sudo
echo "=== Instalando Magic MCP para Blackbox ==="

# Instalar globalmente el paquete magic
echo "Instalando @21st-dev/magic globalmente..."
sudo npm install -g @21st-dev/magic@latest

# Verificar instalación
echo "Verificando instalación..."
which magic || echo "Magic no encontrado en PATH"

# Remover configuración anterior
echo "Removiendo configuración MCP anterior..."
blackbox mcp remove magic 2>/dev/null || echo "No había configuración previa"

# Agregar Magic MCP con ruta absoluta
echo "Agregando Magic MCP a Blackbox..."
MAGIC_PATH=$(which magic 2>/dev/null)
if [ -n "$MAGIC_PATH" ]; then
    blackbox mcp add magic "$MAGIC_PATH" --scope user --env API_KEY="5a49716c4cd84678e3565ba9148e52502f202a030b89e993accae02c7e2bb86b"
else
    # Intentar con npx y ruta completa
    blackbox mcp add magic "/usr/bin/npx @21st-dev/magic" --scope user --env API_KEY="5a49716c4cd84678e3565ba9148e52502f202a030b89e993accae02c7e2bb86b"
fi

# Verificar configuración
echo "Verificando configuración MCP..."
blackbox mcp list

echo "=== Instalación completada ==="