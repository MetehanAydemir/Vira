from typing import List, TypedDict, Optional, Dict, Any, Union
from langchain_core.messages import BaseMessage


class ViraState(TypedDict, total=False):
    """
    Grafımızın durumunu temsil eder.

    Attributes:
        user_id: Kullanıcı için benzersiz tanımlayıcı.
        original_message: Kullanıcıdan gelen ilk mesaj.
        processed_input: Sensory proxy mantığından gelen analiz edilmiş girdiyi içeren sözlük.
        memory_context: Veritabanından alınan ilgili anıları içeren bir dize.
        messages: LLM'e geçirilecek mesajların listesi.
        response: Yapay zeka tarafından üretilen nihai yanıt.
        is_omega_command: Girdinin özel bir komut olup olmadığını belirten bir boolean bayrağı.
        importance_score: Hafızanın önem skoru (0.0-1.0 arası).
        importance_score_reasons: Önem skorunun sebepleri.
        should_promote_to_long_term: Uzun süreli hafızaya yükseltilmeli mi?
        memory_threshold_used: Kullanılan hafıza eşiği.
        memory_type: Hafıza tipi (semantic_analyze'dan gelen).
        memory_saved: Hafızanın kaydedilip kaydedilmediği.
        session_id: Oturum kimliği.
        interaction_id: Etkileşim kimliği.
        short_memory_id: Kısa süreli hafıza kimliği.
        long_memory_id: Uzun süreli hafıza kimliği.
        dynamic_personality: Dinamik kişilik özellikleri.
    """
    user_id: str
    original_message: str
    processed_input: Dict[str, Any]
    memory_context: Optional[str] = None
    messages: List[BaseMessage]
    response: str
    is_omega_command: bool

    # Hafıza ile ilgili alanlar
    importance_score: Optional[float] = None
    importance_score_reasons: Optional[List[str]] = None
    should_promote_to_long_term: Optional[bool] = None
    memory_threshold_used: Optional[float] = None
    memory_type: Optional[str] = None

    # Save memory ile ilgili alanlar
    memory_saved: Optional[bool] = None
    session_id: Optional[str] = None
    interaction_id: Optional[str] = None
    short_memory_id: Optional[str] = None
    long_memory_id: Optional[str] = None
    unified_user_model: Dict[str, Any] = None
    # Kişilik ile ilgili
    dynamic_personality: Optional[Dict[str, float]] = None

    def has_unified_user_model(self):
        """
        State içinde birleşik kullanıcı modeli olup olmadığını kontrol eder.

        Returns:
            bool: Birleşik kullanıcı modeli varsa True, yoksa False
        """
        return "unified_user_model" in self

    def get_unified_user_model(self):
        """
        State içindeki birleşik kullanıcı modelini döndürür.

        Returns:
            dict: Birleşik kullanıcı modeli
            None: Model yoksa None döner
        """
        return self.get("unified_user_model", None)