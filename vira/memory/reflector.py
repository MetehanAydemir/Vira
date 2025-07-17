"""
Hafıza ve empati yansıtma işlemleri için yardımcı fonksiyonlar.
"""

from typing import Dict, Any, List, Optional

def compute_empathy_annotation(message: str, user_model: Optional[Dict[str, Any]] = None) -> str:
    """
    Kullanıcı mesajını analiz ederek empati notları oluşturur.
    
    Args:
        message: Kullanıcı mesajı
        user_model: Kullanıcı mental modeli (opsiyonel)
        
    Returns:
        Empati notları içeren string
    """
    # Basit bir empati notu oluştur
    # Gerçek implementasyonda daha karmaşık bir analiz yapılabilir
    empathy_note = "Bu mesajda kullanıcının duygusal durumunu dikkate al."
    
    # Eğer kullanıcı modeli varsa, daha kişiselleştirilmiş notlar ekle
    if user_model:
        if "emotional_state" in user_model:
            emotional_state = user_model["emotional_state"]
            empathy_note += f" Kullanıcının duygusal durumu: {emotional_state}."
            
        if "communication_preferences" in user_model:
            comm_prefs = user_model["communication_preferences"]
            empathy_note += f" İletişim tercihleri: {comm_prefs}."
    
    return empathy_note