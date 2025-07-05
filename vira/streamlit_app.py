#!/usr/bin/env python3
"""
Vira Streamlit - LangGraph tabanlı web arayüzü
"""
import streamlit as st
import requests
import uuid
import os
from datetime import datetime

# Sayfa yapılandırması
st.set_page_config(
    page_title="Vira AI Asistan",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Stil ekleme
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex;
    align-items: center;
}
.chat-message.user {
    background-color: #2b313e;
}
.chat-message.assistant {
    background-color: #475063;
}
.chat-message .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 1rem;
}
.chat-message .message {
    flex-grow: 1;
}
</style>
""", unsafe_allow_html=True)

# API URL (değiştirebilirsiniz)
API_URL = os.getenv("VIRA_API_URL", "http://localhost:8000")

# Oturum durumunu başlat
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Başlık
st.title("Vira AI Asistan 🤖")

# Sidebar
with st.sidebar:
    st.header("Hakkında")
    st.info("""
    **Vira AI Asistan**
    
    Vira, uzun süreli hafızası olan, LangGraph tabanlı bir yapay zeka asistanıdır.
    
    Özellikler:
    - Uzun süreli hafıza
    - Duygu analizi
    - Omega protokolü
    """)
    
    st.header("Ayarlar")
    if st.button("Yeni Oturum"):
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.success("Yeni oturum başlatıldı!")
    
    st.text(f"Oturum ID: {st.session_state.user_id[:8]}...")
    
    st.header("Bağlantı")
    api_url = st.text_input("API URL", value=API_URL)
    
    # API sağlık kontrolü
    try:
        response = requests.get(f"{api_url}/health", timeout=2)
        if response.status_code == 200:
            st.success("API bağlantısı kuruldu ✅")
        else:
            st.error(f"API hatası: {response.status_code}")
    except Exception as e:
        st.error(f"API bağlantısı kurulamadı: {e}")

# Mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
prompt = st.chat_input("Vira ile konuşmak için bir şeyler yazın...")

if prompt:
    # Kullanıcı mesajını göster
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Mesajı kaydet
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # API'ye istek gönder
    with st.spinner("Vira düşünüyor..."):
        try:
            response = requests.post(
                f"{api_url}/chat",
                json={"user_id": st.session_state.user_id, "message": prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                ai_response = response.json()["response"]
                memory_context = response.json().get("memory_context", "")
                
                # Asistan yanıtını göster
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
                
                # Yanıtı kaydet
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # Eğer hafıza bağlamı varsa, bunu expander içinde göster
                if memory_context:
                    with st.expander("Hafıza Bağlamı"):
                        st.markdown(memory_context)
            else:
                st.error(f"API hatası: {response.status_code} - {response.text}")
        
        except Exception as e:
            st.error(f"İstek sırasında hata oluştu: {e}")

# Footer
st.markdown("---")
st.markdown(f"© {datetime.now().year} Vira AI | LangGraph tabanlı AI Asistan")