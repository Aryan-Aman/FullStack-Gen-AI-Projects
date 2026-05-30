"""hf_video_service.py - Video summarization via HF frame captioning fallback."""

from huggingface_hub import InferenceClient
from app.utils.config import get_hf_token
from app.utils.video_utils import extract_video_frames


def summarize_video_with_hf(video_path: str) -> str:
    """Summarize a video by captioning extracted frames with HF image-to-text."""
    try:
        token = get_hf_token()
        if not token:
            return (
                "Hugging Face token is not configured. "
                "Please set HF_TOKEN in your .env file to use this feature."
            )

        frame_paths = extract_video_frames(video_path, max_frames=5)
        if not frame_paths:
            return (
                "Could not extract frames from the video. "
                "Please ensure the video file is valid and not corrupted."
            )

        client = InferenceClient(token=token)
        model = "Salesforce/blip-image-captioning-large"
        captions = []

        for frame_path in frame_paths:
            result = client.image_to_text(frame_path, model=model)

            # Handle varying response formats from HF
            if isinstance(result, dict) and "generated_text" in result:
                caption = result["generated_text"]
            elif isinstance(result, list) and len(result) > 0:
                first = result[0]
                caption = first.get("generated_text", str(first)) if isinstance(first, dict) else str(first)
            elif hasattr(result, "generated_text"):
                caption = result.generated_text
            else:
                caption = str(result)

            captions.append(caption)

        # Build summary
        summary_lines = ["Fallback video summary based on extracted frames:\n"]
        for i, caption in enumerate(captions, start=1):
            summary_lines.append(f"  Frame {i}: {caption}")

        summary_lines.append(
            "\nOverall: The video appears to show " + ", then ".join(captions[:3]) + "."
            if len(captions) >= 3
            else "\nOverall: " + "; ".join(captions) + "."
        )

        return "\n".join(summary_lines)

    except Exception:
        return (
            "❌ Hugging Face video fallback failed because the selected image-captioning "
            "model is not available through the current inference route. "
            "Please try the OpenRouter Frame Fallback instead."
        )
