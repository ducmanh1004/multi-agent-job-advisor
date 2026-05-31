from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    async def generate_text(self, system: str, prompt: str) -> str:
        raise NotImplementedError

    async def generate_json(self, system: str, prompt: str) -> dict[str, Any]:
        text = await self.generate_text(system, prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("LLM did not return JSON; falling back to text wrapper")
            return {"text": text}


class LocalLLMProvider(LLMProvider):
    async def generate_text(self, system: str, prompt: str) -> str:
        return (
            "Local provider response. Configure OPENAI_API_KEY, GEMINI_API_KEY, "
            "ANTHROPIC_API_KEY, or OLLAMA_BASE_URL to enable model-backed generation."
        )


class OpenAIProvider(LLMProvider):
    async def generate_text(self, system: str, prompt: str) -> str:
        if not settings.openai_api_key:
            return await LocalLLMProvider().generate_text(system, prompt)
        payload = {
            "model": settings.openai_chat_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class OpenRouterProvider(LLMProvider):
    async def generate_text(self, system: str, prompt: str) -> str:
        if not settings.openrouter_api_key:
            return await LocalLLMProvider().generate_text(system, prompt)
        payload_base = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "X-Title": settings.openrouter_app_name,
        }
        if settings.openrouter_site_url:
            headers["HTTP-Referer"] = settings.openrouter_site_url

        models = [settings.openrouter_model_1]
        if settings.openrouter_model_2 and settings.openrouter_model_2 not in models:
            models.append(settings.openrouter_model_2)

        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=60) as client:
            for model in models:
                payload = {**payload_base, "model": model}
                try:
                    response = await client.post(
                        f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
                        json=payload,
                        headers=headers,
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                except Exception as exc:
                    last_error = exc
                    logger.warning("OpenRouter model %s failed: %s", model, exc)
        raise RuntimeError(f"OpenRouter generation failed: {last_error}") from last_error


class OllamaProvider(LLMProvider):
    async def generate_text(self, system: str, prompt: str) -> str:
        payload = {
            "model": "llama3.1",
            "prompt": f"{system}\n\n{prompt}",
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        return OpenAIProvider()
    if settings.llm_provider == "openrouter":
        return OpenRouterProvider()
    if settings.llm_provider == "ollama":
        return OllamaProvider()
    return LocalLLMProvider()
