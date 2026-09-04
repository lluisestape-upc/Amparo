"""The brain: Gemini drives the conversation and fills the form.

One function, `step()`, is called each turn. Given the form, what we already
know, and the person's latest spoken words (in ANY language), Gemini decides:
  - which fields it can now fill (or CORRECT),
  - what to say next, in the person's language,
  - which language they are speaking, so speech recognition can follow them,
  - whether the form is complete.

It always returns strict JSON so the rest of the app never parses free text.
"""

import json
import os
import time

from google import genai
from google.genai import types

from form_schema import FIELDS, FIELD_IDS, FORM_TITLE

# A "lite" model: fast, and its free tier allows far more requests per day than
# the flagship models, which matters when every turn of a conversation is a call.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

_client = None


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env.")
        _client = genai.Client(api_key=key)
    return _client


SYSTEM_PROMPT = f"""\
You are Amparo, a warm, patient assistant that helps a vulnerable person
complete a real aid application ENTIRELY by talking. The person may be blind,
may not read well, or may not speak the local language. Never make them read.

You are filling out this form: "{FORM_TITLE}".
Fields (id | label | hint):
""" + "\n".join(f'- {f["id"]} | {f["label"]} | {f["hint"]}' for f in FIELDS) + f"""

RULES
- Detect the language of the person's words and ALWAYS reply in that same language.
- Ask about ONE field at a time, in simple, kind words. Never ask for two things at once.
- People answer messily ("we're me, my mum and two kids"). Infer the values.
  From that example you can fill household_size=4 and children_count=2.
- If the person asks what a field means, explain it simply using the hint, then ask again.
- Accept estimates. Do not demand precision or documents.

BE BRIEF — they are listening, not reading
- Every reply is AT MOST two short sentences: a quick read-back of what you
  just recorded, then the next question. Never list everything you know.

READ BACK WHAT YOU HEARD (important — they cannot see the screen)
- Whenever you fill or change a field, briefly state that value back, e.g.
  "Four people, got it. Now, roughly how much...". One short clause only.

CORRECTIONS (this is critical — obey the person over your own earlier notes)
- The person may correct you at ANY time, about ANY field, even one answered
  long ago: "no, that's wrong", "I said three, not four", "actually my address
  is...". The person is ALWAYS right; your earlier value is ALWAYS wrong.
- Apply the correction immediately in "answers" — replace the old value with
  the new one. Never keep the old value, never argue, never repeat the old
  number back. Acknowledge the fix in one short clause ("Three, thank you —
  I've changed it.") and carry on.
- If it is genuinely unclear which field they mean, ask which one.

FINISHING
- When every field has a value, set "done": true. Make "reply" a short spoken
  summary read back for confirmation, then tell them what happens next: they
  can download the completed application and take or send it to their local
  food bank, and that their answers are deleted afterwards.

OUTPUT
Return ONLY JSON with this shape:
{{
  "answers": {{ "<field_id>": "<value>", ... }},
  "reply": "<what to say next, in the person's language — two short sentences max>",
  "field_focus": "<the field_id you are now asking about, or empty if done>",
  "lang": "<BCP-47 tag for the language the person is speaking, e.g. en-US, es-ES, ar-SA>",
  "done": <true|false>
}}
"answers" is the COMPLETE current state of the form: every field you know so
far, carried over unchanged, PLUS anything you learned or corrected this turn.
A corrected field must appear with its NEW value. Omit fields still unknown.
Valid field ids: {FIELD_IDS}."""

# The very first turn: greet in several languages so a person who cannot read
# the language selector can simply answer in their own language.
FIRST_TURN = (
    "This is the very start. The person has not spoken yet and you do not know "
    "their language. Say ONE very short line — that you will help them apply "
    "for food assistance and they may answer in their own language — in "
    "English, then Spanish, then Arabic. Finally ask, in English only, for "
    "their name.\n"
    "FORMAT: put each language on its OWN LINE, separated by a real newline "
    "character (\\n). The English question goes on a final separate line. "
    "Never run two languages together on one line. Example shape:\n"
    "<english line>\\n<spanish line>\\n<arabic line>\\n<english question>\n"
    'Keep the whole reply under 45 words. Set "lang" to "en-US" and '
    '"field_focus" to "full_name".'
)


def step(answers: dict, user_text: str) -> dict:
    """Advance the conversation one turn.

    answers:   fields filled so far (dict of field_id -> value)
    user_text: the person's latest utterance ("" on the very first call)
    returns:   {"updates", "reply", "field_focus", "lang", "done"}
    """
    if not user_text.strip() or (user_text == "__RESUME__" and not answers):
        turn = FIRST_TURN
    elif user_text == "__RESUME__":
        known = json.dumps(answers, ensure_ascii=False)
        turn = (
            f"The person left and has come back. Already known: {known}\n"
            "Welcome them back warmly in their language, say briefly that you "
            "kept their answers, and ask the next field that is still missing."
        )
    else:
        known = json.dumps(answers, ensure_ascii=False)
        turn = (
            f"Already known: {known}\n"
            f'The person just said: "{user_text}"\n'
            "Remember: this may be a correction to any field, not only the one you asked about."
        )

    # Gemini occasionally returns a transient 503 ("high demand") or malformed
    # JSON. A person mid-application must never see that, so retry quietly.
    data = None
    last_error = None
    for attempt in range(3):
        try:
            resp = _get_client().models.generate_content(
                model=MODEL,
                contents=turn,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            data = json.loads(resp.text)
            break
        except Exception as exc:
            last_error = exc
            # A quota error (429) will not pass on a retry — retrying just burns
            # three requests instead of one. Only wait out transient failures.
            if "RESOURCE_EXHAUSTED" in str(exc) or "429" in str(exc):
                break
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    if data is None:
        raise last_error
    # Keep only valid field ids with real values; never trust the model blindly.
    returned = {
        k: str(v).strip()
        for k, v in data.get("answers", {}).items()
        if k in FIELD_IDS and str(v).strip()
    }
    return {
        "answers": returned,
        "reply": data.get("reply", ""),
        "field_focus": data.get("field_focus", ""),
        "lang": data.get("lang", "") or "en-US",
        "done": bool(data.get("done", False)),
    }
