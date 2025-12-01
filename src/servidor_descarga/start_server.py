#!/usr/bin/env python3
"""
Script para iniciar el servidor de mapas con persistencia DNS
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

# Configuración
SERVER_PORT = 3000
SERVER_HOST = "0.0.0.0"
REPO_PATH = Path("/home/admin/servidor_descarga")
LOG_FILE = REPO_PATH / "server.log"
PID_FILE = REPO_PATH / "app.pid"

def get_network_info():
    """Obtener información de red"""
    hostname = socket.gethostname()
    try:
        hostname_fqdn = socket.getfqdn()
    except:
        hostname_fqdn = hostname
    
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    
    return {
        "hostname": hostname,
        "hostname_fqdn": hostname_fqdn,
        "local_ip": local_ip
    }

def start_server():
    """Iniciar el servidor"""
    print("🚀 Iniciando servidor de mapas...")
    
    # Detener procesos existentes
    try:
        subprocess.run(["pkill", "-f", "python.*static_app.py"], stderr=subprocess.DEVNULL)
    except:
        pass
    
    # Verificar puerto
    try:
        subprocess.run(["fuser", "-k", f"{SERVER_PORT}/tcp"], stderr=subprocess.DEVNULL)
    except:
        pass
    
    # Obtener información de red
    net_info = get_network_info()
    print(f"📍 Configuración de red detectada:")
    print(f"   🔸 IP Local: {net_info['local_ip']}")
    print(f"   🔸 Hostname: {net_info['hostname']}")
    
    # Crear directorio de mapas estáticos si no existe
    static_maps_dir = REPO_PATH / "static_maps"
    static_maps_dir.mkdir(exist_ok=True)
    
    # Crear archivo de índice si no existe
    index_file = static_maps_dir / "index.json"
    if not index_file.exists():
        with open(index_file, "w") as f:
            f.write('{"generated": "2025-10-27T00:00:00Z", "version": "3.3.0", "maps": {}, "total_maps": 0}')
    
    # Crear archivo HTML si no existe
    html_file = static_maps_dir / "index.html"
    if not html_file.exists():
        with open(html_file, "w") as f:
            f.write("<html><body><h1>Servidor de Mapas</h1><p>Servidor funcionando correctamente</p></body></html>")
    
    # Iniciar servidor
    cmd = [
        "python3", "-O", 
        str(REPO_PATH / "static_app.py"),
        f"--port={SERVER_PORT}",
        f"--host={SERVER_HOST}"
    ]
    
    with open(LOG_FILE, "w") as log:
        process = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=log,
            cwd=str(REPO_PATH)
        )
    
    # Guardar PID
    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))
    
    print(f"✅ Servidor iniciado con PID: {process.pid}")
    print(f"📝 Logs: {LOG_FILE}")
    print()
    print("🌐 ACCESOS DISPONIBLES:")
    print(f"   📍 IP PÚBLICA:   http://{net_info['local_ip']}:{SERVER_PORT}/")
    print(f"   🌍 DNS/HOSTNAME: http://{net_info['hostname']}:{SERVER_PORT}/")
    print(f"   🔗 LOCALHOST:    http://localhost:{SERVER_PORT}/")
    
    return process.pid

if __name__ == "__main__":
    pid = start_server()
    sys.exit(0)