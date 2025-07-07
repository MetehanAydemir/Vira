import React, { useState, useEffect } from 'react';
import useApi from '../../hooks/useApi';

const ApiStatus = () => {
  const [status, setStatus] = useState({ online: false, message: 'Kontrol ediliyor...' });
  const { checkApiHealth } = useApi();
  
  useEffect(() => {
    const checkStatus = async () => {
      const result = await checkApiHealth();
      setStatus(result);
    };
    
    checkStatus();
    
    // Her 30 saniyede bir kontrol et
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, [checkApiHealth]);
  
  // Status dot yerine duruma göre emoji
  const statusEmoji = status.online ? '🟢' : '🔴';

  return (
    <div className={`api-status ${status.online ? 'online' : 'offline'}`}>
      <span className="status-emoji">{statusEmoji}</span>
      <span className="status-text">{status.status}</span>
    </div>
  );
};

export default ApiStatus;