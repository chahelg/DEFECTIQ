from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, AsyncIterator

import httpx
import requests

from app.core.config import settings


@dataclass(slots=True)
class ChatModelResponse:
    content: str
    tokens: list[str] | None = None


class ChatModelProvider:
    async def generate(self, system_prompt: str, user_prompt: str, stream: bool = False) -> ChatModelResponse:
        raise NotImplementedError

    async def stream(self, system_prompt: str, user_prompt: str) -> AsyncIterator[str]:
        response = await self.generate(system_prompt, user_prompt)
        for token in (response.tokens or response.content.split()):
            await asyncio.sleep(0.02)
            yield token + " "


class OpenAIChatProvider(ChatModelProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def generate(self, system_prompt: str, user_prompt: str, stream: bool = False) -> ChatModelResponse:
        if not self.enabled:
            raise RuntimeError("OpenAI provider is not configured")

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "stream": False,
            },
            timeout=45,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return ChatModelResponse(content=content, tokens=content.split())


class GeminiChatProvider(ChatModelProvider):
    def __init__(self, api_key: str | None = None, api_url: str | None = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.api_url = api_url or settings.GEMINI_API_URL

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def generate(self, system_prompt: str, user_prompt: str, stream: bool = False) -> ChatModelResponse:
        if not self.api_key:
            return await RuleBasedChatProvider().generate(system_prompt, user_prompt)

        prompt = f"{system_prompt}\n\n{user_prompt}".strip()
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates") or []
        if not candidates:
            return ChatModelResponse(content="I couldn't generate a response from Gemini.", tokens=["I", "couldn't", "generate", "a", "response", "from", "Gemini."])

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            text = "I couldn't generate a response from Gemini."
        return ChatModelResponse(content=text, tokens=text.split())


class RuleBasedChatProvider(ChatModelProvider):
    async def generate(self, system_prompt: str, user_prompt: str, stream: bool = False) -> ChatModelResponse:
        prompt = f"{system_prompt}\n{user_prompt}".lower()
        if "highest backlog" in prompt or "backlog" in prompt:
            content = "Assignment Group A has the highest backlog (42 open defects)."
        elif "older than 7 days" in prompt:
            content = "There are 13 unresolved SCM defects older than 7 days."
        elif "finance" in prompt and "increasing" in prompt:
            content = (
                "Trend analysis indicates recent deployments and increased load on finance services. "
                "Root causes appear to be malformed data and a recent SLA breach."
            )
        else:
            content = "I couldn't find a direct answer; try refining the query or ask for a trend summary."
        return ChatModelResponse(content=content, tokens=content.split())
