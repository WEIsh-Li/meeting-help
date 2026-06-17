# Bilingual Meeting Copilot

V0.1 demonstrable MVP for a bilingual meeting assistant. This version focuses on a visible web interface, manual English transcript input, local Chinese translation preview, local knowledge upload, pending/submitted transcript state, and bilingual reply suggestions.

## V0.1 Scope

- React/Vite frontend with Chinese and English UI switching.
- FastAPI backend with meeting state, knowledge chunking/search, translation fallback, and deterministic reply generation.
- User-triggered reply generation only.
- API keys are not stored in frontend code.
- Real audio capture, real-time STT, Electron packaging, login, cloud sync, and OAuth are out of V0.1 scope.

## Run Backend

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload
```

Backend runs at `http://127.0.0.1:8000`.

## Run Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend runs at `http://127.0.0.1:5173`.

## Verify

```powershell
python -m pytest backend/tests -v
cd frontend
npm.cmd run build
```
