import React, { useEffect, useState, useRef } from 'react';
import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Desconectado');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');

  const ws = useRef(null);
  const reconnectInterval = useRef(null);

  useEffect(() => {
    const connectWebSocket = () => {
      ws.current = new WebSocket('ws://localhost:8765');

      ws.current.onopen = () => {
        console.log('Conexión establecida');
        setConnectionStatus('Conectado');
        if (reconnectInterval.current) {
          clearInterval(reconnectInterval.current);
          reconnectInterval.current = null;
        }
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'image') {
            // Mostrar imagen recibida
            setImage(data.data);
          } else if (data.type === 'message') {
            // Recibir mensajes
            setMessages((prevMessages) => [
              ...prevMessages,
              { text: data.data, type: 'message', self: false },
            ]);
          } else if (data.type === 'file') {
            // Recibir archivos
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                text: `Archivo recibido: ${data.fileName}`,
                type: 'file',
                self: false,
                fileName: data.fileName,
                fileData: data.fileData,
              },
            ]);
          } else if (data.type === 'command') {
            // Procesar comandos
            setMessages((prevMessages) => [
              ...prevMessages,
              { text: `Comando ejecutado: ${data.command}`, type: 'command', self: false },
            ]);
            switch (data.command) {
              case 'block_input':
                console.log('Bloquear entrada');
                break;
              case 'unblock_input':
                console.log('Desbloquear entrada');
                break;
              case 'shutdown':
                console.log('Apagar PC');
                break;
              default:
                console.log('Comando desconocido');
            }
          }
        } catch (error) {
          console.error('Error procesando mensaje:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('Error en WebSocket:', error);
        setConnectionStatus('Error en la conexión');
      };

      ws.current.onclose = () => {
        console.log('Conexión cerrada');
        setConnectionStatus('Desconectado');
        // Intentar reconectar después de 5 segundos
        if (!reconnectInterval.current) {
          reconnectInterval.current = setInterval(() => connectWebSocket(), 5000);
        }
      };
    };

    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectInterval.current) {
        clearInterval(reconnectInterval.current);
      }
    };
  }, []);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'message', data: newMessage }));
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: newMessage, type: 'message', self: true },
      ]);
      setNewMessage('');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  const handleSendFile = (e) => {
    e.preventDefault();
    if (file && ws.current && ws.current.readyState === WebSocket.OPEN) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const fileData = reader.result.split(',')[1];
        ws.current.send(JSON.stringify({ type: 'file', fileName, fileData }));
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            text: `Archivo enviado: ${fileName}`,
            type: 'file',
            self: true,
            fileName,
            fileData,
          },
        ]);
        setFile(null);
        setFileName('');
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>Pantalla en Vivo</h1>
        <p>Estado de la conexión: {connectionStatus}</p>
        {image ? (
          <div className="image-container">
            <img src={`data:image/jpeg;base64,${image}`} alt="Pantalla en vivo" className="live-image" />
          </div>
        ) : (
          <p>Conectando al servidor...</p>
        )}

        <div className="chat-container">
          <h2>Chat</h2>
          <div className="messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.self ? 'sent' : 'received'}`}>
                {msg.type === 'message' ? (
                  msg.text
                ) : msg.type === 'file' ? (
                  <a href={`data:application/octet-stream;base64,${msg.fileData}`} download={msg.fileName}>
                    Descargar {msg.fileName}
                  </a>
                ) : (
                  <span>{msg.text}</span>
                )}
              </div>
            ))}
          </div>
          <form className="form-container" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Escribe un mensaje..."
            />
            <button type="submit">Enviar</button>
          </form>
        </div>

        <div className="file-container">
          <h2>Transferencia de Archivos</h2>
          <label htmlFor="file-upload" className="custom-file-upload">
            Seleccionar archivo
          </label>
          <input id="file-upload" type="file" onChange={handleFileChange} style={{ display: 'none' }} />
          {fileName && (
            <>
              <p>Archivo seleccionado: {fileName}</p>
              <button onClick={handleSendFile} className="send-file-button">
                Enviar Archivo
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
