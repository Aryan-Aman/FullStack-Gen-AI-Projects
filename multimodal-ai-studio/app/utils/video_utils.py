"""video_utils.py - Extract representative frames from a video for fallback summarization."""

import os
import cv2


def extract_video_frames(
    video_path: str,
    output_dir: str = "app/temp/video_frames",
    max_frames: int = 5,
) -> list[str]:
    """Extract evenly spaced frames from a video and save as JPGs.

    Returns a list of saved frame paths, or an empty list if the video cannot be opened.
    """
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return []

    # Pick evenly spaced frame indexes across the video duration
    if total_frames <= max_frames:
        frame_indexes = list(range(total_frames))
    else:
        step = total_frames / max_frames
        frame_indexes = [int(step * i) for i in range(max_frames)]

    saved_paths = []
    for idx, frame_idx in enumerate(frame_indexes):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        success, frame = cap.read()
        if not success:
            continue

        filepath = os.path.join(output_dir, f"frame_{idx}.jpg")
        cv2.imwrite(filepath, frame)
        saved_paths.append(filepath)

    cap.release()
    return saved_paths
