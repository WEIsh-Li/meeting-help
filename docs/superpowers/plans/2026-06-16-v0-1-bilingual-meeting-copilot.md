# V0.1 Bilingual Meeting Copilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a visible V0.1 bilingual meeting assistant MVP with manual transcript input, knowledge upload, bilingual reply generation, and Chinese/English UI switching.

**Architecture:** The project uses a React/Vite frontend and a FastAPI backend. Backend domain modules own meeting state, knowledge search, local translation fallback, and reply generation; API modules expose a small local HTTP contract. Frontend modules own layout, i18n, API calls, and user interactions.

**Tech Stack:** React, TypeScript, Vite, Python FastAPI, pytest, in-memory V0.1 storage, local deterministic AI fallback.

---

## File Structure

- Create `backend/requirements.txt`: Python runtime and test dependencies.
- Create `backend/app/main.py`: FastAPI app, CORS, router registration.
- Create `backend/app/api/routes.py`: HTTP endpoints.
- Create `backend/app/api/schemas.py`: Pydantic request and response models.
- Create `backend/app/domain/models.py`: dataclasses and typed domain structures.
- Create `backend/app/domain/meeting_service.py`: meeting lifecycle and segment submission state.
- Create `backend/app/domain/knowledge_service.py`: text/markdown upload, chunking, lexical retrieval.
- Create `backend/app/domain/translation_service.py`: deterministic English-to-Chinese demo translation fallback.
- Create `backend/app/domain/reply_service.py`: intent detection and structured bilingual reply generation.
- Create `backend/tests/test_meeting_service.py`: submitted-state behavior.
- Create `backend/tests/test_knowledge_reply.py`: retrieval and reply behavior.
- Create `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/index.html`: React/Vite project shell.
- Create `frontend/src/api.ts`: typed API client.
- Create `frontend/src/i18n.ts`: complete Chinese/English UI dictionary.
- Create `frontend/src/types.ts`: frontend DTOs.
- Create `frontend/src/App.tsx`: application shell and interactions.
- Create `frontend/src/main.tsx`, `frontend/src/styles.css`: rendering and visual design.
- Modify `README.md`: local development instructions.
- Modify `.gitignore`: Python, frontend, and local runtime ignores.

## Tasks

### Task 1: Backend Domain

- [ ] Write tests proving pending segments are selected once and successful replies mark them submitted.
- [ ] Implement meeting service with create, pause, resume, end, clear, add segment, pending lookup, and submit marking.
- [ ] Run `python -m pytest backend/tests/test_meeting_service.py -v`.

### Task 2: Knowledge and Reply Core

- [ ] Write tests proving knowledge search returns relevant chunks and reply generation contains required structured fields.
- [ ] Implement knowledge chunking and lexical scoring.
- [ ] Implement translation fallback and deterministic reply generator.
- [ ] Run `python -m pytest backend/tests/test_knowledge_reply.py -v`.

### Task 3: Backend API

- [ ] Implement Pydantic schemas and FastAPI routes for health, meeting state, segment creation, knowledge upload, reply generation, and clear.
- [ ] Add CORS restricted to local development origins.
- [ ] Run all backend tests with `python -m pytest backend/tests -v`.

### Task 4: Frontend MVP

- [ ] Create React/Vite app structure.
- [ ] Implement API client and shared types.
- [ ] Implement Chinese/English i18n dictionary and language toggle.
- [ ] Implement top bar, transcript pane, reply pane, knowledge upload, add segment, generate reply, copy English answer, clear meeting.
- [ ] Run `npm.cmd install` in `frontend` and `npm.cmd run build`.

### Task 5: Documentation, Verification, and Sync

- [ ] Update README with setup and run instructions.
- [ ] Verify backend tests pass.
- [ ] Verify frontend build passes.
- [ ] Commit implementation.
- [ ] Push `feature/v0-1-mvp` to GitHub.

