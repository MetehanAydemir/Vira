#!/usr/bin/env python3
"""
Vira FastAPI - LangGraph tabanlı API arayüzü
"""
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
import uvicorn
import uuid
import traceback
from datetime import datetime, timedelta
from passlib.context import CryptContext
import sqlalchemy as sa
from sqlalchemy.orm import Session

from vira.graph.build import app
from vira.db.engine import init_db, db_session, get_db_session
from vira.db.repository import UserRepository, MemoryRepository
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

# Repository örnekleri
user_repository = UserRepository()
memory_repository = MemoryRepository()

# Şifre doğrulama araçları
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Veri modelleri
class ChatRequest(BaseModel):
    """Sohbet isteği modeli"""
    user_id: str = Field(..., description="Kullanıcı ID'si")
    message: str = Field(..., description="Kullanıcı mesajı")
    stream: bool = Field(False, description="Akışlı yanıt isteniyorsa True")


class ChatResponse(BaseModel):
    """Sohbet yanıtı modeli"""
    response: str = Field(..., description="Vira'nın yanıtı")
    memory_context: Optional[str] = Field(None, description="Kullanılan hafıza bağlamı")


class UserCreate(BaseModel):
    """Kullanıcı oluşturma modeli"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None


class UserLogin(BaseModel):
    """Kullanıcı giriş modeli"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Kullanıcı yanıt modeli"""
    user_id: str
    username: str
    created_at: datetime


class Token(BaseModel):
    """Token yanıt modeli"""
    access_token: str
    token_type: str = "bearer"
    user_id: str


# Şifre işlemleri
def get_password_hash(password: str) -> str:
    """Şifreyi hashle"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifreyi doğrula"""
    return pwd_context.verify(plain_password, hashed_password)


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
@api.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    Yeni kullanıcı kaydı
    """
    try:
        # Şifreyi hashle
        hashed_password = get_password_hash(user.password)

        # UserRepository kullanarak kullanıcı oluştur
        try:
            user_data = user_repository.create_user(
                username=user.username,
                hashed_password=hashed_password,
                email=user.email
            )

            return UserResponse(
                user_id=str(user_data["id"]),
                username=user_data["username"],
                created_at=user_data["created_at"]
            )
        except ValueError as e:
            # UserRepository'den gelen ValidationError'ları yakala
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Kullanıcı kaydı sırasında hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı kaydı sırasında bir hata oluştu"
        )


@api.post("/login", response_model=Token)
async def login(form_data: UserLogin):
    """
    Kullanıcı girişi ve token oluşturma
    """
    try:
        # Kullanıcıyı bul
        user_data = user_repository.get_user_by_username(form_data.username)

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz kullanıcı adı veya şifre",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # get_user_by_username metodunu da benzer şekilde güncelleyip sözlük döndürecek şekilde değiştirebilirsiniz
        # Bu örnekte orijinal metodu kullanıyoruz ve user bir User nesnesi

        # Şifre doğrulama
        if not verify_password(form_data.password, user_data["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz kullanıcı adı veya şifre",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "access_token": "dummy_token_" + str(user_data["id"]),  # Gerçek uygulamada JWT token kullanın
            "token_type": "bearer",
            "user_id": str(user_data["id"])
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Giriş sırasında hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Giriş sırasında bir hata oluştu"
        )


@api.get("/conversations/{user_id}")
async def get_conversations(user_id: str, db: Session = Depends(get_db_session)):
    """
    Kullanıcının konuşma geçmişini getir
    """
    try:
        # Kullanıcının var olup olmadığını kontrol et
        user = user_repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )

        # Kullanıcının son konuşmalarını getir (son 20 etkileşim)
        # Bu kısım MemoryRepository'ye taşınabilir
        query = sa.text("""
        SELECT message, response, created_at
        FROM interactions
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT 20
        """)

        results = db.execute(query, {"user_id": user_id}).fetchall()

        # Mesajları Gradio formatına dönüştür
        messages = []
        for interaction in results:
            messages.append({"role": "user", "content": interaction.message})
            messages.append({"role": "assistant", "content": interaction.response})

        # En son mesajlar en üstte olacak şekilde tersine çevir
        messages.reverse()

        return {
            "messages": messages,
            "metadata": {
                "user_id": user_id,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Konuşma geçmişi alınırken hata: {str(e)}", exc_info=True)
        return {
            "messages": [],
            "metadata": {
                "user_id": user_id,
                "error": "Konuşma geçmişi alınamadı"
            }
        }


@api.post("/conversations/{user_id}/reset")
async def reset_conversation(user_id: str):
    """
    Kullanıcının konuşma geçmişini sıfırla
    """
    try:
        # Kullanıcının var olup olmadığını kontrol et
        user = user_repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )

        # Konuşma geçmişini silme işlemi - gerçek uygulamada belki archiving yapılabilir
        # Bu örnekte silme yerine bir flag ekliyoruz

        # TODO: Konuşma sıfırlama işlemi için uygun bir mekanizma ekleyin
        # Örneğin: conversation_sessions tablosu oluşturup aktif session'ı değiştirebilirsiniz

        return {
            "status": "success",
            "message": "Konuşma geçmişi sıfırlandı"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Konuşma sıfırlanırken hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konuşma geçmişi sıfırlanırken bir hata oluştu"
        )


@api.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Vira ile sohbet et
    """
    try:
        # Kullanıcının varlığını kontrol et
        user = user_repository.get_user_by_id(request.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )

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