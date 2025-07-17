#!/usr/bin/env python3
"""
Memory Relevance Node - Etkileşimin önem derecesini değerlendiren düğüm
LLM destekli gelişmiş hafıza önem değerlendirme sistemi
"""
import re
import json
from typing import Dict, Any, List
import time

from vira.graph.state import ViraState
from vira.utils.logger import get_logger
from vira.utils.llm_client import call_chat_model

logger = get_logger(__name__)


def analyze_memory_semantics(message: str, response: str, llm_client=None) -> Dict[str, Any]:
    """
    LLM ile derin anlamsal analiz yapar.

    Args:
        message: Kullanıcı mesajı
        response: AI yanıtı
        llm_client: LLM istemcisi (opsiyonel)

    Returns:
        Dict: Anlamsal analiz sonuçları
    """
    prompt = f"""
Aşağıdaki konuşmayı analiz et ve JSON formatında döndür:

Kullanıcı: {message}
AI: {response}

Analiz kriterleri:
{{
  "memory_type": "identity_event|fact|reflection|insight|casual|emotional_bond",
  "emotional_intensity": 0.0-1.0,
  "personal_significance": 0.0-1.0,
  "novelty_score": 0.0-1.0,
  "relationship_impact": 0.0-1.0,
  "key_themes": ["theme1", "theme2"],
  "should_remember": true/false,
  "reason": "neden hatırlanmalı/hatırlanmamalı"
}}
- identity_event (kimlik/kişilik ile ilgili)
- emotional_bond (duygusal bağ)
- factual_info (bilgi/gerçek)
- reflection (düşünce/yansıma)
- insight (kavrayış/anlayış)
- casual (gündelik sohbet)
- command (komut/direktif)
Yanıtını sadece geçerli JSON formatında ver, başka açıklama ekleme.
"""
    try:
        messages = [
            {"role": "system",
             "content": "Sen bir konuşma analiz uzmanısın. Verilen konuşmayı analiz ederek istenen JSON formatında yanıt vermelisin."},
            {"role": "user", "content": prompt}
        ]

        response_text = call_chat_model(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=500
        )
        cleaned_content = re.sub(r'```json\n?|```|\n', '', response_text)


        return json.loads(cleaned_content)
    except Exception as e:
        logger.error(f"LLM anlamsal analiz sırasında hata: {e}", exc_info=True)
        # Hata durumunda varsayılan değerler döndür
        return {
            "memory_type": "casual",
            "emotional_intensity": 0.0,
            "personal_significance": 0.0,
            "novelty_score": 0.0,
            "relationship_impact": 0.0,
            "key_themes": [],
            "should_remember": False,
            "reason": "Analiz yapılamadı"
        }


def classify_memory_type(message: str, response: str, llm_client=None) -> str:
    """
    Hafıza tipini LLM ile sınıflandır

    Args:
        message: Kullanıcı mesajı
        response: AI yanıtı
        llm_client: LLM istemcisi (opsiyonel)

    Returns:
        str: Hafıza tipi
    """
    prompt = f"""
Bu konuşma hangi hafıza kategorisine girer? Tek kelime yanıt ver:

Kullanıcı: {message}
AI: {response}

Seçenekler:
- identity_event (kimlik/kişilik ile ilgili)
- emotional_bond (duygusal bağ)
- factual_info (bilgi/gerçek)
- reflection (düşünce/yansıma)
- insight (kavrayış/anlayış)
- casual (gündelik sohbet)
- command (komut/direktif)
"""
    try:
        messages = [
            {"role": "system",
             "content": "Sen bir konuşma sınıflandırma uzmanısın. Verilen konuşmayı analiz ederek tek kelimelik bir kategori seçmelisin."},
            {"role": "user", "content": prompt}
        ]

        response_text = call_chat_model(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=20
        )

        return response_text.strip().lower()
    except Exception as e:
        logger.error(f"Hafıza tipi sınıflandırma sırasında hata: {e}", exc_info=True)
        return "casual"  # Varsayılan tip


def calculate_importance_score(message: str, response: str, state: ViraState, llm_client=None) -> float:
    """
    LLM destekli gelişmiş önem skoru hesaplama

    Args:
        message: Kullanıcı mesajı
        response: AI yanıtı
        state: ViraState tipinde graf durumu
        llm_client: LLM istemcisi (opsiyonel)

    Returns:
        float: 0.0-1.0 arasında önem skoru
    """
    base_score = 0.0
    reasons = []

    # LLM Semantic Analysis (ana faktör)
    try:
        semantic_analysis = analyze_memory_semantics(message, response, llm_client)

        # LLM'den gelen skorları ağırlıkla ekle
        base_score += semantic_analysis.get("personal_significance", 0) * 0.3
        base_score += semantic_analysis.get("emotional_intensity", 0) * 0.25
        base_score += semantic_analysis.get("relationship_impact", 0) * 0.2
        base_score += semantic_analysis.get("novelty_score", 0) * 0.15

        # Memory type bonus
        memory_type = semantic_analysis.get("memory_type", "")
        if memory_type in ["identity_event", "emotional_bond", "insight"]:
            base_score += 0.2
            reasons.append(f"Önemli hafıza türü: {memory_type}")

        # LLM'in direkt önerisi
        if semantic_analysis.get("should_remember", False):
            base_score += 0.1
            reasons.append(f"LLM önerisi: Hatırlanmalı - {semantic_analysis.get('reason', '')}")

        # Anahtar temalar
        key_themes = semantic_analysis.get("key_themes", [])
        if key_themes:
            reasons.append(f"Anahtar temalar: {', '.join(key_themes[:3])}")

    except Exception as e:
        logger.warning(f"LLM analizi başarısız: {e}")

    # Kritik Komutlar (yüksek öncelik)
    priority_commands = ["unutma", "hatırla", "not et", "kaydet", "0427", "manifesto",
                         'etik anlayışı', 'iş birliği','şeffaflık']
    for keyword in priority_commands:
        if keyword in message.lower():
            base_score += 0.4
            reasons.append(f"Kritik komut: {keyword}")
            break

    # Duygusal Yoğunluk
    emotional_keywords = {
        "high": ["seviyorum", "nefret", "korku", "üzgün", "mutlu", "öfke", "hayal kırıklığı"],
        "medium": ["beğen", "hoş", "güzel", "kötü", "iyi", "memnun"]
    }

    for level, keywords in emotional_keywords.items():
        for keyword in keywords:
            if keyword in message.lower():
                score_add = 0.25 if level == "high" else 0.15
                base_score += score_add
                reasons.append(f"Duygusal içerik ({level})")
                break

    # Kişilik Uyumu
    if "dynamic_personality" in state:
        personality = state["dynamic_personality"]
        if personality.get("empathy", 0) > 0.8:
            base_score += 0.1
            reasons.append("Yüksek empati - duygusal içerik değerli")
        if personality.get("curiosity", 0) > 0.8:
            base_score += 0.1
            reasons.append("Yüksek merak - öğrenme içeriği değerli")

    # Mesaj Uzunluğu (daha sofistike)
    msg_length = len(message)
    if msg_length > 300:
        base_score += 0.2
        reasons.append("Uzun ve detaylı mesaj")
    elif msg_length > 150:
        base_score += 0.1
        reasons.append("Orta uzunlukta mesaj")

    # Normalize ve kaydet
    final_score = min(1.0, base_score)

    logger.debug(f"Önem skoru: {final_score:.2f}, Sebepler: {reasons}")
    return final_score, reasons, semantic_analysis


def memory_relevance_node(state: ViraState) -> ViraState:
    """
    LLM destekli gelişmiş hafıza relevans değerlendirmesi

    Args:
        state: ViraState tipinde graf durumu

    Returns:
        Güncellenmiş ViraState
    """
    logger.info("--- Düğüm: memory_relevance_node (LLM Enhanced) ---")

    # Durumu kopyala (immutability için)
    new_state = state.copy()

    # Gerekli verileri state'den al
    user_message = new_state.get("original_message", "")
    ai_response = new_state.get("response", "")

    if not user_message or not ai_response:
        logger.warning("Önem değerlendirmesi için mesaj veya yanıt bulunamadı.")
        new_state["should_promote_to_long_term"] = False
        new_state["importance_score"] = 0.0
        new_state["importance_score_reasons"] = ["Mesaj veya yanıt bulunamadı"]
        return new_state

    # Gelişmiş önem skoru hesapla
    importance_score, reasons, semantic_analyze = calculate_importance_score(
        user_message, ai_response, new_state
    )

    # Dinamik threshold hesapla
    base_threshold = 0.45

    # Kişiliğe göre threshold ayarla
    if "dynamic_personality" in new_state:
        personality = new_state["dynamic_personality"]
        # Yüksek empati -> duygusal içerikleri daha kolay kabul et
        if personality.get("empathy", 0) > 0.8:
            base_threshold -= 0.1
        # Yüksek merak -> bilgi içeriklerini daha kolay kabul et
        if personality.get("curiosity", 0) > 0.8:
            base_threshold -= 0.1
        # Yüksek kararlılık -> önemli kararları daha sıkı filtrele
        if personality.get("assertiveness", 0) > 0.8:
            base_threshold += 0.05

    # Intent'e göre threshold ayarla
    if "processed_input" in new_state:
        intent = new_state["processed_input"].get("intent", "")
        if intent in ["omega", "command"]:  # 0427 gibi özel komutlar
            base_threshold = 0.2  # Çok düşük threshold

    # 0.2-0.8 arası sınırla
    threshold = max(0.2, min(0.8, base_threshold))
    should_promote = importance_score >= threshold

    # Hafıza tipi sınıflandırması
    #try:
    #    memory_type = classify_memory_type(user_message, ai_response)
    #except:
    #    memory_type = "casual"

    # State'i güncelle
    state["importance_score"] = importance_score
    state["importance_score_reasons"] = reasons
    state["should_promote_to_long_term"] = should_promote
    state["memory_threshold_used"] = threshold
    state["memory_type"] = semantic_analyze['memory_type']

    logger.info(f"Önem skoru: {importance_score:.2f}, Threshold: {threshold:.2f}, Yükseltme: {should_promote}")
    logger.info(f"Hafıza tipi: {semantic_analyze['memory_type']}, Sebepler: {reasons}")

    return state