import React from 'react';
import ApiStatus from '../UI/ApiStatus';

const ChatHeader = ({ username, onLogout }) => {
  return (
    <header className="chat-header">
      <div className="header-logo">
        {/* Logo resmi yerine emoji kullanıyoruz */}
        <div className="emoji-logo">🤖</div>
        <div>
          <h1>Vira AI</h1>
          <p>Kişisel Asistanınız</p>
        </div>
      </div>

      <div className="header-info">
        <ApiStatus />
        <span className="username">{username || 'Misafir'}</span>
      </div>

      <div className="header-actions">
        <button
          className="btn btn-secondary"
          onClick={onLogout}
        >
          {/* Çıkış butonuna emoji ekleyelim */}
          🚪 Çıkış Yap
        </button>
      </div>
    </header>
  );
};

export default ChatHeader;