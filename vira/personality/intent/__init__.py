"""
Intent handler mimarisi için paket başlatıcı.

Bu paket, farklı niyet türlerine göre özelleştirilmiş davranışları
ve sistem prompt'larını yönetir.
"""

from vira.personality.intent.base import BaseIntentHandler
from vira.personality.intent.registry import IntentHandlerFactory

__all__ = ["BaseIntentHandler", "IntentHandlerFactory"]