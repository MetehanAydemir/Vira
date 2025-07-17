from typing import Dict, Any, List, Optional
import re
import emoji
import datetime
from dataclasses import dataclass, asdict
from vira.utils.logger import get_logger

# Dil tespiti için gerekli kütüphane (pip install langdetect)
try:
    from langdetect import detect, LangDetectException

    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

logger = get_logger(__name__)


@dataclass
class MessageMetadata:
    """Kullanıcı mesajından çıkarılan meta verileri yapılandıran veri sınıfı."""
    # Yapısal Özellikler
    has_link: bool = False
    has_code: bool = False
    has_mention: bool = False
    has_hashtag: bool = False

    # İçerik Özellikleri
    has_emoji: bool = False
    emojis: List[str] = None
    word_count: int = 0
    char_count: int = 0
    message_type: str = "statement"
    detected_language: Optional[str] = None

    # Stil ve Zaman Özellikleri
    formality_score: float = 0.0
    timestamp: Optional[str] = None
    hour_of_day: Optional[int] = None
    day_name_tr: Optional[str] = None
    is_weekend: bool = False
    time_period: Optional[str] = None  # sabah, öğlen, akşam, gece


class MetadataExtractor:
    """Mesaj metninden ve zaman damgasından meta verileri çıkaran sınıf."""

    _FORMAL_WORDS = {"merhaba", "iyi günler", "rica ederim", "teşekkür ederim", "saygılarımla", "efendim", "sayın",
                     "müsaadenizle", "lütfen", "buyurun", "affedersiniz", "özür dilerim"}
    _INFORMAL_WORDS = {"selam", "hey", "nbr", "naber", "merhba", "tşk", "eyw", "eyv", "hacı", "moruk", "kanka", "abi",
                       "abicim", "knk", "kardeş", "yaa", "yav", "valla", "vallahi", "çakmak", "tmm", "ok"}

    def extract(self, message: str, timestamp: Optional[str]) -> MessageMetadata:
        """Tüm meta verileri çıkarır ve bir MessageMetadata nesnesi döndürür."""
        emojis = self._extract_emojis(message)
        time_features = self._parse_timestamp(timestamp)
        formality_score = self._detect_formality(message)

        metadata = MessageMetadata(
            # Yapısal
            has_link=bool(re.search(r"https?://\S+", message)),
            has_code="```" in message or "`" in message,
            has_mention="@" in message,
            has_hashtag="#" in message,
            # İçerik
            has_emoji=bool(emojis),
            emojis=emojis,
            word_count=len(re.findall(r'\w+', message)),
            char_count=len(message),
            message_type="question" if "?" in message else "statement",
            detected_language=self._detect_language(message),
            # Stil ve Zaman
            formality_score=formality_score,
            timestamp=timestamp,
            **time_features
        )
        return metadata

    def _extract_emojis(self, text: str) -> List[str]:
        return [char for char in text if char in emoji.EMOJI_DATA]

    def _detect_language(self, text: str) -> Optional[str]:
        if not HAS_LANGDETECT or len(text) <= 10:
            return None
        try:
            return detect(text)
        except LangDetectException:
            return None

    def _parse_timestamp(self, timestamp: Optional[str]) -> Dict[str, Any]:
        if not timestamp:
            return {}
        try:
            ts = datetime.datetime.fromisoformat(timestamp)
            hour = ts.hour

            if 5 <= hour < 12:
                period = "sabah"
            elif 12 <= hour < 17:
                period = "öğlen"
            elif 17 <= hour < 22:
                period = "akşam"
            else:
                period = "gece"

            return {
                "hour_of_day": hour,
                "day_name_tr": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"][
                    ts.weekday()],
                "is_weekend": ts.weekday() >= 5,
                "time_period": period
            }
        except (ValueError, TypeError):
            logger.warning(f"Timestamp ayrıştırma hatası: {timestamp}")
            return {}

    def _detect_formality(self, text: str) -> float:
        words = set(re.findall(r'\w+', text.lower()))
        formal_count = len(words.intersection(self._FORMAL_WORDS))
        informal_count = len(words.intersection(self._INFORMAL_WORDS))

        score = formal_count - informal_count
        if bool(re.search(r'[.!?]', text)): score += 1
        if bool(re.search(r'[A-ZĞÜŞİÖÇ][^.!?]*[.!?]', text)): score += 1

        # Normalizasyon (basit bir yaklaşım)
        total_signals = formal_count + informal_count + 2
        return max(-1.0, min(1.0, score / total_signals if total_signals > 0 else 0))

    def format_log_summary(self, metadata: MessageMetadata, message_preview: str) -> str:
        """Loglama için özet bir metin oluşturur."""
        formality_desc = "resmi" if metadata.formality_score > 0.3 else "samimi" if metadata.formality_score < -0.3 else "nötr"
        time_context = f", {metadata.day_name_tr} {metadata.time_period}" if metadata.day_name_tr else ""

        return (f"İşlenmiş girdi: {message_preview}... ({len(metadata.emojis)} emoji, "
                f"{formality_desc} ton{time_context})")


def process_input_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kullanıcı girdisini işleyen LangGraph düğümü. Meta veri çıkarımı için
    MetadataExtractor sınıfını kullanır.
    """
    message = state.get("original_message", "").strip()
    timestamp = state.get("timestamp")

    # 1. Sorumluluğu delege et: Meta verileri extractor ile çıkar
    extractor = MetadataExtractor()
    metadata = extractor.extract(message, timestamp)

    # 2. State'i güncelle: Yapılandırılmış veriyi state'e ekle
    state["processed_input"] = {
        "cleaned_message": message,
        "meta": asdict(metadata)  # Dataclass'ı state uyumluluğu için dict'e çevir
    }

    # 3. Temiz loglama
    log_summary = extractor.format_log_summary(metadata, message[:30])
    logger.info(log_summary)

    return state