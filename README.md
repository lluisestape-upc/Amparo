# 🕊️ Amparo

**Apply for aid entirely by talking — in your own language.**

Billions in aid go unclaimed every year, and one of the reasons is painfully
simple: the form itself is the wall. If you are blind, if you don't read well,
or if you don't speak the language the form is written in, the help you are
entitled to is out of reach.

Amparo removes the form. It asks you a few simple questions out loud, you
answer in your own words in whatever language you speak, and it fills in a real
aid application for you — then hands you the completed PDF.

Built for the [DEV Weekend Challenge: Generosity Edition](https://dev.to/events/challenges/weekend-2026-09-03).

---

## How it works

```
    you speak  ──►  Web Speech API  ──►  Gemini (the brain)  ──►  filled form
        ▲                                       │
        └────────  ElevenLabs (the voice)  ◄────┘
```

1. **Gemini 3.6 Flash** reads the blank form, asks about one field at a time in
   simple, kind words, and understands messy human answers. Say *"we're me, my
   mum and two little kids"* and it fills `household_size = 4` and
   `children_count = 2` without asking you to do the arithmetic.
2. **ElevenLabs** (`eleven_multilingual_v2`) speaks every question in a warm
   human voice, in whatever language you're speaking.
3. The form fills in **live on screen** as you talk, and you download the
   completed application as a PDF.

## What makes it usable by the people it's for

- **No reading required anywhere.** The first greeting is spoken in several
  languages, so you simply answer in yours — there is no language menu to read.
- **It reads back what it heard.** Every value is confirmed out loud, because
  the person can't see the screen.
- **You can correct it at any time.** Say *"no, I said three, not four"* about
  any field, however long ago you answered it. The person is always right.
- **Errors are spoken, never silent text.** A tool for people who can't read
  must not report failures in writing.
- **Interrupt freely.** Tap the mic while it's talking and it stops to listen.
- **You never lose your place.** Answers survive a page reload or a dropped
  connection, and it welcomes you back where you left off.
- Respects `prefers-reduced-motion`, works with keyboard and screen readers,
  and adapts to light and dark themes.

## Privacy

Answers include income and home address, so: nothing is sent anywhere except
to the language models needed to process the answer, data is kept only for the
duration of the session, and **everything is deleted the moment the applicant
downloads their PDF**.

## Run it

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env                                # then add your two keys
python app.py
```

Open <http://127.0.0.1:5000> in Chrome (the microphone needs Chrome + localhost).

You'll need a free [Gemini API key](https://aistudio.google.com/apikey) and an
[ElevenLabs API key](https://elevenlabs.io) with the *Text to Speech* scope.

## Project layout

| File | What it does |
|---|---|
| `form_schema.py` | The one form being filled (a food-bank intake). Swap fields here to target a different aid program — nothing else changes. |
| `brain.py` | Gemini conversation logic. Returns strict JSON: the complete form state, what to say next, the detected language. |
| `tts.py` | ElevenLabs text-to-speech. |
| `pdf_fill.py` | Renders the answers into the completed PDF. |
| `app.py` | Flask server and API. |
| `static/index.html` | The accessible, voice-first interface. |

## Roadmap

- Speech-to-text via a model that handles accented and disfluent speech better
  than the browser's built-in recognition
- More aid programs, and pre-screening for which ones a person qualifies for
- A caseworker view for the food bank receiving the applications

## License

MIT — see [LICENSE](LICENSE).
