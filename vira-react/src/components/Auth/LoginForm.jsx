import React, { useState } from 'react';

const LoginForm = ({ onSubmit }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) return;
    
    setLoading(true);
    try {
      await onSubmit(username, password);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="username">👤 Kullanıcı Adı</label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Kullanıcı adınızı girin"
          required
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">🔒 Şifre</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Şifrenizi girin"
          required
          disabled={loading}
        />
      </div>

      <div className="form-actions">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !username.trim() || !password.trim()}
        >
          {loading ? '⏳ Giriş Yapılıyor...' : '✅ Giriş Yap'}
        </button>

        <div className="form-help">
          <a href="#forgot-password">🔍 Şifremi Unuttum</a>
        </div>
      </div>
    </form>
  );
};

export default LoginForm;