"""model_router.py - Routes requests to the selected provider."""

from app.services.gemini_service import generate_text_response, analyze_image, transcribe_audio, summarize_video
from app.services.hf_image_service import generate_image_from_text
from app.services.hf_asr_service import transcribe_audio_with_hf
from app.services.hf_video_service import summarize_video_with_hf
from app.services.openrouter_video_service import summarize_video_with_openrouter_frames
from app.services.openrouter_service import (
    generate_openrouter_response,
    analyze_image_with_openrouter,
    generate_image_with_openrouter,
)


def generate_text_with_provider(provider: str, prompt: str, model: str, temperature: float) -> str:
    """Route text generation to the selected provider."""
    if provider == "Gemini":
        return generate_text_response(prompt, model=model, temperature=temperature)
    elif provider == "OpenRouter":
        return generate_openrouter_response(prompt, model=model, temperature=temperature)
    return "❌ Unsupported provider selected."


def analyze_image_with_provider(provider: str, image_path: str, question: str, model: str, temperature: float) -> str:
    """Route image analysis to the selected provider."""
    if provider == "Gemini":
        return analyze_image(image_path, question)
    elif provider == "OpenRouter":
        return analyze_image_with_openrouter(image_path, question, model=model, temperature=temperature)
    return "❌ Unsupported provider selected."


def generate_image_with_provider(provider: str, prompt: str, model: str = None, temperature: float = 0.7):
    """Route image generation to the selected provider."""
    if provider == "Hugging Face":
        return generate_image_from_text(prompt)
    elif provider == "OpenRouter":
        return generate_image_with_openrouter(prompt=prompt, model=model, temperature=temperature)
    return "❌ Unsupported image generation provider selected."


def transcribe_audio_with_provider(provider: str, audio_path: str, model: str = None) -> str:
    """Route audio transcription to the selected provider. Gemini falls back to HF on failure."""
    if provider == "Gemini":
        result = transcribe_audio(audio_path)
        if result.startswith("❌"):
            return transcribe_audio_with_hf(audio_path)
        return result
    elif provider == "Hugging Face":
        return transcribe_audio_with_hf(audio_path)
    return "❌ Unsupported audio transcription provider selected."


def summarize_video_with_provider(provider: str, video_path: str) -> str:
    """Route video summarization to the selected provider. Gemini falls back to OpenRouter."""
    if provider == "Gemini":
        result = summarize_video(video_path)
        if result.startswith("❌"):
            return summarize_video_with_openrouter_frames(video_path)
        return result
    elif provider == "Hugging Face Fallback":
        return summarize_video_with_hf(video_path)
    elif provider == "OpenRouter Frame Fallback":
        return summarize_video_with_openrouter_frames(video_path)
    return "❌ Unsupported video summary provider selected."
