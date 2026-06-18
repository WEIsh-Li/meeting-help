from __future__ import annotations

import os
import re
from typing import Protocol

import httpx


class TranslationClient(Protocol):
    def translate(self, text: str, source: str, target: str) -> str:
        ...


class LibreTranslateClient:
    def __init__(self, base_url: str, api_key: str = "", timeout_seconds: float = 6.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def translate(self, text: str, source: str, target: str) -> str:
        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": "text",
        }
        if self._api_key:
            payload["api_key"] = self._api_key

        response = httpx.post(f"{self._base_url}/translate", json=payload, timeout=self._timeout_seconds)
        response.raise_for_status()
        translated = response.json().get("translatedText", "")
        if not isinstance(translated, str) or not translated.strip():
            raise RuntimeError("LibreTranslate returned an empty translation")
        return translated.strip()


class TranslationService:
    def __init__(self, libretranslate_client: TranslationClient | None = None) -> None:
        self._phrases = {
            "what is your suggestion": "你的建议是什么",
            "client": "客户",
            "workflow": "流程",
            "too complex": "过于复杂",
            "first-time users": "首次使用者",
            "mvp": "MVP",
            "release": "发布",
            "risk": "风险",
            "onboarding": "新用户引导",
        }
        self._libretranslate_client = libretranslate_client or self._client_from_env()

    def translate(self, text_en: str) -> str:
        normalized = text_en.strip()
        if not normalized:
            return ""
        if self._libretranslate_client:
            try:
                return self._libretranslate_client.translate(normalized, "en", "zh")
            except Exception:
                pass
        return self._fallback_translate(normalized)

    def _fallback_translate(self, normalized: str) -> str:
        lowered = normalized.lower()
        matched = [cn for en, cn in self._phrases.items() if en in lowered]
        if matched:
            return "，".join(dict.fromkeys(matched)) + "。"
        compact = re.sub(r"\s+", " ", normalized)
        return f"本地翻译预览：{compact}"

    def _client_from_env(self) -> TranslationClient | None:
        base_url = os.getenv("LIBRETRANSLATE_URL", "").strip()
        if not base_url:
            return None
        return LibreTranslateClient(base_url=base_url, api_key=os.getenv("LIBRETRANSLATE_API_KEY", "").strip())
