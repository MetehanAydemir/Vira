import React, { useState } from 'react';

const RegisterForm = ({ onSubmit }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const validate = () => {
    const newErrors = {};
    
    if (!username.trim()) {
      newErrors.username = 'Kullanıcı adı gereklidir';
    } else if (username.length < 3) {
      newErrors.username = 'Kullanıcı adı en az 3 karakter olmalıdır';
    }
    
    if (!password) {
      newErrors.password = 'Şifre gereklidir';
    } else if (password.length < 6) {
      newErrors.password = 'Şifre en az 6 karakter olmalıdır';
    }
    
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Şifreler eşleşmiyor';
    }
    
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Geçerli bir e-posta adresi giriniz';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setLoading(true);
    try {
      await onSubmit({ username, password, email });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="reg-username">👤 Kullanıcı Adı</label>
        <input
          type="text"
          id="reg-username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Kullanıcı adınızı girin"
          required
          disabled={loading}
        />
        {errors.username && <div className="form-error">⚠️ {errors.username}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="reg-email">📧 E-posta (İsteğe bağlı)</label>
        <input
          type="email"
          id="reg-email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="E-posta adresinizi girin"
          disabled={loading}
        />
        {errors.email && <div className="form-error">⚠️ {errors.email}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="reg-password">🔒 Şifre</label>
        <input
          type="password"
          id="reg-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Şifrenizi girin"
          required
          disabled={loading}
        />
        {errors.password && <div className="form-error">⚠️ {errors.password}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="reg-confirm-password">🔐 Şifre Tekrar</label>
        <input
          type="password"
          id="reg-confirm-password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Şifrenizi tekrar girin"
          required
          disabled={loading}
        />
        {errors.confirmPassword && <div className="form-error">⚠️ {errors.confirmPassword}</div>}
      </div>

      <div className="form-actions">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !username.trim() || !password.trim()}
        >
          {loading ? '⏳ Hesap Oluşturuluyor...' : '📝 Hesap Oluştur'}
        </button>
      </div>
    </form>
  );
};

export default RegisterForm;