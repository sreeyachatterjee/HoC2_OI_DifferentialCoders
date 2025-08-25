import os
import sys

from gtts import gTTS
from pydub import AudioSegment

try:
    import simpleaudio  # optional runtime playback
except Exception:
    simpleaudio = None

# Optional: ElevenLabs for English voices
try:
    from elevenlabs.client import ElevenLabs
except Exception:
    ElevenLabs = None


def _play_wav_cross_platform(wav_path: str) -> None:
    """
    Best-effort cross-platform WAV playback.
    If simpleaudio is not available or playback fails, it silently returns.
    """
    try:
        if simpleaudio is None:
            return
        wave_obj = simpleaudio.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception:
        # Non-fatal; UI/browser can still play the file
        pass


def text_to_speech_with_gtts(text: str, language: str, output_mp3: str) -> None:
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(output_mp3)


def text_to_speech_with_elevenlabs(text: str, language: str, output_mp3: str) -> None:
    """
    Uses ElevenLabs if available and API key is provided.
    Falls back to gTTS if ElevenLabs is unavailable.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key or ElevenLabs is None:
        # Fallback to gTTS (English)
        text_to_speech_with_gtts(text, "en", output_mp3)
        return

    client = ElevenLabs(api_key=api_key)
    # Choose a default voice; replace "Aria" with a voice you have access to
    audio = client.generate(text=text, voice="Aria")  # returns bytes
    with open(output_mp3, "wb") as f:
        f.write(audio)


def text_to_speech(input_text: str, language: str = "en", output_file: str = "final.mp3", play_audio: bool = True) -> str:
    """
    Main TTS entrypoint used by the app.
    - Generates MP3 (final.mp3 by default)
    - Converts to WAV (response.wav) for consistent playback
    - Attempts cross-platform playback via simpleaudio (best effort)
    Returns the MP3 path.
    """
    # Generate MP3
    if language.lower() in {"hi", "kn"}:
        text_to_speech_with_gtts(input_text, language.lower(), output_file)
    else:
        text_to_speech_with_elevenlabs(input_text, language.lower(), output_file)

    # Convert to WAV for broader playback support
    wav_file = "response.wav"
    try:
        audio = AudioSegment.from_file(output_file)
        audio.export(wav_file, format="wav")
    except Exception:
        # If conversion fails, still return the MP3 path
        return output_file

    # Try local playback (optional; no-op in server or CI)
    if play_audio:
        _play_wav_cross_platform(wav_file)

    return output_file
