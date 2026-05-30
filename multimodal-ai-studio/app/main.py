"""main.py - Streamlit entry point for Multimodal AI Studio."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.core.model_config import (
    AUDIO_TRANSCRIPTION_PROVIDERS,
    DEFAULT_TEMPERATURE,
    GEMINI_TEXT_MODELS,
    HF_ASR_MODELS,
    IMAGE_ANALYSIS_PROVIDERS,
    IMAGE_GENERATION_PROVIDERS,
    OPENROUTER_IMAGE_MODELS,
    OPENROUTER_TEXT_MODELS,
    OPENROUTER_VISION_MODELS,
    TEXT_PROVIDERS,
    VIDEO_SUMMARY_PROVIDERS,
)
from app.core.model_router import (
    analyze_image_with_provider,
    generate_image_with_provider,
    generate_text_with_provider,
    summarize_video_with_provider,
    transcribe_audio_with_provider,
)
from app.services.hf_audio_service import generate_speech_from_text
from app.utils.config import get_gemini_api_key, get_hf_token, get_openrouter_api_key
from app.utils.file_utils import cleanup_file, save_uploaded_file


# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────

st.set_page_config(page_title="Multimodal AI Studio", page_icon="🤖", layout="wide")


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────

with st.sidebar:
    st.title("🤖 Multimodal AI Studio")
    st.markdown("---")

    st.subheader("Supported Modalities")
    st.markdown(
        "1. 💬 Text → Text\n"
        "2. 🎨 Text → Image\n"
        "3. 🖼️ Image → Text\n"
        "4. 🎧 Audio → Text\n"
        "5. 🔊 Text → Audio\n"
        "6. 🎬 Video → Text"
    )
    st.markdown("---")

    st.subheader("Providers")
    st.markdown(
        "- **Google Gemini** — Text, Image Analysis, Audio, Video\n"
        "- **Hugging Face** — Image Generation, Text-to-Speech"
    )
    st.markdown("---")

    st.info("ℹ️ Text → Video is intentionally not included in this project.")
    st.markdown("---")

    with st.expander("API Key Status"):
        gemini_ok = "Yes" if get_gemini_api_key() else "No"
        hf_ok = "Yes" if get_hf_token() else "No"
        or_ok = "Yes" if get_openrouter_api_key() else "No"
        st.markdown(
            f"- Gemini: **{gemini_ok}**\n"
            f"- Hugging Face: **{hf_ok}**\n"
            f"- OpenRouter: **{or_ok}**"
        )


# ──────────────────────────────────────────────
# Main Content
# ──────────────────────────────────────────────

st.title("🤖 Multimodal AI Studio")
st.caption("Gemini and OpenRouter for text; Gemini and Hugging Face for other modalities.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Text Chat",
    "🎨 Text to Image",
    "🖼️ Image Analysis",
    "🎧 Audio Transcription",
    "🔊 Text to Speech",
    "🎬 Video Summary",
])


# ──────────────────────────────────────────────
# Tab 1: Text Chat
# ──────────────────────────────────────────────

with tab1:
    st.header("💬 Text Chat")
    st.markdown("Send a prompt and get a text response from your chosen provider.")

    col_provider, col_model = st.columns(2)
    with col_provider:
        text_provider = st.selectbox("Provider:", TEXT_PROVIDERS, key="text_chat_provider")
    with col_model:
        text_models = GEMINI_TEXT_MODELS if text_provider == "Gemini" else OPENROUTER_TEXT_MODELS
        text_model = st.selectbox("Model:", text_models, key="text_chat_model")

    text_temperature = st.slider(
        "Temperature", 0.0, 2.0, DEFAULT_TEMPERATURE, 0.1, key="text_chat_temperature"
    )

    text_prompt = st.text_area(
        "Enter your prompt:",
        placeholder="Explain multimodal AI in simple terms.",
        key="text_chat_input",
    )

    if st.button("Generate Response", key="text_chat_btn"):
        if not text_prompt.strip():
            st.warning("Please enter a prompt before generating.")
        else:
            with st.spinner("Generating response..."):
                result = generate_text_with_provider(
                    provider=text_provider,
                    prompt=text_prompt,
                    model=text_model,
                    temperature=text_temperature,
                )
            st.markdown("### Response")
            st.markdown(result)


# ──────────────────────────────────────────────
# Tab 2: Text to Image
# ──────────────────────────────────────────────

with tab2:
    st.header("🎨 Text to Image")
    st.markdown("Describe an image and generate it using your chosen provider.")

    img_gen_provider = st.selectbox(
        "Provider:", IMAGE_GENERATION_PROVIDERS, key="image_generation_provider_select"
    )

    if img_gen_provider == "Hugging Face":
        img_gen_model = None
        img_gen_temp = 0.7
        st.info("Using Hugging Face text-to-image model.")
    else:
        img_gen_model = st.selectbox(
            "Model:", OPENROUTER_IMAGE_MODELS, key="openrouter_image_model_select"
        )
        img_gen_temp = st.slider(
            "Temperature", 0.0, 2.0, 0.7, 0.1, key="image_generation_temperature_slider"
        )

    img_gen_prompt = st.text_area(
        "Enter your image description:",
        placeholder="A futuristic classroom where students learn with AI holograms.",
        key="text_to_image_input",
    )

    if st.button("Generate Image", key="text_to_image_btn"):
        if not img_gen_prompt.strip():
            st.warning("Please enter a description before generating.")
        else:
            with st.spinner("Generating image..."):
                image_result = generate_image_with_provider(
                    provider=img_gen_provider,
                    prompt=img_gen_prompt,
                    model=img_gen_model,
                    temperature=img_gen_temp,
                )

            if isinstance(image_result, bytes):
                st.image(image_result, caption="Generated Image", use_container_width=True)
            elif isinstance(image_result, str):
                st.error(image_result)
            else:
                st.error("Could not generate the image. Please try again later.")


# ──────────────────────────────────────────────
# Tab 3: Image Analysis
# ──────────────────────────────────────────────

with tab3:
    st.header("🖼️ Image Analysis")
    st.markdown("Upload an image and ask a question about it.")

    vision_provider = st.selectbox(
        "Provider:", IMAGE_ANALYSIS_PROVIDERS, key="image_provider_select"
    )

    if vision_provider == "Gemini":
        vision_model = "gemini-2.0-flash"
        st.info("Using Gemini for image analysis.")
    else:
        vision_model = st.selectbox(
            "Model:", OPENROUTER_VISION_MODELS, key="openrouter_vision_model_select"
        )

    vision_temperature = st.slider(
        "Temperature", 0.0, 2.0, 0.7, 0.1, key="image_temperature_slider"
    )

    uploaded_image = st.file_uploader(
        "Upload an image:", type=["png", "jpg", "jpeg", "webp"], key="image_analysis_upload"
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image Preview", use_container_width=True)

    vision_question = st.text_area(
        "Your question about the image:",
        value="Describe this image in detail.",
        key="image_analysis_question",
    )

    if st.button("Analyze Image", key="image_analysis_btn"):
        if not uploaded_image:
            st.warning("Please upload an image first.")
        elif uploaded_image.size > 10 * 1024 * 1024:
            st.warning("Image too large (max 10 MB).")
        else:
            image_path = save_uploaded_file(uploaded_image)
            with st.spinner("Analyzing image..."):
                result = analyze_image_with_provider(
                    provider=vision_provider,
                    image_path=image_path,
                    question=vision_question,
                    model=vision_model,
                    temperature=vision_temperature,
                )
            st.markdown("### Analysis")
            st.markdown(result)
            cleanup_file(image_path)


# ──────────────────────────────────────────────
# Tab 4: Audio Transcription
# ──────────────────────────────────────────────

with tab4:
    st.header("🎧 Audio Transcription")
    st.markdown("Upload an audio file and get a transcription.")

    asr_provider = st.selectbox(
        "Provider:", AUDIO_TRANSCRIPTION_PROVIDERS, key="audio_transcription_provider_select"
    )

    if asr_provider == "Gemini":
        asr_model = "gemini-2.0-flash"
        st.info("Using Gemini. Falls back to Hugging Face on failure.")
    else:
        asr_model = st.selectbox(
            "Model:", HF_ASR_MODELS, key="hf_asr_model_select"
        )

    uploaded_audio = st.file_uploader(
        "Upload an audio file:", type=["mp3", "wav", "m4a", "ogg"], key="audio_transcription_upload"
    )
    if uploaded_audio:
        st.audio(uploaded_audio)

    if st.button("Transcribe Audio", key="audio_transcription_btn"):
        if not uploaded_audio:
            st.warning("Please upload an audio file first.")
        elif uploaded_audio.size > 25 * 1024 * 1024:
            st.warning("Audio too large (max 25 MB).")
        else:
            audio_path = save_uploaded_file(uploaded_audio)
            with st.spinner("Transcribing audio..."):
                result = transcribe_audio_with_provider(
                    provider=asr_provider, audio_path=audio_path, model=asr_model
                )
            st.markdown("### Transcription")
            st.markdown(result)
            cleanup_file(audio_path)


# ──────────────────────────────────────────────
# Tab 5: Text to Speech
# ──────────────────────────────────────────────

with tab5:
    st.header("🔊 Text to Speech")
    st.markdown("Enter text and convert it to speech via Hugging Face (with offline fallback).")

    tts_text = st.text_area(
        "Enter text to speak:",
        placeholder="Welcome to my multimodal AI studio project.",
        key="text_to_speech_input",
    )

    if st.button("Generate Speech", key="text_to_speech_btn"):
        if not tts_text.strip():
            st.warning("Please enter some text before generating.")
        else:
            with st.spinner("Generating speech..."):
                audio_result = generate_speech_from_text(tts_text)

            if isinstance(audio_result, bytes):
                st.audio(audio_result, format="audio/wav")
                st.success("Speech generated successfully.")
            elif isinstance(audio_result, str):
                st.error(audio_result)
            else:
                st.error("Could not generate speech. Please try again later.")


# ──────────────────────────────────────────────
# Tab 6: Video Summary
# ──────────────────────────────────────────────

with tab6:
    st.header("🎬 Video Summary")
    st.markdown("Upload a video and get an AI-generated summary.")
    st.warning("Video processing may take some time depending on file size.")

    vid_provider = st.selectbox(
        "Provider:", VIDEO_SUMMARY_PROVIDERS, key="video_summary_provider_select"
    )

    if vid_provider == "Gemini":
        st.info("Using Gemini for direct video understanding. Falls back to OpenRouter on failure.")
    elif vid_provider == "Hugging Face Fallback":
        st.info("Summarizes by extracting frames and captioning them individually.")

    uploaded_video = st.file_uploader(
        "Upload a video file:", type=["mp4", "mov", "avi", "mkv"], key="video_summary_upload"
    )
    if uploaded_video:
        st.video(uploaded_video)

    if st.button("Summarize Video", key="video_summary_btn"):
        if not uploaded_video:
            st.warning("Please upload a video file first.")
        elif uploaded_video.size > 100 * 1024 * 1024:
            st.warning("Video too large (max 100 MB).")
        else:
            video_path = save_uploaded_file(uploaded_video)
            with st.spinner("Summarizing video..."):
                result = summarize_video_with_provider(
                    provider=vid_provider, video_path=video_path
                )
            st.markdown("### Summary")
            st.markdown(result)
            cleanup_file(video_path)
