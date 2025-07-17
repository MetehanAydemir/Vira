import logging
import sys

# Log formatını belirle
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# Temel yapılandırmayı yap
logging.basicConfig(
    level=logging.INFO,      # Görüntülenecek en düşük log seviyesi
    format=LOG_FORMAT,       # Logların hangi formatta olacağı
    stream=sys.stdout,       # Logların konsola (standart çıktıya) yazdırılması
    force=True               # Diğer kütüphanelerin log ayarlarını ezmek için
)

def get_logger(name: str) -> logging.Logger:
    """
    Belirtilen isim için bir logger nesnesi alır ve döndürür.
    Bu, projenin her yerinde aynı log yapılandırmasını kullanmayı sağlar.
    """
    return logging.getLogger(name)
