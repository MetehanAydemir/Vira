import React, { useEffect, useRef, useContext } from 'react';
import { ChatContext } from '../../contexts/ChatContext'; // useChat yerine ChatContext kullanacağız
import ChatMessage from './ChatMessage';

const ChatArea = () => {
  const { messages, isTyping } = useContext(ChatContext); // useChat hook'u yerine ChatContext kullanımı
  const messagesEndRef = useRef(null);

  // Yeni mesajlar geldiğinde otomatik kaydırma
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // console.log kullanarak gelen mesajları kontrol et
  console.log('Render edilen mesajlar:', messages);

  return (
    <div className="chat-area">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <p>Merhaba! Vira ile sohbet etmeye başlayın.</p>
          </div>
        ) : (
          // messages dizisinin boş olmadığını ve map edilebilir olduğunu kontrol et
          Array.isArray(messages) && messages.map((message, index) => (
            <ChatMessage
              key={index}
              message={message}
              isLastMessage={index === messages.length - 1}
              isTyping={isTyping && index === messages.length - 1 && message.role === 'assistant'}
            />
          ))
        )}
        {isTyping && messages.length > 0 && (
          <ChatMessage
            message={{ role: 'assistant', content: '' }}
            isTyping={true}
          />
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatArea;