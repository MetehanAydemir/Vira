import { useState, useEffect, useCallback, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { getConversationHistory, resetConversation } from '../services/chatService';
import useStreaming from './useStreaming';

/**
 * Sohbet işlevlerini yönetmek için özel hook
 */
const useChat = () => {
  const { user } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [memoryContext, setMemoryContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { streamMessage, isStreaming } = useStreaming();

  // Konuşma geçmişini yükle
  const loadHistory = useCallback(async () => {
    if (!user?.userId) return;

    setLoading(true);
    try {
      const history = await getConversationHistory(user.userId);

      if (history && history.length > 0) {
        setMessages(history);
      } else {
        setMessages([{
          role: "assistant",
          content: "Merhaba! Size nasıl yardımcı olabilirim?"
        }]);
      }
    } catch (err) {
      setError("Konuşma geçmişi yüklenemedi");
      setMessages([{
        role: "assistant",
        content: "Merhaba! Size nasıl yardımcı olabilirim?"
      }]);
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Kullanıcı değiştiğinde geçmişi yükle
  useEffect(() => {
    if (user) {
      loadHistory();
    }
  }, [user, loadHistory]);

  // Mesaj gönder
  const sendMessage = useCallback(async (message) => {
    if (!message.trim() || !user?.userId) return;

    // Kullanıcı mesajını ekle
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setLoading(true);

    try {
      // Asistan yanıtı için boş bir mesaj başlat
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // Stream yanıtı al
      await streamMessage(user.userId, message, (token, context) => {
        // Token geldikçe mesajı güncelle
        if (token) {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            newMessages[newMessages.length - 1] = {
              ...lastMessage,
              content: lastMessage.content + token
            };
            return newMessages;
          });
        }

        // Hafıza bağlamı geldikçe güncelle
        if (context) {
          setMemoryContext(context);
        }
      });
    } catch (err) {
      setError("Mesaj gönderilemedi");
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          role: 'assistant',
          content: `❌ Bir hata oluştu: ${err.message}`
        };
        return newMessages;
      });
    } finally {
      setLoading(false);
    }
  }, [user, streamMessage]);

  // Oturumu sıfırla
  const resetChat = useCallback(async () => {
    if (!user?.userId) return;

    setLoading(true);
    try {
      await resetConversation(user.userId);
      setMessages([{
        role: "assistant",
        content: "Merhaba! Yeni bir oturum başlattınız."
      }]);
      setMemoryContext("");
    } catch (err) {
      setError("Oturum sıfırlanamadı");
    } finally {
      setLoading(false);
    }
  }, [user]);

  return {
    messages,
    memoryContext,
    loading: loading || isStreaming,
    error,
    sendMessage,
    resetChat,
    loadHistory
  };
};

export default useChat;