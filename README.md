# First Aid Assistant — Voice + (Optional) Image Triage

## Technology Stack & Features

**Core Technologies**
- Python 3.10+
- [Gradio](https://gradio.app) — UI with multiple tabs
- [Groq API](https://groq.com) — LLM & Whisper STT, multimodal vision + judge models
- [pydub](https://github.com/jiaaro/pydub) + ffmpeg — audio format conversion
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) — microphone recording
- [ElevenLabs API](https://elevenlabs.io) — English voice synthesis
- [gTTS](https://pypi.org/project/gTTS/) — Hindi/Kannada text-to-speech
- [simpleaudio](https://simpleaudio.readthedocs.io) — cross-platform audio playback (optional)
- [requests](https://docs.python-requests.org) — IP geolocation + API calls
- Docker (optional) — containerized deployment

**Key Features**
- 🎙️ **Voice input** via microphone (Groq Whisper transcription)
- 🖼️ **Optional image input** (Groq multimodal models)
- 🧠 **Model ensembling** (multiple text/vision models + judge model)
- 🔊 **Cross-platform TTS** (ElevenLabs for EN, gTTS for HI/KN, optional playback)
- 🌍 **Nearby hospitals tab** (IP geolocation → JSON via LLM)
- 📜 **Conversation history tab** (auto-logged to JSON)
- 📞 **Emergency contacts tab**
- 🐳 **Docker support** (with ffmpeg preinstalled)


An educational **first-aid assistant**

---

## Technology Stack

- **Frontend/UI:** Gradio (Blocks, Tabs, CSS styling)
- **Speech to Text (STT):** Groq Whisper (`whisper-large-v3`)
- **Language Models (LLM):** Groq API (Gemma2-9b-it, DeepSeek-R1, Llama-3.3-70B, Llama Vision)
- **Ensembling/Judge:** Groq LLM (Gemma2-9b-it) for merging responses
- **Text to Speech (TTS):**
  - ElevenLabs (English, voice "Aria")
  - gTTS (Hindi, Kannada)
- **Audio Conversion/Playback:** pydub + simpleaudio (cross-platform)
- **Geolocation:** ipinfo.io + Groq LLM (hospital JSON fabrication)
- **Other Libraries:** SpeechRecognition (mic input), requests, geopy (optional)
- **Containerization:** Docker (Debian slim + ffmpeg + Python 3.11)
- **OS Dependency:** ffmpeg

---

An educational **first-aid assistant** that:
- records or accepts **voice** input (microphone),
- optionally accepts an **image** of an injury/condition,
- queries multiple **Groq** language and vision models,
- **ensembles** the candidate answers into one concise first‑aid response,
- and speaks the result aloud using **ElevenLabs** (EN) or **gTTS** (HI/KN),
- with extra tabs for **conversation history**, **nearby hospitals** (auto‑generated JSON), and **emergency contacts**.

> ⚠️ **Medical disclaimer (recommended):** This project is for educational and prototyping purposes. It is not a substitute for professional medical advice or emergency services.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [OS Dependencies](#os-dependencies)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Roadmap & Nice-to-haves](#roadmap--nice-to-haves)
- [License](#license)

---

## Features

- 🎙️ **Speech to Text** using `Groq` Whisper (`whisper-large-v3`).
- 🖼️ **Vision**: optional injury/condition image is sent to Groq multimodal models.
- 🧠 **Model ensembling**: multiple model candidates are compared and the best/merged answer is produced via a “judge” model.
- 🔊 **Text to Speech**: 
  - English via **ElevenLabs**,
  - Hindi/Kannada via **gTTS** with WAV playback.
- 🌐 **Nearby hospitals**: auto‑generated JSON list (by model call) using your IP‑based location.
- 🗂️ **History**: stores Q/A pairs into `history.json` and renders a scrollable card list in the UI.
- 🧩 **Gradio UI** with multiple tabs.

---

## Project Structure

```
.
├── app.py                         # Main Gradio app with tabs and UI logic
├── assistant.py                   # (Windows playback) TTS; EN via ElevenLabs, HI/KN via gTTS
├── assistant_crossplatform.py     # Cross‑platform TTS (simpleaudio for WAV playback, optional)
├── Brain.py                       # Groq helpers: image encode, chat calls, judge/compare
├── firstaid.py                    # CLI tester (type or record; speaks result)
├── location.py                    # IP geolocation + (LLM‑fabricated) nearby hospitals JSON
├── patient.py                     # Mic record + Groq Whisper transcription
├── requirements.txt               # Pinned Python dependencies
├── Dockerfile                     # Container build (installs ffmpeg, runs app.py)
└── (runtime) history.json, response.wav/mp3, final.mp3
```

---

## New Supporting Files

### `requirements.txt`
- Lists all Python dependencies (Gradio, Groq, pydub, SpeechRecognition, ElevenLabs, gTTS, geopy, requests, simpleaudio).
- Install with `pip install -r requirements.txt`.

### `Dockerfile`
- Based on `python:3.11-slim`, installs `ffmpeg`.
- Copies project and installs deps.
- Exposes port 7860.
- Entrypoint: `python app.py`.
- Run with:
  ```bash
  docker build -t firstaid-assistant .
  docker run -p 7860:7860 -e GROQ_API_KEY=... -e ELEVENLABS_API_KEY=... firstaid-assistant
  ```

### `assistant_crossplatform.py`
- Safe drop-in replacement for `assistant.py`.
- Removes Windows-only PowerShell playback.
- Uses `simpleaudio` (if available) for cross-platform WAV playback.
- Falls back to gTTS for EN if ElevenLabs not configured.

---

## Key Components

### 1) `app.py` (Gradio UI)
- **Inputs:** Microphone audio file path + optional image.
- **Flow:** 
  1. Transcribe audio → `patient.transcribe_audio`
  2. If image provided: call three **vision** prompts + three **text** prompts; else only text prompts.
  3. **Compare/Judge:** Send all candidate answers to a **judge** model to pick/merge and return one final response.
  4. **TTS:** Speak final response and save as `final.mp3` (+ `response.wav` for playback).
  5. **History:** Append `{query, response}` to `history.json`.
- **Tabs:** *Main Assistant*, *Conversation History*, *Nearby Hospitals*, *Emergency Contacts*.
- **Styling:** light custom CSS.

### 2) `assistant.py` (Text to Speech)
- **EN:** uses **ElevenLabs** (voice “Aria”) → mp3 → convert to WAV → playback with PowerShell on Windows.
- **HI/KN:** uses **gTTS** → mp3 → convert to WAV → playback with PowerShell on Windows.
- Uses `pydub.AudioSegment` for conversions.

### 3) `Brain.py` (Groq helpers)
- `encode_image(path)` → base64
- `putting_query_with_image(query, model, encoded_image)` → multimodal chat
- `putting_query_without_image(query, model)` → text-only chat
- `compare(query, model)` → judge model to select/merge best answer

### 4) `patient.py` (Audio I/O)
- `record_audio(file_path, timeout, phrase_time_limit)` using `speech_recognition` microphone stream → mp3 via `pydub`.
- `transcribe_audio(audio_path, stt_model, GROQ_API_KEY, lang)` → Groq Whisper transcription.

### 5) `location.py` (Hospitals JSON generator)
- Retrieves **lat/long** via `https://ipinfo.io`,
- Assembles a **prompt** to ask a model to return the *10 nearest hospitals* as JSON,
- Exposes `hospital_json` string consumed by the app’s *Nearby Hospitals* tab.

---

## Quickstart

### 0) Prereqs
- **Python** 3.10+ (3.11 recommended)
- **ffmpeg** installed and on PATH (required by `pydub` for mp3/wav conversions)
- Microphone access (OS prompt)
- Internet connectivity (Groq, ElevenLabs, ipinfo)

### 1) Create and activate a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies (via `requirements.txt`)
Create a `requirements.txt` with the following (or copy from below) and install:
```txt
gradio>=4.44
groq>=0.5
pydub>=0.25
SpeechRecognition>=3.10
elevenlabs>=1.5
gTTS>=2.5
geopy>=2.4
requests>=2.32
```
Then:
```bash
pip install -r requirements.txt
```

### 3) Set environment variables
```bash
# Required for Groq (both LLM and Whisper)
export GROQ_API_KEY="YOUR_GROQ_API_KEY"

# Required if you want EN speech via ElevenLabs
export ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY"
```
On Windows PowerShell:
```powershell
setx GROQ_API_KEY "YOUR_GROQ_API_KEY"
setx ELEVENLABS_API_KEY "YOUR_ELEVENLABS_API_KEY"
```

### 4) Run the Gradio app
```bash
python app.py
```
Gradio will print a local URL. Open it in your browser.  
- **Main Assistant**: record or upload audio; optionally add an image; click **Process**.
- **Conversation History**: click “View History”.
- **Nearby Hospitals**: click “View Nearby Hospitals” (auto‑generated JSON rendered as cards).
- **Emergency Contacts**: quick phone list (editable in code).

### 5) Try the CLI tester (optional)
```bash
python firstaid.py
```
- Enter `1` to **type** a query.
- Enter `2` to **record** and auto‑transcribe.  
If you choose `2`, it records to `patient_audio.mp3`, transcribes with Groq Whisper, runs the ensemble, and speaks the result.

---


---

## Docker

Build and run the app in a container (ffmpeg preinstalled):

```bash
docker build -t firstaid-assistant .
docker run --rm -it -p 7860:7860   -e GROQ_API_KEY="YOUR_GROQ_API_KEY"   -e ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY"   firstaid-assistant
```

## Configuration

- **Models used** (default; change in `app.py` / `firstaid.py`):
  - Vision: `llama-3.2-90b-vision-preview`, `llama-3.2-11b-vision-preview`
  - Text: `gemma2-9b-it`, `deepseek-r1-distill-llama-70b`, `llama-3.3-70b-versatile`
  - Judge: currently `gemma2-9b-it`
- **Prompts:** tuned for **short, simple, first‑aid** guidance phrased as if talking to a real person.
- **History file:** `history.json` in repo root (auto‑created).

---

## How It Works

1. **Capture audio** → `patient.record_audio` or directly uploaded file path (Gradio `Audio`).
2. **Transcribe** → Groq Whisper returns text query.
3. **(Optional) Encode image** → `Brain.encode_image` as base64 for multimodal calls.
4. **Generate candidates** → call 3× vision + 3× text models with tightly scoped “doctor‑style” prompts.
5. **Judge/Compare** → one “judge” call receives the original query and all candidate strings, outputs the best/merged response.
6. **Speak** → `assistant.text_to_speech` creates mp3 + wav and plays it (Windows PowerShell call).  
7. **Persist** → append `{query, response}` to `history.json` for the UI *History* tab.

---


---

## Cross‑platform TTS (recommended)

The default `assistant.py` uses a Windows‑only PowerShell playback call. Use the cross‑platform module instead:

**Option A — rename the file**  
```bash
mv assistant_crossplatform.py assistant.py
```

**Option B — import explicitly**  
Change your imports to:
```python
from assistant_crossplatform import text_to_speech
```

`assistant_crossplatform.py` plays WAV using `simpleaudio` when available (no OS‑specific subprocess). If playback isn't possible (e.g., headless), the function still returns the audio path for browser playback in Gradio.


## OS Dependencies

- **ffmpeg**: required by `pydub` to transcode mp3/wav.  
  - macOS: `brew install ffmpeg`  
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`  
  - Windows: install from ffmpeg.org and add to PATH.
- **Playback**:  
  - `assistant.py` (default) uses **PowerShell** and is **Windows-only**.  
  - `assistant_crossplatform.py` uses **simpleaudio** (optional) and works on macOS/Linux/Windows.
- **Docker**: The provided `Dockerfile` installs `ffmpeg` and starts `app.py`. Supply your API keys at run time via `-e` flags.

---

## Troubleshooting

- **No audio playback on macOS/Linux**  
  Edit `assistant.text_to_speech` to skip the Windows PowerShell call. Gradio will still provide the generated audio file to play in the browser.

- **`ffmpeg` not found** / conversion errors  
  Ensure `ffmpeg` is installed and on PATH. `pydub` needs it for mp3 ↔ wav.

- **Groq auth/model errors**  
  Confirm `GROQ_API_KEY` is set and the model IDs are accessible to your account. Consider reducing to a single text model first to confirm plumbing.

- **ElevenLabs errors**  
  Confirm `ELEVENLABS_API_KEY` or switch to gTTS (set `language="hi"` or `"kn"`).

- **Hospitals tab returns “Invalid hospital data”**  
  `location.hospital_json` is produced by **another model call** using your IP geolocation. Ensure `GROQ_API_KEY` is set and outbound network is available.

---

## Security Notes

- **Secrets**: Use environment variables or a `.env` loader; do not commit keys.  
- **PII**: Audio and images may contain sensitive data; consider adding explicit user consent and data retention policies.  
- **Prompt safety**: Consider adding a visible UI disclaimer and safe‑completion rules for high‑risk topics.

---

## Roadmap & Nice-to-haves

- [ ] Cross‑platform audio playback (avoid PowerShell)
- [ ] Cache/model timeouts + retries
- [ ] Rate‑limit and length limits on uploads
- [ ] Switch hospital finder to a deterministic data source (e.g., Overpass/OSM) instead of LLM fabrication
- [ ] `requirements.txt` and `Dockerfile`
- [ ] Add unit tests for helpers
- [ ] Make judge model configurable from UI

---

## License

Choose a license (e.g., MIT) and include it here.
