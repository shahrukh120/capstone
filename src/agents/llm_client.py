"""Unified LLM client — routes to Groq or Ollama based on settings."""
import json
import logging
import requests
from groq import Groq
from config.settings import settings

logger = logging.getLogger(__name__)


def llm_chat(
    system_prompt: str,
    user_prompt: str,
    provider: str = None,
    temperature: float = 0.1,
    max_tokens: int = 1500,
    json_mode: bool = True,
) -> str:
    """Send a chat completion request to the active LLM provider.

    Returns the raw response text.
    """
    provider = provider or settings.llm_provider

    if provider == "groq":
        return _groq_chat(system_prompt, user_prompt, temperature, max_tokens, json_mode)
    elif provider == "ollama":
        return _ollama_chat(system_prompt, user_prompt, temperature, max_tokens, json_mode)
    elif provider == "nvidia":
        return _nvidia_chat(system_prompt, user_prompt, temperature, max_tokens, json_mode)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def llm_chat_json(
    system_prompt: str,
    user_prompt: str,
    provider: str = None,
    temperature: float = 0.1,
    max_tokens: int = 1500,
) -> dict:
    """Send a chat completion and parse the response as JSON."""
    text = llm_chat(system_prompt, user_prompt, provider, temperature, max_tokens, json_mode=True)
    return json.loads(text)


def _groq_chat(system_prompt, user_prompt, temperature, max_tokens, json_mode):
    client = Groq(api_key=settings.groq_api_key, timeout=30.0, max_retries=2)
    kwargs = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def _ollama_chat(system_prompt, user_prompt, temperature, max_tokens, json_mode):
    prompt = f"{system_prompt}\n\n{user_prompt}"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    if json_mode:
        payload["format"] = "json"

    response = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]


def _nvidia_chat(system_prompt, user_prompt, temperature, max_tokens, json_mode):
    """Send a chat completion request to NVIDIA NIM API (OpenAI-compatible)."""
    headers = {
        "Authorization": f"Bearer {settings.nvidia_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.nvidia_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    response = requests.post(
        f"{settings.nvidia_base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    # Strip markdown code fences if present (NVIDIA models often wrap JSON)
    content = content.strip()
    if content.startswith("```"):
        # Remove first line (```json or ```)
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()
