"""
Intent handler sınıflarının merkezi kayıt defteri.

Bu modül, farklı niyet türlerinin ilgili handler sınıflarına eşlendiği
merkezi bir kayıt defteri sağlar.
"""

from typing import Dict, Type, Any, List, Optional, Tuple
from vira.graph.nodes.intent_classifier import IntentType
from vira.personality.intent.base import BaseIntentHandler

# Handler sınıflarını sonradan içe aktaracağız
from vira.personality.intent.question import QuestionIntentHandler
from vira.personality.intent.greeting import GreetingIntentHandler
from vira.personality.intent.farewell import FarewellIntentHandler
from vira.personality.intent.command import CommandIntentHandler
from vira.personality.intent.request import RequestIntentHandler
from vira.personality.intent.information import InformationIntentHandler
from vira.personality.intent.opinion import OpinionIntentHandler
from vira.personality.intent.omega import OmegaIntentHandler
from vira.personality.intent.philosophical import PhilosophicalIntentHandler
from vira.personality.intent.reflection import ReflectionIntentHandler
from vira.personality.intent.emotional import EmotionalIntentHandler
from vira.personality.intent.identity_probe import IdentityProbeIntentHandler
from vira.personality.intent.creative_request import CreativeRequestIntentHandler
from vira.personality.intent.unknown import UnknownIntentHandler

# Niyet türlerini handler sınıflarına eşleyen sözlük
INTENT_HANDLERS: Dict[str, Type[BaseIntentHandler]] = {
    IntentType.QUESTION: QuestionIntentHandler,
    IntentType.GREETING: GreetingIntentHandler,
    IntentType.FAREWELL: FarewellIntentHandler,
    IntentType.COMMAND: CommandIntentHandler,
    IntentType.REQUEST: RequestIntentHandler,
    IntentType.INFORMATION: InformationIntentHandler,
    IntentType.OPINION: OpinionIntentHandler,
    IntentType.OMEGA: OmegaIntentHandler,
    IntentType.PHILOSOPHICAL: PhilosophicalIntentHandler,
    IntentType.REFLECTION: ReflectionIntentHandler,
    IntentType.EMOTIONAL: EmotionalIntentHandler,
    IntentType.IDENTITY_PROBE: IdentityProbeIntentHandler,
    IntentType.CREATIVE_REQUEST: CreativeRequestIntentHandler,
    IntentType.UNKNOWN: UnknownIntentHandler,
}


class IntentHandlerFactory:
    """
    Intent handler nesnelerini oluşturan fabrika sınıfı.
    """
    
    @staticmethod
    def get_handler(intent_type: str) -> BaseIntentHandler:
        """
        Belirtilen niyet türü için uygun handler'ı döndürür.

        Args:
            intent_type: Niyet türü (IntentType sınıfından)

        Returns:
            BaseIntentHandler alt sınıfı
            
        Raises:
            ValueError: Desteklenmeyen bir niyet türü için
        """
        handler_class = INTENT_HANDLERS.get(intent_type)
        
        if handler_class is None:
            # Bilinmeyen niyet için varsayılan handler'a yönlendir
            handler_class = INTENT_HANDLERS[IntentType.UNKNOWN]
            
        # Handler sınıfının yeni bir örneğini oluştur ve döndür
        return handler_class()