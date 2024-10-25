import axios from 'axios';

const SERVER_URL = 'http://<IP_DEL_SERVIDOR>:5000'; // Reemplaza <IP_DEL_SERVIDOR> con la IP correcta

export const getScreenshot = async () => {
    try {
        const response = await axios.get(`${SERVER_URL}/screenshot`, { responseType: 'blob' });
        return URL.createObjectURL(response.data); // Convierte el blob en una URL para la imagen
    } catch (error) {
        console.error('Error obteniendo la captura de pantalla:', error);
        return null;
    }
};

export const moveMouse = async (x, y) => {
    try {
        await axios.post(`${SERVER_URL}/move_mouse`, { x, y });
    } catch (error) {
        console.error('Error moviendo el mouse:', error);
    }
};

export const pressKey = async (key) => {
    try {
        await axios.post(`${SERVER_URL}/press_key`, { key });
    } catch (error) {
        console.error('Error presionando la tecla:', error);
    }
};
