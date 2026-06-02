import os
import logging
import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        print(f"DEBUG: DEEPSEEK_API_KEY = {api_key[:10]}...")  # Mostra só os primeiros 10 caracteres
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set")

        # Cria um cliente httpx que ignora verificação SSL
        httpx_client = httpx.Client(verify=False)

        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            http_client=httpx_client,  # <-- passa o cliente customizado
            timeout=30.0,
            max_retries=3
        )
    return _client


def chat(prompt: str, system: str = "", temperature: float = 0.4, max_tokens: int = 500) -> str:
    """Single-turn chat completion. Returns the LLM's text response."""
    client = _get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

