from io import BytesIO
from huggingface_hub import InferenceClient
from app.utils.config import get_hf_token


def generate_image_from_text(prompt: str) -> bytes | str | None:
    """
    Generate an image using Hugging Face InferenceClient.

    Args:
        prompt: Text description of the image to generate.

    Returns:
        Image bytes if successful, an error string, or None.
    """

    token = get_hf_token()

    if not token:
        return "❌ Hugging Face token is not configured. Please set HF_TOKEN in your .env file."

    try:
        client = InferenceClient(token=token)

        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    except Exception:
        return "❌ Something went wrong while generating the image with Hugging Face. Please try again later."
