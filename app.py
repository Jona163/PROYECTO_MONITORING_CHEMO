from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO
from flask_cors import CORS
import pyautogui
import os
import io
from PIL import Image
import ctypes

app = Flask(__name__)
# Permitir solicitudes CORS desde cualquier origen
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app)

# 3.1 Observar lo que hace otro PC remoto (Captura de pantalla)
@app.route('/screenshot', methods=['GET'])
def screenshot():
    try:
        screenshot = pyautogui.screenshot()
        img_io = io.BytesIO()
        screenshot.save(img_io, 'JPEG')
        img_io.seek(0)
        return Response(img_io, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3.2 Transferencia de información en ambas direcciones (Chat)
@socketio.on('message')
def handle_message(msg):
    print(f'Message received: {msg}')
    socketio.send(msg)

# 3.3 Exhibir un cliente (manejar múltiples PCs)
clients = {}

@socketio.on('register')
def register_client(data):
    client_id = data.get('client_id')
    clients[client_id] = request.sid
    print(f'Client {client_id} registered.')

@socketio.on('disconnect')
def disconnect_client():
    client_id = [k for k, v in clients.items() if v == request.sid]
    if client_id:
        clients.pop(client_id[0])
        print(f'Client {client_id[0]} disconnected.')

# 3.4 Mostrar lo que hace el servidor (por ejemplo, log de acciones)
@app.route('/log', methods=['GET'])
def get_logs():
    # Aquí podrías retornar registros almacenados en un archivo o base de datos
    return jsonify({"log": "Mostrar registros de acciones del servidor."})

# 3.6 Bloquear teclado y mouse
@app.route('/block_input', methods=['POST'])
def block_input():
    try:
        ctypes.windll.user32.BlockInput(True)
        return jsonify({"status": "Input blocked."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3.7 Desbloquear teclado y mouse
@app.route('/unblock_input', methods=['POST'])
def unblock_input():
    try:
        ctypes.windll.user32.BlockInput(False)
        return jsonify({"status": "Input unblocked."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3.8 Apagar el PC remotamente
@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        os.system("shutdown /s /t 1")
        return jsonify({"status": "Shutting down..."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3.9 Denegar el acceso a páginas web específicas
@app.route('/block_website', methods=['POST'])
def block_website():
    try:
        data = request.get_json()
        website = data.get('website')
        # Agregar el dominio al archivo hosts de Windows para bloquearlo
        with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as file:
            file.write(f"127.0.0.1 {website}\n")
        return jsonify({"status": f"Website {website} blocked."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3.10 Denegar ping y permitir ping remotamente
@app.route('/set_ping', methods=['POST'])
def set_ping():
    try:
        data = request.get_json()
        allow_ping = data.get('allow', True)
        firewall_command = "netsh advfirewall firewall add rule name=\"Block ICMP\" protocol=icmpv4:8,any dir=in action=block"
        if allow_ping:
            firewall_command = "netsh advfirewall firewall delete rule name=\"Block ICMP\""
        os.system(firewall_command)
        status = "allowed" if allow_ping else "blocked"
        return jsonify({"status": f"Ping {status}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ejecutar la aplicación
    socketio.run(app, host='0.0.0.0', port=5000)
