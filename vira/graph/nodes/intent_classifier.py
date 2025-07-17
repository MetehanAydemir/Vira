from typing import Dict, Any, List
from vira.graph.state import ViraState
from vira.config import settings
from vira.utils.logger import get_logger
from vira.utils.llm_client import call_chat_model
from vira.metacognition.engine import MetaCognitiveEngine
import re

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
            "command": "Emir, doğrudan talimat. Örnek: 'Müzik çal', 'Işıkları kapat', 'Dosyayı sil'",
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

        intent_descriptions_formatted = "\n".join([f"- **{intent}**: {desc}" for intent, desc in intent_descriptions.items()])

        prompt = f"""
## GÖREV
Kullanıcının son mesajının niyetini, konuşma geçmişini dikkate alarak sınıflandır.

## KONUŞMA BAĞLAMI
{history_str if history_str else "Konuşma geçmişi yok."}
---
Kullanıcı Mesajı: "{message}"
---

## SINIFLANDIRMA KRİTERLERİ
{intent_descriptions_formatted}

## ANALİZ SÜRECİ (Adım Adım Düşün)
1.  **Mesajın Tonu ve Fiili:** Mesajın ana eylemi ne? (istemek, sormak, emretmek, söylemek). Tonu nazik mi, doğrudan mı, yoksa duygusal mı?
2.  **Temel Farklar:**
    *   `command` (dosyayı sil) vs `request` (dosyayı silebilir misin?).
    *   `question` (Ankara'nın nüfusu kaç?) vs `opinion` (Sence en iyi film hangisi?).
    *   `information` (Bana kuantum fiziğini anlat) vs `philosophical` (Zaman nedir?).
    *   `identity_probe` özellikle Vira'nın kimliği, doğası veya varlığıyla ilgili olmalıdır.
3.  **Karar:** Bu analizlere dayanarak, yukarıdaki listeden en uygun TEK bir niyet kategorisi seç.

## ÇIKTI FORMATI
Analizini yaptıktan sonra, kararını SADECE aşağıdaki formatta ver. Başka hiçbir metin ekleme.
<intent>niyet_burada</intent>
"""

        # LLM istemcisini kullanarak çağrı yap
        messages = [
            {"role": "system",
             "content": "Sen, kullanıcı girdilerini analiz eden ve önceden tanımlanmış niyet kategorilerine göre sınıflandıran bir uzmansın. Görevin, analizini yaptıktan sonra sonucu `<intent>...</intent>` etiketleri içinde, tek bir kelime olarak sunmaktır."},
            {"role": "user", "content": prompt}
        ]

        response = call_chat_model(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=50
        )

        # Yanıtı işleme - daha esnek hale getirildi
        raw_response = response.strip().lower()
        logger.debug(f"LLM'den alınan ham yanıt: {raw_response}")

        # Özel durum: 0427 kodu varsa Omega intent'ini döndür
        if "0427" in message:
            logger.info("Omega protokolü kodu tespit edildi.")
            return IntentType.OMEGA

        # XML etiketlerini işleme - çeşitli format olasılıklarını ele al
        intent = raw_response

        # 1. <intent>niyet</intent> formatını işle
        intent_match = re.search(r'<intent>(.*?)</intent>', raw_response)
        if intent_match:
            intent = intent_match.group(1).strip()
            logger.debug(f"XML etiketleri arasından niyet çıkarıldı: {intent}")
        # 2. Basit metin işleme ile etiketleri temizlemeyi dene
        elif raw_response.startswith('<intent>') and raw_response.endswith('</intent>'):
            intent = raw_response.replace('<intent>', '').replace('</intent>', '').strip()
            logger.debug(f"String işleme ile niyet çıkarıldı: {intent}")
        # 3. Yalnızca geçerli niyet kelimelerini ara
        else:
            for valid_intent in VALID_INTENTS:
                if valid_intent in raw_response:
                    intent = valid_intent
                    logger.debug(f"Ham yanıttan geçerli niyet bulundu: {intent}")
                    break

        if intent in VALID_INTENTS:
            logger.info(f"LLM tarafından belirlenen niyet: {intent}")
            return intent
        else:
            logger.warning(
                f"LLM geçersiz bir niyet döndürdü: '{raw_response}' -> '{intent}'. Varsayılan olarak 'unknown' kullanılıyor.")
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
    new_state = ViraState(state)

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

    # [YENİ] MetaCognitive Engine entegrasyonu: Birleşik kullanıcı modeli kontrolü
    unified_model = None
    #TODO Meta Cognitive not completed.
    if (new_state['unified_user_model'] is not None) and (new_state['unified_user_model'] is None):
        unified_model = new_state['unified_user_model']
        logger.info("Birleşik kullanıcı modeli bulundu. MetaCognitive niyet geliştirmeleri etkinleştirildi.")

    # [YENİ] Eğer birleşik model mevcutsa, LLM isteklerini kişiselleştir
    if unified_model:
        # Kişilik eğilimleri ve tercihlerine göre LLM isteklerini ayarla
        # Örneğin: Mizahi kişilik profiline sahipse bunu LLM'e bildir
        personality_context = ""
        if unified_model.personality_trends.get("humor", {}).get("current", 0) > 0.7:
            personality_context = "Kullanıcı genellikle mizahi bir yaklaşımı tercih eder. "
        if unified_model.personality_trends.get("curiosity", {}).get("current", 0) > 0.7:
            personality_context += "Kullanıcı genellikle derin düşünmeyi ve keşfetmeyi tercih eder. "

        if personality_context:
            logger.debug(f"LLM'e kişilik bağlamı eklendi: {personality_context}")
            # Bu bilgiyi LLM çağrısında kullanmak için kodları buraya ekleyebiliriz
            # Şu an için sadece logluyoruz

    # Niyet belirleme
    if not message:
        logger.warning("Intent tespiti için mesaj bulunamadı. 'unknown' olarak ayarlandı.")
        intent = IntentType.UNKNOWN
    else:
        # Artık doğrudan LLM sınıflandırmasını kullan
        intent = call_llm_for_intent(message, history)

    # [YENİ] MetaCognitive Engine ile niyet geliştirme
    if unified_model and intent != IntentType.OMEGA:  # Omega komutları dokunulmaz kalır
        try:
            # MetaCognitive Engine oluştur
            engine = MetaCognitiveEngine()

            # Niyeti kullanıcı modeliyle geliştir
            enhanced_intent = engine.enhance_intent_classification(intent, unified_model)

            if enhanced_intent != intent:
                logger.info(f"Niyet MetaCognitive Engine ile geliştirildi: {intent} -> {enhanced_intent}")
                intent = enhanced_intent

            # [YENİ] Kişilik profiline göre belirsiz niyetleri geliştir
            if intent == IntentType.UNKNOWN:
                # Kişilik özelliklerine göre belirsiz niyetleri yorumla
                if unified_model.personality_trends.get("curiosity", {}).get("current", 0) > 0.7:
                    # Meraklı kişilik profili için belirsiz ifadeleri soru olarak yorumla
                    intent = IntentType.QUESTION
                    logger.debug("Belirsiz niyet, kişilik profiline göre 'question' olarak yorumlandı")
                elif unified_model.personality_trends.get("empathy", {}).get("current", 0) > 0.7:
                    # Empatik kişilik profili için belirsiz ifadeleri duygusal olarak yorumla
                    intent = IntentType.EMOTIONAL
                    logger.debug("Belirsiz niyet, kişilik profiline göre 'emotional' olarak yorumlandı")

            # [YENİ] Konuşma örüntülerine göre niyet düzeltmesi
            preferred_topics = unified_model.conversation_patterns.get("preferred_topics", [])
            if preferred_topics:
                # Kullanıcının tercih ettiği konuları kontrol et
                for topic in preferred_topics:
                    if topic.lower() in message.lower():
                        if "philosophical" in topic.lower() and intent == IntentType.INFORMATION:
                            intent = IntentType.PHILOSOPHICAL
                            logger.debug(f"Niyet, tercih edilen konu '{topic}' nedeniyle 'philosophical' olarak güncellendi")
                        elif "creative" in topic.lower() and intent in [IntentType.REQUEST, IntentType.INFORMATION]:
                            intent = IntentType.CREATIVE_REQUEST
                            logger.debug(f"Niyet, tercih edilen konu '{topic}' nedeniyle 'creative_request' olarak güncellendi")
                        # Diğer tema-niyet eşleştirmeleri eklenebilir

            # [YENİ] Duygu durumuna göre niyet zenginleştirme
            current_emotion = unified_model.current_state.get("emotional_state", {}).get("primary", "")
            if current_emotion:
                # Duygu durumunu niyet sınıflandırıcıya ekleyen mantık
                new_state["emotional_context"] = current_emotion
                logger.debug(f"Duygu durumu bağlamı eklendi: {current_emotion}")

        except Exception as e:
            logger.error(f"MetaCognitive niyet geliştirme sırasında hata: {e}", exc_info=True)

    # Processed input'u güncelle
    if "processed_input" not in new_state:
        new_state["processed_input"] = {}

    new_state["processed_input"]["intent"] = intent
    new_state["is_omega_command"] = (intent == IntentType.OMEGA)

    # [YENİ] MetaCognitive bilgileri ekle
    if unified_model:
        new_state["processed_input"]["metacognitive_context"] = {
            "personality_match": True,  # Niyet kişilik profiline uyumlu mu?
            "confidence_boost": unified_model.personality_trends.get(
                "assertiveness", {}).get("current", 0),  # Kendine güven seviyesi
            "emotional_state": unified_model.current_state.get("emotional_state", {}),
            "interaction_mode": unified_model.current_state.get("interaction_mode", "")
        }

    logger.info(f"Belirlenen niyet: {intent} (Mesaj: {message[:30]}...)")
    return new_state