#server cliente 
import asyncio
import websockets
import base64
import os
import json

# Directorio para almacenar archivos enviados por el cliente
UPLOAD_FOLDER = "uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Lista de conexiones activas
clients = set()

# Función para enviar la pantalla (en formato de imagen base64)
async def send_image(websocket):
    try:
        # Simula una imagen de pantalla en vivo, reemplaza esto por un método real de captura
        while True:
            with open("screenshot.jpg", "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                image_message = json.dumps({"type": "image", "data": encoded_image})
                await websocket.send(image_message)
            await asyncio.sleep(1)  # Intervalo de envío de imágenes
    except Exception as e:
        print(f"Error al enviar la imagen: {e}")

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
            data = json.loads(message)

            if data["type"] == "message":
                # Reenviar el mensaje recibido a todos los clientes conectados
                for client in clients:
                    if client != websocket:  # Evitar enviar el mensaje al mismo cliente que lo envió
                        await client.send(json.dumps({"type": "message", "data": data["data"]}))

            elif data["type"] == "file":
                # Decodificar y guardar el archivo recibido
                file_data = base64.b64decode(data["fileData"])
                file_path = os.path.join(UPLOAD_FOLDER, data["fileName"])

                with open(file_path, "wb") as file:
                    file.write(file_data)

                # Notificar a todos los clientes sobre el archivo recibido
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
        # Remover cliente de la lista cuando se desconecta
        clients.remove(websocket)
        print(f"Cliente desconectado: {websocket.remote_address}")

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
