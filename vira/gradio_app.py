#!/usr/bin/env python3
"""
Vira Gradio - LangGraph tabanlı web arayüzü
"""
import gradio as gr
import requests
import uuid
import os
from datetime import datetime

# API URL (değiştirebilirsiniz)
API_URL = os.getenv("VIRA_API_URL", "http://localhost:8000")

# Kullanıcı ID'si
user_id = str(uuid.uuid4())


def check_api_health():
    """API sağlık kontrolü"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            return "✅ API bağlantısı kuruldu"
        else:
            return f"❌ API hatası: {response.status_code}"
    except Exception as e:
        return f"❌ API bağlantısı kurulamadı: {e}"


def chat_with_vira(message, history):
    """Vira ile sohbet et"""
    # Boş mesaj kontrolü
    if not message or not message.strip():
        return history

    try:
        # API'ye istek gönder
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "user_id": user_id,
                "message": message.strip()  # Mesajı temizle
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            ai_response = data["response"]

            # Yeni mesaj çiftini history'ye ekle ve history'yi döndür
            history = history + [(message, ai_response)]
            return history
        else:
            error_msg = f"API hatası: {response.status_code} - {response.text}"
            history = history + [(message, error_msg)]
            return history

    except Exception as e:
        error_msg = f"İstek sırasında hata oluştu: {e}"
        history = history + [(message, error_msg)]
        return history


def reset_conversation():
    """Yeni bir oturum başlat"""
    global user_id
    user_id = str(uuid.uuid4())
    return None, []  # Temizle


# Gradio arayüzü
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.Markdown("# 🤖 Vira AI Asistan")
    gr.Markdown("LangGraph tabanlı, uzun süreli hafızaya sahip yapay zeka asistanı")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=500,
                show_label=False,
            )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Vira ile konuşmak için bir şeyler yazın...",
                    container=False,
                    scale=9,
                    show_label=False,  # Label'ı kaldır
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
            - Omega protokolü

            **Kullanım:**
            - Herhangi bir konuda sohbet edebilirsiniz
            - Vira önceki konuşmalarınızı hatırlayacaktır
            - "0427" yazarak Omega protokolünü etkinleştirebilirsiniz
            """)

            gr.Markdown(f"**Oturum ID:** {user_id[:8]}...")
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
    )

    submit_btn.click(
        chat_with_vira,
        [msg, chatbot],
        [chatbot]
    ).then(
        lambda: None,  # Mesaj kutusunu temizle
        None,
        [msg]
    )

    clear_btn.click(reset_conversation, outputs=[msg, chatbot])

# Uygulamayı çalıştır
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Güvenlik için paylaşımı kapalı tut
    )