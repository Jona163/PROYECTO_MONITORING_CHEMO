from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO
from flask_cors import CORS
import pyautogui
import os
import io
from PIL import Image
import ctypes
