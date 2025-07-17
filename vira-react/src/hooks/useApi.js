import { useState, useCallback } from 'react';
import api from '../services/api';

/**
 * API istekleri için özel hook
 * @returns {Object} API işlemlerini yönetmek için fonksiyonlar
 */
const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * API isteği gönderme fonksiyonu
   * @param {Function} apiCall - API çağrı fonksiyonu
   * @param {Object} options - İstek seçenekleri
   * @returns {Promise<any>} API yanıtı
   */
  const callApi = useCallback(async (apiCall, options = {}) => {
    const { onSuccess, onError, showLoading = true } = options;
    
    if (showLoading) setLoading(true);
    setError(null);
    
    try {
      const response = await apiCall();
      
      if (onSuccess) {
        onSuccess(response);
      }
      
      return response;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      setError(errorMessage);
      
      if (onError) {
        onError(errorMessage);
      }
      
      throw new Error(errorMessage);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  /**
   * API durumunu kontrol etme
   * @returns {Promise<{status: string, online: boolean}>} API durumu
   */
  const checkApiHealth = useCallback(async () => {
    try {
      const response = await api.get('/health');
      return { status: 'API bağlantısı kuruldu', online: true };
    } catch (err) {
      return { status: 'API bağlantısı kurulamadı', online: false };
    }
  }, []);

  return {
    loading,
    error,
    callApi,
    checkApiHealth,
  };
};

export default useApi;