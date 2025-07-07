import logging
import json
from typing import Dict, Any

# JSON formatlayıcı
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
            "funcName": record.funcName,
        }
        # Ekstra verileri ekle
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
            
        return json.dumps(log_record, ensure_ascii=False)

# get_logger fonksiyonunu güncelleyebilir veya yeni bir tane oluşturabiliriz.
# Şimdilik basit tutalım ve adaptör kullanalım.

class ViraLoggerAdapter(logging.LoggerAdapter):
    """
    Log kayıtlarına otomatik olarak session_id ve diğer bağlamsal
    verileri ekleyen bir adaptör.
    """
    def process(self, msg, kwargs):
        # 'extra' sözlüğünü al veya oluştur
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        # Adaptör başlatılırken verilen ekstra verileri ekle
        kwargs['extra'].update(self.extra)
        
        # Mesajın kendisi bir dict ise, onu 'data' anahtarı altına al
        if isinstance(msg, dict):
            # 'message' anahtarını logdan çıkar, ana mesaj olarak kullan
            message = msg.pop('message', 'Structured log event')
            kwargs['extra']['data'] = msg
            return message, kwargs
            
        return msg, kwargs

# Kullanım:
# logger = logging.getLogger(__name__)
# adapter = ViraLoggerAdapter(logger, {'session_id': 'some-uuid'})
# adapter.info("Bu bir testtir")