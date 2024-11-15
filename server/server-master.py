import asyncio
import websockets
import mss
from PIL import Image
from io import BytesIO
import base64
import json
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
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=50)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            print("Imagen capturada y convertida a base64")
            return img_str
    except Exception as e:
        print(f"Error al capturar la pantalla: {e}")
        return None

# Manejo de los mensajes de los clientes
async def handle_message(websocket, message):
    try:
        command = json.loads(message)
        action = command.get("action")
        
        if action == "block_input":
            print("Enviando comando de bloqueo de entrada al cliente")
            await websocket.send(json.dumps({"action": "block_input"}))
        elif action == "unblock_input":
            print("Enviando comando de desbloqueo de entrada al cliente")
            await websocket.send(json.dumps({"action": "unblock_input"}))
        elif action == "shutdown":
            print("Enviando comando para apagar el PC del cliente")
            await websocket.send(json.dumps({"action": "shutdown"}))
        elif action == "block_sites":
            sites = command.get("sites", [])
            print(f"Enviando comando de bloqueo de sitios al cliente: {sites}")
            await websocket.send(json.dumps({"action": "block_sites", "sites": sites}))
        elif action == "unblock_sites":
            sites = command.get("sites", [])
            print("Enviando comando de desbloqueo de sitios al cliente")
            await websocket.send(json.dumps({"action": "unblock_sites", "sites": sites}))
        elif action == "allow_ping":
            print("Enviando comando para permitir ping al cliente")
            await websocket.send(json.dumps({"action": "allow_ping"}))
        elif action == "block_ping":
            print("Enviando comando para bloquear ping al cliente")
            await websocket.send(json.dumps({"action": "block_ping"}))
        else:
            print("Acción desconocida o no implementada.")
    except Exception as e:
        print(f"Error manejando el mensaje del cliente: {e}")

# Transmisión de pantalla y recepción de comandos de los clientes
async def screen_stream(websocket, path):
    connected_clients.add(websocket)
    print(f"Cliente conectado: {websocket.remote_address}")
    try:
        while True:
            # Enviar captura de pantalla a los clientes conectados
            img_str = capture_screen()
            if img_str:
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
                break
    except websockets.ConnectionClosed:
        print(f"Conexión cerrada con el cliente {websocket.remote_address}")
    except Exception as e:
        print(f"Error en la captura o envío de pantalla: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"Cliente desconectado: {websocket.remote_address}")

# Ejecución del servidor
async def main():
    async with websockets.serve(screen_stream, "0.0.0.0", 8765, ping_interval=30, ping_timeout=30):
        print("Servidor iniciado en ws://192.168.30.85:8765")
        await asyncio.Future()

# Iniciar servidor
if __name__ == "__main__":
    if is_admin():
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nServidor detenido manualmente.")
    else:
        print("Este programa requiere permisos de administrador para ciertas funcionalidades.")
