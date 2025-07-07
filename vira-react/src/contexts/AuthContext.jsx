import React, { createContext, useState, useEffect } from 'react';
import { login, register, checkSession, logout as logoutService } from '../services/authService';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadSession = async () => {
      try {
        const sessionData = await checkSession();
        if (sessionData) {
          setUser({
            userId: sessionData.user_id,
            username: sessionData.username
          });
          setToken(sessionData.token);
          setIsAuthenticated(true);
        }
      } catch (err) {
        console.error("Oturum yükleme hatası:", err);
      } finally {
        setLoading(false);
      }
    };

    loadSession();
  }, []);

  const loginUser = async (username, password) => {
    setError(null);
    try {
      const response = await login(username, password);
      
      setUser({
        userId: response.user_id,
        username: response.username
      });
      setToken(response.token);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (err) {
      setError(err.message || "Giriş başarısız");
      return { success: false, message: err.message };
    }
  };

  const registerUser = async (username, password, email) => {
    setError(null);
    try {
      await register(username, password, email);
      return { success: true, message: "Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz." };
    } catch (err) {
      setError(err.message || "Kayıt başarısız");
      return { success: false, message: err.message };
    }
  };

  const logout = () => {
    logoutService();
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        token,
        isAuthenticated, 
        loading, 
        error,
        login: loginUser, 
        register: registerUser, 
        logout 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};