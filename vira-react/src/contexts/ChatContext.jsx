import React, { createContext, useState, useCallback, useEffect } from 'react';
import { sendMessage as sendMessageApi, resetConversation } from '../services/chatService';

export const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userId, setUserId] = useState(null);

  // Komponent yüklendiğinde kullanıcı kimliğini belirle
  useEffect(() => {
    const id = getUserId();
    setUserId(id);
    console.log('Kullanıcı kimliği yüklendi:', id);
  }, []);

  // Yerel depolamadan mesajları yükleme
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (err) {
        console.error('Mesaj yükleme hatası:', err);
      }
    }
  }, []);

  // Mesajları yerel depolamaya kaydetme
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chatMessages', JSON.stringify(messages));
    }
  }, [messages]);

  // Kullanıcı kimliğini getir - daha kompakt ve verimli hali
  const getUserId = () => {
    // Önce llm_login'i kontrol et
    const llmLoginId = localStorage.getItem('llm_login');
    if (llmLoginId) return llmLoginId;

    let uid = null;

    // Potansiyel veri kaynaklarını bir dizi halinde tanımlayalım
    const dataSources = [
      // viraSession'dan kullanıcı kimliğini alma (authService.js ile uyumlu)
      {
        key: 'viraSession',
        parser: (data) => {
          const parsed = JSON.parse(data);
          return parsed.user_id || null;
        }
      },
      {
        key: 'persist:registration',
        parser: (data) => {
          const parsed = JSON.parse(data);
          if (parsed.user && parsed.user !== 'null') {
            const user = JSON.parse(parsed.user);
            return user.uid;
          }
          return null;
        }
      },
      {
        key: 'login_user',
        parser: (data) => JSON.parse(data)?.uid || null
      },
      {
        key: 'registrationData',
        parser: (data) => {
          const parsed = JSON.parse(data);
          return (Array.isArray(parsed) && parsed.length > 0 && parsed[0].uid) || null;
        }
      }
    ];

    // Her bir veri kaynağını sırayla kontrol et
    for (const source of dataSources) {
      try {
        const data = localStorage.getItem(source.key);
        if (data) {
          uid = source.parser(data);
          if (uid) {
            console.log(`Kullanıcı kimliği ${source.key} kaynağından alındı:`, uid);
            break;
          }
        }
      } catch (err) {
        console.error(`${source.key} bilgisi alma hatası:`, err);
      }
    }

    // Eğer bir kullanıcı kimliği bulunmuşsa, llm_login'e kaydet
    if (uid) {
      localStorage.setItem('llm_login', uid);
      return uid;
    }

    // Hiçbir yerden kullanıcı kimliği bulunamadıysa, sabit bir değer kullan ve kaydet
    const fixedId = 'llm_user_fixed_id';
    localStorage.setItem('llm_login', fixedId);
    return fixedId;
  };

  // Mesaj gönderme işlevi
  const sendMessage = useCallback(async (content) => {
    // Kullanıcı kimliğini al - state'de varsa oradan al, yoksa getUserId() fonksiyonunu çağır
    const currentUserId = userId || getUserId();

    // Kullanıcı mesajını ekle
    const userMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);

    setLoading(true);
    setIsTyping(true);
    setError(null);

    try {
      // API isteğinin detaylarını logla
      console.log('API isteği gönderiliyor:', {
        user_id: currentUserId,
        message: content,
        stream: false
      });

      const response = await sendMessageApi(currentUserId, content);

      // API'den gelen yanıtı ekle
      if (response) {
        console.log('API yanıtı:', response);

        // Yanıtı doğru alandan çıkarmaya çalış
        let responseContent = '';
        if (typeof response === 'string') {
          responseContent = response;
        } else if (response.response) {
          responseContent = response.response;
        } else if (response.message) {
          responseContent = response.message;
        } else if (response.content) {
          responseContent = response.content;
        } else {
          responseContent = JSON.stringify(response);
        }

        const assistantMessage = {
          role: 'assistant',
          content: responseContent
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (err) {
      console.error('Mesaj gönderme hatası:', err);
      const errorMessage = err.message || 'Bilinmeyen hata';
      setError(errorMessage);

      // Hata detaylarını konsola yazdır
      if (err.response) {
        console.error('Hata yanıtı:', err.response);
        console.error('Hata durumu:', err.response.status);
        console.error('Hata verileri:', err.response.data);
      }

      // Hata mesajını göster
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Üzgünüm, bir hata oluştu: ${errorMessage}`
      }]);
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  }, [userId]);

  // Sohbeti sıfırlama işlevi
  const resetChat = useCallback(async () => {
    setMessages([]);
    localStorage.removeItem('chatMessages');

    // Mevcut kullanıcı kimliğiyle API'yi çağır
    const currentUserId = userId || getUserId();

    try {
      // Sunucu tarafında da oturumu sıfırla
      await resetConversation(currentUserId);
      console.log('Oturum sunucu tarafında sıfırlandı');
    } catch (err) {
      console.error('Oturum sıfırlama hatası:', err);
    }
  }, [userId]);

  return (
    <ChatContext.Provider
      value={{
        messages,
        isTyping,
        loading,
        error,
        sendMessage,
        resetChat,
        userId
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};