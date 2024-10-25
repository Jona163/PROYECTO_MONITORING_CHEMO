import React, { useState, useEffect } from 'react';
import { getScreenshot, moveMouse, pressKey } from './remoteService';

const RemoteDesktop = () => {
    const [screenshotUrl, setScreenshotUrl] = useState(null);

    useEffect(() => {
        const fetchScreenshot = async () => {
            const url = await getScreenshot();
            setScreenshotUrl(url);
        };

        // Actualizar la captura de pantalla cada segundo
        const intervalId = setInterval(fetchScreenshot, 1000);

        // Limpiar intervalo al desmontar
        return () => clearInterval(intervalId);
    }, []);

    const handleMouseMove = (e) => {
        const x = e.clientX;
        const y = e.clientY;
        moveMouse(x, y);
    };

    const handleKeyPress = (e) => {
        pressKey(e.key);
    };

    return (
        <div
            onMouseMove={handleMouseMove}
            onKeyDown={handleKeyPress}
            tabIndex="0"
            style={{ outline: 'none' }}
        >
            {screenshotUrl ? (
                <img src={screenshotUrl} alt="Remote Desktop" style={{ width: '100%', height: 'auto' }} />
            ) : (
                <p>Cargando captura de pantalla...</p>
            )}
        </div>
    );
};

export default RemoteDesktop;
