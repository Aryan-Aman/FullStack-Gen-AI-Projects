# Multimodal AI Studio

A Streamlit application covering six AI modalities (text, image, audio, video) with provider selection and automatic fallback. Uses Google Gemini, OpenRouter, and Hugging Face APIs.

---
## Demo Video

Watch the demo here: [Multimodal AI Studio Demo](https://youtu.be/WtX7yKJtHqg)

## Project Scope

- 6 modalities implemented via a modular service layer
- Provider selection per modality with fallback on failure
- Clean error handling — no raw API responses exposed to the user
- Text → Video is intentionally excluded

---

## Modalities

| # | Modality | Primary Provider | Fallback |
|---|----------|-----------------|----------|
| 1 | Text → Text | OpenRouter | Gemini |
| 2 | Text → Image | Hugging Face | OpenRouter (credits may apply) |
| 3 | Image → Text | OpenRouter Vision | Gemini |
| 4 | Audio → Text | Gemini | Hugging Face Whisper (auto) |
| 5 | Text → Audio | Hugging Face TTS | pyttsx3 offline (auto) |
| 6 | Video → Text | Gemini | OpenRouter/HF frame captioning (auto) |

"Auto" fallbacks trigger when the primary provider fails. Others are user-selectable via dropdown.

---

## Models

| Modality | Provider | Model |
|----------|----------|-------|
| Text → Text | Gemini | `gemini-2.0-flash` |
| Text → Text | OpenRouter | `openrouter/free`, `google/gemini-2.0-flash-exp:free`, `meta-llama/llama-3.3-70b-instruct:free`, `mistralai/mistral-7b-instruct:free`, `deepseek/deepseek-r1:free` |
| Text → Image | Hugging Face | `black-forest-labs/FLUX.1-schnell` |
| Text → Image | OpenRouter | `openai/gpt-5.4-image-2`, `black-forest-labs/flux.2-pro`, `black-forest-labs/flux.2-flex` |
| Image → Text | Gemini | `gemini-2.0-flash` |
| Image → Text | OpenRouter | `openrouter/free`, `google/gemini-2.0-flash-exp:free`, `qwen/qwen2.5-vl-72b-instruct:free`, `meta-llama/llama-3.2-11b-vision-instruct:free` |
| Audio → Text | Gemini | `gemini-2.0-flash` |
| Audio → Text | Hugging Face | `openai/whisper-large-v3` |
| Text → Audio | Hugging Face | `facebook/mms-tts-eng` |
| Text → Audio | Local | `pyttsx3` (offline fallback) |
| Video → Text | Gemini | `gemini-2.0-flash` |
| Video → Text | HF Fallback | `Salesforce/blip-image-captioning-large` |
| Video → Text | OpenRouter Fallback | `openrouter/free` (frame description + summary) |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| UI | Streamlit |
| Text/Vision APIs | Google Gemini, OpenRouter |
| Image/Audio/ASR APIs | Hugging Face Inference |
| Offline TTS | pyttsx3 |
| Video Frame Extraction | OpenCV |
| Config | python-dotenv |
| Language | Python 3.11 |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│               Streamlit UI (main.py)                │
├─────────────────────────────────────────────────────┤
│            Model Router (model_router.py)            │
│        Dispatches to provider based on selection     │
├──────────┬───────────┬──────────┬───────────────────┤
│  Gemini  │ OpenRouter │ Hugging │  pyttsx3 local    │
│ Service  │  Service   │  Face   │  fallback         │
├──────────┴───────────┴──────────┴───────────────────┤
│              Utilities (config, file, video)         │
├─────────────────────────────────────────────────────┤
│         Model Config (provider/model constants)      │
└─────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
multimodal-ai-studio/
├── .env                          # API keys (not committed)
├── .gitignore
├── README.md
├── requirements.txt
├── app/
│   ├── main.py                   # Streamlit entry point
│   ├── core/
│   │   ├── model_config.py       # Provider/model constants
│   │   └── model_router.py       # Request routing + fallback
│   ├── services/
│   │   ├── gemini_service.py     # Gemini (text, image, audio, video)
│   │   ├── openrouter_service.py # OpenRouter (text, vision, image gen)
│   │   ├── hf_image_service.py   # HF image generation
│   │   ├── hf_audio_service.py   # HF TTS + pyttsx3 fallback
│   │   ├── hf_asr_service.py     # HF Whisper transcription
│   │   ├── hf_video_service.py   # HF frame captioning
│   │   └── openrouter_video_service.py
│   ├── utils/
│   │   ├── config.py             # .env loader
│   │   ├── file_utils.py         # File save/cleanup
│   │   └── video_utils.py        # OpenCV frame extraction
│   └── temp/                     # Temporary uploads
└── notebook/
    └── multimodal_ai_model_exploration.ipynb
```

---

## Setup

### Prerequisites

- Python 3.11+
- At least one API key (Gemini, Hugging Face, or OpenRouter)

### Installation

```bash
git clone <repository-url>
cd multimodal-ai-studio

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### Environment Variables

Create `.env` in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
HF_TOKEN=your_huggingface_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

| Variable | Required | Source |
|----------|----------|--------|
| `GEMINI_API_KEY` | Recommended | [Google AI Studio](https://aistudio.google.com/) |
| `HF_TOKEN` | Recommended | [Hugging Face Settings](https://huggingface.co/settings/tokens) |
| `OPENROUTER_API_KEY` | Optional | [OpenRouter](https://openrouter.ai/keys) |

Keys are never exposed in error messages or the UI.

### Running

```bash
streamlit run app/main.py
```

Opens at `http://localhost:8501`.

### Notebook

```bash
jupyter notebook notebook/multimodal_ai_model_exploration.ipynb
```

Or open directly in VS Code with the Jupyter extension.

---

## Fallback Strategy

| Modality | Trigger | Behavior |
|----------|---------|----------|
| Audio → Text | Gemini fails | Auto-switches to HF Whisper |
| Text → Audio | HF API unreachable | Auto-switches to pyttsx3 (offline) |
| Video → Text | Gemini fails | Auto-switches to OpenRouter frame extraction |

Other provider options (OpenRouter for text/vision/image, HF frame captioning for video) are user-selectable via dropdown — not automatic fallbacks.

Video fallbacks work by extracting frames with OpenCV and captioning/describing them individually.

---

## Limitations

- Free-tier Gemini keys may hit quota limits
- Some OpenRouter image models require credits
- HF serverless inference may intermittently reject certain models
- pyttsx3 speech quality is lower than cloud TTS
- Video uploads capped at 100 MB
- Frame-based video summarization loses motion/audio/temporal context
- Text → Video not implemented (out of scope)

---

## Possible Improvements

- Streaming text generation
- Multi-language TTS and ASR
- Chat memory / conversation history
- Video audio track extraction for combined summarization
- Deployment to Streamlit Cloud or HF Spaces

---

## Checklist

- [x] 6 modalities implemented
- [x] Text → Video excluded by design
- [x] Multiple providers with UI selection
- [x] Automatic fallback for audio, video, TTS
- [x] No raw API responses or stack traces exposed
- [x] API keys from `.env`, never displayed
- [x] Modular service/config/routing architecture
- [x] `requirements.txt` and `.gitignore` configured
- [x] Jupyter notebook for exploration
