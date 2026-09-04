"""Quick end-to-end check of the two API integrations (no server needed)."""
from dotenv import load_dotenv
load_dotenv()

import brain
import tts

print("== Gemini: first turn (greeting + question 1) ==")
r1 = brain.step({}, "")
print("reply:", r1["reply"])
print("focus:", r1["field_focus"], "| done:", r1["done"])

print("\n== Gemini: messy answer inference ==")
r2 = brain.step({"full_name": "Fatima Nour"}, "we are me, my mum and two little kids")
print("updates:", r2["updates"])
print("reply:", r2["reply"])

print("\n== ElevenLabs: text to speech ==")
audio = tts.speak("Hello, I will help you apply for food assistance.")
print("audio bytes:", len(audio))

print("\nALL OK" if audio else "TTS returned nothing")
