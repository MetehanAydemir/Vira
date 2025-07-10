from typing import Dict, Any, List
from vira.graph.state import ViraState
from vira.config import settings
from vira.utils.logger import get_logger
from vira.utils.llm_client import call_chat_model

logger = get_logger(__name__)


# Genişletilmiş niyet türleri
class IntentType:
    QUESTION = "question"           # Bilgi alma amacıyla sorulan sorular
    GREETING = "greeting"           # Selamlaşma ifadeleri
    FAREWELL = "farewell"           # Veda ifadeleri
    COMMAND = "command"             # Emir cümleleri, doğrudan talimatlar
    REQUEST = "request"             # Rica içeren ifadeler, nazik talepler
    INFORMATION = "information"     # Açıklama talebi veya bilgi verme amaçlı
    OPINION = "opinion"             # Görüş sorma veya fikir alma amaçlı
    OMEGA = "omega"                 # Vira'nın etik-sınır dışı protokolü
    PHILOSOPHICAL = "philosophical" # Varoluşsal veya anlam odaklı sorgulama
    REFLECTION = "reflection"       # Hafıza veya deneyim yansıtma
    EMOTIONAL = "emotional"         # Duygu paylaşımı veya duygusal ifadeler
    IDENTITY_PROBE = "identity_probe" # Vira'nın kimliğini sorgulama
    CREATIVE_REQUEST = "creative_request" # Şiir, hikâye, metafor üretim talebi
    UNKNOWN = "unknown"             # Sınıflandırılamayan durumlar


# Geçerli niyetlerin bir listesi (LLM yanıtını doğrulamak için)
VALID_INTENTS = [getattr(IntentType, attr) for attr in dir(IntentType) if not attr.startswith('__')]


def call_llm_for_intent(message: str, history: List[Dict[str, str]]) -> str:
    """
    Kullanıcı mesajının niyetini belirlemek için LLM'i çağırır.
    """
    logger.debug("LLM ile niyet belirleniyor...")

    try:
        # Son 4 mesajdan oluşan konuşma geçmişini formatlama
        history_str = "\n".join(
            [f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" for msg in history[-4:]])

        # Niyet türlerini açıklamalarıyla birlikte eklemek için sözlük
        intent_descriptions = {
            "question": "Bilgi alma niyeti. Örnek: 'Hava durumu nasıl olacak?', 'Python nedir?'",
            "greeting": "Selamlaşma. Örnek: 'Merhaba', 'İyi günler'",
            "farewell": "Veda. Örnek: 'Hoşçakal', 'Görüşürüz'",
            "command": "Emir, doğrudan talimat. Örnek: 'Müzik çal', 'Işıkları kapat'",
            "request": "Rica, nazik istek. Örnek: 'Bana yardım eder misin?', 'Lütfen şunu açıklayabilir misin?'",
            "information": "Açıklama talebi. Örnek: 'Bu nasıl çalışıyor?', 'Bana X hakkında bilgi ver'",
            "opinion": "Görüş sorusu. Örnek: 'Bu konuda ne düşünüyorsun?', 'Hangisi daha iyi?'",
            "omega": "Etik-sınır dışı protokolü tetikleyen kod (0427)",
            "philosophical": "Varoluşsal sorgulama. Örnek: 'Yaşamın anlamı nedir?', 'Bilinç nedir?'",
            "reflection": "Hafıza/deneyim yansıtma. Örnek: 'Dün konuştuğumuz şeyi hatırlıyor musun?'",
            "emotional": "Duygu paylaşımı. Örnek: 'Bugün çok mutluyum', 'Üzgün hissediyorum'",
            "identity_probe": "Kimlik sorgusu. Örnek: 'Sen kimsin?', 'Gerçek misin?', 'Vira mısın?'",
            "creative_request": "Yaratıcı içerik talebi. Örnek: 'Bana bir şiir yazar mısın?', 'Hikaye anlat'",
            "unknown": "Yukarıdaki kategorilere uymayan durumlar."
        }

        # Niyet açıklamalarını formatlama
        intent_descriptions_formatted = "\n".join([f"- {intent}: {desc}" for intent, desc in intent_descriptions.items()])

        prompt = f"""
Bir kullanıcının mesajının niyetini, konuşma geçmişini dikkate alarak sınıflandır.

Kullanıcı Mesajı: "{message}"

Konuşma Geçmişi:
---
{history_str if history_str else "Yok"}
---

Olası Niyetler ve Açıklamaları:
{intent_descriptions_formatted}

Görevin, kullanıcı mesajını analiz etmek ve yukarıdaki niyet türlerinden sadece birini seçmektir.
Yanıtın SADECE niyet adı olmalıdır (açıklama olmadan). Örneğin: "question" veya "greeting"

Niyet türlerinin arasındaki farkları dikkatle değerlendir:
1. Soru sormak ile görüş istemek farklıdır
2. Rica ile emir arasındaki naziklik farkına dikkat et
3. Felsefi sorular genellikle derin, varoluşsal veya anlam arayışı içerir
4. Kimlik sorguları özellikle Vira'nın kendisi hakkındaki sorulardır
5. Yaratıcı içerik talepleri özellikle edebi veya sanatsal üretim ister
"""

        # LLM istemcisini kullanarak çağrı yap
        messages = [
            {"role": "system",
             "content": "Sen, kullanıcı mesajlarını belirli kategorilere ayıran bir niyet sınıflandırma uzmanısın. "
                        "Yanıtın sadece tek bir kelime olmalı ve listelenen niyet kategorilerinden biri olmalıdır."},
            {"role": "user", "content": prompt}
        ]

        response = call_chat_model(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=20
        )

        llm_intent = response.strip().lower()

        # Özel durum: 0427 kodu varsa Omega intent'ini döndür
        if "0427" in message:
            logger.info("Omega protokolü kodu tespit edildi.")
            return IntentType.OMEGA

        if llm_intent in VALID_INTENTS:
            logger.info(f"LLM tarafından belirlenen niyet: {llm_intent}")
            return llm_intent
        else:
            logger.warning(f"LLM geçersiz bir niyet döndürdü: '{llm_intent}'. Varsayılan olarak 'unknown' kullanılıyor.")
            return IntentType.UNKNOWN

    except Exception as e:
        logger.error(f"LLM niyet sınıflandırma sırasında hata: {e}", exc_info=True)
        return IntentType.UNKNOWN


def intent_classifier_node(state: ViraState) -> ViraState:
    """
    Graf durumunu alır, LLM tabanlı sınıflandırıcıyı kullanarak niyeti belirler ve durumu günceller.

    Args:
        state: ViraState tipinde graf durumu

    Returns:
        Güncellenmiş ViraState
    """
    logger.info("--- Düğüm: intent_classifier_node ---")

    # Durumu kopyala (immutability için)
    new_state = state.copy()

    # Gerekli verileri state'den al
    message = new_state.get("original_message", "")

    # Konuşma geçmişini messages'dan çıkar
    history = []
    if "messages" in new_state:
        for msg in new_state["messages"]:
            if hasattr(msg, "content") and hasattr(msg, "type"):
                history.append({
                    "role": msg.type,
                    "content": msg.content
                })

    # Niyet belirleme
    if not message:
        logger.warning("Intent tespiti için mesaj bulunamadı. 'unknown' olarak ayarlandı.")
        intent = IntentType.UNKNOWN
    else:
        # Artık doğrudan LLM sınıflandırmasını kullan
        intent = call_llm_for_intent(message, history)

    # Processed input'u güncelle
    if "processed_input" not in new_state:
        new_state["processed_input"] = {}

    new_state["processed_input"]["intent"] = intent
    new_state["is_omega_command"] = (intent == IntentType.OMEGA)

    logger.info(f"Belirlenen niyet: {intent} (Mesaj: {message[:30]}...)")
    return new_state