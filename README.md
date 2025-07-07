# Vira - LangGraph Tabanlı Yapay Zeka Asistanı

Vira, uzun süreli hafıza ve dinamik kişilik özellikleriyle donatılmış, LangGraph tabanlı modern bir yapay zeka asistanıdır. Azure OpenAI ve PostgreSQL (pgvector) altyapısını kullanarak çok katmanlı hafıza yönetimi ve uyarlanabilir kişilik sistemi sunar.

![Vira](https://via.placeholder.com/800x400?text=Vira+AI+Assistant)

## Temel Özellikler

- **LangGraph Tabanlı Akış Mimarisi**: Modüler düğümler ve koşullu yönlendirmeler içeren esnek yapı.
- **İki Katmanlı Hafıza Sistemi**:
  - **Uzun Süreli Hafıza**: pgvector ile benzerlik araması yapılarak derin anılar saklanır.
  - **Kısa Süreli Hafıza**: Aktif oturumlardaki güncel konuşma bağlamı korunur.
- **Dinamik Kişilik Sistemi**: Kullanıcı etkileşimleriyle evrimleşen, beş boyutlu kişilik vektörü.
- **Yanıt Kalite Değerlendirmesi**: Her yanıtın dil modeli tarafından öz değerlendirilmesi.
- **Çoklu Arayüz Seçenekleri**: FastAPI, Gradio, Streamlit ve CLI desteği.
- **Azure OpenAI Entegrasyonu**: GPT-4o ve text-embedding-3-small modelleriyle çalışma.
- **Konfigüre Edilebilir Önem Değerlendirme**: Anıların uzun süreli hafızaya kaydedilme kriterlerinin özelleştirilebilmesi.

## Mimari

### LangGraph Akış Mimarisi

Vira, aşağıdaki adımları izleyen modüler bir LangGraph akış mimarisi kullanır:

1. **process_input**: Kullanıcı girdisini işler ve ön analiz yapar.
2. **intent_classifier**: Kullanıcının amacını ve talebini sınıflandırır.
3. **handle_omega/retrieve_memory**: Özel komut veya hafıza geri çağırma yoluna karar verir.
4. **context_refiner**: Bellek ve bağlamı yapılandırır ve zenginleştirir.
5. **prepare_prompt**: Dil modeli için optimize edilmiş sistem mesajı ve giriş hazırlar.
6. **generate_response**: Yanıt üretir ve yanıt kalitesini değerlendirir.
7. **save_memory**: Etkileşimin önemine göre hafızaya kaydeder.

### Hafıza Sistemi

Vira'nın iki katmanlı hafıza sistemi:

- **Uzun Süreli Hafıza**: 
  - pgvector ile vektör benzerliği araması.
  - İlgili anıların seçici olarak saklanması.
  - Önem skoru hesaplanarak anı filtreleme.
  
- **Kısa Süreli Hafıza**:
  - Aktif oturumdaki son konuşmaları kronolojik sırayla saklama.
  - Hızlı erişim için oturum ID'si ile ilişkilendirme.

### Kişilik Sistemi

Vira'nın dinamik kişilik sistemi, beş boyutlu bir vektörle temsil edilir:

- **Empati**: Kullanıcının duygularını ve bakış açısını anlama yeteneği.
- **Merak**: Yeni bilgiler öğrenme veya derinleşme isteği.
- **Kararlılık**: Kendinden emin ve doğrudan yanıt verme kapasitesi.
- **Mizah**: Esprili veya eğlenceli unsurlar içerme eğilimi.
- **Şüphecilik**: Eleştirel düşünce ve sorgulama seviyesi.

Bu vektör, her etkileşimde LLM tarafından değerlendirilerek küçük adımlarla güncellenir ve kişilik evriminin geçmişi veritabanında saklanır.

## Kurulum

### Ön Gereksinimler

- Python 3.10+
- PostgreSQL 14+ (pgvector eklentisi ile)
- Azure OpenAI API erişimi
- Docker ve Docker Compose (opsiyonel)

### Ortam Kurulumu


1. Depoyu klonlayın:
git clone https://github.com/yourusername/vira.git cd vira


2. Sanal ortam oluşturun ve bağımlılıkları yükleyin:
python -m venv venv source venv/bin/activate # Windows: venv\Scripts\activate pip install -r requirements.txt


3. `.env` dosyası oluşturun (örnek):
Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/ AZURE_OPENAI_API_VERSION=2023-12-01-preview AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt4-deployment AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment

Database
POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=vira_db POSTGRES_USER=vira POSTGRES_PASSWORD=sifre

Application
LOG_LEVEL=INFO MEMORY_SIMILARITY_THRESHOLD=0.7


### Veritabanı Kurulumu

PostgreSQL veritabanı ve pgvector eklentisini kurun:
### Veritabanı Kurulumu

PostgreSQL veritabanı ve pgvector eklentisini kurun:


# Docker ile
docker-compose up -d postgres

# Veya manuel olarak
psql -U postgres -c "CREATE DATABASE vira_db;"
psql -U postgres -d vira_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

Vira - Yol arkadaşı, alet değil.


Şimdi de akış şemasını içeren dosyayı hazırlayalım:


# Vira LangGraph Akış Şeması

Aşağıda, Vira AI Asistanı'nın LangGraph tabanlı akışının detaylı bir şeması bulunmaktadır. Bu şema, giriş işlemeden hafızaya kaydetmeye kadar tüm adımları ve karar noktalarını göstermektedir.

graph TD
    A[Kullanıcı Girdisi] --> B[process_input_node]
    B -->|Girdi analizi| C[intent_classifier_node]
    C -->|Amaç belirleme| D{is_omega_command?}

    D -->|Evet| E[handle_omega_node]
    D -->|Hayır| F[retrieve_memory_node]

    F --> |Hafıza çağırma| G[context_refiner_node]
    G --> |Bağlam zenginleştirme| H[prepare_prompt_node]
    H --> |Prompt hazırlama| I[generate_response_node]

    subgraph LLM İşlemi
        I --> I1[Chain-of-Thought ekle]
        I1 --> I2[LLM çağrısı yap]
        I2 --> I3[Yanıt kalitesini değerlendir]
        I3 --> I4[Kişilik vektörünü güncelle]
        I4 --> I5[Önem skorunu hesapla]
    end

    I --> J[save_memory_node]

    subgraph Hafıza Yönetimi
        J --> J1{should_promote_to_long_term?}
        J1 -->|Evet| J2[Uzun Süreli Hafızaya Kaydet]
        J1 -->|Hayır| J3[Kısa Süreli Hafızaya Kaydet]
    end

    E --> K[END]
    J --> K[END]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#bbf,stroke:#333,stroke-width:2px
    style I fill:#bfb,stroke:#333,stroke-width:2px
    style J fill:#fbf,stroke:#333,stroke-width:2px
Vira Akış Adımları Detaylı Açıklaması
1. Giriş İşleme (Input Processing)
process_input_node: Kullanıcı girdisi alınır ve temel analiz yapılır (dil tespiti, kelime sayısı, temel duygu analizi)
intent_classifier_node: Kullanıcının niyeti sınıflandırılır (soru, komut, sohbet, vb.)

2. Yol Ayrımı (Decision Point)
is_omega_command?: Özel komut mu normal sohbet mi kararı verilir
Eğer özel komutsa: handle_omega_node çalışır
Değilse: Normal sohbet akışına devam edilir

3. Hafıza ve Bağlam İşleme (Memory & Context Processing)
retrieve_memory_node: İki tür hafıza çekilir
Uzun Süreli Hafıza: pgvector ile benzerlik araması
Kısa Süreli Hafıza: Son konuşmalar
context_refiner_node: Hafıza ve bağlam birleştirilir, LLM için optimize edilir

4. Yanıt Üretimi (Response Generation)
prepare_prompt_node: LLM için sistem talimatları ve girdiler hazırlanır
generate_response_node: Yanıt üretilir
Chain-of-Thought ile düşünce adımları eklenir
LLM çağrısı yapılır
Yanıt kalitesi değerlendirilir (alaka, doğruluk, yardımcılık)
Kişilik vektörü güncellenir
Önem skoru hesaplanır

5. Hafıza Yönetimi (Memory Management)
save_memory_node: Etkileşim hafızaya kaydedilir
Önem skoruna göre uzun/kısa süreli hafızaya kaydedilir
Kişilik günlüğü güncellenir
Kişilik Sistemi Alt Akışı
graph TD
    A[Yanıt Üretildi] --> B[evaluate_response]
    B --> C[LLM Değerlendirmesi]
    C --> D[Kişilik Skorları]

    D --> E[calculate_delta]
    E --> F[update_vector]
    F --> G[save_personality_vector]

    G --> H[Veritabanı Güncellemesi]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px

Kişilik Değerlendirme Adımları
evaluate_response: Vira'nın yanıtı analiz edilir
Empati, merak, kararlılık, mizah ve şüphecilik boyutları puanlanır
calculate_delta: Mevcut kişilik vektörü ile yeni değerlendirme arasındaki fark hesaplanır
update_vector: Kişilik vektörü küçük adımlarla güncellenir
save_personality_vector: Güncellenmiş vektör ve değişim günlüğü veritabanına kaydedilir
Bu akış şeması, Vira'nın çalışma prensibi ve bileşenlerin nasıl etkileşime girdiğini göstermek için tasarlanmıştır. LangGraph mimarisi sayesinde akış modüler ve genişletilebilirdir.


Bu iki dosya ile projenin hem detaylı bir açıklamasını hem de görsel bir akış şemasını sunmuş oluyorum. README.md dosyası, projenin genel özelliklerini, kurulumunu ve kullanımını anlatırken, FLOW_DIAGRAM.md dosyası özellikle LangGraph akışının nasıl çalıştığını mermaid diyagramları ile görselleştiriyor. Bu şekilde projeyle ilgilenenlere hem yüksek seviye bir bakış hem de derinlemesine teknik ayrıntılar sunulmuş oluyor.



