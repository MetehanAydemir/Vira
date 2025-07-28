#!/usr/bin/env python3
"""
Gelişmiş hafıza analizi ve proaktif içgörü üretimi sistemini test eder.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Vira modüllerini import et
sys.path.append('.')
from vira.metacognition.engine import MetaCognitiveEngine
from vira.memory.reflector import Reflector
from vira.reflection.insight_generator import InsightGenerator
from vira.graph.build_reflection import process_user_reflection, extract_temporal_patterns, extract_behavioral_patterns
from vira.utils.logger import get_logger

logger = get_logger(__name__)

def test_metacognitive_engine():
    """MetaCognitive Engine'i test eder."""
    print("\n=== MetaCognitive Engine Test ===")
    
    try:
        # Mock conversation data
        mock_conversations = [
            {
                "content": "Merhaba, bugün nasılsın?",
                "timestamp": datetime.now().isoformat(),
                "user_id": "test_user"
            },
            {
                "content": "Python öğrenmek istiyorum, nereden başlamalıyım?",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "user_id": "test_user"
            },
            {
                "content": "Bu konuda yardım alabilir miyim?",
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "user_id": "test_user"
            }
        ]
        
        # Engine'i başlat
        engine = MetaCognitiveEngine()
        
        # Duygusal durum analizi test et
        emotional_state = engine._extract_emotional_state(mock_conversations)
        print(f"✓ Duygusal durum analizi: {emotional_state}")
        
        # Konu odağı analizi test et
        topic_focus = engine._extract_topic_focus(mock_conversations)
        print(f"✓ Konu odağı analizi: {topic_focus}")
        
        # Etkileşim modu analizi test et
        interaction_mode = engine._extract_interaction_mode(mock_conversations)
        print(f"✓ Etkileşim modu analizi: {interaction_mode}")
        
        # Tercih edilen konular analizi test et
        preferred_topics = engine._extract_preferred_topics(mock_conversations)
        print(f"✓ Tercih edilen konular: {preferred_topics}")
        
        print("✅ MetaCognitive Engine testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ MetaCognitive Engine testi başarısız: {str(e)}")
        return False

def test_memory_reflector():
    """Memory Reflector'ı test eder."""
    print("\n=== Memory Reflector Test ===")
    
    try:
        # Reflector'ı başlat
        reflector = Reflector()
        
        # Mock messages
        mock_messages = [
            {"message": "Python öğrenmek istiyorum"},
            {"message": "Zaman yönetimi konusunda zorlanıyorum"},
            {"message": "Yeni projeler için motivasyon arıyorum"}
        ]
        
        # İçgörü çıkarma test et
        insights = reflector.extract_meaningful_insights(
            "Kullanıcı Python öğrenmek istiyor ve zaman yönetimi konusunda zorlanıyor",
            count=2
        )
        print(f"✓ İçgörü çıkarma: {insights}")
        
        # Tema çıkarma test et
        themes = reflector.extract_themes(mock_messages, top_n=3)
        print(f"✓ Tema çıkarma: {themes}")
        
        # Duygusal analiz test et
        emotional_analysis = reflector.analyze_emotional_patterns(mock_messages)
        print(f"✓ Duygusal analiz: {emotional_analysis}")
        
        print("✅ Memory Reflector testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Memory Reflector testi başarısız: {str(e)}")
        return False

def test_insight_generator():
    """Insight Generator'ı test eder."""
    print("\n=== Insight Generator Test ===")
    
    try:
        # Generator'ı başlat
        reflector = Reflector()
        generator = InsightGenerator(reflector=reflector)
        
        # Mock temporal patterns
        temporal_patterns = {
            "hourly_activity": {"9": 5, "14": 3, "20": 7},
            "daily_activity": {"monday": 10, "tuesday": 8, "wednesday": 12},
            "frequency_pattern": "düzenli"
        }
        
        # Mock behavioral patterns
        behavioral_patterns = {
            "message_types": {"questions": 15, "statements": 10, "requests": 5},
            "interaction_frequency": 8,
            "preferred_topics": ["python", "zaman_yönetimi", "proje_yönetimi"],
            "communication_style": "sorgulayıcı"
        }
        
        # Zamansal içgörüler test et
        temporal_insights = generator.generate_temporal_insights(temporal_patterns)
        print(f"✓ Zamansal içgörüler ({len(temporal_insights)} adet): {[i['text'][:50] + '...' for i in temporal_insights]}")
        
        # Davranışsal içgörüler test et
        behavioral_insights = generator.generate_behavioral_insights(behavioral_patterns)
        print(f"✓ Davranışsal içgörüler ({len(behavioral_insights)} adet): {[i['text'][:50] + '...' for i in behavioral_insights]}")
        
        # Çapraz desen analizi test et
        all_patterns = {
            'temporal': temporal_patterns,
            'behavioral': behavioral_patterns,
            'emotional': {"dominant_emotion": "curious", "emotion_intensity": 0.7}
        }
        cross_insights = generator.synthesize_cross_pattern_insights(all_patterns)
        print(f"✓ Çapraz desen analizi: {len(cross_insights.get('proactive_actions', []))} proaktif aksiyon")
        
        print("✅ Insight Generator testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Insight Generator testi başarısız: {str(e)}")
        return False

def test_pattern_extraction():
    """Desen çıkarma fonksiyonlarını test eder."""
    print("\n=== Pattern Extraction Test ===")
    
    try:
        # Mock data
        mock_conversations = [
            {
                "content": "Python öğrenmek istiyorum, nereden başlamalıyım?",
                "timestamp": datetime.now().isoformat()
            },
            {
                "content": "Bu konuda yardım alabilir miyim?",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
        
        mock_memories = [
            {"content": "Kullanıcı Python ile ilgili sorular soruyor"},
            {"content": "Öğrenme motivasyonu yüksek görünüyor"}
        ]
        
        # Zamansal desen çıkarma test et
        temporal_patterns = extract_temporal_patterns(mock_conversations)
        print(f"✓ Zamansal desenler: {temporal_patterns}")
        
        # Davranışsal desen çıkarma test et
        behavioral_patterns = extract_behavioral_patterns(mock_conversations, mock_memories)
        print(f"✓ Davranışsal desenler: {behavioral_patterns}")
        
        print("✅ Pattern Extraction testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Pattern Extraction testi başarısız: {str(e)}")
        return False

def test_integration():
    """Tüm bileşenlerin entegrasyonunu test eder."""
    print("\n=== Integration Test ===")
    
    try:
        # Mock environment variable for testing
        os.environ["VIRA_USE_MOCK_LLM"] = "true"
        
        print("Mock LLM modu aktif - gerçek API çağrısı yapılmayacak")
        
        # Tüm bileşenleri birlikte test et
        reflector = Reflector()
        generator = InsightGenerator(reflector=reflector)
        engine = MetaCognitiveEngine()
        
        # Mock data ile tam bir analiz döngüsü
        mock_conversations = [
            {"content": "Merhaba, Python öğrenmek istiyorum", "timestamp": datetime.now().isoformat()},
            {"content": "Zaman yönetimi konusunda zorlanıyorum", "timestamp": datetime.now().isoformat()}
        ]
        
        # 1. Desenler çıkar
        temporal_patterns = extract_temporal_patterns(mock_conversations)
        behavioral_patterns = extract_behavioral_patterns(mock_conversations, [])
        
        # 2. İçgörüler üret
        temporal_insights = generator.generate_temporal_insights(temporal_patterns)
        behavioral_insights = generator.generate_behavioral_insights(behavioral_patterns)
        
        # 3. Çapraz analiz yap
        all_patterns = {
            'temporal': temporal_patterns,
            'behavioral': behavioral_patterns,
            'emotional': {}
        }
        cross_insights = generator.synthesize_cross_pattern_insights(all_patterns)
        
        print(f"✓ Entegrasyon testi tamamlandı:")
        print(f"  - Zamansal içgörüler: {len(temporal_insights)}")
        print(f"  - Davranışsal içgörüler: {len(behavioral_insights)}")
        print(f"  - Çapraz analiz güveni: {cross_insights.get('synthesis_confidence', 0)}")
        
        print("✅ Integration testi başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Integration testi başarısız: {str(e)}")
        return False
    finally:
        # Mock mode'u temizle
        if "VIRA_USE_MOCK_LLM" in os.environ:
            del os.environ["VIRA_USE_MOCK_LLM"]

def main():
    """Ana test fonksiyonu."""
    print("🚀 Gelişmiş Hafıza Analizi ve Proaktif İçgörü Üretimi Sistemi Testi")
    print("=" * 70)
    
    tests = [
        ("MetaCognitive Engine", test_metacognitive_engine),
        ("Memory Reflector", test_memory_reflector),
        ("Insight Generator", test_insight_generator),
        ("Pattern Extraction", test_pattern_extraction),
        ("Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} testi kritik hata: {str(e)}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Sonuçları: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Sistem hazır.")
        return True
    else:
        print("⚠️  Bazı testler başarısız. Lütfen hataları kontrol edin.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)