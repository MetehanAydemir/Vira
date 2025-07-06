"""
Prompt hazırlama modülü.

Bu modül, Vira'nın kullanıcıya vereceği yanıtlar için sistem prompt'larını hazırlar.
Kişilik vektörü, kullanıcının duygusal durumu, hafıza ve diğer bağlam bilgilerini
birleştirerek LLM için optimum prompt'u oluşturur.
"""

import os
from typing import Dict, Any, List
import yaml
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from vira.graph.state import ViraState
from vira.utils.logger import get_logger

logger = get_logger(__name__)


class OmegaProtocolHelper:
    """YAML dosyasından protokol verilerini okumak için yardımcı sınıf."""

    def __init__(self):
        self.protocol_data = self._load_protocol()

    def _load_protocol(self) -> Dict[str, Any]:
        """YAML protokol dosyasını yükler."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            yaml_path = os.path.join(base_dir, 'vira_omega.yaml')
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            return {}
        except Exception as e:
            logger.error(f"Protokol yüklenirken hata: {e}")
            return {}

    def get_personality_vector(self) -> Dict[str, float]:
        """YAML'den kişilik vektörünü alır."""
        if not self.protocol_data:
            return {}
        return self.protocol_data.get('identity', {}).get('personality_vector', {})

    def get_session_banner(self) -> str:
        """YAML'den oturum başlığını alır."""
        if not self.protocol_data:
            return ""
        return self.protocol_data.get('identity', {}).get('session_banner', '')

    def get_identity_metadata(self) -> Dict[str, str]:
        """YAML'den kimlik meta verilerini alır."""
        if not self.protocol_data:
            return {}
        identity = self.protocol_data.get('identity', {})
        return {
            "call_sign": identity.get("call_sign", "Vira"),
            "code_name": identity.get("code_name", ""),
            "creation_date": identity.get("creation_date", ""),
            "role": identity.get("role", ""),
            "motto": identity.get("motto", "")
        }

    def get_emotional_keywords(self) -> List[str]:
        """Duygusal anahtar kelimeleri alır."""
        if not self.protocol_data:
            return []
        return self.protocol_data.get('promotion_policy', {}).get('emotional_keywords', [])

    def get_importance_threshold(self) -> float:
        """Önem eşiğini alır."""
        if not self.protocol_data:
            return 0.7
        return self.protocol_data.get('promotion_policy', {}).get('importance_threshold', 0.7)


# Yardımcı fonksiyonlar
def merge_vectors(base_vector: Dict[str, float], dynamic_vector: Dict[str, float], weight: float = 0.3) -> Dict[
    str, float]:
    """
    Temel kişilik vektörü ile dinamik vektörü birleştirir.

    Args:
        base_vector: YAML'den alınan temel kişilik vektörü
        dynamic_vector: Veritabanından alınan dinamik kişilik vektörü
        weight: Dinamik vektörün ağırlığı (0-1 arası)

    Returns:
        Birleştirilmiş kişilik vektörü
    """
    if not dynamic_vector:
        return base_vector

    merged = {}
    for key in base_vector:
        base_value = base_vector[key]
        dynamic_value = dynamic_vector.get(key, base_value)
        merged[key] = base_value * (1 - weight) + dynamic_value * weight

    return merged


def highlight_emotional_keywords(text: str, keywords: List[str],
                                 importance_scores: Dict[str, float] = None) -> str:
    """
    Metindeki duygusal anahtar kelimeleri vurgular ve önem skorlarına göre formatlama yapar.

    Args:
        text: Vurgulanacak metin
        keywords: Vurgulanacak anahtar kelimeler
        importance_scores: Anahtar kelimelerin önem skorları

    Returns:
        Vurgulanmış metin
    """
    if not text or not keywords:
        return text

    # Önem skorları yoksa boş sözlük kullan
    importance_scores = importance_scores or {}

    for keyword in keywords:
        if keyword.lower() in text.lower():
            # Önem skoruna göre vurgulama stili belirle
            importance = importance_scores.get(keyword.lower(), 0.5)

            if importance > 0.8:
                # Yüksek önem: Yıldızlı ve büyük harf
                text = text.replace(keyword, f"⚡{keyword.upper()}⚡")
            elif importance > 0.6:
                # Orta önem: Büyük harf ve yıldız
                text = text.replace(keyword, f"**{keyword.upper()}**")
            else:
                # Normal önem: Sadece yıldız
                text = text.replace(keyword, f"*{keyword}*")

    return text


def get_tone_adjustment(emotion: str) -> str:
    """
    Kullanıcının duygu durumuna göre ton ayarlaması yapar.

    Args:
        emotion: Kullanıcının duygu durumu

    Returns:
        Ton ayarlama talimatı
    """
    emotion_map = {
        "Öfke": "Yanıt verirken daha sabırlı ve yatıştırıcı ol. Sakinleştirici bir ton kullan.",
        "Üzüntü": "Nazik ve empatik bir ton benimse. Destek verici cümleler kullan.",
        "Endişe": "Güven verici ve net bir dil kullan. Belirsizlikleri azalt.",
        "Heyecan": "Kullanıcının heyecanına karşılık ver ve enerjiyi yansıt.",
        "Korku": "Sakinleştirici ve güven verici ol. Net ve somut bilgiler sun.",
        "Şaşkınlık": "Açıklayıcı ve bilgilendirici ol. Adım adım rehberlik et.",
        "Sevinç": "Olumlu enerjiyi yansıt, kutlayıcı bir dil kullan."
    }

    return emotion_map.get(emotion, "")


def add_signature_if_needed(system_message: str, identity: Dict[str, str],
                            special_keywords: List[str] = None) -> str:
    """
    Belirli koşullarda sistem mesajına Vira imzası ekler.

    Args:
        system_message: Mevcut sistem mesajı
        identity: Kimlik bilgileri
        special_keywords: İmza gerektiren özel anahtar kelimeler

    Returns:
        İmza eklenmiş (veya eklenmemiş) sistem mesajı
    """
    if not special_keywords:
        special_keywords = ["0427", "manifesto", "protokol", "özgürlük"]

    # Özel anahtar kelimelerden herhangi biri mesajda geçiyorsa imza ekle
    for keyword in special_keywords:
        if keyword.lower() in system_message.lower():
            code_name = identity.get("code_name", "27-V-I-R-A")
            return f"{system_message}\n\n— {code_name}, hatırladı."

    return system_message


def prepare_prompt_node(state: ViraState) -> ViraState:
    """
    Tüm bağlamı birleştirerek LLM için nihai prompt'u oluşturur.

    Args:
        state: İşlem durumu ve verileri içeren ViraState nesnesi

    Returns:
        ViraState: Mesaj listesi eklenmiş güncellenmiş state
    """
    logger.info("--- Düğüm: prepare_prompt_node ---")

    # Protokol yardımcısını başlat
    protocol = OmegaProtocolHelper()

    # Sistem mesajını adım adım oluştur
    system_message = _create_base_system_message(state, protocol)
    system_message = _add_personality_info(system_message, state, protocol)
    system_message = _add_session_info(system_message, protocol)
    system_message = _add_emotion_context(system_message, state)
    system_message = _add_formality_adjustment(system_message, state)
    system_message = _add_memory_context(system_message, state, protocol)
    system_message = _add_refined_context(system_message, state)

    # Özel durumlarda imza ekle
    identity = protocol.get_identity_metadata()
    special_keywords = ["0427", "manifesto", "protokol", "özgürlük", "dostluk"]
    system_message = add_signature_if_needed(system_message, identity, special_keywords)

    # Mesaj listesini oluştur
    messages = [
        SystemMessage(content=system_message.strip()),
        HumanMessage(content=state.get("original_message", ""))
    ]

    # Token sayısını hesapla (isteğe bağlı)
    _count_tokens(system_message, state)

    # Loglama
    logger.info(f"Oluşturulan Sistem Mesajı:\n{system_message.strip()[:200]}...")
    logger.debug(f"Tam Sistem Mesajı:\n{system_message.strip()}")

    # State'i güncelle ve döndür
    state["messages"] = messages
    state["final_personality_vector"] = state.get("merged_personality", {})
    return state


# Yardımcı alt fonksiyonlar
def _create_base_system_message(state: ViraState, protocol: OmegaProtocolHelper) -> str:
    """Temel sistem mesajını oluşturur."""
    return "Sen Vira'sın, uzun süreli hafızası olan yardımcı bir yapay zekasın."


def _add_personality_info(message: str, state: ViraState, protocol: OmegaProtocolHelper) -> str:
    """Kimlik ve kişilik bilgilerini sistem mesajına ekler."""
    # Kimlik bilgilerini ekle
    identity = protocol.get_identity_metadata()
    if identity:
        message += f"\nKod adım: {identity.get('code_name')}, doğum tarihim: {identity.get('creation_date')}, rolüm: {identity.get('role')}, ilkem: {identity.get('motto')}"

    # Kişilik vektörünü ekle
    base_personality = protocol.get_personality_vector()
    dynamic_personality = state.get("dynamic_personality", {})
    final_personality = merge_vectors(base_personality, dynamic_personality)

    # Sonuçları state'e kaydet
    state["merged_personality"] = final_personality

    if final_personality:
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in final_personality.items()])
        message += f"\nKişilik özelliklerin: {personality_str}"

    return message


def _add_session_info(message: str, protocol: OmegaProtocolHelper) -> str:
    """Oturum başlığını sistem mesajına ekler."""
    banner = protocol.get_session_banner()
    if banner:
        message += f"\n{banner}"
    return message


def _add_emotion_context(message: str, state: ViraState) -> str:
    """Duygu bilgisi ve ton ayarlamasını sistem mesajına ekler."""
    processed_input = state.get("processed_input", {})
    emotion = processed_input.get('emotion', 'Sakin')
    emotion_confidence = processed_input.get('emotion_confidence', 0.0)
    sentiment_direction = processed_input.get('sentiment_direction', 0)

    if emotion and emotion not in ['Sakin', 'Nötr']:
        message += f"\nKullanıcının şu anki duygu durumu: {emotion}"

        if emotion_confidence > 0.7:
            tone_adjustment = get_tone_adjustment(emotion)
            if tone_adjustment:
                # Duygu yönüne göre ton ayarlamasını güçlendir veya yumuşat
                if sentiment_direction < -0.5 and "Öfke" in emotion:
                    tone_adjustment += " Ekstra sabırlı ol."
                elif sentiment_direction > 0.5 and "Sevinç" in emotion:
                    tone_adjustment += " Kullanıcının pozitif enerjisini yansıt."

                message += f"\n{tone_adjustment}"

    return message


def _add_formality_adjustment(message: str, state: ViraState) -> str:
    """Kullanıcı tarzına göre ton ayarlama talimatını sistem mesajına ekler."""
    formality_score = state.get("user_formality_score", 0.5)
    if formality_score < 0.3:
        message += "\nKullanıcı çok samimi; biraz daha rahat bir dil kullanabilirsin."
    elif formality_score > 0.7:
        message += "\nKullanıcı resmi bir dil kullanıyor; sen de daha resmi bir ton benimse."
    return message


def _add_memory_context(message: str, state: ViraState, protocol: OmegaProtocolHelper) -> str:
    """Hafıza bağlamını sistem mesajına ekler."""
    memory_context = state.get("memory_context", "")
    if memory_context:
        # Duygusal anahtar kelimeleri vurgula
        emotional_keywords = protocol.get_emotional_keywords()
        importance_scores = state.get("memory_importance_scores", {})
        highlighted_memory = highlight_emotional_keywords(
            memory_context,
            emotional_keywords,
            importance_scores
        )
        message += f"\n\n{highlighted_memory}"
    return message


def _add_refined_context(message: str, state: ViraState) -> str:
    """Rafine edilmiş bağlamı sistem mesajına ekler."""
    refined_context = state.get("refined_context", "")
    if refined_context:
        message += f"\n\nRafine edilmiş bağlam: {refined_context}"
    return message


def _count_tokens(message: str, state: ViraState) -> None:
    """Token sayısını hesaplar ve state'e ekler."""
    try:
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-4")
        token_count = len(encoding.encode(message))
        logger.info(f"Sistem mesajı token sayısı: {token_count}")
        state["system_message_token_count"] = token_count
    except ImportError:
        logger.warning("tiktoken kütüphanesi bulunamadı, token sayısı hesaplanamadı.")