"""hf_audio_service.py - Text-to-speech with HF API and local pyttsx3 fallback."""

from pathlib import Path
import requests
import pyttsx3
from app.utils.config import get_hf_token

API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"


def _offline_tts(text: str) -> bytes | str | None:
    """Local TTS fallback using pyttsx3 when HF API is unreachable."""
    try:
        output_dir = Path("app/temp")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "generated_speech.wav"

        engine = pyttsx3.init()
        engine.save_to_file(text, str(output_path))
        engine.runAndWait()

        if output_path.exists():
            return output_path.read_bytes()
        return "❌ Offline TTS failed: audio file was not created."

    except Exception:
        return "❌ Offline text-to-speech failed. Please check your system audio configuration."


def generate_speech_from_text(text: str) -> bytes | str | None:
    """Generate speech from text. Tries HF first, falls back to pyttsx3."""
    token = get_hf_token()
    if not token:
        return _offline_tts(text)

    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"inputs": text},
            timeout=30
        )

        content_type = response.headers.get("content-type", "")
        if response.status_code == 200 and (
            content_type.startswith("audio")
            or content_type.startswith("application/octet-stream")
        ):
            return response.content

        # Non-audio response from HF — use local fallback
        return _offline_tts(text)

    except Exception:
        return _offline_tts(text)

