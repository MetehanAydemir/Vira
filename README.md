# Vira - LangGraph Tabanlı AI Asistanı

Vira, uzun süreli hafıza özelliklerine sahip, Azure OpenAI ve PostgreSQL (pgvector) kullanan, çok arayüzlü bir AI asistanıdır. LangGraph tabanlı mimarisi sayesinde karmaşık düşünce akışları oluşturabilir.

![Vira](https://via.placeholder.com/800x400?text=Vira+AI+Assistant)

## Özellikler

- **LangGraph Tabanlı İş Akışı**: Modüler ve genişletilebilir yapay zeka iş akışı
- **Uzun Süreli Hafıza**: PostgreSQL ve pgvector kullanarak vektör gömmeleriyle hafıza depolama ve benzerlik araması
- **Çoklu Arayüz Seçenekleri**:
  - FastAPI REST API
  - Web arayüzü (Gradio)
  - Dashboard (Streamlit)
  - Komut satırı arayüzü (CLI)
- **Azure OpenAI Entegrasyonu**: GPT-4o-mini ve text-embedding-3-small modelleri
- **Hafıza Yönetimi**: Konuşma geçmişini akıllıca saklama ve ilgili anıları geri getirme
- **Yapılandırılabilir Kişilik**: Farklı kullanım senaryolarına uyarlanabilir kişilik özellikleri
- **Docker Desteği**: Kolay dağıtım ve ölçeklendirme

## Kurulum

### Ön Gereksinimler

- Python 3.10+
- PostgreSQL 14+ (pgvector eklentisi ile)
- Azure OpenAI API erişimi
- Docker ve Docker Compose (isteğe bağlı)

### Ortam Kurulumu

1. Depoyu klonlayın:
   ```
   git clone https://github.com/yourusername/vira.git
   cd vira
   ```

2. Sanal ortam oluşturun ve bağımlılıkları yükleyin:
   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. `.env` dosyası oluşturun (örnek):
   ```
   # Azure OpenAI
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2023-12-01-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt4-deployment
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment

   # Database
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=vira
   DB_USER=postgres
   DB_PASSWORD=password

   # Application
   LOG_LEVEL=INFO
   ```

### Veritabanı Kurulumu

PostgreSQL veritabanı ve pgvector eklentisini kurun:

```bash
# Docker ile
docker-compose up -d postgres

# Veya manuel olarak
psql -U postgres -c "CREATE DATABASE vira;"
psql -U postgres -d vira -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Veritabanı şemasını oluşturmak için:

```bash
# Uygulama başlatıldığında otomatik yapılır veya
python -m vira.db.engine --init
```

## Kullanım

### API Sunucusu

REST API'yi başlatmak için:

```bash
python -m vira.api
# veya
uvicorn vira.api:api --host 0.0.0.0 --port 8000 --reload
```

API dökümantasyonuna erişmek için: http://localhost:8000/docs

### Web Arayüzü (Gradio)

Gradio web arayüzünü başlatmak için:

```bash
python -m vira.gradio_app
```

Arayüze erişmek için: http://localhost:7860

### Dashboard (Streamlit)

Streamlit dashboard'unu başlatmak için:

```bash
python -m vira.streamlit_app
```

Dashboard'a erişmek için: http://localhost:8501

### Komut Satırı Arayüzü

CLI üzerinden Vira ile etkileşim için:

```bash
python -m vira.cli
```

### Docker ile Çalıştırma

Tüm servisleri Docker ile başlatmak için:

```bash
docker-compose up -d
```

## Mimari

Vira'nın mimari yapısı şu bileşenlerden oluşur:

```
vira/
├── graph/                 # LangGraph tabanlı akış
│   ├── build.py           # Graf yapısının oluşturulması
│   ├── state.py           # Graf durumu tanımları
│   └── nodes/             # Graf düğümleri
├── db/                    # Veritabanı işlemleri
│   ├── engine.py          # Veritabanı bağlantı motoru
│   ├── models.py          # SQLAlchemy modelleri
│   └── repository.py      # Veritabanı erişim katmanı
├── services/              # Dış servis entegrasyonları
│   ├── azure_openai.py    # Azure OpenAI entegrasyonu
│   ├── embedding.py       # Gömme (embedding) servisi
│   └── custom_chat.py     # Özelleştirilmiş sohbet servisi
├── config/                # Yapılandırma
│   └── settings.py        # Uygulama ayarları
├── utils/                 # Yardımcı araçlar
│   └── logger.py          # Loglama yardımcıları
├── api.py                 # FastAPI arayüzü
├── gradio_app.py          # Gradio web arayüzü
├── streamlit_app.py       # Streamlit dashboard
└── cli.py                 # Komut satırı arayüzü
```

### LangGraph Akışı

Vira, şu adımları izleyen bir LangGraph akışı kullanır:

1. **process_input**: Kullanıcı girdisini işler ve analiz eder
2. **retrieve_memory**: İlgili hafıza öğelerini vektör benzerliğine göre getirir
3. **prepare_prompt**: Yanıt için gerekli içeriği hazırlar
4. **generate_response**: Azure OpenAI kullanarak yanıt üretir
5. **save_memory**: Etkileşimi uzun süreli hafızaya kaydeder

## Geliştirme

### Yeni Node Ekleme

LangGraph akışına yeni bir düğüm (node) eklemek için:

1. `vira/graph/nodes/` altında yeni bir Python modülü oluşturun
2. Düğüm fonksiyonunu tanımlayın
3. `vira/graph/build.py` içinde düğümü akışa ekleyin

### Test Etme

Testleri çalıştırmak için:

```bash
pytest
```

## Ortam Değişkenleri

| Değişken | Açıklama | Örnek Değer |
|----------|----------|------------|
| AZURE_OPENAI_API_KEY | Azure OpenAI API anahtarı | sk-... |
| AZURE_OPENAI_ENDPOINT | Azure OpenAI endpoint URL | https://your-resource.openai.azure.com/ |
| AZURE_OPENAI_API_VERSION | API versiyonu | 2023-12-01-preview |
| AZURE_OPENAI_DEPLOYMENT_NAME | Chat modeli deployment adı | gpt-4o-mini |
| AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME | Embedding modeli deployment adı | text-embedding-3-small |
| DB_HOST | PostgreSQL veritabanı sunucusu | localhost |
| DB_PORT | PostgreSQL port | 5432 |
| DB_NAME | Veritabanı adı | vira |
| DB_USER | Veritabanı kullanıcısı | postgres |
| DB_PASSWORD | Veritabanı şifresi | password |
| LOG_LEVEL | Loglama seviyesi | INFO |

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## Katkıda Bulunma

Katkıda bulunmak için lütfen bir Issue açın veya bir Pull Request gönderin.

---

Vira - Yol arkadaşı, alet değil.