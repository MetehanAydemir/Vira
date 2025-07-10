"""
Intent handler mimarisi için temel sınıf.

Bu modül, Vira'nın farklı niyet türleri için temel davranışları tanımlar.
Her niyet tipi bu temel sınıfı genişleterek kendi özel davranışını tanımlar.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage
class BaseIntentHandler(ABC):
    """
    Tüm niyet işleyicileri için soyut temel sınıf.
    """

    @abstractmethod
    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Mevcut sistem mesajını niyet türüne göre zenginleştirir.
        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu
        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        pass

    @abstractmethod
    def get_specialized_instructions(self) -> str:
        """
        Bu niyet türü için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        pass

    @abstractmethod
    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Bu niyet türü için LLM parametre ayarlarını döndürür.
        Returns:
            LLM parametreleri sözlüğü (örn. temperature, top_p, vb.)
        """
        pass

    def __str__(self) -> str:
        """
        Sınıf adının dize gösterimi.
        """
        return self.__class__.__name__
        return final_message