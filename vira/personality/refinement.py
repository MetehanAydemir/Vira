from typing import Dict, Any, List, Tuple
from vira.db.repository import PersonalityRepository
from vira.utils.llm_client import call_chat_model
from vira.utils.logger import get_logger
import json
logger = get_logger(__name__)

class PersonalityRefinementPipeline:
    """
    Vira'nın kişilik vektörünü zaman içinde etkileşimlere göre güncelleyen pipeline.
    
    ContinuousGrowth ilkesini uygulayan bu sınıf, Vira'nın kendi yanıtlarını
    değerlendirerek kişilik vektörünü küçük adımlarla evrimleştirir.
    """
    
    def __init__(self, repo: PersonalityRepository = None):
        """PersonalityRepository ile başlatır."""
        self.repo = repo or PersonalityRepository()
        self.learning_rate = 0.01  # Küçük adımlarla öğrenme

    def evaluate_response(self, prompt: str, response: str) -> Dict[str, float]:
        """
        Vira'nın yanıtını analiz ederek kişilik boyutlarını değerlendirir.

        Bu fonksiyon, LLM kullanarak yanıtın çeşitli kişilik boyutlarını (empati,
        merak, kararlılık, mizah, şüphecilik) ne kadar yansıttığını ölçer.

        Args:
            prompt: Kullanıcının orijinal mesajı
            response: Vira'nın yanıtı

        Returns:
            Kişilik boyutlarının değerlendirme skorları
        """


        # LLM değerlendirmesi için mesajları hazırla
        messages = [
            {"role": "system",
             "content": "Sen bir kişilik analisti botsun. Verilen yanıtı kişilik boyutları açısından değerlendir."},
            {"role": "user", "content": f"""
            Kullanıcının mesajı: {prompt}

            Vira'nın cevabı: {response}

            Şimdi bu yanıtı aşağıdaki kişilik boyutlarına göre 0.0 ile 1.0 arasında değerlendir:
            - Empati: Yanıt kullanıcının duygularını ve bakış açısını ne kadar anladığını gösteriyor?
            - Merak: Yanıt yeni bilgiler öğrenme veya derinleşme isteği içeriyor mu?
            - Kararlılık: Yanıt ne kadar kendinden emin ve doğrudan?
            - Mizah: Yanıt esprili veya eğlenceli unsurlar içeriyor mu?
            - Şüphecilik: Yanıt eleştirel düşünce veya sorgulama içeriyor mu?

            Sadece bir JSON formatında cevap ver:
            {"empathy": X.XX, "curiosity": X.XX, "assertiveness": X.XX, "humour": X.XX, "scepticism": X.XX}
            """}
        ]

        try:
            # LLM'den değerlendirme al
            result = call_chat_model(
                messages=messages,
                model="gpt-4o-mini",  # Yüksek kaliteli değerlendirme için GPT-4
                temperature=0.3,  # Tutarlı sonuçlar için düşük sıcaklık
                max_tokens=150,
                response_format={"type": "json_object"}  # JSON formatında yanıt al
            )

            # JSON yanıtı parse et
            scores = json.loads(result)
            logger.info(f"Kişilik değerlendirme sonuçları: {scores}")

            # Tüm gerekli boyutların olduğundan emin ol
            expected_dimensions = ["empathy", "curiosity", "assertiveness", "humour", "scepticism"]
            for dim in expected_dimensions:
                if dim not in scores:
                    scores[dim] = 0.5  # Eksik boyut varsa varsayılan değer ata

            return scores

        except Exception as e:
            logger.error(f"Kişilik değerlendirmesi sırasında hata: {e}")
            # Hata durumunda varsayılan değerleri döndür
            return {
                "empathy": 0.5,
                "curiosity": 0.5,
                "assertiveness": 0.5,
                "humour": 0.5,
                "scepticism": 0.5
            }
    
    def calculate_delta(self, old_vector: Dict[str, float], 
                        analysis: Dict[str, float]) -> Dict[str, float]:
        """
        Mevcut vektör ile analiz sonuçları arasındaki farkı hesaplar.
        
        Args:
            old_vector: Mevcut kişilik vektörü
            analysis: Yanıt analizinden elde edilen skorlar
            
        Returns:
            Her boyut için hesaplanmış delta değerleri
        """
        delta = {}
        for key in old_vector:
            if key in analysis:
                # Delta = (yeni_değer - eski_değer) * öğrenme_hızı
                delta[key] = (analysis[key] - old_vector[key]) * self.learning_rate
        
        return delta
    
    def update_vector(self, old_vector: Dict[str, float], 
                     delta: Dict[str, float]) -> Dict[str, float]:
        """
        Kişilik vektörünü delta değerlerine göre günceller.
        
        Args:
            old_vector: Mevcut kişilik vektörü
            delta: Hesaplanmış delta değerleri
            
        Returns:
            Güncellenmiş kişilik vektörü
        """
        new_vector = {}
        for key in old_vector:
            if key in delta:
                # Yeni değer = eski_değer + delta
                new_value = old_vector[key] + delta[key]
                # 0-1 aralığında sınırla
                new_vector[key] = max(0.0, min(1.0, new_value))
            else:
                new_vector[key] = old_vector[key]
                
        return new_vector
    
    def refine_personality(self, user_id: str, prompt: str, 
                          response: str) -> Dict[str, float]:
        """
        Kullanıcı etkileşimine göre kişilik vektörünü günceller ve kaydeder.
        
        Args:
            user_id: Kullanıcı kimliği
            prompt: Kullanıcının orijinal mesajı
            response: Vira'nın yanıtı
            
        Returns:
            Güncellenmiş kişilik vektörü
        """
        try:
            # 1. Mevcut kişilik vektörünü al
            old_vector = self.repo.get_personality_vector(user_id)
            
            # 2. Yanıtı analiz et
            analysis = self.evaluate_response(prompt, response)
            
            # 3. Delta hesapla
            delta = self.calculate_delta(old_vector, analysis)
            
            # 4. Vektörü güncelle
            new_vector = self.update_vector(old_vector, delta)
            
            # 5. Güncellenmiş vektörü kaydet
            self.repo.save_personality_vector(
                user_id=user_id,
                vector=new_vector,
                old_vector=old_vector,
                delta=delta,
                reason=f"Response analysis: {prompt[:50]}..."
            )
            
            logger.info(f"Kişilik vektörü güncellendi: {user_id}")
            return new_vector
            
        except Exception as e:
            logger.error(f"Kişilik vektörü güncellenirken hata: {e}")
            return old_vector