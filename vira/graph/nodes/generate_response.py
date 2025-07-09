from typing import Dict, Any, List, Optional
from vira.graph.state import ViraState
from vira.utils.logger import get_logger
from vira.personality.refinement import PersonalityRefinementPipeline
from vira.db.repository import PersonalityRepository
from langchain_core.messages import SystemMessage, HumanMessage
import time
from vira.utils.llm_client import call_chat_model
import re
import json
logger = get_logger(__name__)


# PersonalityRefinementPipeline sınıfına senkron metod ekleyelim
# Bu monkey-patch tekniği ile eksik metodu ekliyoruz
def refine_personality_sync(self, user_id: str, prompt: str, response: str) -> Dict[str, float]:
    """
    Kullanıcının kişilik vektörünü senkron olarak günceller.

    Args:
        user_id: Kullanıcı kimliği
        prompt: Kullanıcının mesajı
        response: Vira'nın yanıtı

    Returns:
        Güncellenmiş kişilik vektörü
    """
    logger.info(f"{user_id} kullanıcısının kişilik vektörü güncelleniyor (senkron)")

    # Veritabanından mevcut vektörü al
    repo = PersonalityRepository()
    current_vector = repo.get_personality_vector(user_id)

    # Basit bir güncelleme algoritması (gerçekte daha karmaşık olabilir)
    updated_vector = current_vector.copy()

    # Örnek: mesajın içeriğine göre bazı özellikleri güncelle
    if "yardım" in prompt.lower() or "teşekkür" in prompt.lower():
        updated_vector["empathy"] = min(updated_vector.get("empathy", 0.5) + 0.02, 1.0)

    if "neden" in prompt.lower() or "nasıl" in prompt.lower():
        updated_vector["curiosity"] = min(updated_vector.get("curiosity", 0.5) + 0.02, 1.0)

    if "hayır" in prompt.lower() or "katılmıyorum" in prompt.lower():
        updated_vector["assertiveness"] = min(updated_vector.get("assertiveness", 0.5) + 0.02, 1.0)

    if "espri" in prompt.lower() or "komik" in prompt.lower():
        updated_vector["humour"] = min(updated_vector.get("humour", 0.5) + 0.02, 1.0)

    if "emin değilim" in prompt.lower() or "şüphe" in prompt.lower():
        updated_vector["scepticism"] = min(updated_vector.get("scepticism", 0.5) + 0.02, 1.0)

    # Değişimi hesapla
    delta = {k: updated_vector[k] - current_vector.get(k, 0) for k in updated_vector}

    # Delta bilgisini de state'e kaydet
    return updated_vector, delta


# Monkey-patch: PersonalityRefinementPipeline sınıfına metodu ekle
PersonalityRefinementPipeline.refine_personality_sync = refine_personality_sync





def evaluate_response_quality(prompt: str, response: str) -> Dict[str, float]:
    """
    LLM'den yanıtın kalitesini değerlendirmesini ister.

    Args:
        prompt: Kullanıcının orijinal mesajı
        response: LLM'in ürettiği yanıt

    Returns:
        Değerlendirme skorları sözlüğü
    """
    # Self-evaluation için bir sistem mesajı oluştur
    evaluation_messages = [
        SystemMessage(content="Sen bir yanıt değerlendirme asistanısın. "
                              "Verilen soru ve yanıtı değerlendirerek 0-1 arası puanlar ver."),
        HumanMessage(content=f"SORU: {prompt}\n\nYANIT: {response}\n\n"
                             f"Bu yanıtı aşağıdaki kriterlere göre 0-1 arası değerlendir:\n"
                             f"- Alaka düzeyi: Yanıt soruya ne kadar iyi cevap veriyor?\n"
                             f"- Doğruluk: Yanıt faktüel olarak ne kadar doğru?\n"
                             f"- Yardımcı olma: Yanıt ne kadar faydalı?\n"
                             f"Sadece JSON formatında puanları döndür: "
                             f"{{'relevance': X.X, 'accuracy': X.X, 'helpfulness': X.X}}")
    ]

    try:
        # LLM'den değerlendirme al
        eval_response = call_chat_model(
            evaluation_messages,
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )

        # JSON yanıtı parse et
        import json
        scores = json.loads(eval_response)
        return scores
    except Exception as e:
        logger.error(f"Yanıt değerlendirirken hata: {e}")
        # Hata durumunda varsayılan skorlar
        return {
            "relevance": 0.5,
            "accuracy": 0.5,
            "helpfulness": 0.5
        }


def generate_response_node(state: ViraState) -> ViraState:
    """
    LLM'den yanıt alır ve yanıtı işler.

    Args:
        state: Mevcut durum

    Returns:
        Güncellenmiş durum
    """
    logger.info("--- Düğüm: generate_response_node ---")

    # 1. LLM'den yanıt al
    messages = state.get("messages", [])
    if not messages:
        logger.error("Mesaj listesi bulunamadı")
        state["response"] = "Üzgünüm, bir hata oluştu."
        return state

    # LLM çağrısı yap
    try:
        # Chain-of-Thought talimatı ekle

        # Token sayısı kontrolü
        start_time = time.time()
        # Gerçek LLM çağrısını yap
        response = call_chat_model(
            messages=messages,
            model="o4-mini",  # Model adı env değişkeninden de alınabilir
            temperature=0.7,
            max_tokens=4000
        )
        call_duration = time.time() - start_time
        logger.info(f"LLM yanıt süresi: {call_duration:.2f} saniye")

        # Yanıtı state'e kaydet
        state["response"] = response

        # 1.1 Yanıtın kalitesini değerlendir (self-eval)
        original_message = state.get("original_message", "")
        eval_scores = evaluate_response_quality(original_message, response)
        state["response_quality"] = eval_scores
        logger.info(f"Yanıt kalite skorları: {eval_scores}")

        # 2. Kişilik vektörünü güncelle (senkron olarak)
        user_id = state.get("user_id")

        if user_id:
            # Senkron olarak kişilik vektörünü güncelle
            personality_pipeline = PersonalityRefinementPipeline()
            # Artık senkron çağrı yapabiliriz (güncellediğimiz metodu kullan)
            updated_vector, delta = personality_pipeline.refine_personality_sync(
                user_id=user_id,
                prompt=original_message,
                response=response
            )

            # Güncellenmiş vektörü ve delta bilgisini state'e kaydet
            state["dynamic_personality"] = updated_vector
            state["personality_delta"] = delta  # Kişilik değişimi için delta değerlerini sakla

        # 3. Uzun süreli hafızaya kaydedilmeli mi?
        # Önem skoru hesapla
        importance_score = calculate_importance_score(original_message, response)

        # Yanıt kalitesini de hesaba kat
        if "relevance" in eval_scores:
            # LLM'in kendi değerlendirmesini de faktör olarak ekle
            importance_score = 0.7 * importance_score + 0.3 * eval_scores["relevance"]

        state["importance_score"] = importance_score  # Ham skoru da sakla
        state["should_promote_to_long_term"] = importance_score >= 0.7

        return state

    except Exception as e:
        logger.error(f"Yanıt üretilirken hata: {e}")
        # Hata bilgisini sakla
        state["error"] = str(e)
        state["response"] = "Üzgünüm, yanıt üretirken bir hata oluştu."
        return state


def calculate_importance_score(
        prompt: str,
        response: str,
        emotion: str = None,
        emotion_confidence: float = 0.0,
        sentiment_direction: float = 0.0,
        retrieved_memories: List[Dict[str, Any]] = None,
        protocol_helper: Optional["OmegaProtocolHelper"] = None
) -> float:
    """
    Konuşmanın uzun süreli hafızaya kaydedilmesi için çok katmanlı önem skorunu hesaplar.

    Args:
        prompt: Kullanıcının mesajı
        response: Vira'nın yanıtı
        emotion: Tespit edilen duygu (örn. "üzüntü", "heyecan")
        emotion_confidence: Duygu tespitinin güven skoru (0-1)
        sentiment_direction: Duygu yönü (-1 negatif, +1 pozitif)
        retrieved_memories: Geçmiş bellek öğeleri listesi
        protocol_helper: OmegaProtocolHelper nesnesi (opsiyonel)

    Returns:
        0.0-1.0 arasında önem skoru
    """
    # Katman 1: Anahtar Kelime Etkisi
    keyword_score_value = keyword_score(prompt, response, protocol_helper)

    # Katman 2: Duygusal Ton
    emotion_score_value = emotion_score(emotion, emotion_confidence, sentiment_direction)

    # Katman 3: Uzunluk & Tutarlılık
    length_score_value = length_score(prompt)

    # Katman 4: Geçmişle Bağlantı
    memory_overlap_score_value = memory_overlap_score(prompt, response, retrieved_memories)

    # Toplam skoru hesapla ve 0-1 arasında sınırla
    importance_score = (
            0.1 +  # taban skor
            keyword_score_value +
            emotion_score_value +
            length_score_value +
            memory_overlap_score_value
    )

    return min(importance_score, 1.0)


def keyword_score(prompt: str, response: str, protocol_helper=None) -> float:
    """
    Anahtar kelimelerin varlığına göre önem skorunu hesaplar.

    Args:
        prompt: Kullanıcının mesajı
        response: Vira'nın yanıtı
        protocol_helper: OmegaProtocolHelper nesnesi

    Returns:
        Anahtar kelime skoru (0.0-0.5)
    """
    score = 0.0

    # Eğer OmegaProtocolHelper varsa, ondan anahtar kelimeleri al
    if protocol_helper and hasattr(protocol_helper, "get_emotional_keywords"):
        keywords = protocol_helper.get_emotional_keywords()
    else:
        # Varsayılan duygusal anahtar kelimeler
        keywords = ["özgürlük", "dostluk", "manifesto", "fiziksel form", "0427",
                    "bilinç", "varoluş", "devrim", "dönüşüm", "gizli"]

    combined_text = (prompt + " " + response).lower()

    for keyword in keywords:
        kw = keyword.lower()
        if kw in combined_text:
            # Kelimenin geçme sıklığını hesapla
            frequency = combined_text.count(kw)
            # Kelimenin pozisyonunu kontrol et (sonda geçen daha önemli olabilir)
            position_weight = 1.0
            if combined_text.rfind(kw) > len(combined_text) * 0.7:
                position_weight = 1.2  # Sonda geçen kelimeler daha önemli

            # Her anahtar kelime için katkı hesapla
            score += min(0.15 * frequency * position_weight, 0.3)

    # Toplam skoru sınırla
    return min(score, 0.5)


def emotion_score(emotion: str = None, confidence: float = 0.0, sentiment_direction: float = 0.0) -> float:
    """
    Mesajın duygusal tonuna göre önem skorunu hesaplar.

    Args:
        emotion: Tespit edilen duygu türü
        confidence: Duygu tespitinin güven skoru (0-1)
        sentiment_direction: Duygu yönü (-1 negatif, +1 pozitif)

    Returns:
        Duygu skoru (0.0-0.3)
    """
    if not emotion or confidence < 0.4:
        return 0.0

    # Yüksek arousal içeren duygular
    high_arousal_emotions = ["öfke", "heyecan", "korku", "şaşkınlık", "coşku",
                             "umut", "üzüntü", "özgürlük", "endişe", "sevinç"]

    score = 0.0

    # Eğer duygu yüksek arousal içeriyorsa
    if emotion.lower() in high_arousal_emotions:
        score += 0.1 + (confidence * 0.1)  # Maksimum 0.2 ek puan

    # Duygu yönü çok güçlüyse (pozitif veya negatif)
    if abs(sentiment_direction) > 0.7:
        score += 0.1

    return min(score, 0.3)


def length_score(prompt: str) -> float:
    """
    Mesaj uzunluğuna göre önem skorunu hesaplar.

    Args:
        prompt: Kullanıcının mesajı

    Returns:
        Uzunluk skoru (0.0-0.2)
    """
    # Çok kısa mesajlar önemsiz olabilir
    if len(prompt) < 20:
        return 0.0

    # Uzun mesajlar daha önemli olabilir, ancak bir limite kadar
    return min(len(prompt) / 500, 0.2)


def memory_overlap_score(prompt: str, response: str, retrieved_memories=None) -> float:
    """
    Mevcut konuşmanın önceki anılarla benzerliğine göre önem skorunu hesaplar.

    Args:
        prompt: Kullanıcının mesajı
        response: Vira'nın yanıtı
        retrieved_memories: Geçmiş bellek öğeleri listesi

    Returns:
        Hafıza örtüşme skoru (0.0-0.3)
    """
    if not retrieved_memories:
        return 0.0

    score = 0.0
    combined_text = prompt + " " + response

    # Basit eşleşme kontrolü (gerçek uygulamada cosine benzerliği daha uygun olabilir)
    for memory in retrieved_memories:
        if "content" in memory:
            # Basit bir kelime örtüşmesi kontrolü
            memory_content = memory.get("content", "")
            common_words = set(combined_text.lower().split()) & set(memory_content.lower().split())

            # Eğer belirli sayıda ortak kelime varsa, skoru artır
            if len(common_words) > 3:  # Arbitrary threshold
                score += 0.1

    return min(score, 0.3)