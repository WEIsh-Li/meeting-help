from app.domain.knowledge_service import KnowledgeService
from app.domain.reply_service import ReplyService
from app.domain.translation_service import TranslationService


class FakeLibreTranslateClient:
    def __init__(self, translated_text: str | None = None, error: Exception | None = None) -> None:
        self.translated_text = translated_text
        self.error = error
        self.requests: list[tuple[str, str, str]] = []

    def translate(self, text: str, source: str, target: str) -> str:
        self.requests.append((text, source, target))
        if self.error:
            raise self.error
        return self.translated_text or ""


def test_translation_service_returns_readable_chinese_for_known_terms():
    translator = TranslationService()

    translated = translator.translate("The client is concerned that the workflow is too complex for first-time users.")

    assert "客户" in translated
    assert "流程" in translated
    assert "过于复杂" in translated
    assert "首次使用者" in translated


def test_translation_service_uses_libretranslate_when_configured():
    client = FakeLibreTranslateClient(translated_text="客户认为入门流程过于复杂。")
    translator = TranslationService(libretranslate_client=client)

    translated = translator.translate("The client thinks onboarding is too complex.")

    assert translated == "客户认为入门流程过于复杂。"
    assert client.requests == [("The client thinks onboarding is too complex.", "en", "zh")]


def test_translation_service_falls_back_when_libretranslate_fails():
    client = FakeLibreTranslateClient(error=RuntimeError("service unavailable"))
    translator = TranslationService(libretranslate_client=client)

    translated = translator.translate("The client is concerned that the workflow is too complex.")

    assert "客户" in translated
    assert "流程" in translated


def test_knowledge_search_returns_relevant_sources():
    service = KnowledgeService()
    service.add_text_file(
        filename="prd.md",
        content="The MVP should keep onboarding simple and reduce first-time user friction.",
    )
    service.add_text_file(
        filename="notes.md",
        content="Database backup jobs run every night and are not related to onboarding.",
    )

    results = service.search("client worried about onboarding complexity", limit=1)

    assert len(results) == 1
    assert results[0].source == "prd.md"
    assert "onboarding" in results[0].content


def test_reply_generator_returns_required_bilingual_fields():
    knowledge = KnowledgeService()
    knowledge.add_text_file(
        filename="prd.md",
        content="For the MVP, simplify the first-time user flow and keep risky features out of scope.",
    )
    translator = TranslationService()
    reply_service = ReplyService()

    transcript_en = "The client is concerned that the workflow may be too complex for first-time users."
    transcript_cn = translator.translate(transcript_en)
    retrieved = knowledge.search(transcript_en, limit=3)

    reply = reply_service.generate(
        transcript_en=transcript_en,
        transcript_cn=transcript_cn,
        retrieved_knowledge=retrieved,
        meeting_summary="The team is discussing MVP scope.",
    )

    assert reply.intent == "risk_or_issue"
    assert reply.need_response is True
    assert reply.summary_cn
    assert reply.strategy_cn
    assert reply.answer_cn
    assert reply.answer_en
    assert reply.short_answer_en
    assert reply.follow_up_question_en
    assert reply.confidence in {"low", "medium", "high"}
    assert reply.knowledge_used[0].source == "prd.md"
