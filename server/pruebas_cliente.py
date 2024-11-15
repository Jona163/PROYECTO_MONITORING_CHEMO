import asyncio
import websockets
import json
import ctypes
import os

# Funciones específicas para cada acción
def block_input(block):
    ctypes.windll.user32.BlockInput(block)

def shutdown_pc():
    os.system("shutdown /s /t 0")

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT = "127.0.0.1"

def block_sites(sites):
    with open(HOSTS_PATH, "a") as file:
        for site in sites:
            file.write(f"{REDIRECT} {site}\n")

def unblock_sites(sites):
    with open(HOSTS_PATH, "r") as file:
        lines = file.readlines()
    with open(HOSTS_PATH, "w") as file:
        for line in lines:
            if not any(site in line for site in sites):
                file.write(line)

def block_ping():
    os.system("netsh advfirewall firewall add rule name='Block Ping' protocol=icmpv4:8,any dir=in action=block")

def allow_ping():
    os.system("netsh advfirewall firewall delete rule name='Block Ping'")

# Escucha y ejecución de comandos
async def listen_server():
    async with websockets.connect("ws://192.168.30.85:8765") as websocket:
        while True:
            try:
                message = await websocket.recv()
                print(f"Comando recibido: {message}")
                command = json.loads(message)
                action = command.get("action")
                
                if action == "block_input":
                    block_input(True)
                elif action == "unblock_input":
                    block_input(False)
                elif action == "shutdown":
                    shutdown_pc()
                elif action == "block_sites":
                    sites = command.get("sites", [])
                    block_sites(sites)
                elif action == "unblock_sites":
                    sites = command.get("sites", [])
                    unblock_sites(sites)
                elif action == "block_ping":
                    block_ping()
                elif action == "allow_ping":
                    allow_ping()
                else:
                    print(f"Acción no reconocida: {action}")
            except Exception as e:
                print(f"Error al procesar comando: {e}")

# Iniciar cliente
if __name__ == "__main__":
    try:
        asyncio.run(listen_server())
    except KeyboardInterrupt:
        print("Cliente detenido manualmente.")
