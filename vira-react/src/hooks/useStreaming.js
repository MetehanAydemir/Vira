import { useState, useCallback, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import api from '../services/api';

const useStreaming = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const { token } = useContext(AuthContext);
  
  const streamMessage = useCallback(async (userId, message, callback) => {
    setIsStreaming(true);
    
    try {
      const response = await fetch(`${api.defaults.baseURL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token || JSON.parse(localStorage.getItem('viraSession'))?.token}`
        },
        body: JSON.stringify({
          user_id: userId,
          message,
          stream: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        // Chunk'ı decode et ve buffer'a ekle
        buffer += decoder.decode(value, { stream: true });
        
        // Buffer'da tam JSON objelerini bul ve işle
        let startIdx = 0;
        let endIdx = buffer.indexOf('}\n', startIdx);
        
        while (endIdx > -1) {
          try {
            const jsonStr = buffer.substring(startIdx, endIdx + 1);
            const data = JSON.parse(jsonStr);
            
            if (data.token) {
              callback(data.token, null);
            }
            
            if (data.memory_context) {
              callback(null, data.memory_context);
            }
          } catch (e) {
            console.error('JSON parsing error:', e);
          }
          
          // Sonraki JSON objesini ara
          startIdx = endIdx + 2; // '}\n' sonrası
          endIdx = buffer.indexOf('}\n', startIdx);
        }
        
        // İşlenmemiş kısmı buffer'da tut
        if (startIdx > 0) {
          buffer = buffer.substring(startIdx);
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      throw error;
    } finally {
      setIsStreaming(false);
    }
  }, [token]);
  
  return { streamMessage, isStreaming };
};

export default useStreaming;