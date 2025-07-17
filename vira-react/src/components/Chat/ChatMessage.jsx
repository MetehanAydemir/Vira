import React from 'react';
import ReactMarkdown from 'react-markdown';
import MemoryContext from './MemoryContext';
const ChatMessage = ({ message, isLastMessage, isTyping }) => {
  const { role, content, memoryContext } = message;
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
            // Paragrafları düzgün gösterme
            p: ({node, ...props}) => <p className="markdown-paragraph" {...props} />,
            // Başlıkları düzgün gösterme
            h1: ({node, ...props}) => <h1 className="markdown-heading" {...props} />,
            h2: ({node, ...props}) => <h2 className="markdown-heading" {...props} />,
            h3: ({node, ...props}) => <h3 className="markdown-heading" {...props} />,
            h4: ({node, ...props}) => <h4 className="markdown-heading" {...props} />,
            h5: ({node, ...props}) => <h5 className="markdown-heading" {...props} />,
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

        {/* Asistan mesajları için hafıza bağlamını göster */}
        {!isUser && memoryContext && (
          <div className="message-memory-context">
            <MemoryContext memoryContext={memoryContext} />
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