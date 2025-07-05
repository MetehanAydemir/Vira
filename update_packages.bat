@echo off
echo Paketler güncelleniyor...

:: Önce mevcut paketleri kaldır
pip uninstall -y langgraph langchain-core langchain

:: Sonra uyumlu sürümleri yükle
pip install langgraph==0.0.46 langchain-core==0.1.27 langchain==0.1.9

echo Paket güncellemesi tamamlandı!
pause