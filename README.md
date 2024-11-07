# 🚀 Proyecto de Monitoreo Remoto

¡Bienvenido al **Proyecto de Monitoreo Remoto**! Este software permite el monitoreo y control remoto de computadoras a través de una interfaz web intuitiva, utilizando Flask y React. 

## 📋 Características

- **Captura de Pantalla**: Toma capturas de pantalla de la computadora remota.
- **Control Remoto**: Mueve el ratón y presiona teclas en la computadora remota.
- **Chat en Tiempo Real**: Comunicación bidireccional entre cliente y servidor.
- **Apagar PC Remotamente**: Permite apagar la computadora de forma remota.
- **Bloquear y Desbloquear Teclado y Ratón**: Control total sobre el input de la computadora remota.
- **Negar Acceso a Páginas Web**: Restringe el acceso a ciertas URLs.
- **Gestión de Pings**: Permite o deniega pings de forma remota.

## ⚙️ Requisitos

- Python 3.x
- Node.js
- npm
- Flask
- Flask-SocketIO
- Flask-CORS
- pyautogui
- PIL (Pillow)

## 🚀 Instalación

### Servidor (Flask)

1. **Clona este repositorio:**

   ```bash
   git clone https://github.com/Jona163/PROYECTO_MONITORING_CHEMO.git
   cd PROYECTO_MONITORING_CHEMO
   ```

2. **Crea un entorno virtual y actívalo:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Para Linux/Mac
   venv\Scripts\activate     # Para Windows
   ```

3. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta el servidor:**

   ```bash
   python app.py
   ```

### Cliente (React)

1. **Navega a la carpeta del cliente:**

   ```bash
   cd client
   ```

2. **Instala las dependencias:**

   ```bash
   npm install
   ```

3. **Cambia la URL del servidor en `src/App.js`:**

   ```javascript
   const socket = io('http://<IP_DEL_SERVIDOR>:5000');
   ```

4. **Ejecuta el cliente:**

   ```bash
   npm start
   ```

## 🛠️ Uso

1. Asegúrate de que el servidor Flask esté ejecutándose.
2. Inicia la aplicación React en el cliente.
3. Conéctate al servidor y utiliza las funcionalidades disponibles a través de la interfaz de usuario.

## ⚠️ Notas

- **Seguridad**: Este proyecto está diseñado para ser utilizado en un entorno de prueba. Asegúrate de implementar medidas de seguridad adecuadas antes de usarlo en producción.
- **Limitaciones**: Este software está destinado a fines educativos y de desarrollo.

## 💡 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas contribuir, por favor sigue estos pasos:

1. **Fork** este repositorio.
2. **Crea una nueva rama** (`git checkout -b feature/tu-rama`).
3. **Realiza tus cambios y realiza un commit** (`git commit -m 'Agrega nueva característica'`).
4. **Haz un push a tu rama** (`git push origin feature/tu-rama`).
5. **Abre un Pull Request**.

## 📄 Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).

---

Para más información, visita el [repositorio en GitHub](https://github.com/Jona163/PROYECTO_MONITORING_CHEMO).
```
