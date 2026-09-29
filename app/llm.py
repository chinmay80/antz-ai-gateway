"""Thin Mistral client. Swap the base URL later to point at a self-hosted
vLLM server (it exposes the same OpenAI-style /chat/completions API)."""
import asyncio
import json
from collections.abc import AsyncIterator

import httpx

from .config import settings


class LLMError(Exception):
    pass


async def stream_chat(messages: list[dict]) -> AsyncIterator[str]:
    """Yield text deltas from the model."""
    if settings.mock_llm:
        for word in "This is a mock reply from the gateway. Streaming works.".split(" "):
            await asyncio.sleep(0.05)
            yield word + " "
        return

    if not settings.mistral_api_key:
        raise LLMError("MISTRAL_API_KEY is not set")

    payload = {
        "model": settings.mistral_model,
        "messages": messages,
        "stream": True,
        "temperature": 0.3,
        "max_tokens": 800,
    }
    headers = {"Authorization": f"Bearer {settings.mistral_api_key}"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
        async with client.stream(
            "POST", f"{settings.mistral_base_url}/chat/completions", json=payload, headers=headers
        ) as resp:
            if resp.status_code != 200:
                body = await resp.aread()
                raise LLMError(f"Model API error {resp.status_code}: {body[:300]!r}")
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0].get("delta", {}).get("content")
                if delta:
                    yield delta
