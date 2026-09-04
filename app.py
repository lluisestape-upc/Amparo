"""Amparo — Flask backend.

Endpoints:
  GET  /              -> the (accessible) single-page UI
  GET  /api/form      -> the form definition, for the live-filling panel
  POST /api/step      -> {session_id, text} -> {reply, answers, lang, done, ...}
  POST /api/tts       -> {text}             -> spoken audio (ElevenLabs)
  POST /api/pdf       -> {session_id}       -> the filled PDF
  POST /api/forget    -> {session_id}       -> erase this person's answers

Sessions are persisted to a small JSON file so a page reload (or a server
restart) never makes a person start over — the browser keeps its session id
in localStorage. Answers are deleted as soon as the PDF is downloaded.
"""

import io
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file, send_from_directory

import brain
import tts
from form_schema import FIELDS, FIELD_IDS, FORM_TITLE
from pdf_fill import build_pdf

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
# Don't let a browser hold on to stale art or an old page between edits.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

STORE = Path(__file__).with_name("sessions.json")


def _load() -> dict:
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(sessions: dict) -> None:
    STORE.write_text(json.dumps(sessions, ensure_ascii=False), encoding="utf-8")


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/form")
def api_form():
    return jsonify(
        {
            "title": FORM_TITLE,
            "fields": [{"id": f["id"], "label": f["label"]} for f in FIELDS],
        }
    )


@app.post("/api/step")
def api_step():
    body = request.get_json(force=True)
    sid = body.get("session_id", "default")
    text = body.get("text", "")

    sessions = _load()
    answers = sessions.get(sid, {})

    try:
        result = brain.step(answers, text)
    except Exception as exc:  # API down, quota, bad JSON — never leave them stuck
        app.logger.error("brain.step failed: %s", exc)
        return jsonify(
            {
                "reply": "I'm sorry, I had trouble just then. Please tap the "
                         "microphone and say that again.",
                "answers": answers,
                "field_focus": "",
                "lang": "en-US",
                "done": False,
                "error": True,
                "total_fields": len(FIELD_IDS),
                "filled_fields": len(answers),
            }
        )

    # The brain returns the complete state, so a corrected value replaces the
    # old one. Fields it omits keep whatever we already had.
    answers.update(result["answers"])
    sessions[sid] = answers
    _save(sessions)

    return jsonify(
        {
            "reply": result["reply"],
            "answers": answers,
            "field_focus": result["field_focus"],
            "lang": result["lang"],
            "done": result["done"],
            "error": False,
            "total_fields": len(FIELD_IDS),
            "filled_fields": len(answers),
        }
    )


@app.post("/api/tts")
def api_tts():
    text = request.get_json(force=True).get("text", "")
    if not text.strip():
        return ("", 204)
    try:
        return send_file(io.BytesIO(tts.speak(text)), mimetype="audio/mpeg")
    except Exception as exc:
        app.logger.error("tts failed: %s", exc)
        return ("", 204)  # stay silent rather than break the flow


@app.post("/api/pdf")
def api_pdf():
    sid = request.get_json(force=True).get("session_id", "default")
    answers = _load().get(sid, {})
    return send_file(
        io.BytesIO(build_pdf(answers)),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="food_assistance_application.pdf",
    )


@app.post("/api/forget")
def api_forget():
    """Erase this person's answers. Called right after they download the PDF."""
    sid = request.get_json(force=True).get("session_id", "default")
    sessions = _load()
    if sessions.pop(sid, None) is not None:
        _save(sessions)
    return jsonify({"forgotten": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
