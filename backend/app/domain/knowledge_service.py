from __future__ import annotations

import re

from .models import KnowledgeChunk, new_id


class KnowledgeService:
    def __init__(self) -> None:
        self._chunks: list[KnowledgeChunk] = []

    def add_text_file(self, filename: str, content: str) -> list[KnowledgeChunk]:
        if not filename.lower().endswith((".txt", ".md")):
            raise ValueError("V0.1 supports .txt and .md knowledge files")
        cleaned = content.strip()
        if not cleaned:
            raise ValueError("Knowledge file is empty")
        chunks = []
        for index, chunk_text in enumerate(self._chunk(cleaned)):
            chunk = KnowledgeChunk(
                id=new_id("chunk"),
                source=filename,
                content=chunk_text,
                chunk_index=index,
            )
            self._chunks.append(chunk)
            chunks.append(chunk)
        return chunks

    def list_chunks(self) -> list[KnowledgeChunk]:
        return list(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()

    def search(self, query: str, limit: int = 5) -> list[KnowledgeChunk]:
        query_terms = self._terms(query)
        if not query_terms:
            return []
        scored = []
        for chunk in self._chunks:
            content_terms = self._terms(chunk.content)
            overlap = query_terms & content_terms
            if overlap:
                scored.append(
                    KnowledgeChunk(
                        id=chunk.id,
                        source=chunk.source,
                        content=chunk.content,
                        chunk_index=chunk.chunk_index,
                        score=len(overlap) / max(len(query_terms), 1),
                    )
                )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]

    def _chunk(self, text: str, size: int = 700) -> list[str]:
        paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs or [text]:
            if len(current) + len(paragraph) > size and current:
                chunks.append(current.strip())
                current = paragraph
            else:
                current = f"{current}\n\n{paragraph}".strip()
        if current:
            chunks.append(current.strip())
        return chunks

    def _terms(self, text: str) -> set[str]:
        return {term for term in re.findall(r"[a-zA-Z][a-zA-Z-]{2,}", text.lower())}

