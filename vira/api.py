#!/usr/bin/env python3
"""
Vira FastAPI - LangGraph tabanlı API arayüzü
"""
import os
from vira.graph.state import ViraState
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
from apscheduler.schedulers.background import BackgroundScheduler

# Reflection enhanced workflow için import
from vira.graph.build import app as base_app
from vira.graph.build_reflection import create_reflection_enhanced_workflow, schedule_actions
from vira.db.engine import init_db, db_session, get_db_session
from vira.db.repository import UserRepository, MemoryRepository
from vira.db.reflection_repository import ReflectionRepository
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

# LangGraph akışını reflection-enhanced workflow ile değiştir
app = create_reflection_enhanced_workflow()

# Zamanlanmış görevler için scheduler
scheduler = BackgroundScheduler()

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
reflection_repository = None  # Başlatma sırasında oluşturulacak

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


# Zamanlanmış görevleri başlat
def start_scheduler():
    """Zamanlanmış görevleri başlat"""
    try:
        # Yansıtma aksiyonlarını her 15 dakikada bir çalıştır
        # APScheduler için parametresiz wrapper fonksiyon kullan
        def scheduled_reflection_job():
            """APScheduler için wrapper fonksiyon"""
            try:
                logger.info("Scheduled reflection job başlatılıyor...")
                result = schedule_actions()
                logger.info(f"Scheduled reflection job tamamlandı: {result}")
            except Exception as e:
                logger.error(f"Scheduled reflection job hatası: {str(e)}", exc_info=True)
        
        scheduler.add_job(
            scheduled_reflection_job,
            'interval',
            minutes=15,
            id='reflection_actions',
            max_instances=1,  # Aynı anda sadece bir instance çalışsın
            coalesce=True,    # Birden fazla job birikirse birleştir
            misfire_grace_time=300  # 5 dakika grace time
        )

        # Scheduler'ı başlat
        if not scheduler.running:
            scheduler.start()
            logger.info("Background scheduler başarıyla başlatıldı. Yansıtma aksiyonları 15 dakikada bir çalışacak.")
        else:
            logger.info("Background scheduler zaten çalışıyor.")
            
    except Exception as e:
        logger.error(f"Scheduler başlatılırken hata oluştu: {str(e)}", exc_info=True)
        # Scheduler hatası uygulamanın çalışmasını engellememelidir


# Veritabanı başlatma
@api.on_event("startup")
async def startup_event():
    """API başlatıldığında çalışacak fonksiyon"""
    try:
        # Ortam değişkenlerini kontrol et
        check_environment()

        # Veritabanını başlat (tabloları oluştur)
        init_db(force_recreate=False)

        # ReflectionRepository'yi başlat
        global reflection_repository
        reflection_repository = ReflectionRepository()

        # Zamanlanmış görevleri başlat
        start_scheduler()

        logger.info("Veritabanı ve self-reflection sistemi başarıyla başlatıldı")
    except Exception as e:
        logger.error(f"Başlatma sırasında hata oluştu: {e}", exc_info=True)
        # Hatayı yut ve devam et, çünkü veritabanı zaten kurulu olabilir


@api.on_event("shutdown")
async def shutdown_event():
    """API kapatıldığında çalışacak fonksiyon"""
    try:
        # Scheduler'ı güvenli bir şekilde durdur
        if scheduler.running:
            logger.info("Background scheduler durduruluyor...")
            scheduler.shutdown(wait=True)  # Çalışan job'ların bitmesini bekle
            logger.info("Background scheduler başarıyla durduruldu")
        else:
            logger.info("Background scheduler zaten durdurulmuş")
    except Exception as e:
        logger.error(f"Scheduler durdurulurken hata oluştu: {str(e)}", exc_info=True)


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
        # Validate user existence
        user = user_repository.get_user_by_id(request.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Initialize the state as a ViraState object
        initial_state = ViraState({
            "user_id": request.user_id,
            "original_message": request.message,
            "processed_input": {},
            "memory_context": "",
            "messages": [],
            "response": "",
            "is_omega_command": False,
            "dynamic_personality": {},
            # Self-reflection için gerekli ek alanlar
            "reflection_triggered": False,
            "reflection_data": {},
            "insights": []
        })

        logger.info(f"Chat request: {request.user_id}, Message: {request.message[:30]}...")

        try:
            config = {"recursion_limit": 25}  # Prevent infinite loops

            # Enhanced workflow'u kullan
            final_state = app.invoke(initial_state, config=config)

            logger.info(f"Response: {final_state.get('response', 'No response')}")

            # Yansıtma tetiklenmiş mi kontrol et ve logla
            if final_state.get("reflection_triggered", False):
                logger.info(f"Self-reflection triggered during chat: {final_state.get('reflection_data', {})}")

            return ChatResponse(
                response=final_state["response"],
                memory_context=final_state.get("memory_context", "")
            )
        except Exception as e:
            logger.error(f"LangGraph execution error: {e}")
            logger.error(traceback.format_exc())
            return ChatResponse(
                response="Sorry, an error occurred and I couldn't generate a response. The technical team has been notified.",
                memory_context=""
            )

    except Exception as e:
        logger.error(f"Error during chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")


# Yeni endpoint: Self-reflection verilerini getir
@api.get("/reflections/{user_id}")
async def get_reflections(user_id: str):
    """
    Kullanıcının yansıtma verilerini getir
    """
    try:
        # Kullanıcının var olup olmadığını kontrol et
        user = user_repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )

        # ReflectionRepository kullanarak verileri getir
        sessions = reflection_repository.get_reflection_sessions(user_id, limit=10)
        insights = reflection_repository.get_insights(user_id, limit=10)
        goals = reflection_repository.get_active_goals(user_id)

        # Sonuçları formatlayıp döndür
        return {
            "sessions": sessions,
            "insights": insights,
            "goals": goals,
            "metadata": {
                "user_id": user_id,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Yansıtma verileri alınırken hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yansıtma verileri alınırken bir hata oluştu"
        )


# Self-reflection tetikleme endpoint'i
@api.post("/reflections/{user_id}/trigger")
async def trigger_reflection(user_id: str, background_tasks: BackgroundTasks):
    """
    Kullanıcı için manuel yansıtma oturumu tetikle
    """
    try:
        # Kullanıcının var olup olmadığını kontrol et
        user = user_repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )

        # ReflectionRepository kullanarak manuel yansıtma başlat
        session_id = reflection_repository.create_reflection_session(
            user_id=user_id,
            reflection_type="manual",
            trigger_reasons=["user_triggered"]
        )

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Yansıtma oturumu oluşturulamadı"
            )

        # Yansıtma işlemini arka planda başlat
        background_tasks.add_task(
            schedule_actions,
            user_id=user_id,
            force=True,
            reflection_type="manually_triggered"
        )

        return {
            "status": "success",
            "message": "Yansıtma oturumu başlatıldı",
            "session_id": session_id,
            "triggered_at": datetime.utcnow().isoformat()
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Yansıtma tetiklenirken hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yansıtma tetiklenirken bir hata oluştu"
        )


@api.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint'i"""
    try:
        # Scheduler durumunu detaylı kontrol et
        scheduler_info = {
            "running": scheduler.running,
            "jobs_count": len(scheduler.get_jobs()),
            "next_run_time": None
        }
        
        # Reflection job'ının bir sonraki çalışma zamanını al
        reflection_job = scheduler.get_job('reflection_actions')
        if reflection_job:
            scheduler_info["next_run_time"] = reflection_job.next_run_time.isoformat() if reflection_job.next_run_time else None
            scheduler_info["reflection_job_active"] = True
        else:
            scheduler_info["reflection_job_active"] = False
            
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "self_reflection_enabled": True,
                "scheduler": scheduler_info
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return {
            "status": "degraded",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "features": {
                "self_reflection_enabled": False,
                "scheduler": {"running": False, "error": str(e)}
            }
        }


# API'yi doğrudan çalıştırma
if __name__ == "__main__":
    uvicorn.run("vira.api:api", host="0.0.0.0", port=8000, reload=True)