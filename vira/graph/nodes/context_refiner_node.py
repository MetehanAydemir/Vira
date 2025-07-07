#!/usr/bin/env python3
"""
Context Refiner Node - Hatırlanan anıları mevcut bağlama göre işler ve rafine eder.
(Refactor edilmiş versiyon)
"""
import textwrap
from typing import Dict, Any

from openai import OpenAI
from vira.graph.state import ViraState
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)


def get_custom_chat_client() -> OpenAI:
    """OpenRouter gibi özel bir OpenAI uyumlu API için istemci başlatır."""
    return OpenAI(
        api_key=settings.CUSTOM_CHAT_API_KEY,
        base_url=settings.CUSTOM_CHAT_API_ENDPOINT,
    )


def context_refiner_node(state: ViraState) -> ViraState:
    """
    Kullanıcının mesajı ve geri çağrılan anıları kullanarak, LLM aracılığıyla
    rafine edilmiş, yoğunlaştırılmış bir bağlam oluşturur ve state'i günceller.
    """
    logger.info("--- Düğüm: context_refiner_node ---")

    # Gerekli verileri state'ten al
    processed_input = state.get("processed_input", {})
    cleaned_message = processed_input.get("cleaned_message")
    retrieved_memories = state.get("memory_context", [])

    # Başlangıçta rafine edilmiş bağlamı boş olarak ayarla
    state["refined_context"] = ""

    # Rafine edilecek anı yoksa adımı atla
    if not retrieved_memories:
        logger.info("Rafine edilecek anı bulunamadı, adım atlanıyor.")
        return state

    # ÖNERİ UYGULANDI: Anıları LLM'e göndermeden önce eşiğe göre filtrele
    threshold = getattr(settings, "MEMORY_SIMILARITY_THRESHOLD", 0.7)

    memory_str = retrieved_memories

    try:
        client = get_custom_chat_client()
        model_name = settings.CUSTOM_CHAT_MODEL_NAME
        if not model_name:
            logger.error("Yapılandırma hatası: CUSTOM_CHAT_MODEL_NAME ayarı eksik.")
            return state

        # ÖNERİ UYGULANDI: textwrap.dedent ile temizlenmiş ve daha net talimatlı prompt
        prompt = textwrap.dedent(f"""
            GÖREV: Bir kullanıcının güncel mesajını ve geçmiş konuşmalardan hatırlanan anıları analiz et. Bu anılardan SADECE güncel mesajla doğrudan ilgili ve ona değer katacak olanları kullanarak kısa, yoğun ve anlamlı bir özet çıkar. Alakasız veya tekrarlayan bilgileri ele.

            KULLANICININ GÜNCEL MESAJI:
            "{cleaned_message}"

            GEÇMİŞTEN HATIRLANAN ANILAR (Benzerliğe göre sıralı):
            {memory_str}

            İSTENEN ÇIKTI:
            Yukarıdaki anılardan faydalanarak, güncel konuşma için en faydalı olacak şekilde 1-2 cümlelik rafine bir bağlam özeti oluştur. Eğer anıların hiçbiri güncel mesajla anlamlı bir şekilde ilgili değilse, SADECE "" (boş bir metin) döndür.
        """)

        logger.debug(f"Context refiner prompt'u: {prompt}")

        # ÖNERİ UYGULANDI: max_tokens düşürüldü
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system",
                 "content": "Sen, geçmiş bilgileri sentezleyerek bir konuşma için en alakalı bağlamı çıkaran zeki bir asistansın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150,
        )

        refined_context = response.choices[0].message.content.strip()

        if refined_context:
            logger.info(f"Rafine edilmiş bağlam oluşturuldu: {refined_context[:100]}...")
        else:
            logger.info("LLM, anıların mevcut bağlamla ilgisiz olduğuna karar verdi.")

        # ÖNERİ UYGULANDI: State'in tamamını güncelle ve döndür
        state["refined_context"] = refined_context
        return state

    except Exception as e:
        logger.error(f"Bağlam rafine edilirken hata oluştu: {e}", exc_info=True)
        # Hata durumunda bile state'in tutarlı kalmasını sağla
        state["refined_context"] = ""
        return state