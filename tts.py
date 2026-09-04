"""ElevenLabs text-to-speech: turn each spoken reply into a warm human voice.

`eleven_multilingual_v2` speaks the reply in whatever language Gemini wrote it,
so an Arabic answer gets an Arabic voice with no extra work.
"""

import os

from elevenlabs.client import ElevenLabs

# A warm default voice. Swap via VOICE_ID in .env, or pick one in the dashboard.
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
MODEL = "eleven_multilingual_v2"

_client = None


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set. Add it to .env.")
        _client = ElevenLabs(api_key=key)
    return _client


def speak(text: str) -> bytes:
    """Return MP3 audio bytes for `text`."""
    stream = _get_client().text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=MODEL,
        text=text,
        output_format="mp3_44100_128",
    )
    return b"".join(stream)
