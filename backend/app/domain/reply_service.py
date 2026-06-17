from __future__ import annotations

from .models import KnowledgeChunk, KnowledgeUse, Reply


class ReplyService:
    def generate(
        self,
        transcript_en: str,
        transcript_cn: str,
        retrieved_knowledge: list[KnowledgeChunk],
        meeting_summary: str,
    ) -> Reply:
        intent = self._detect_intent(transcript_en)
        has_knowledge = bool(retrieved_knowledge)
        source_clause = " based on the available knowledge" if has_knowledge else ""
        answer_en = self._answer_en(intent, transcript_en, source_clause)
        knowledge_used = [
            KnowledgeUse(source=item.source, reason="Matched the current meeting context.")
            for item in retrieved_knowledge[:3]
        ]
        return Reply(
            intent=intent,
            need_response=intent != "description",
            summary_cn=transcript_cn or "对方提出了与当前会议相关的新信息。",
            strategy_cn=self._strategy_cn(intent, has_knowledge),
            answer_cn=self._answer_cn(intent, has_knowledge),
            answer_en=answer_en,
            short_answer_en=self._short_answer_en(intent),
            follow_up_question_en=self._follow_up(intent),
            knowledge_used=knowledge_used,
            confidence="high" if has_knowledge else "medium",
        )

    def _detect_intent(self, text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["concern", "worried", "risk", "issue", "complex"]):
            return "risk_or_issue"
        if "?" in text or any(word in lowered for word in ["what", "how", "could", "should", "can we"]):
            return "question"
        if any(word in lowered for word in ["suggestion", "opinion", "recommend"]):
            return "request_opinion"
        return "description"

    def _strategy_cn(self, intent: str, has_knowledge: bool) -> str:
        suffix = "并结合命中的知识库依据。" if has_knowledge else "如信息不足，保持稳妥并请求确认。"
        if intent == "risk_or_issue":
            return f"先认可风险，再提出降低复杂度和交付风险的回应。{suffix}"
        if intent == "question":
            return f"直接回答问题，先给结论再补充理由。{suffix}"
        return f"先总结对方信息，再给出可追问点。{suffix}"

    def _answer_cn(self, intent: str, has_knowledge: bool) -> str:
        if intent == "risk_or_issue":
            return "这是一个合理的担忧。建议先简化首次使用流程，减少必要步骤，并增加清晰的新手引导。"
        if has_knowledge:
            return "根据当前资料，建议优先保证 MVP 范围清晰，把高风险能力放到后续阶段。"
        return "我建议先确认这是 MVP 必需项还是后续优化项，再决定是否纳入当前版本。"

    def _answer_en(self, intent: str, transcript_en: str, source_clause: str) -> str:
        if intent == "risk_or_issue":
            return (
                "That is a valid concern. We can simplify the first-time user flow by reducing "
                f"required steps and adding clearer onboarding guidance{source_clause}."
            )
        if intent == "question":
            return f"My suggestion is to keep the MVP focused and move higher-risk items to a later phase{source_clause}."
        return f"I understand the point. We can summarize the impact first and then confirm the next decision{source_clause}."

    def _short_answer_en(self, intent: str) -> str:
        if intent == "risk_or_issue":
            return "We can reduce risk by simplifying the first-time user flow."
        if intent == "question":
            return "I suggest keeping the MVP focused."
        return "Let me summarize the impact and confirm the next step."

    def _follow_up(self, intent: str) -> str:
        if intent == "risk_or_issue":
            return "Do we know which step is causing the most friction for first-time users?"
        if intent == "question":
            return "Could we confirm whether this is required for the MVP?"
        return "Could you clarify what decision we need to make from this point?"

