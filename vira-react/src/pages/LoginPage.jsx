import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import LoginForm from '../components/Auth/LoginForm';
import RegisterForm from '../components/Auth/RegisterForm';
import ApiStatus from '../components/UI/ApiStatus';
import '../styles/auth.css';

const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [notification, setNotification] = useState({ message: '', type: '' });
  const { login, register } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const handleLogin = async (username, password) => {
    setNotification({ message: 'Giriş yapılıyor...', type: 'info' });
    const result = await login(username, password);
    
    if (result.success) {
      setNotification({ message: 'Giriş başarılı! Yönlendiriliyorsunuz...', type: 'success' });
      setTimeout(() => navigate('/chat'), 1000);
    } else {
      setNotification({ message: result.message || 'Giriş başarısız', type: 'error' });
    }
  };
  
  const handleRegister = async (userData) => {
    setNotification({ message: 'Hesap oluşturuluyor...', type: 'info' });
    const result = await register(userData.username, userData.password, userData.email);
    
    if (result.success) {
      setNotification({ message: result.message, type: 'success' });
      setTimeout(() => setActiveTab('login'), 2000);
    } else {
      setNotification({ message: result.message, type: 'error' });
    }
  };
  
  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          {/* Logo resmi yerine emoji kullanıyoruz */}
          <div className="emoji-avatar">🤖</div>
          <div className="login-title">
            <h1>Vira AI</h1>
            <p>Devam etmek için giriş yapın</p>
          </div>
        </div>

        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => setActiveTab('login')}
          >
            {/* Giriş sekmesine emoji ekliyoruz */}
            🔑 Giriş Yap
          </button>
          <button
            className={`tab-btn ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => setActiveTab('register')}
          >
            {/* Kayıt sekmesine emoji ekliyoruz */}
            📝 Hesap Oluştur
          </button>
        </div>

        {notification.message && (
          <div className={`notification ${notification.type}`}>
            {/* Bildirim türüne göre emoji ekliyoruz */}
            {notification.type === 'success' && '✅ '}
            {notification.type === 'error' && '❌ '}
            {notification.type === 'info' && 'ℹ️ '}
            {notification.message}
          </div>
        )}
        
        <div className="tab-content">
          {activeTab === 'login' ? (
            <LoginForm onSubmit={handleLogin} />
          ) : (
            <RegisterForm onSubmit={handleRegister} />
          )}
        </div>
        
        <ApiStatus />
        
        <div className="login-footer">
          © {new Date().getFullYear()} Vira AI | v1.0.0
        </div>
      </div>
    </div>
  );
};

export default LoginPage;