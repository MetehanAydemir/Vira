#!/usr/bin/env python3
"""
Vira CLI - LangGraph tabanlı sohbet arayüzü
"""
import os
import sys
import argparse
from typing import List, Dict, Any

from vira.graph.build import app
from vira.db.engine import init_db
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)


def check_environment() -> bool:
    """
    Gerekli ortam değişkenlerinin ayarlanıp ayarlanmadığını kontrol eder.
    """
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME",
    ]

    missing = []
    for var in required_vars:
        if not getattr(settings, var):
            missing.append(var)

    if missing:
        print("HATA: Aşağıdaki gerekli ortam değişkenleri eksik:")
        for var in missing:
            print(f"  - {var}")
        return False

    return True


def init_database(force_recreate: bool = False) -> bool:
    """
    Veritabanını başlatır.
    """
    try:
        init_db(force_recreate=force_recreate)
        return True
    except Exception as e:
        logger.error(f"Veritabanı başlatılırken hata oluştu: {e}", exc_info=True)
        print(f"Veritabanı hatası: {e}")
        return False


def run_chat_loop():
    """
    Komut satırı sohbet döngüsünü başlatır.
    """
    print("\n" + "=" * 50)
    print("Vira LangGraph CLI v1.0")
    print("Çıkmak için 'exit' veya 'quit' yazın.")
    print("=" * 50 + "\n")

    user_id = os.getenv("VIRA_USER_ID", "cli_user")

    while True:
        try:
            # Kullanıcı girdisini al
            user_input = input("\nSen: ")

            # Çıkış kontrolü
            if user_input.lower() in ["exit", "quit", "çıkış"]:
                print("\nGörüşmek üzere!")
                break

            # Boş girdi kontrolü
            if not user_input.strip():
                continue

            # Başlangıç durumunu hazırla
            initial_state = {
                "user_id": user_id,
                "original_message": user_input,
                "processed_input": {},
                "memory_context": "",
                "messages": [],
                "response": "",
                "is_omega_command": False
            }

            # Grafı çağır
            try:
                final_state = app.invoke(initial_state)
                print(f"\nVira: {final_state['response']}")
            except Exception as e:
                logger.error(f"Graf çalıştırılırken hata oluştu: {e}", exc_info=True)
                print(f"\nVira: Üzgünüm, bir hata oluştu: {str(e)}")

        except KeyboardInterrupt:
            print("\n\nProgram kullanıcı tarafından sonlandırıldı.")
            break
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}", exc_info=True)
            print(f"\nBeklenmeyen bir hata oluştu: {e}")


def main():
    """
    Ana program fonksiyonu.
    """
    parser = argparse.ArgumentParser(description="Vira LangGraph CLI")
    parser.add_argument("--init-db", action="store_true", help="Veritabanını başlat")
    parser.add_argument("--force-recreate", action="store_true", help="Veritabanını sil ve yeniden oluştur")
    args = parser.parse_args()

    # Ortam değişkenlerini kontrol et
    if not check_environment():
        sys.exit(1)

    # Veritabanını başlat
    if args.init_db or args.force_recreate:
        if not init_database(force_recreate=args.force_recreate):
            sys.exit(1)
        print("Veritabanı başarıyla başlatıldı!")
        if not args.force_recreate:  # Sadece --init-db verilmişse çık
            sys.exit(0)

    # Sohbet döngüsünü başlat
    run_chat_loop()


if __name__ == "__main__":
    main()