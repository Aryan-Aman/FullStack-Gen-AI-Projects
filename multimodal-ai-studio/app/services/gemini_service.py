"""gemini_service.py - Gemini API integration for text, image, audio, and video."""

import time
from google import genai
from google.genai import types
from app.utils.config import get_gemini_api_key

def _get_client():
    """Create and return a Gemini client, or None if key is missing."""
    api_key = get_gemini_api_key()
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def wait_for_file_active(client, uploaded_file, max_wait_seconds=180):
    """Poll until an uploaded file reaches ACTIVE state, or return None on timeout/failure."""
    elapsed = 0
    wait_interval = 5

    while elapsed < max_wait_seconds:
        file_info = client.files.get(name=uploaded_file.name)

        if file_info.state.name == "ACTIVE":
            return file_info
        if file_info.state.name == "FAILED":
            return None

        time.sleep(wait_interval)
        elapsed += wait_interval

    return None


# --- 1. Text → Text ---

def generate_text_response(
    prompt: str,
    model: str = "gemini-2.0-flash",
    temperature: float = 0.7
) -> str:
    """Generate a text response from Gemini given a prompt."""
    client = _get_client()
    if not client:
        return "❌ Error: Gemini API key is missing. Please add it to your .env file."

    try:
        config = types.GenerateContentConfig(temperature=temperature)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        return response.text

    except Exception:
        return "❌ Something went wrong while generating the text response. Please try again later."


def analyze_image(image_path: str, question: str) -> str:
    """Upload an image to Gemini and ask a question about it."""
    client = _get_client()
    if not client:
        return "❌ Error: Gemini API key is missing. Please add it to your .env file."

    try:
        uploaded_file = client.files.upload(file=image_path)
        active_file = wait_for_file_active(client, uploaded_file)
        if not active_file:
            return "❌ The image could not be processed by Gemini. Please try a different file."

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[active_file, question]
        )
        return response.text

    except Exception:
        return "❌ Something went wrong while analyzing the image. Please try again later."


def transcribe_audio(audio_path: str) -> str:
    """Upload an audio file to Gemini and return its transcription."""
    client = _get_client()
    if not client:
        return "❌ Error: Gemini API key is missing. Please add it to your .env file."

    try:
        uploaded_file = client.files.upload(file=audio_path)
        active_file = wait_for_file_active(client, uploaded_file)
        if not active_file:
            return "❌ The audio file could not be processed by Gemini. Please try a different file."

        instruction = "Transcribe this audio clearly. Return only the transcription text."
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[active_file, instruction]
        )
        return response.text

    except Exception:
        return "❌ Something went wrong while transcribing the audio. Please try again later."


def summarize_video(video_path: str) -> str:
    """Upload a video to Gemini and return a summary with key points."""
    client = _get_client()
    if not client:
        return "❌ Error: Gemini API key is missing. Please add it to your .env file."

    try:
        uploaded_file = client.files.upload(file=video_path)
        active_file = wait_for_file_active(client, uploaded_file)
        if not active_file:
            return "❌ The video file could not be processed by Gemini. Please try a different file."

        instruction = "Summarize this video. Provide a short summary and 5 key points."
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[active_file, instruction]
        )
        return response.text

    except Exception:
        return "❌ Something went wrong while summarizing the video. Please try again later."

