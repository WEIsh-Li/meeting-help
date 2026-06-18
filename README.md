# Bilingual Meeting Copilot

V0.1 demonstrable MVP for a bilingual meeting assistant. This version focuses on a visible web interface, manual English transcript input, optional uploaded or live audio transcription, local or LibreTranslate Chinese translation, local knowledge upload, pending/submitted transcript state, and bilingual reply suggestions.

## V0.1 Scope

- React/Vite frontend with Chinese and English UI switching.
- FastAPI backend with meeting state, knowledge chunking/search, translation fallback, optional LibreTranslate integration, optional faster-whisper file and live-chunk transcription, and deterministic reply generation.
- User-triggered reply generation only.
- API keys are not stored in frontend code.
- Electron packaging, login, cloud sync, and OAuth are out of V0.1 scope.

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

Audio upload and live transcription use `faster-whisper` as an optional backend dependency. Install it only when you need speech recognition.

On Windows, use Python 3.11 or 3.12 for the speech environment:

```powershell
cd D:\cursor\projects\meeting_help
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
python -m pip install -r backend/requirements-speech.txt
```

Optional model settings:

```powershell
$env:WHISPER_MODEL_SIZE = "base"
$env:WHISPER_DEVICE = "cpu"
$env:WHISPER_COMPUTE_TYPE = "int8"
```

The first transcription may take longer because the Whisper model can be downloaded or initialized locally.

## Manual Validation Flow

Start the backend in one terminal:

```powershell
cd D:\cursor\projects\meeting_help
.\.venv\Scripts\Activate.ps1
$env:WHISPER_MODEL_SIZE = "base"
$env:WHISPER_DEVICE = "cpu"
$env:WHISPER_COMPUTE_TYPE = "int8"
python -m uvicorn app.main:app --app-dir backend --reload
```

Start the frontend in a second terminal:

```powershell
cd D:\cursor\projects\meeting_help\frontend
npm.cmd install
npm.cmd run dev
```

Open `http://127.0.0.1:5173`.

Test manual text:

1. Click `New Meeting`.
2. Paste English meeting text into the transcript composer.
3. Click `Add Segment`.
4. Confirm a bilingual segment appears.
5. Click `Generate Reply`.
6. Confirm bilingual reply suggestions appear.

Test uploaded audio:

1. Click `Upload Audio`.
2. Select an English audio file.
3. Wait for transcription.
4. Confirm the audio text appears as a new transcript segment.

Test live microphone:

1. Set `Audio Source` to `Microphone`.
2. Click `Start Live Transcription`.
3. Allow browser microphone permission.
4. Speak English for at least 6 seconds.
5. Confirm transcript segments appear.
6. Click `Stop Transcription`.

Test computer audio:

1. Play meeting audio or a video with English speech on the computer.
2. Set `Audio Source` to `Computer Audio`.
3. Click `Start Live Transcription`.
4. In the browser sharing prompt, select a tab, window, or screen and enable shared audio.
5. Let the audio play for at least 6 seconds.
6. Confirm transcript segments appear.
7. Click `Stop Transcription`.

If no transcript appears for computer audio, repeat the browser sharing step and make sure shared audio is enabled. Some browsers only expose tab audio, not every app's system audio.

## Verify

```powershell
cd D:\cursor\projects\meeting_help
python -m pytest backend/tests -v

cd D:\cursor\projects\meeting_help\frontend
npm.cmd test
npm.cmd run build
```
