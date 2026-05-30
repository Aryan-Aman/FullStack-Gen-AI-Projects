"""hf_asr_service.py - Audio transcription via Hugging Face Whisper."""

from huggingface_hub import InferenceClient
from app.utils.config import get_hf_token


def transcribe_audio_with_hf(audio_path: str) -> str:
    """Transcribe audio using HF Whisper. Returns transcription text or error string."""
    token = get_hf_token()
    if not token:
        return "❌ Error: HF_TOKEN is missing. Please add it to your .env file."

    try:
        client = InferenceClient(token=token)
        response = client.automatic_speech_recognition(
            audio_path,
            model="openai/whisper-large-v3"
        )

        # Handle varying response formats
        if isinstance(response, dict) and "text" in response:
            return response["text"]
        if hasattr(response, "text"):
            return response.text
        return str(response)

    except Exception:
        return "❌ Something went wrong while transcribing audio with Hugging Face. Please try again later."
