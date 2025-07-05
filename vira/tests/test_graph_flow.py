import pytest
from unittest.mock import patch

# Test edilecek ana uygulama grafiği
from vira.graph.build import app

# --- Test Senaryoları ---

@patch("vira.graph.build.handle_omega_node")
@patch("vira.graph.build.retrieve_memory_node")
def test_omega_command_flow(retrieve_mock, omega_mock):
    """'0427' komutu girildiğinde akışın doğru bir şekilde omega dalına gitmesini test eder."""
    print("\n--- Test: Omega Komut Akışı ---")
    # Girdiyi hazırla
    inputs = {
        "user_id": "test_user",
        "original_message": "0427"
    }

    # Grafı çalıştır
    # stream() yerine invoke() kullanarak son durumu tek seferde alıyoruz
    app.invoke(inputs)

    # Doğrulamalar
    # 1. handle_omega_node çağrılmalı
    omega_mock.assert_called_once()
    print("Doğrulandı: handle_omega_node çağrıldı.")

    # 2. retrieve_memory_node çağrılmamalı
    retrieve_mock.assert_not_called()
    print("Doğrulandı: retrieve_memory_node çağrılmadı.")


@patch("vira.graph.build.save_memory_node")
@patch("vira.graph.build.generate_response_node")
@patch("vira.graph.build.prepare_prompt_node")
@patch("vira.graph.build.retrieve_memory_node")
@patch("vira.graph.build.handle_omega_node")
def test_normal_chat_flow(omega_mock, retrieve_mock, prepare_mock, generate_mock, save_mock):
    """Normal bir mesaj girildiğinde akışın standart sohbet zincirini takip etmesini test eder."""
    print("\n--- Test: Normal Sohbet Akışı ---")
    # Girdiyi hazırla
    inputs = {
        "user_id": "test_user",
        "original_message": "Merhaba Vira, nasılsın?"
    }

    # Mock'ların dönüş değerlerini ayarla ki akış devam edebilsin
    retrieve_mock.return_value = {"memory_context": "Bir anı bulundu."}
    prepare_mock.return_value = {"messages": []} # İçerik önemli değil, sadece var olması yeterli
    generate_mock.return_value = {"response": "Ben iyiyim, teşekkürler!"}

    # Grafı çalıştır
    app.invoke(inputs)

    # Doğrulamalar
    # 1. handle_omega_node çağrılmamalı
    omega_mock.assert_not_called()
    print("Doğrulandı: handle_omega_node çağrılmadı.")

    # 2. Standart akıştaki tüm düğümler birer kez çağrılmalı
    retrieve_mock.assert_called_once()
    print("Doğrulandı: retrieve_memory_node çağrıldı.")
    prepare_mock.assert_called_once()
    print("Doğrulandı: prepare_prompt_node çağrıldı.")
    generate_mock.assert_called_once()
    print("Doğrulandı: generate_response_node çağrıldı.")
    save_mock.assert_called_once()
    print("Doğrulandı: save_memory_node çağrıldı.")
