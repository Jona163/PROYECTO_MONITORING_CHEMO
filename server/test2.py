import asyncio
import websockets
import base64
import os
import json
import subprocess
import pyautogui
from pynput import keyboard, mouse
from threading import Thread

# Ruta para almacenar archivos enviados por el cliente
UPLOAD_FOLDER = "uploads/"

# Asegúrate de que la carpeta de uploads exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Lista de conexiones activas
clients = set()

# Función para tomar una captura de pantalla
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_path = "screenshot.jpg"
    screenshot.save(screenshot_path)
    return screenshot_path

# Función para enviar la pantalla (en formato de imagen base64)
async def send_image(websocket):
    try:
        # Enviar imagen de la pantalla cada 1 segundo
        while True:
            screenshot_path = take_screenshot()  # Captura de pantalla
            with open(screenshot_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                image_message = json.dumps({"type": "image", "data": encoded_image})
                await websocket.send(image_message)
            await asyncio.sleep(1)  # Enviar cada 1 segundo
    except Exception as e:
        print(f"Error al enviar la imagen: {e}")

# Funciones para manejar las acciones del esclavo
def block_input():
    def on_press(key):
        return False  # Bloquea el teclado

    def on_move(x, y):
        return False  # Bloquea el ratón

    with keyboard.Listener(on_press=on_press) as listener:
        listener.start()  # Ejecutar en un hilo para no bloquear

    with mouse.Listener(on_move=on_move) as listener:
        listener.start()  # Ejecutar en un hilo para no bloquear

    print("Teclado y ratón bloqueados...")

def unblock_input():
    print("Teclado y ratón desbloqueados...")

def shutdown_pc():
    print("Apagando PC...")
    subprocess.run(["shutdown", "/s", "/f"])

# Función para manejar los mensajes de los clientes
async def handle_client(websocket, path):
    # Añadir cliente a la lista de clientes conectados
    clients.add(websocket)
    print(f"Nuevo cliente conectado: {websocket.remote_address}")

    try:
        # Enviar la imagen de la pantalla al cliente
        await send_image(websocket)

        # Recibir mensajes y archivos desde el cliente
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            data = json.loads(message)

            # Manejar comandos recibidos
            if data["type"] == "command":
                if data["command"] == "block_input":
                    block_input()
                    await websocket.send(json.dumps({"type": "response", "data": "Teclado y ratón bloqueados"}))
                elif data["command"] == "unblock_input":
                    unblock_input()
                    await websocket.send(json.dumps({"type": "response", "data": "Teclado y ratón desbloqueados"}))
                elif data["command"] == "shutdown":
                    shutdown_pc()
                    await websocket.send(json.dumps({"type": "response", "data": "PC apagada"}))

            elif data["type"] == "message":
                # Enviar el mensaje recibido a todos los clientes
                for client in clients:
                    if client != websocket:  # Evitar enviar el mensaje al mismo cliente
                        await client.send(json.dumps({"type": "message", "data": data["data"]}))

            elif data["type"] == "file":
                # Decodificar y guardar el archivo recibido
                file_data = base64.b64decode(data["fileData"])
                file_path = os.path.join(UPLOAD_FOLDER, data["fileName"])

                with open(file_path, "wb") as file:
                    file.write(file_data)

                # Notificar a todos los clientes que se ha recibido un archivo
                for client in clients:
                    if client != websocket:
                        await client.send(json.dumps({
                            "type": "file",
                            "fileName": data["fileName"],
                            "fileData": base64.b64encode(file_data).decode("utf-8")
                        }))
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Cliente desconectado: {websocket.remote_address} - {e}")
    finally:
        # Eliminar cliente de la lista cuando se desconecta
        clients.remove(websocket)

# Función principal para ejecutar el servidor WebSocket
async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("Servidor WebSocket iniciado en ws://0.0.0.0:8765")

    # Mantener el servidor activo
    try:
        while True:
            await asyncio.sleep(3600)  # Mantener el servidor activo durante 1 hora a la vez
    except KeyboardInterrupt:
        print("Servidor detenido manualmente")
        server.close()
        await server.wait_closed()

# Ejecutar el servidor WebSocket
if __name__ == "__main__":
    asyncio.run(main())
