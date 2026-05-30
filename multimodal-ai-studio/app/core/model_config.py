"""
model_config.py - Model and provider configuration for the Streamlit UI.

This file stores available providers, model lists, and default settings.
No API calls are made here — this is purely configuration.
"""

# Available providers for text generation
TEXT_PROVIDERS = ["Gemini", "OpenRouter"]

# Gemini models available for text generation
GEMINI_TEXT_MODELS = [
    "gemini-2.0-flash"
]

# OpenRouter models available for text generation (free tier)
OPENROUTER_TEXT_MODELS = [
    "openrouter/free",
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "deepseek/deepseek-r1:free"
]

# Default temperature for text generation
DEFAULT_TEMPERATURE = 0.7

# Available providers for image analysis (vision)
IMAGE_ANALYSIS_PROVIDERS = ["Gemini", "OpenRouter"]

# OpenRouter vision-capable models for image analysis
OPENROUTER_VISION_MODELS = [
    "openrouter/free",
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen2.5-vl-72b-instruct:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free"
]

# Available providers for text → image generation
IMAGE_GENERATION_PROVIDERS = ["Hugging Face", "OpenRouter"]

# OpenRouter image generation models may require credits and availability can change.
OPENROUTER_IMAGE_MODELS = [
    "openai/gpt-5.4-image-2",
    "black-forest-labs/flux.2-pro",
    "black-forest-labs/flux.2-flex"
]

# Available providers for audio → text transcription
AUDIO_TRANSCRIPTION_PROVIDERS = ["Gemini", "Hugging Face"]

# Hugging Face ASR models
HF_ASR_MODELS = [
    "openai/whisper-large-v3"
]

# Available providers for video → text summarization
VIDEO_SUMMARY_PROVIDERS = [
    "Gemini",
    "Hugging Face Fallback",
    "OpenRouter Frame Fallback"
]
