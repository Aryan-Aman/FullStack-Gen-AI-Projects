"""openrouter_service.py - Text, vision, and image generation via OpenRouter API."""

import base64
import requests
from pathlib import Path
from app.utils.config import get_openrouter_api_key

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_openrouter_response(
    prompt: str,
    model: str = "openrouter/free",
    temperature: float = 0.7
) -> str:
    """Generate a text response from OpenRouter."""
    api_key = get_openrouter_api_key()
    if not api_key:
        return "❌ Error: OpenRouter API key is missing. Please add it to your .env file."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Multimodal AI Studio"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            return f"❌ OpenRouter request failed with status code {response.status_code}."

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except (KeyError, IndexError):
        return "❌ Unexpected response format from OpenRouter. Please try again."

    except Exception:
        return "❌ Something went wrong while contacting OpenRouter. Please try again later."


def analyze_image_with_openrouter(
    image_path: str,
    question: str,
    model: str = "openrouter/free",
    temperature: float = 0.7
) -> str:
    """Analyze an image using OpenRouter's vision-capable models."""
    api_key = get_openrouter_api_key()
    if not api_key:
        return "❌ Error: OpenRouter API key is missing. Please add it to your .env file."

    try:
        image_file = Path(image_path)
        image_bytes = image_file.read_bytes()
        base64_string = base64.b64encode(image_bytes).decode("utf-8")

        # Detect MIME type from extension
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime_type = mime_map.get(image_file.suffix.lower(), "image/jpeg")
        data_url = f"data:{mime_type};base64,{base64_string}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Multimodal AI Studio"
        }

        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }],
            "temperature": temperature
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            return f"❌ OpenRouter vision request failed (status {response.status_code}). Please try again or choose a different model."

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except (KeyError, IndexError):
        return "❌ Unexpected response format from OpenRouter vision. Please try again."

    except Exception:
        return "❌ Something went wrong while analyzing the image with OpenRouter. Please try again later."


def generate_image_with_openrouter(
    prompt: str,
    model: str,
    temperature: float = 0.7
):
    """Generate an image via OpenRouter. Returns bytes on success, error string on failure."""
    api_key = get_openrouter_api_key()
    if not api_key:
        return "❌ Error: OpenRouter API key is missing. Please add it to your .env file."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Multimodal AI Studio"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "temperature": temperature
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            return f"❌ OpenRouter image request failed (status {response.status_code}). Please try again or choose a different model."

        data = response.json()
        images = data.get("choices", [{}])[0].get("message", {}).get("images", [])

        if not images:
            return "❌ No image was returned by the model. This model may not support image generation, or the request was filtered. Please try a different model."

        image_data = images[0]

        # Handle base64 data URL
        if isinstance(image_data, str) and image_data.startswith("data:image"):
            base64_part = image_data.split(",", 1)[1]
            return base64.b64decode(base64_part)

        # Handle direct HTTP URL
        if isinstance(image_data, str) and image_data.startswith("http"):
            img_response = requests.get(image_data, timeout=60)
            if img_response.status_code == 200:
                return img_response.content
            return f"❌ Failed to download generated image (status {img_response.status_code})."

        return "❌ The image was returned in an unsupported format. Please try a different model."

    except (KeyError, IndexError):
        return "❌ Unexpected response format from OpenRouter image generation. Please try again."

    except Exception:
        return "❌ Something went wrong while generating the image with OpenRouter. Please try again later."
