import api from './api';

export const login = async (username, password) => {
  try {
    const response = await api.post('/login', { username, password });
    const userData = response.data;
    
    // Oturumu localStorage'a kaydet
    localStorage.setItem('viraSession', JSON.stringify({
      user_id: userData.user_id,
      username: username,
      token: userData.access_token,
      is_authenticated: true
    }));
    
    return {
      user_id: userData.user_id,
      username: username,
      token: userData.access_token
    };
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Giriş başarısız');
  }
};

export const register = async (username, password, email = '') => {
  try {
    const requestData = { username, password };
    if (email) requestData.email = email;
    
    await api.post('/register', requestData);
    return { success: true };
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Kayıt başarısız');
  }
};

export const checkSession = async () => {
  try {
    const sessionString = localStorage.getItem('viraSession');
    if (!sessionString) {
      return null;
    }

    const session = JSON.parse(sessionString);

    if (!session || !session.token) {
      return null;
    }

    // Burada API doğrulaması yapmadan oturumu dönüyoruz
    // Gerçek bir API çağrısı yerine localStorage'daki veriye güveniyoruz
    // Böylece sayfa yenilendiğinde oturum korunacak

    return {
      user_id: session.user_id,
      username: session.username,
      token: session.token
    };
  } catch (error) {
    console.error('Oturum kontrol hatası:', error);
    localStorage.removeItem('viraSession');
    return null;
  }
};

export const logout = () => {
  localStorage.removeItem('viraSession');
};