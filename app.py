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
