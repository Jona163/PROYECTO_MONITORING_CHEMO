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
  const imageRef = useRef(null);

  useEffect(() => {
    // Conectar al servidor WebSocket
    ws.current = new WebSocket('ws://localhost:8765');

    ws.current.onopen = () => {
      console.log('Conexión establecida');
      setConnectionStatus('Conectado');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'image') {
        setImage(data.data);
      } else if (data.type === 'message') {
        setMessages((prevMessages) => [
          ...prevMessages, 
          { text: data.data, type: 'message', self: false }
        ]);
      } else if (data.type === 'file') {
        setMessages((prevMessages) => [
          ...prevMessages,
          { 
            text: `Archivo recibido: ${data.fileName}`, 
            type: 'file', 
            self: false, 
            fileName: data.fileName, 
            fileData: data.fileData 
          }
        ]);
      } else if (data.type === 'command') {
        // Ejecutar comandos recibidos del maestro
        executeCommand(data.command);
      }
    };

    ws.current.onerror = (error) => {
      console.error('Error en WebSocket:', error);
      setConnectionStatus('Error en la conexión');
    };

    ws.current.onclose = () => {
      console.log('Conexión cerrada');
      setConnectionStatus('Desconectado');
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const executeCommand = (command) => {
    switch (command) {
      case 'block_input':
        console.log('Bloqueando entrada...');
        // Aquí se llamaría a la función que bloquea el teclado y ratón.
        // Por ejemplo: blockKeyboardAndMouse();
        break;
      case 'unblock_input':
        console.log('Desbloqueando entrada...');
        // Aquí se llamaría a la función que desbloquea el teclado y ratón.
        // Por ejemplo: unblockKeyboardAndMouse();
        break;
      case 'shutdown':
        console.log('Apagando PC...');
        // Aquí se podría ejecutar un comando de apagado remoto.
        // Por ejemplo, en un sistema Windows se podría usar: shutdown -s -t 0
        break;
      case 'block_sites':
        console.log('Restringiendo acceso a sitios web...');
        // Aquí se implementaría la lógica para bloquear sitios web específicos.
        // Por ejemplo, se puede usar una extensión de navegador o un proxy.
        break;
      case 'allow_ping':
        console.log('Permitiendo ping...');
        // Lógica para permitir ping.
        break;
      case 'block_ping':
        console.log('Bloqueando ping...');
        // Lógica para bloquear ping.
        break;
      default:
        console.log('Comando desconocido');
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'message', data: newMessage }));
      setMessages((prevMessages) => [
        ...prevMessages, 
        { text: newMessage, type: 'message', self: true }
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
            fileData 
          }
        ]);
        setFile(null);
        setFileName('');
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="App">
      {/* Código HTML y JSX omitido para brevedad */}
    </div>
  );
}

export default App;
