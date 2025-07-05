#!/usr/bin/env python3
"""
Vira FastAPI - LangGraph tabanlı API arayüzü
"""
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import uuid
import traceback

from vira.graph.build import app
from vira.db.engine import init_db
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

# FastAPI uygulaması
api = FastAPI(
    title="Vira API",
    description="LangGraph tabanlı Vira AI API'si",
    version="1.0.0"
)

# CORS ayarları (tüm kaynaklardan erişime izin ver)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Üretimde güvenlik için belirli domainleri belirtin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Veri modelleri
class ChatRequest(BaseModel):
    """Sohbet isteği modeli"""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Kullanıcı ID'si")
    message: str = Field(..., description="Kullanıcı mesajı")


class ChatResponse(BaseModel):
    """Sohbet yanıtı modeli"""
    response: str = Field(..., description="Vira'nın yanıtı")
    memory_context: Optional[str] = Field(None, description="Kullanılan hafıza bağlamı")


# Veritabanı başlatma
@api.on_event("startup")
async def startup_event():
    """API başlatıldığında çalışacak fonksiyon"""
    try:
        # Ortam değişkenlerini kontrol et
        check_environment()

        # Veritabanını başlat (tabloları oluştur)
        init_db(force_recreate=False)
        logger.info("Veritabanı başarıyla başlatıldı")
    except Exception as e:
        logger.error(f"Başlatma sırasında hata oluştu: {e}", exc_info=True)
        # Hatayı yut ve devam et, çünkü veritabanı zaten kurulu olabilir


def check_environment():
    """Gerekli ortam değişkenlerini kontrol et"""
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
        error_msg = f"Eksik ortam değişkenleri: {', '.join(missing)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


# API endpoint'leri
# API endpoint'leri
@api.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Vira ile sohbet et
    """
    try:
        # Başlangıç durumunu hazırla
        initial_state = {
            "user_id": request.user_id,
            "original_message": request.message,
            "processed_input": {},
            "memory_context": "",
            "messages": [],
            "response": "",
            "is_omega_command": False
        }

        logger.info(f"Chat isteği: {request.user_id}, Mesaj: {request.message[:30]}...")

        try:
            # LangGraph'ı çağır - eski sürümle uyumlu
            config = {"recursion_limit": 25}  # Sonsuz döngülerden kaçınmak için
            final_state = app.invoke(initial_state, config=config)

            # Yanıtı oluştur
            return ChatResponse(
                response=final_state["response"],
                memory_context=final_state.get("memory_context", "")
            )
        except Exception as e:
            logger.error(f"LangGraph çalıştırma hatası: {e}")
            logger.error(traceback.format_exc())
            return ChatResponse(
                response="Üzgünüm, bir hata oluştu ve yanıt üretemedim. Teknik ekibimiz bilgilendirildi.",
                memory_context=""
            )

    except Exception as e:
        logger.error(f"Sohbet sırasında hata oluştu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"İşlem sırasında hata oluştu: {str(e)}")


@api.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint'i"""
    return {"status": "healthy", "version": "1.0.0"}


# API'yi doğrudan çalıştırma
if __name__ == "__main__":
    uvicorn.run("vira.api:api", host="0.0.0.0", port=8000, reload=True)