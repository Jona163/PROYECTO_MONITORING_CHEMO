import asyncio
import websockets
import mss
from PIL import Image
from io import BytesIO
import base64
import json
import os
import subprocess
import ctypes

connected_clients = set()

# Verificar permisos de administrador en Windows
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Función para capturar la pantalla y convertirla a base64
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=50)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        print("Imagen capturada y convertida a base64")
        return img_str

# Manejo de los mensajes de los clientes
async def handle_message(websocket, message):
    command = json.loads(message)
    action = command.get("action")
    
    if action == "block_input":
        print("Comando recibido: Bloquear entrada")
        subprocess.call("powershell -ExecutionPolicy Bypass -File block_input.ps1", shell=True)
    elif action == "unblock_input":
        print("Comando recibido: Desbloquear entrada")
        subprocess.call("powershell -ExecutionPolicy Bypass -File unblock_input.ps1", shell=True)
    elif action == "shutdown":
        print("Comando recibido: Apagar el PC")
        os.system("shutdown /s /t 1")
    elif action == "block_sites":
        if is_admin():
            sites = command.get("sites", [])
            print(f"Comando recibido: Bloquear sitios {sites}")
            with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as hosts_file:
                for site in sites:
                    hosts_file.write(f"127.0.0.1 {site}\n")
        else:
            print("Error: Se requieren permisos de administrador para bloquear sitios.")
    elif action == "unblock_sites":
        if is_admin():
            print("Comando recibido: Desbloquear sitios")
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r+") as hosts_file:
                lines = hosts_file.readlines()
                hosts_file.seek(0)
                for line in lines:
                    if not any(site in line for site in command.get("sites", [])):
                        hosts_file.write(line)
                hosts_file.truncate()
        else:
            print("Error: Se requieren permisos de administrador para desbloquear sitios.")
    elif action == "allow_ping":
        print("Comando recibido: Permitir ping")
        os.system("netsh advfirewall firewall delete rule name=\"Block Ping\"")
    elif action == "block_ping":
        print("Comando recibido: Bloquear ping")
        os.system("netsh advfirewall firewall add rule name=\"Block Ping\" protocol=icmpv4:any,icmpv6:any dir=in action=block")
    else:
        print("Acción desconocida o no implementada.")

# Transmisión de pantalla y recepción de comandos de los clientes
async def screen_stream(websocket, path):
    connected_clients.add(websocket)
    print(f"Cliente conectado: {websocket.remote_address}")
    try:
        while True:
            # Enviar captura de pantalla a los clientes conectados
            img_str = capture_screen()
            await asyncio.gather(
                *[client.send(json.dumps({"type": "image", "data": img_str})) for client in connected_clients]
            )
            await asyncio.sleep(2)

            # Escuchar comandos del cliente con un tiempo de espera
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2)
                await handle_message(websocket, message)
            except asyncio.TimeoutError:
                continue
    except websockets.ConnectionClosed:
        print(f"Conexión cerrada con el cliente {websocket.remote_address}")
    except Exception as e:
        print(f"Error en la captura o envío de pantalla: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"Cliente desconectado: {websocket.remote_address}")

# Ejecución del servidor
async def main():
    async with websockets.serve(screen_stream, "172.168.0.167", 8765, ping_interval=30, ping_timeout=15):
        print("Servidor iniciado en ws://172.168.0.167:8765")
        await asyncio.Future()

# Iniciar servidor
if is_admin():
    asyncio.run(main())
else:
    print("Este programa requiere permisos de administrador para ciertas funcionalidades.")
