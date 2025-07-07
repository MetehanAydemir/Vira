import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Her istekte token'ı eklemek için interceptor
api.interceptors.request.use(
  (config) => {
    const sessionData = localStorage.getItem('viraSession');
    if (sessionData) {
      try {
        const { token } = JSON.parse(sessionData);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (e) {
        console.error('Token parse hatası:', e);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 401 hataları için interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 401 hatası durumunda (yetkisiz erişim)
    if (error.response && error.response.status === 401) {
      console.warn('Yetkilendirme hatası, otomatik çıkış yapılıyor...');
      // Çıkış yapmadan önce kullanıcıyı bilgilendir
      // localStorage.removeItem('viraSession');
      // Sayfayı yeniden yükleme yerine kullanıcıyı uyararak devam edebilirsiniz
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;