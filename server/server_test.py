import asyncio
import websockets
import json
import os
import platform
import ctypes
import subprocess

async def handler(websocket, path):
    async for message in websocket:
        data = json.loads(message)

        if data['action'] == 'control_pc':
            await websocket.send(json.dumps({"response": "Control de PC activado"}))

        elif data['action'] == 'block_input':
            # Comando para bloquear teclado y mouse (requiere permisos de administrador)
            ctypes.windll.user32.BlockInput(True)
            await websocket.send(json.dumps({"response": "Teclado y ratón bloqueados"}))

        elif data['action'] == 'unblock_input':
            ctypes.windll.user32.BlockInput(False)
            await websocket.send(json.dumps({"response": "Teclado y ratón desbloqueados"}))

        elif data['action'] == 'shutdown':
            # Comando para apagar la PC
            if platform.system() == "Windows":
                os.system("shutdown /s /t 1")
            elif platform.system() == "Linux":
                os.system("poweroff")
            await websocket.send(json.dumps({"response": "PC remota apagada"}))

        elif data['action'] == 'block_sites':
            # Bloqueo de acceso a sitios web
            hosts_path = "/etc/hosts" if platform.system() == "Linux" else r"C:\Windows\System32\drivers\etc\hosts"
            with open(hosts_path, "a") as hosts_file:
                for site in data['sites']:
                    hosts_file.write(f"127.0.0.1 {site}\n")
            await websocket.send(json.dumps({"response": "Sitios bloqueados"}))

        elif data['action'] == 'allow_ping':
            # Comando para permitir ping (varía según el sistema operativo)
            await websocket.send(json.dumps({"response": "Ping permitido"}))

        elif data['action'] == 'block_ping':
            # Comando para bloquear ping
            await websocket.send(json.dumps({"response": "Ping bloqueado"}))

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket en ejecución...")
        await asyncio.Future()  # Mantiene el servidor en ejecución

asyncio.run(main())

