import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';

const socket = io('http://localhost:5000'); // Asegúrate de cambiar esto a la IP del servidor en producción

const App = () => {
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const [screenshot, setScreenshot] = useState(null);
    const [website, setWebsite] = useState('');
    const [allowPing, setAllowPing] = useState(true);

    useEffect(() => {
        // Escuchar mensajes de chat
        socket.on('message', (msg) => {
            setMessages((prev) => [...prev, msg]);
        });

        // Registrar el cliente
        socket.emit('register', { client_id: 'cliente_1' });

        return () => {
            socket.off('message');
        };
    }, []);

    const sendMessage = () => {
        socket.send(message);
        setMessage('');
    };

    const handleShutdown = async () => {
        await axios.post('http://localhost:5000/shutdown');
        alert('El equipo se apagará...');
    };

    const handleScreenshot = async () => {
        const response = await axios.get('http://localhost:5000/screenshot', {
            responseType: 'blob'
        });
        const imageUrl = URL.createObjectURL(response.data);
        setScreenshot(imageUrl);
    };

    const handleMoveMouse = async (x, y) => {
        await axios.post('http://localhost:5000/move_mouse', { x, y });
    };

    const handlePressKey = async (key) => {
        await axios.post('http://localhost:5000/press_key', { key });
    };

    const handleBlockInput = async () => {
        await axios.post('http://localhost:5000/block_input');
        alert('Teclado y ratón bloqueados.');
    };

    const handleUnblockInput = async () => {
        await axios.post('http://localhost:5000/unblock_input');
        alert('Teclado y ratón desbloqueados.');
    };

    const handleBlockWebsite = async () => {
        await axios.post('http://localhost:5000/block_website', { website });
        alert(`El acceso a ${website} ha sido bloqueado.`);
    };

    const handleSetPing = async () => {
        await axios.post('http://localhost:5000/set_ping', { allow: allowPing });
        alert(`Ping ha sido ${allowPing ? 'permitido' : 'denegado'}.`);
    };

    return (
        <div>
            <h1>Monitoreo Remoto</h1>

            {/* 3.2 - Chat bidireccional */}
            <div>
                <h2>Chat</h2>
                <div style={{ border: '1px solid black', height: '200px', overflowY: 'scroll' }}>
                    {messages.map((msg, index) => (
                        <div key={index}>{msg}</div>
                    ))}
                </div>
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                />
                <button onClick={sendMessage}>Enviar</button>
            </div>

            {/* 3.1 - Mostrar captura de pantalla */}
            <div>
                <h2>Captura de Pantalla</h2>
                <button onClick={handleScreenshot}>Obtener Captura</button>
                {screenshot && <img src={screenshot} alt="Captura de pantalla" width="300" />}
            </div>

            {/* 3.6 y 3.7 - Bloquear/Desbloquear teclado y mouse */}
            <div>
                <h2>Control de Teclado y Mouse</h2>
                <button onClick={handleBlockInput}>Bloquear Input</button>
                <button onClick={handleUnblockInput}>Desbloquear Input</button>
            </div>

            {/* 3.8 - Apagar el PC */}
            <div>
                <h2>Apagar PC</h2>
                <button onClick={handleShutdown}>Apagar</button>
            </div>

            {/* 3.9 - Bloquear sitios web */}
            <div>
                <h2>Bloquear Sitios Web</h2>
                <input
                    type="text"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    placeholder="http://example.com"
                />
                <button onClick={handleBlockWebsite}>Bloquear Sitio Web</button>
            </div>

            {/* 3.10 - Control de Ping */}
            <div>
                <h2>Control de Ping</h2>
                <label>
                    <input
                        type="checkbox"
                        checked={allowPing}
                        onChange={(e) => setAllowPing(e.target.checked)}
                    />
                    Permitir Ping
                </label>
                <button onClick={handleSetPing}>{allowPing ? 'Permitir' : 'Denegar'} Ping</button>
            </div>
        </div>
    );
};

export default App;
