import asyncio
import websockets
import base64
import os
import json
import time
import subprocess  # Para comandos del sistema como apagado
import ctypes      # Para el bloqueo/desbloqueo de teclado y ratón en Windows

# Ruta para almacenar archivos enviados por el cliente
UPLOAD_FOLDER = "uploads/"

# Asegúrate de que la carpeta de uploads exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Lista de conexiones activas
clients = set()

# Función para bloquear y desbloquear el teclado y el ratón
def toggle_keyboard_mouse(block=True):
    user32 = ctypes.windll.User32
    if block:
        user32.BlockInput(True)
        print("Teclado y ratón bloqueados.")
    else:
        user32.BlockInput(False)
        print("Teclado y ratón desbloqueados.")

# Función para enviar la pantalla (en formato de imagen base64)
async def send_image(websocket):
    try:
        # Simula una imagen de pantalla en vivo, reemplaza esto por un método real
        while True:
            with open("screenshot.jpg", "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                image_message = json.dumps({"type": "image", "data": encoded_image})
                await websocket.send(image_message)
            await asyncio.sleep(1)  # Enviar imagen cada 1 segundo
    except Exception as e:
        print(f"Error al enviar la imagen: {e}")

# Función para apagar la PC
def shutdown_pc():
    try:
        print("Apagando PC...")
        subprocess.run("shutdown /s /t 1", shell=True, check=True)
    except Exception as e:
        print(f"Error al intentar apagar la PC: {e}")

# Función para manejar los mensajes de los clientes
async def handle_client(websocket, path):
    clients.add(websocket)
    print(f"Nuevo cliente conectado: {websocket.remote_address}")

    try:
        # Envía la pantalla al cliente
        asyncio.create_task(send_image(websocket))

        # Recibir mensajes y comandos desde el cliente maestro
        async for message in websocket:
            data = json.loads(message)

            # Manejar mensajes de chat
            if data["type"] == "message":
                for client in clients:
                    if client != websocket:
                        await client.send(json.dumps({"type": "message", "data": data["data"]}))

            # Manejar archivos
            elif data["type"] == "file":
                file_data = base64.b64decode(data["fileData"])
                file_path = os.path.join(UPLOAD_FOLDER, data["fileName"])

                with open(file_path, "wb") as file:
                    file.write(file_data)

                for client in clients:
                    if client != websocket:
                        await client.send(json.dumps({
                            "type": "file",
                            "fileName": data["fileName"],
                            "fileData": base64.b64encode(file_data).decode("utf-8")
                        }))

            # Comando de apagado
            elif data["action"] == "shutdown":
                shutdown_pc()

            # Bloqueo de teclado y ratón
            elif data["action"] == "block_input":
                toggle_keyboard_mouse(block=True)

            # Desbloqueo de teclado y ratón
            elif data["action"] == "unblock_input":
                toggle_keyboard_mouse(block=False)

            # Bloqueo de sitios
            elif data["action"] == "block_sites":
                restricted_sites = data.get("sites", [])
                print(f"Acceso restringido a: {restricted_sites}")

            # Control de ping
            elif data["action"] == "allow_ping":
                print("Ping permitido.")

            elif data["action"] == "block_ping":
                print("Ping bloqueado.")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Cliente desconectado: {websocket.remote_address} - {e}")
    finally:
        clients.remove(websocket)

# Función principal para ejecutar el servidor WebSocket
async def main():
    server = await websockets.serve(handle_client, "192.168.30.181", 8765)
    print("Servidor WebSocket iniciado en ws://192.168.30.181:8765")

    try:
        while True:
            await asyncio.sleep(3600)  # Mantener el servidor activo
    except KeyboardInterrupt:
        print("Servidor detenido manualmente")
        server.close()
        await server.wait_closed()

# Ejecutar el servidor WebSocket
if __name__ == "__main__":
    asyncio.run(main())
