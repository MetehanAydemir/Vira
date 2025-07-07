import React, { useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { formatDate } from '../../utils/formatters';

const Sidebar = () => {
  const { user } = useContext(AuthContext);

  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <h3>Vira Hakkında</h3>
        <p className="sidebar-description">
          <strong>Vira AI Asistan</strong>, uzun süreli hafızaya sahip, 
          LangGraph tabanlı bir yapay zeka asistanıdır.
        </p>
        
        <div className="sidebar-features">
          <div className="feature-item">
            <span className="feature-icon">🧠</span>
            <span className="feature-text">Uzun süreli hafıza</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">😊</span>
            <span className="feature-text">Duygu analizi</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <span className="feature-text">Niyet algılama</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔒</span>
            <span className="feature-text">Omega protokolü</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔄</span>
            <span className="feature-text">Gerçek zamanlı yanıtlar</span>
          </div>
        </div>
      </div>
      
      <div className="sidebar-section">
        <h3>Kullanım İpuçları</h3>
        <ul className="sidebar-tips">
          <li>Herhangi bir konuda sohbet edebilirsiniz</li>
          <li>Vira önceki konuşmalarınızı hatırlayacaktır</li>
          <li>Sayfa yenilense bile konuşma geçmişi korunur</li>
          <li>"0427" yazarak Omega protokolünü etkinleştirebilirsiniz</li>
        </ul>
      </div>
      
      <div className="sidebar-section">
        <h3>Oturum Bilgileri</h3>
        <div className="sidebar-session-info">
          <div className="session-item">
            <strong>Kullanıcı:</strong> {user?.username || 'Misafir'}
          </div>
          <div className="session-item">
            <strong>Son güncelleme:</strong> {formatDate(new Date())}
          </div>
        </div>
      </div>
      
      <div className="sidebar-footer">
        © {new Date().getFullYear()} Vira AI | v1.0.0
      </div>
    </div>
  );
};

export default Sidebar;