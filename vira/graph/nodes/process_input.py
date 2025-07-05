from datetime import datetime
from typing import Dict, Any

from vira.graph.state import ViraState

def process_input_node(state: ViraState) -> Dict[str, Any]:
    """
    Kullanıcı girdisini analiz eder, duygu/niyet çıkarır ve özel komutları tespit eder.
    Bu düğüm, orijinal koddaki SensoryProxy'nin işlevini taklit eder.
    """
    user_message = state["original_message"]
    user_id = state["user_id"]

    # Orijinal ChatMessageInput.analyze() mantığını buraya taşı
    text = user_message.lower().strip()
    emotion = "Sakin"  # Varsayılan duygu
    metadata = {}

    # Duygu/niyet anahtar kelime kümeleri
    curiosity_keywords = ['?', 'nasıl', 'neden', 'hangi', 'kim', 'ne zaman', 'nerede']
    supportive_keywords = ['teşekkür', 'harika', 'iyi iş', 'mükemmel', 'tebrik', 'sevgili', 'beğendim', 'seviyorum']
    anxious_keywords = ['zor', 'problem', 'korkuyorum', 'anlamıyorum', 'endişe', 'kötü', 'üzgün', 'zorlanıyorum']
    motivational_keywords = ['yapabilirsin', 'dene', 'bence', 'olabilir', 'harika olur', 'başarabilirsin', 'güzel fikir', 'devam et']
    reflective_keywords = ['düşünmek', 'aklıma geldi', 'belki', 'önemli', 'fikir', 'öneri', 'gözlem']
    neutral_keywords = ['merhaba', 'selam', 'tamam', 'peki', 'evet', 'hayır']

    # Duygu ataması
    if not text:
        emotion = "Belirsiz"
    elif any(word in text for word in curiosity_keywords):
        emotion = "Meraklı"
    elif any(word in text for word in supportive_keywords):
        emotion = "Destekleyici"
    elif any(word in text for word in anxious_keywords):
        emotion = "Endişeli"
    elif any(word in text for word in motivational_keywords):
        emotion = "Motivasyonel"
    elif any(word in text for word in reflective_keywords):
        emotion = "Yansıtıcı"
    elif any(word in text for word in neutral_keywords):
        emotion = "Nötr"
    else:
        emotion = "Sakin"

    # Metadata güncellemeleri
    metadata['contains_question'] = any(q in text for q in curiosity_keywords)
    metadata['length'] = len(text)

    # İşlenmiş girdi verisini oluştur
    processed_input_data = {
        'content': user_message,
        'timestamp': datetime.now().isoformat(),
        'emotion': emotion,
        'user_id': user_id,
        'input_type': 'chat_message',
        'metadata': metadata
    }

    # Özel komut kontrolü
    is_omega_command = text == "0427"

    print(f"--- Düğüm: process_input_node ---")
    print(f"Duygu: {emotion}")
    print(f"Omega Komutu mu?: {is_omega_command}")

    return {
        "processed_input": processed_input_data,
        "is_omega_command": is_omega_command
    }
