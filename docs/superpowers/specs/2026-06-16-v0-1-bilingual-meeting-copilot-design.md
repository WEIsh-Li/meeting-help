# V0.1 Bilingual Meeting Copilot Design

## Goal

Build the V0.1 demonstrable MVP for Bilingual Meeting Copilot. The first version must be visible in the browser, support Chinese and English UI switching, and demonstrate the core loop from meeting transcript input to knowledge-enhanced bilingual reply suggestions.

## Scope

V0.1 implements the PRD milestone "可演示原型":

- Main application UI with a top control bar and left/right workspace.
- Manual English meeting transcript input to simulate real-time transcription.
- Local Chinese translation display for each transcript segment.
- Segment buffer with submitted and pending states.
- Upload local knowledge files for demo retrieval.
- Generate bilingual reply suggestions from pending meeting content.
- Show intent, Chinese understanding, Chinese reply advice, English ready-to-say answer, short English answer, follow-up question, confidence, and knowledge sources.
- Copy English answer.
- New meeting, pause/resume, end meeting, and clear meeting records.
- Full UI language toggle between Chinese and English.

V0.1 does not implement real system audio capture, microphone capture, cloud real-time STT, Electron packaging, login, OAuth, team collaboration, cloud knowledge sync, or automatic speech output.

## Architecture

Use a Web MVP with a local API boundary:

- `frontend/`: React, TypeScript, Vite. It owns visual layout, UI language switching, user interaction, and API calls.
- `backend/`: FastAPI. It owns meeting state, knowledge processing, reply generation orchestration, and security-sensitive configuration.
- `backend/app/domain/`: pure business logic for meetings, knowledge search, translation fallback, and reply generation.
- `backend/app/api/`: HTTP routes and request/response schemas.
- `backend/tests/`: tests for domain behavior and API safety.

This structure keeps the UI visible quickly while preserving clean integration boundaries for the V0.2 Electron and audio work.

## Data Flow

1. User creates or opens a local demo meeting.
2. User enters an English meeting sentence and clicks Add Segment.
3. Backend creates a transcript segment with English text, local Chinese translation, source, timestamp, and `submitted=false`.
4. Frontend renders the segment in the left pane.
5. User uploads one or more knowledge files. V0.1 supports `.txt` and `.md` directly. PDF/DOCX are represented in the API contract and return a clear unsupported-parser message until parser dependencies are added.
6. Backend chunks knowledge text and stores chunks locally in memory for the running process.
7. User clicks Generate Reply or presses the page-level shortcut.
8. Backend reads only pending segments, retrieves top knowledge chunks, assembles a bounded context, and generates a structured reply.
9. If reply generation succeeds, backend marks only those pending segments as submitted.
10. If generation fails, pending segments remain unsubmitted.

## AI Strategy

The backend supports two modes:

- Local deterministic demo mode when no `OPENAI_API_KEY` is present. This returns structured replies using intent heuristics and retrieved knowledge snippets.
- Optional OpenAI-compatible mode is represented by a backend-only provider interface in V0.1. The implementation reads API keys only from backend environment variables when enabled.

V0.1 must not put API keys in frontend code, browser storage, or committed files.

## UI Design

The application uses a work-focused dashboard layout:

- Top bar: meeting name, status, New, Pause/Resume, End, Clear, Upload Knowledge, language toggle, model status.
- Left pane: bilingual transcript feed, submitted divider, pending highlight, manual transcript composer.
- Right pane: AI reply result with intent, Chinese understanding, response strategy, bilingual answers, knowledge sources, copy button, and a visible follow-up input disabled with a V0.1 note.
- Settings/security notice area: explains that AI is called only when the user triggers reply generation and only pending text plus retrieved snippets are sent.

The UI language toggle must switch all operational labels, empty states, buttons, status text, section headings, and notices between Chinese and English.

## Security and Privacy

- No secrets in frontend source.
- No committed `.env` files.
- AI generation is user-triggered only.
- Reply requests send only pending transcript content and top retrieved snippets.
- Knowledge files remain local to the backend process in V0.1.
- Clear Meeting removes local meeting segments and reply state.
- AI failure does not mark segments as submitted.
- CORS is restricted to local development origins.

## Error Handling

- Empty transcript input returns a user-visible validation error.
- Generate Reply with no pending segments returns a user-visible message and does not mutate state.
- Knowledge upload with unsupported file type returns a clear error.
- AI generation failure keeps pending segments unchanged.
- Translation fallback always preserves English text if Chinese translation is unavailable.

## Testing

Backend tests cover:

- Pending segments are selected once and marked submitted only after successful reply generation.
- No pending segment produces a clear error.
- Knowledge search returns relevant chunks and source names.
- Reply generator returns required structured fields.
- AI failure preserves pending segment state.

Frontend tests or build checks cover:

- TypeScript compilation.
- UI language dictionary completeness for Chinese and English.
- Production build succeeds.

## Acceptance Criteria

- Running the app shows a visible bilingual meeting assistant page.
- User can switch UI between Chinese and English.
- User can add English meeting content and see bilingual transcript cards.
- Pending and submitted transcript states are visually distinct.
- User can upload local text or markdown knowledge files.
- User can generate a structured bilingual reply from pending content.
- English answer can be copied from the UI.
- Clear Meeting removes transcript and reply state.
- Backend tests pass.
- Frontend build passes.
