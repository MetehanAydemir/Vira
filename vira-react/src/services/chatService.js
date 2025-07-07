import api from './api';

export const getConversationHistory = async (userId) => {
  try {
    const response = await api.get(`/conversations/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Konuşma geçmişi alınamadı:', error);
    throw error;
  }
};

export const sendMessage = async (userId, message) => {
  try {
    const response = await api.post('/chat', {
      user_id: userId,  // Doğru user_id
      message: message, // Mesaj içeriği için doğru alan
      stream: false     // Stream değeri
    });
    return response.data;
  } catch (error) {
    console.error('Mesaj gönderilemedi:', error);
    throw error;
  }
};

export const streamMessage = async (userId, message, onToken) => {
  try {
    const response = await api.post('/chat', {
      user_id: userId,   // Doğru user_id
      message: message,  // Mesaj içeriği için doğru alan
      stream: true       // Stream özelliği etkin
    }, {
      responseType: 'stream',
      onDownloadProgress: (progressEvent) => {
        const chunk = progressEvent.currentTarget.response;
        // Stream işleme mantığı
        if (chunk && onToken) {
          onToken(chunk);
        }
      }
    });
    return response.data;
  } catch (error) {
    console.error('Stream mesaj hatası:', error);
    throw error;
  }
};

export const resetConversation = async (userId) => {
  try {
    const response = await api.post('/reset', { user_id: userId });
    return response.data;
  } catch (error) {
    console.error('Oturum sıfırlama hatası:', error);
    throw error;
  }
};