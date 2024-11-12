#Server maestro 
import asyncio
import websockets
import mss
from PIL import Image
from io import BytesIO
import base64
import json
import os

connected_clients = set()

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

async def handle_message(websocket, message):
    command = json.loads(message)
    action = command.get("action")
    
    if action == "block_input":
        print("Comando recibido: Bloquear entrada")
    elif action == "unblock_input":
        print("Comando recibido: Desbloquear entrada")
    elif action == "shutdown":
        print("Comando recibido: Apagar el PC")
        os.system("shutdown /s /t 1")
    elif action == "block_sites":
        sites = command.get("sites", [])
        print(f"Comando recibido: Bloquear sitios {sites}")
        with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as hosts_file:
            for site in sites:
                hosts_file.write(f"127.0.0.1 {site}\n")
    elif action == "allow_ping":
        print("Comando recibido: Permitir ping")
        os.system("netsh advfirewall firewall delete rule name=\"Block Ping\"")
    elif action == "block_ping":
        print("Comando recibido: Bloquear ping")
        os.system("netsh advfirewall firewall add rule name=\"Block Ping\" protocol=icmpv4:any,icmpv6:any dir=in action=block")
    else:
        print("Acción desconocida o no implementada.")

async def screen_stream(websocket, path):
    connected_clients.add(websocket)
    print("Cliente conectado")
    try:
        while True:
            img_str = capture_screen()
            print("Captura de pantalla realizada, enviando datos...")
            for client in connected_clients:
                await client.send(json.dumps({"type": "image", "data": img_str}))
            await asyncio.sleep(2)  # Envía una captura cada 2 segundos

            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2)
                await handle_message(websocket, message)
            except asyncio.TimeoutError:
                continue
    except websockets.ConnectionClosed:
        print("Conexión cerrada")
    except Exception as e:
        print(f"Error en la captura o envío de pantalla: {e}")
    finally:
        connected_clients.remove(websocket)
        print("Cliente desconectado, intentando reconectar...")
        asyncio.create_task(reconnect_client(websocket))

async def reconnect_client(websocket):
    await asyncio.sleep(5)
    if websocket.closed:
        await screen_stream(websocket, "/")

async def main():
    async with websockets.serve(
        screen_stream, "localhost", 8765,
        ping_interval=30,  # Intervalo de ping más largo
        ping_timeout=15    # Tiempo de espera de ping ajustado
    ):
        print("Servidor iniciado en ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
