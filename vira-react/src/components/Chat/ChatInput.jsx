import React, { useState, useContext } from 'react';
import { ChatContext } from '../../contexts/ChatContext';
import Button from '../UI/Button';

const ChatInput = () => {
  const [message, setMessage] = useState('');
  const { sendMessage, loading, resetChat } = useContext(ChatContext);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || loading) return;
    
    await sendMessage(message);
    setMessage('');
  };
  
  return (
    <div className="chat-input-container">
      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          className="message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Vira ile konuşmak için bir şeyler yazın... (Örn: Merhaba, sen kimsin?)"
          disabled={loading}
          rows={2}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <div className="chat-controls">
          <Button 
            type="submit" 
            variant="primary"
            disabled={loading || !message.trim()}
          >
            {loading ? 'Gönderiliyor...' : 'Gönder'}
          </Button>
          <Button 
            type="button" 
            variant="secondary"
            onClick={resetChat}
          >
            Yeni Oturum
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ChatInput;