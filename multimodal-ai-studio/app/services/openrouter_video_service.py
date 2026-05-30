"""openrouter_video_service.py - Video summarization via frame extraction + OpenRouter Vision."""

from app.utils.video_utils import extract_video_frames
from app.services.openrouter_service import (
    analyze_image_with_openrouter,
    generate_openrouter_response,
)


def summarize_video_with_openrouter_frames(video_path: str) -> str:
    """Summarize a video by describing extracted frames with OpenRouter vision."""
    try:
        frame_paths = extract_video_frames(video_path, max_frames=5)
        if not frame_paths:
            return "❌ Could not extract frames from the video."

        # Describe each frame
        frame_descriptions = []
        for frame_path in frame_paths:
            description = analyze_image_with_openrouter(
                image_path=frame_path,
                question="Describe this video frame in detail. Focus on visible actions, objects, scene, text, people, and context.",
                model="openrouter/free",
                temperature=0.3,
            )
            frame_descriptions.append(description)

        # Generate cohesive summary from individual descriptions
        combined_descriptions = "\n\n".join(
            f"Frame {i+1}: {desc}" for i, desc in enumerate(frame_descriptions)
        )

        summary = generate_openrouter_response(
            prompt=f"Create a short video summary and 5 key points from these frame descriptions:\n\n{combined_descriptions}",
            model="openrouter/free",
            temperature=0.4,
        )

        frame_list = "\n".join(
            f"- Frame {i+1}: {desc}" for i, desc in enumerate(frame_descriptions)
        )

        return (
            f"## OpenRouter Frame-Based Video Summary\n\n"
            f"{summary}\n\n"
            f"## Frame Descriptions\n\n"
            f"{frame_list}"
        )

    except Exception:
        return "❌ Something went wrong while summarizing the video with OpenRouter. Please try again later."
