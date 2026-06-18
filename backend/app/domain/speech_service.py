from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class SpeechUnavailableError(RuntimeError):
    pass


class SpeechService:
    def __init__(
        self,
        model_size: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
    ) -> None:
        self._model_size = model_size or os.getenv("WHISPER_MODEL_SIZE", "base")
        self._device = device or os.getenv("WHISPER_DEVICE", "cpu")
        self._compute_type = compute_type or os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        self._model: Any | None = None

    def transcribe(self, audio_path: Path) -> str:
        if not audio_path.exists():
            raise ValueError("Audio file not found")
        model = self._load_model()
        segments, _info = model.transcribe(str(audio_path), vad_filter=True)
        transcript = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
        if not transcript:
            raise ValueError("No speech was recognized in the audio file")
        return transcript

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise SpeechUnavailableError(
                "faster-whisper is not installed. Install backend/requirements-speech.txt to enable audio transcription."
            ) from exc
        try:
            self._model = WhisperModel(self._model_size, device=self._device, compute_type=self._compute_type)
        except Exception as exc:
            raise SpeechUnavailableError(f"faster-whisper model is not available: {exc}") from exc
        return self._model
