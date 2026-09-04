"""Verify the audio path without a microphone.

Synthesise a spoken answer with ElevenLabs, post it to /api/step_audio, and
check that Gemini heard it and filled the form — the same journey a real
recording takes.
"""
import time

import requests
from dotenv import load_dotenv

load_dotenv()
import tts

BASE = "http://127.0.0.1:5000"
SID = f"audio_test_{int(time.time())}"
SPOKEN = "My name is Fatima Nour and there are four of us at home, two are kids"

print("Synthesising the spoken answer…")
clip = tts.speak(SPOKEN)
print(f"  {len(clip)} bytes of audio\n")

print("Posting it as if the browser had failed to transcribe…")
t = time.time()
r = requests.post(
    f"{BASE}/api/step_audio",
    files={"audio": ("answer.mp3", clip, "audio/mp3")},
    data={"session_id": SID},
    timeout=120,
)
d = r.json()
print(f"  HTTP {r.status_code} in {time.time() - t:.1f}s\n")
print("heard  :", d.get("heard"))
print("reply  :", (d.get("reply") or "")[:120])
print("answers:", d.get("answers"))

a = d.get("answers", {})
ok = a.get("full_name") and a.get("household_size") == "4" and a.get("children_count") == "2"
print("\nRESULT:", "PASS - Gemini transcribed the audio and filled the form" if ok else "FAIL")

requests.post(f"{BASE}/api/forget", json={"session_id": SID}, timeout=30)
