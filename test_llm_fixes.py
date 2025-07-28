#!/usr/bin/env python3
"""
LLM model adı düzeltmelerini test eden script.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vira.config import settings
from vira.utils.llm_client import call_chat_model
from vira.graph.nodes.intent_classifier import call_llm_for_intent
from vira.personality.refinement import PersonalityRefinementPipeline
from vira.utils.logger import get_logger

logger = get_logger(__name__)

def test_config_settings():
    """Konfigürasyon ayarlarını test et."""
    print("=== Konfigürasyon Testi ===")
    print(f"AZURE_OPENAI_DEPLOYMENT_NAME: {settings.AZURE_OPENAI_DEPLOYMENT_NAME}")
    print(f"CUSTOM_CHAT_MODEL_NAME: {settings.CUSTOM_CHAT_MODEL_NAME}")
    print(f"AZURE_OPENAI_ENDPOINT: {settings.AZURE_OPENAI_ENDPOINT}")
    print(f"AZURE_OPENAI_API_KEY: {'***' if settings.AZURE_OPENAI_API_KEY else 'None'}")
    print()

def test_llm_client():
    """LLM client'ın model seçimini test et."""
    print("=== LLM Client Testi ===")
    
    # Mock mode'u aktif et
    os.environ["VIRA_USE_MOCK_LLM"] = "true"
    
    try:
        messages = [
            {"role": "user", "content": "Merhaba, nasılsın?"}
        ]
        
        # Model belirtmeden çağır (varsayılan model kullanılmalı)
        response = call_chat_model(messages=messages)
        print(f"Varsayılan model ile yanıt: {response}")
        
        # Belirli model ile çağır
        response2 = call_chat_model(messages=messages, model="test-model")
        print(f"Belirli model ile yanıt: {response2}")
        
        print("✅ LLM Client testi başarılı")
        
    except Exception as e:
        print(f"❌ LLM Client testi başarısız: {e}")
    
    print()

def test_intent_classifier():
    """Intent classifier'ın model kullanımını test et."""
    print("=== Intent Classifier Testi ===")
    
    # Mock mode'u aktif et
    os.environ["VIRA_USE_MOCK_LLM"] = "true"
    
    try:
        # Test mesajı
        test_message = "Merhaba, nasılsın?"
        test_history = []
        
        intent = call_llm_for_intent(test_message, test_history)
        print(f"Tespit edilen niyet: {intent}")
        print("✅ Intent Classifier testi başarılı")
        
    except Exception as e:
        print(f"❌ Intent Classifier testi başarısız: {e}")
    
    print()

def test_personality_refinement():
    """Personality refinement'ın model kullanımını test et."""
    print("=== Personality Refinement Testi ===")
    
    # Mock mode'u aktif et
    os.environ["VIRA_USE_MOCK_LLM"] = "true"
    
    try:
        pipeline = PersonalityRefinementPipeline()
        
        # Test değerlendirmesi
        prompt = "Bugün nasılsın?"
        response = "İyiyim, teşekkür ederim!"
        
        scores = pipeline.evaluate_response(prompt, response)
        print(f"Kişilik skorları: {scores}")
        print("✅ Personality Refinement testi başarılı")
        
    except Exception as e:
        print(f"❌ Personality Refinement testi başarısız: {e}")
    
    print()

def main():
    """Ana test fonksiyonu."""
    print("🔧 Vira LLM Model Düzeltmeleri Test Scripti")
    print("=" * 50)
    
    test_config_settings()
    test_llm_client()
    test_intent_classifier()
    test_personality_refinement()
    
    print("🎉 Tüm testler tamamlandı!")

if __name__ == "__main__":
    main()