# Bilingual Meeting Copilot

V0.1 demonstrable MVP for a bilingual meeting assistant. This version focuses on a visible web interface, manual English transcript input, optional audio transcription, local or LibreTranslate Chinese translation, local knowledge upload, pending/submitted transcript state, and bilingual reply suggestions.

## V0.1 Scope

- React/Vite frontend with Chinese and English UI switching.
- FastAPI backend with meeting state, knowledge chunking/search, translation fallback, optional LibreTranslate integration, optional faster-whisper transcription, and deterministic reply generation.
- User-triggered reply generation only.
- API keys are not stored in frontend code.
- Real-time audio capture, Electron packaging, login, cloud sync, and OAuth are out of V0.1 scope.

## Run Backend

From the project root:

```powershell
cd D:\cursor\projects\meeting_help
python -m pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload
```

Backend runs at `http://127.0.0.1:8000`.

## Run Frontend

Open a second terminal:

```powershell
cd D:\cursor\projects\meeting_help\frontend
npm.cmd install
npm.cmd run dev
```

Frontend runs at `http://127.0.0.1:5173`.

## Enable LibreTranslate

The app works without LibreTranslate by using a local fallback preview. To use LibreTranslate, start a LibreTranslate service and set `LIBRETRANSLATE_URL` before starting the backend.

Example with Docker:

```powershell
docker run -it -p 5000:5000 libretranslate/libretranslate
```

Then start the backend in another terminal:

```powershell
$env:LIBRETRANSLATE_URL = "http://127.0.0.1:5000"
python -m uvicorn app.main:app --app-dir backend --reload
```

If your LibreTranslate service requires a key:

```powershell
$env:LIBRETRANSLATE_API_KEY = "your-key"
```

## Enable Audio Transcription

Audio upload uses `faster-whisper` as an optional backend dependency. Install it only when you need speech recognition:

```powershell
cd D:\cursor\projects\meeting_help
python -m pip install -r backend/requirements-speech.txt
```

Optional model settings:

```powershell
$env:WHISPER_MODEL_SIZE = "base"
$env:WHISPER_DEVICE = "cpu"
$env:WHISPER_COMPUTE_TYPE = "int8"
```

The first transcription may take longer because the Whisper model can be downloaded or initialized locally.

## Verify

```powershell
cd D:\cursor\projects\meeting_help
python -m pytest backend/tests -v

cd D:\cursor\projects\meeting_help\frontend
npm.cmd test
npm.cmd run build
```
