#!/usr/bin/env python3
"""
Vira Gradio - LangGraph tabanlı gelişmiş web arayüzü
"""
import gradio as gr
import requests
import uuid
import os
import json
import time
from datetime import datetime
from typing import List, Tuple, Optional

# API URL (değiştirebilirsiniz)
API_URL = os.getenv("VIRA_API_URL", "http://localhost:8000")

# Konuşma geçmişi için dosya yolu
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "../data/history")
os.makedirs(HISTORY_DIR, exist_ok=True)


# Kullanıcı işlemleri
def get_or_create_user_id() -> str:
    """Kullanıcı ID'sini al veya oluştur"""
    # Kullanıcı ID'si için bir cookie dosyası
    cookie_file = os.path.join(HISTORY_DIR, "user_cookie.json")

    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("user_id", str(uuid.uuid4()))
        except:
            pass

    # Cookie yoksa yeni ID oluştur
    user_id = str(uuid.uuid4())
    try:
        with open(cookie_file, "w", encoding="utf-8") as f:
            json.dump({"user_id": user_id}, f)
    except:
        pass

    return user_id


# Kullanıcı ID'si
user_id = get_or_create_user_id()


def save_conversation_history(history: List[Tuple[str, str]]) -> None:
    """Konuşma geçmişini kaydet"""
    if not history:
        return

    history_file = os.path.join(HISTORY_DIR, f"{user_id}.json")
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Konuşma geçmişi kaydedilirken hata: {e}")


def load_conversation_history() -> List[Tuple[str, str]]:
    """Konuşma geçmişini yükle"""
    history_file = os.path.join(HISTORY_DIR, f"{user_id}.json")
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Konuşma geçmişi yüklenirken hata: {e}")

    return []


def check_api_health() -> str:
    """API sağlık kontrolü"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            return "✅ API bağlantısı kuruldu"
        else:
            return f"❌ API hatası: {response.status_code}"
    except Exception as e:
        return f"❌ API bağlantısı kurulamadı: {e}"


def chat_with_vira(message: str, history: List[Tuple[str, str]], progress=gr.Progress()) -> List[Tuple[str, str]]:
    """Vira ile sohbet et"""
    # Boş mesaj kontrolü
    if not message or not message.strip():
        return history

    progress(0.1, desc="İstek gönderiliyor...")

    try:
        # API'ye istek gönder
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "user_id": user_id,
                "message": message.strip()
            },
            timeout=60
        )

        progress(0.7, desc="Yanıt alınıyor...")

        if response.status_code == 200:
            data = response.json()
            ai_response = data["response"]

            # İşlem süresini hesapla
            elapsed = round(time.time() - start_time, 2)
            print(f"Yanıt süresi: {elapsed}s")

            # Yeni mesaj çiftini history'ye ekle ve history'yi döndür
            history = history + [(message, ai_response)]

            # Geçmişi kaydet
            save_conversation_history(history)

            progress(1.0, desc="Tamamlandı")
            return history
        else:
            error_msg = f"API hatası: {response.status_code} - {response.text}"
            history = history + [(message, error_msg)]
            save_conversation_history(history)
            return history

    except Exception as e:
        error_msg = f"İstek sırasında hata oluştu: {e}"
        history = history + [(message, error_msg)]
        save_conversation_history(history)
        return history


def reset_conversation() -> Tuple[str, List[Tuple[str, str]]]:
    """Yeni bir oturum başlat"""
    global user_id
    user_id = str(uuid.uuid4())

    # Kullanıcı ID'sini güncelle
    cookie_file = os.path.join(HISTORY_DIR, "user_cookie.json")
    try:
        with open(cookie_file, "w", encoding="utf-8") as f:
            json.dump({"user_id": user_id}, f)
    except:
        pass

    # Konuşma geçmişini temizle
    save_conversation_history([])

    return None, []


# Özel CSS
css = """
.chatbot {
    border: 1px solid #E5E7EB;
    border-radius: 0.5rem;
}
.user-message {
    background-color: #EFF6FF !important; 
    color: #1E40AF !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem !important;
    margin-bottom: 0.5rem !important;
}
.bot-message {
    background-color: #F9FAFB !important;
    color: #1F2937 !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem !important;
    margin-bottom: 0.5rem !important;
}
.message-box {
    border-radius: 0.375rem !important;
}
footer {
    display: none !important;
}
"""

# Gradio arayüzü
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue"), css=css) as demo:
    # Oturum bilgisini yükle
    conversation_history = load_conversation_history()

    gr.Markdown("# 🤖 Vira AI Asistan")
    gr.Markdown("LangGraph tabanlı, uzun süreli hafızaya sahip yapay zeka asistanı")

    with gr.Row():
        with gr.Column(scale=3):
            # Gradio 4.19.2 ile uyumlu chatbot parametreleri
            chatbot = gr.Chatbot(
                value=conversation_history,
                height=500,
                show_label=False,
                elem_classes="chatbot",
                elem_id="chat-box"
            )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Vira ile konuşmak için bir şeyler yazın... (Örn: Merhaba, sen kimsin?)",
                    container=False,
                    scale=9,
                    show_label=False,
                    autofocus=True,
                    elem_classes="message-box"
                )
                submit_btn = gr.Button("Gönder", variant="primary", scale=1)

            with gr.Row():
                clear_btn = gr.Button("Yeni Oturum", variant="secondary")
                api_status = gr.Textbox(
                    value=check_api_health(),
                    label="API Durumu",
                    interactive=False
                )

        with gr.Column(scale=1):
            gr.Markdown("### Hakkında")
            gr.Markdown("""
            **Vira AI Asistan**, uzun süreli hafızası olan, LangGraph tabanlı bir yapay zeka asistanıdır.

            **Özellikler:**
            - Uzun süreli hafıza
            - Duygu analizi
            - Niyet algılama
            - Omega protokolü

            **Kullanım:**
            - Herhangi bir konuda sohbet edebilirsiniz
            - Vira önceki konuşmalarınızı hatırlayacaktır
            - Sayfa yenilense bile konuşma geçmişi korunur
            - "0427" yazarak Omega protokolünü etkinleştirebilirsiniz
            """)

            gr.Markdown(f"**Oturum ID:** {user_id[:8]}...")

            # Son güncelleme zamanı
            update_time = gr.Markdown(f"*Son güncelleme: {datetime.now().strftime('%H:%M:%S')}*")

            gr.Markdown(f"© {datetime.now().year} Vira AI")

    # Etkileşimler
    msg.submit(
        chat_with_vira,
        [msg, chatbot],
        [chatbot],
        api_name="chat"  # API endpoint adı
    ).then(
        lambda: None,  # Mesaj kutusunu temizle
        None,
        [msg]
    ).then(
        lambda: f"*Son güncelleme: {datetime.now().strftime('%H:%M:%S')}*",
        None,
        [update_time]
    )

    submit_btn.click(
        chat_with_vira,
        [msg, chatbot],
        [chatbot]
    ).then(
        lambda: None,  # Mesaj kutusunu temizle
        None,
        [msg]
    ).then(
        lambda: f"*Son güncelleme: {datetime.now().strftime('%H:%M:%S')}*",
        None,
        [update_time]
    )

    clear_btn.click(reset_conversation, outputs=[msg, chatbot]).then(
        lambda: f"*Son güncelleme: {datetime.now().strftime('%H:%M:%S')}*",
        None,
        [update_time]
    )

    # Periyodik güncelleme için JavaScript (otomatik sağlık kontrolü)
    demo.load(
        fn=check_api_health,
        inputs=None,
        outputs=api_status,
        js="async () => {setInterval(() => document.getElementById('refresh-btn').click(), 30000);}"
    )
    # Gizli yenileme düğmesi
    refresh_btn = gr.Button("Yenile", elem_id="refresh-btn", visible=False)
    refresh_btn.click(fn=check_api_health, inputs=None, outputs=api_status)

# Uygulamayı çalıştır
if __name__ == "__main__":
    print("Vira Gradio arayüzü başlatılıyor...")
    print(f"Gradio sürümü: {gr.__version__}")
    print(f"Konuşma geçmişi dizini: {HISTORY_DIR}")
    print(f"API URL: {API_URL}")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Güvenlik için paylaşımı kapalı tut
        show_error=True
    )