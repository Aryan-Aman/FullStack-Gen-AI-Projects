"""file_utils.py - Save and clean up uploaded files."""

from pathlib import Path


def save_uploaded_file(uploaded_file, upload_dir="app/temp"):
    """Save a Streamlit UploadedFile to disk and return the path as a string."""
    dir_path = Path(upload_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def cleanup_file(file_path):
    """Delete a file if it exists."""
    path = Path(file_path)
    if path.exists():
        path.unlink()
