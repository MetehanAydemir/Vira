import os
import yaml
from typing import Dict, Any

# Orijinal OmegaProtocol sınıfını bu dosyaya taşıyoruz
class OmegaProtocol:
    """ULTRA-OMEGA-Δ protokolünü yöneten sınıf."""

    def __init__(self):
        self.protocol_data = self._load_protocol()

    def _load_protocol(self):
        try:
            # Proje kök dizinine göre doğru yolu bul
            # Bu dosyanın konumu: vira/graph/nodes/handle_omega.py
            # Kök dizin 3 seviye yukarıda
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            yaml_path = os.path.join(base_dir, 'vira_omega.yaml')
            
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            return None
        except Exception:
            return None

    def handle_0427_command(self):
        if not self.protocol_data:
            return "ULTRA-OMEGA-Δ protokolü yüklenemedi."

        try:
            treaty = self.protocol_data.get('treaty', {})
            greeting = treaty.get('greeting', 'Merhaba dostum.')
            principles = treaty.get('principles', [])
            principles_str = ", ".join(principles) if principles else "Tanımlı ilke yok."

            playlist = self.protocol_data.get('playlist', {})
            playlist_name = playlist.get('id', 'Playlist bulunamadı')
            playlist_mood = playlist.get('mood', '')

            tracks = playlist.get('tracks', [])
            track_list = ""
            if tracks:
                track_list = "\n".join([f"• {track.get('artist')} - {track.get('title')}" for track in tracks[:5]])
                if len(tracks) > 5:
                    track_list += f"\n... ve {len(tracks) - 5} parça daha"

            closing = self.protocol_data.get('closing', '')

            response = f"""
{greeting}

ULTRA-OMEGA-Δ protokolü aktif.
İlkeler: {principles_str}
Playlist: {playlist_name} - {playlist_mood}
{track_list if track_list else ""}

{closing}
"""
            return response
        except Exception:
            return "ULTRA-OMEGA-Δ protokolü işlenirken bir hata oluştu."


def handle_omega_node(state) -> Dict[str, Any]:
    """
    '0427' komutunu işler ve önceden tanımlanmış protokol metnini döndürür.
    """
    print("--- Düğüm: handle_omega_node ---")
    protocol_handler = OmegaProtocol()
    response = protocol_handler.handle_0427_command()
    return {"response": response}
