import asyncio
import websockets
import mss
from PIL import Image
from io import BytesIO
import base64
import json
import os

# Lista de conexiones activas
clients = set()

# Función para capturar la pantalla
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Usa el primer monitor, puedes cambiarlo si tienes más
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=50)  # Puedes ajustar la calidad aquí
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')  # Convertir a base64
        return img_str

# Función para manejar los mensajes del cliente
async def handle_client(websocket, path):
    clients.add(websocket)
    print("Nuevo cliente conectado")
    try:
        while True:
            # Capturar la pantalla y enviarla al cliente conectado
            img_str = capture_screen()
            message = json.dumps({"type": "image", "data": img_str})
            await websocket.send(message)
            await asyncio.sleep(1)  # Esperar un segundo antes de capturar otra imagen
    except websockets.ConnectionClosed:
        print(f"Cliente desconectado: {websocket.remote_address}")
    finally:
        clients.remove(websocket)

# Función principal para ejecutar el servidor WebSocket
async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("Servidor WebSocket iniciado en ws://0.0.0.0:8765")
        await asyncio.Future()  # Mantener el servidor activo

asyncio.run(main())
