"""
Kullanıcı için birleşik mental model oluşturan düğüm.
"""

from vira.graph.state import ViraState
from vira.metacognition.engine import MetaCognitiveEngine
from vira.db.repository import UserRepository, MemoryRepository, PersonalityRepository

def build_mental_model_node(state: ViraState) -> ViraState:
    """
    Kullanıcı için birleşik zihinsel model oluşturur.

    Bu düğüm, tüm hafıza sistemlerinden (LongTerm, ShortTerm, Personality, Interaction)
    veri toplayarak bütünsel bir kullanıcı anlayışı oluşturur.

    Args:
        state: Vira sistem durumu

    Returns:
        Güncellenmiş sistem durumu
    """
    new_state = ViraState(state)
    # Kullanıcı kimliğini al
    user_id = state.get("user_id")

    if not user_id:
        # Kullanıcı kimliği yoksa, model oluşturulamaz
        return state

    # Repository'leri doğrudan oluştur
    db_repos = {
        "user_repo": UserRepository(),
        "memory_repo": MemoryRepository(),
        "personality_repo": PersonalityRepository()
    }

    # MetaCognitive engine'i oluştur
    engine = MetaCognitiveEngine(db_repos)

    # Zaman penceresini ayarla (varsayılan: son 7 gün)
    time_window = {
        "days": 7,       # Son durum için
        "trend_days": 90 # Eğilimler için
    }

    # Kullanıcı modeli oluştur
    user_model = engine.build_unified_user_model(user_id, time_window)

    # Modeli dict formatına dönüştür ve state'e ekle
    state["unified_user_model"] = user_model.to_dict()
    
    return state