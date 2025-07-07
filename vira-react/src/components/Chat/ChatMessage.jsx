import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message, isLastMessage, isTyping }) => {
  const { role, content } = message;
  const isUser = role === 'user';
  
  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {/* Resim yerine emoji kullanıyoruz */}
        <div className="emoji-avatar">
          {isUser ? '👤' : '🤖'}
        </div>
      </div>
      <div className="message-content">
        {/* Content kontrolü */}
        {content !== undefined && content !== null ? (
          <ReactMarkdown components={{
            // ReactMarkdown için kod bloklarını düzgün göstermek üzere ayarlar
            code: ({node, inline, className, children, ...props}) => {
              return !inline ? (
                <pre className="code-block">
                  <code className={className} {...props}>
                    {children}
                  </code>
                </pre>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
            // Listeleri düzgün gösterme
            ul: ({node, ...props}) => <ul className="markdown-list" {...props} />,
            ol: ({node, ...props}) => <ol className="markdown-list" {...props} />,
            li: ({node, ...props}) => <li className="markdown-list-item" {...props} />,
          }}>
            {content}
          </ReactMarkdown>
        ) : (
          <p>İçerik yüklenemedi.</p>
        )}
        
        {isTyping && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        
        {!isUser && (
          <div className="message-timestamp">
            {new Date().toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;