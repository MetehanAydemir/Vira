from typing import List, TypedDict, Optional
from langchain_core.messages import BaseMessage


class ViraState(TypedDict):
    """
    Grafımızın durumunu temsil eder.

    Attributes:
        user_id: Kullanıcı için benzersiz tanımlayıcı.
        original_message: Kullanıcıdan gelen ilk mesaj.
        processed_input: Sensory proxy mantığından gelen analiz edilmiş girdiyi içeren sözlük.
        memory_context: Veritabanından alınan ilgili anıları içeren bir dize.
        messages: LLM'e geçirilecek mesajların listesi.
        response: Yapay zeka tarafından üretilen nihai yanıt.
        is_omega_command: Girdinin özel bir komut olup olmadığını belirten bir boolean bayrağı.
    """
    user_id: str
    original_message: str
    processed_input: dict
    memory_context: str
    messages: List[BaseMessage]
    response: str
    is_omega_command: bool
