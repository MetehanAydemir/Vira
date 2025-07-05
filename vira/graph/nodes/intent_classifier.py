#!/usr/bin/env python3
"""
Intent Classifier - Kullanıcı niyetini belirleyen hibrit (Regex + LLM) düğüm
"""
import re
from typing import Dict, Any, List

# OpenAI istemcisi için gerekli importlar
from openai import OpenAI
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)


# Niyet türleri
class IntentType:
    QUESTION = "question"
    GREETING = "greeting"
    FAREWELL = "farewell"
    COMMAND = "command"
    CHAT = "chat"
    INFORMATION = "information"
    REQUEST = "request"
    OPINION = "opinion"
    OMEGA = "omega"
    UNKNOWN = "unknown"


# Geçerli niyetlerin bir listesi (LLM yanıtını doğrulamak için)
VALID_INTENTS = [getattr(IntentType, attr) for attr in dir(IntentType) if not attr.startswith('__')]

# Regex pattern'ları (hızlı ve net durumlar için)
INTENT_PATTERNS = {
    IntentType.OMEGA: r'\b(?:0427)\b',
    IntentType.QUESTION: r'\?|\b(ne|neden|nasıl|kim|nerede|hangi|kaç|mı|mi|mu|mü)\b',
    IntentType.GREETING: r'\b(merhaba|selam|günaydın|iyi\s*(günler|akşamlar|geceler)|hey|sa)\b',
    IntentType.FAREWELL: r'\b(hoşçakal|görüşürüz|bay bay|iyi\s*(geceler|akşamlar))\b',
    IntentType.COMMAND: r'\b(yap|bul|göster|aç|kapat|hesapla|çalıştır|oluştur|getir)\b',
    IntentType.REQUEST: r'\b(lütfen|rica\s*etsem|mısın|misin|yapar\s*mısın)\b',
}


def get_custom_chat_client() -> OpenAI:
    """OpenRouter gibi özel bir OpenAI uyumlu API için istemci başlatır."""
    return OpenAI(
        api_key=settings.CUSTOM_CHAT_API_KEY,
        base_url=settings.CUSTOM_CHAT_API_ENDPOINT,
    )


def call_llm_for_intent(message: str, history: List[Dict[str, str]]) -> str:
    """
    Belirsiz durumlar için niyeti belirlemek üzere LLM'i çağırır.
    """
    logger.debug("Regex ile niyet belirlenemedi, LLM'e başvuruluyor...")

    try:
        client = get_custom_chat_client()

        history_str = "\n".join(
            [f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" for msg in history[-4:]])

        prompt = f"""
Bir kullanıcının mesajının niyetini, konuşma geçmişini dikkate alarak sınıflandır.
Mesaj: "{message}"

Konuşma Geçmişi:
---
{history_str if history_str else "Yok"}
---

Olası Niyetler: {', '.join(VALID_INTENTS)}

Görevin, yukarıdaki listeden en uygun niyet türünü seçmek ve SADECE o niyetin adını döndürmektir. Örneğin: question
"""
        response = client.chat.completions.create(
            model=settings.CUSTOM_CHAT_MODEL_NAME,
            messages=[
                {"role": "system",
                 "content": "Sen, kullanıcı mesajlarını belirli kategorilere ayıran bir niyet sınıflandırma uzmanısın. Yanıtın sadece tek bir kelime olmalı."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            # --- DÜZELTME: max_tokens değeri API'nin minimum gereksinimi olan 16'ya yükseltildi ---
            max_tokens=20,
        )
        llm_intent = response.choices[0].message.content.strip().lower()

        if llm_intent in VALID_INTENTS:
            logger.info(f"LLM tarafından belirlenen niyet: {llm_intent}")
            return llm_intent
        else:
            logger.warning(f"LLM geçersiz bir niyet döndürdü: '{llm_intent}'. Varsayılan olarak 'chat' kullanılıyor.")
            return IntentType.CHAT

    except Exception as e:
        logger.error(f"LLM niyet sınıflandırma sırasında hata: {e}", exc_info=True)
        return IntentType.CHAT

# --- (Dosyanın geri kalanı değişmedi) ---

def classify_intent_hybrid(message: str, history: List[Dict[str, str]]) -> str:
    """
    Kullanıcı mesajının niyetini hibrit bir yaklaşımla (Regex + LLM) belirler.
    """
    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, message, re.IGNORECASE):
            logger.info(f"Regex ile belirlenen niyet: {intent}")
            return intent
    return call_llm_for_intent(message, history)


def intent_classifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Graf durumunu alır, hibrit sınıflandırıcıyı kullanarak niyeti belirler ve durumu günceller.
    """
    logger.info("--- Düğüm: intent_classifier_node ---")
    new_state = state.copy()
    processed_input = new_state.get("processed_input", {})
    message = processed_input.get("cleaned_message", "")
    history = new_state.get("conversation_history", [])
    if not message:
        logger.warning("Intent tespiti için mesaj bulunamadı. 'unknown' olarak ayarlandı.")
        intent = IntentType.UNKNOWN
    else:
        intent = classify_intent_hybrid(message, history)
    if "processed_input" not in new_state:
        new_state["processed_input"] = {}
    new_state["processed_input"]["intent"] = intent
    new_state["is_omega_command"] = (intent == IntentType.OMEGA)
    logger.info(f"Belirlenen niyet: {intent} (Mesaj: {message[:30]}...)")
    return new_state