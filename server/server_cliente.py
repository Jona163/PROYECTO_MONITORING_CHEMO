import asyncio
import websockets
import json
import base64
import subprocess
import ctypes
import os
import time

# Dirección del servidor maestro
SERVER_URI = "ws://172.168.2.87:8765"

# Archivo hosts en sistemas Windows
HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts"

# Función para bloquear y desbloquear teclado y ratón
def toggle_keyboard_mouse(block=True):
    try:
        user32 = ctypes.windll.User32
        user32.BlockInput(block)
        action = "bloqueados" if block else "desbloqueados"
        print(f"Teclado y ratón {action}.")
    except Exception as e:
        print(f"Error al cambiar el estado del teclado y ratón: {e}")

# Función para bloquear un sitio web
def block_website(domain):
    try:
        with open(HOSTS_FILE, "a") as hosts_file:
            hosts_file.write(f"127.0.0.1 {domain}\n")
        print(f"Sitio bloqueado: {domain}")
    except Exception as e:
        print(f"Error al bloquear sitio: {e}")

# Función para desbloquear un sitio web
def unblock_website(domain):
    try:
        with open(HOSTS_FILE, "r") as hosts_file:
            lines = hosts_file.readlines()
        with open(HOSTS_FILE, "w") as hosts_file:
            for line in lines:
                if domain not in line:
                    hosts_file.write(line)
        print(f"Sitio desbloqueado: {domain}")
    except Exception as e:
        print(f"Error al desbloquear sitio: {e}")

# Función para realizar ping a un host
def perform_ping(host):
    try:
        print(f"Realizando ping a {host}...")
        start_time = time.time()
        response = subprocess.run(
            ["ping", "-n", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if response.returncode == 0:
            duration = time.time() - start_time
            print(f"Ping exitoso a {host} en {duration:.2f} segundos.")
        else:
            print(f"Ping fallido a {host}.")
    except Exception as e:
        print(f"Error al realizar ping: {e}")

# Función para manejar mensajes del servidor maestro
async def handle_server_commands(websocket):
    try:
        async for message in websocket:
            try:
                data = json.loads(message)

                # Procesar comandos del servidor maestro
                if data["type"] == "command":
                    action = data["action"]
                    print(f"Recibido comando: {action}")

                    # Apagar la PC
                    if action == "shutdown":
                        print("Ejecutando apagado...")
                        subprocess.run("shutdown /s /t 1", shell=True, check=True)

                    # Bloquear teclado y ratón
                    elif action == "block_input":
                        toggle_keyboard_mouse(block=True)

                    # Desbloquear teclado y ratón
                    elif action == "unblock_input":
                        toggle_keyboard_mouse(block=False)

                    # Bloquear sitio web
                    elif action == "block_website":
                        domain = data["domain"]
                        block_website(domain)

                    # Desbloquear sitio web
                    elif action == "unblock_website":
                        domain = data["domain"]
                        unblock_website(domain)

                    # Realizar ping
                    elif action == "ping":
                        host = data["host"]
                        perform_ping(host)

                    # Ejecutar un archivo recibido
                    elif action == "execute_file":
                        file_name = data["fileName"]
                        file_data = base64.b64decode(data["fileData"])
                        file_path = f"./{file_name}"

                        # Guardar el archivo en el sistema local
                        with open(file_path, "wb") as file:
                            file.write(file_data)
                        print(f"Archivo recibido y guardado: {file_path}")

                        # Ejecutar el archivo (asegúrate de que sea seguro)
                        subprocess.run(file_path, shell=True)

                    # Comando desconocido
                    else:
                        print(f"Comando no reconocido: {action}")

                else:
                    print(f"Tipo de mensaje no reconocido: {data}")

            except Exception as e:
                print(f"Error al procesar mensaje: {e}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Conexión cerrada: {e}")
        print("Intentando reconectar...")

# Función principal del cliente
async def main():
    while True:  # Intentar reconectar si la conexión se pierde
        try:
            print(f"Conectando al servidor maestro en {SERVER_URI}...")
            async with websockets.connect(SERVER_URI) as websocket:
                print("Conexión establecida.")

                # Mantener la conexión abierta y escuchar mensajes
                await handle_server_commands(websocket)

        except Exception as e:
            print(f"Error en el cliente: {e}")
            print("Reintentando en 5 segundos...")
            await asyncio.sleep(5)  # Espera antes de intentar nuevamente

# Ejecutar el cliente
if __name__ == "__main__":
    asyncio.run(main())
