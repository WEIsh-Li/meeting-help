from __future__ import annotations

import re


class TranslationService:
    def __init__(self) -> None:
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

    def translate(self, text_en: str) -> str:
        normalized = text_en.strip()
        if not normalized:
            return ""
        lowered = normalized.lower()
        matched = [cn for en, cn in self._phrases.items() if en in lowered]
        if matched:
            return "；".join(dict.fromkeys(matched)) + "。"
        compact = re.sub(r"\s+", " ", normalized)
        return f"本地翻译预览：{compact}"

