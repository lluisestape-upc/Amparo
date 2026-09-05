---
title: "Amparo: applying for food aid without reading a single word"
published: false
tags: weekendchallenge, ai, accessibility, gemini
---

*This is a submission for [Weekend Challenge: Generosity Edition](https://dev.to/challenges/weekend-2026-09-03)*

## What I Built

Every year an enormous amount of aid money goes unclaimed. Not because it runs
out, and not because nobody needs it, but because of something much stupider.

**The form is the wall.**

If you are blind, if you never learned to read well, or if you arrived last month
and don't yet speak the language the form is printed in, the help you are
entitled to is sitting behind a document you cannot fill in. You need a
neighbour, a caseworker, or a volunteer to sit down with you. So you wait. Or you
never apply at all.

I wanted to see if the wall could just be removed.

**Amparo** completes a real aid application **entirely by talking**. No reading.
No typing. No form. It asks a few simple questions out loud, you answer in your
own words in whatever language you speak, it reads back what it understood so you
can catch mistakes, and it hands you a finished PDF to take to your local food
bank.

The part I care most about is that it accepts answers the way people actually
give them. Nobody says "household size: four". They say:

> "We're me, my mum and two little kids."

Amparo works out that there are **4 people in the household, 2 of them
children**, and moves on. It does the paperwork thinking so the person doesn't
have to.

You can also correct it at any time, about any field, however long ago you
answered. Say *"no, I said three, not four"* and it fixes that value and carries
on. That mattered more than I expected. A voice interface without a correction
path is a trap, because you cannot see what it wrote down.

## Demo

<!-- TODO: embed the 90-second demo video -->

<!-- TODO: screenshot: conversation on the left, form filling itself on the right -->

<!-- TODO: screenshot: the completed PDF -->

The moment worth watching: one messy spoken sentence, and three fields fill
themselves in on the right.

## Code

{% embed https://github.com/lluisestape-upc/Amparo %}

MIT licensed. `form_schema.py` defines the one form being filled. Swap the fields
there and the whole app targets a different aid program without another line
changing.

## How I Built It

Two models, each doing what it is genuinely good at, behind a Flask backend and
a single accessible HTML page.

**Google Gemini is the brain.** It is not transcribing. It is conducting an
interview. It reads the blank form, decides what to ask next one field at a time,
and pulls structured values out of unstructured human speech. Every turn it
returns strict JSON: the complete state of the form, what to say next, and which
language the person is speaking.

Returning the *whole* form state rather than a diff is the decision that made
corrections work. My first version returned only the fields learned that turn,
and corrections silently failed: the model kept its earlier answer. Sending back
the full state each turn removed the ambiguity entirely, because a corrected
value simply replaces the old one.

**ElevenLabs is the voice.** `eleven_multilingual_v2` speaks every question in a
warm human voice, in whatever language Gemini detected. The opening greeting is
spoken in several languages at once, so there is no language menu to read before
you can begin. You just answer in yours, and everything follows from there.

### The decisions I would defend

- **It reads back every value it records.** The person cannot see the screen, so
  a value that is not spoken aloud is a value they cannot check.
- **Errors are spoken, never silent text.** An accessibility tool that reports
  its failures in writing has failed twice.
- **When the browser cannot understand you, Gemini listens instead.** Browser
  speech recognition is weakest on accented and hesitant speech, precisely the
  people this is for, which is an awkward gap for an accessibility product. So
  every answer is recorded alongside it, and when it gives up, the audio goes to
  Gemini, which transcribes it directly and answers in the same call. Recordings
  are re-encoded to 16 kHz mono WAV in the browser rather than trusting container
  support for whatever the browser happens to record.
- **It tells you where to take it, and it does not guess.** Once the form is
  complete, the applicant's own address finds the nearest real food bank, which
  is spoken aloud and printed on the form. Those places come from OpenStreetMap,
  never from the model. I could have asked Gemini for nearby food banks and it
  would happily have answered, but sending someone who is already struggling to
  an address a model invented is worse than telling them nothing. When nothing is
  found, nothing is claimed.
- **Nothing is kept.** Answers include income and home address. They are deleted
  the moment the PDF is downloaded, and abandoned sessions expire within the
  hour. A tool that asks vulnerable people for their address should be able to
  say exactly how long it keeps it.
- **You never lose your place.** Answers survive a reload or a dropped
  connection, and it welcomes you back where you left off.

The interface itself translates into five languages and flips to right-to-left
for Arabic, because an app that speaks your language while its buttons don't is
only half accessible.

## Prize Categories

**Best Use of Google AI.** Gemini runs the entire conversation: choosing
questions, extracting structured data from natural speech, detecting the
language, applying corrections to any earlier field, and transcribing the audio
itself when the browser's recognition fails.

**Best Use of ElevenLabs.** Every word the app speaks, multilingual, including
the opening greeting that lets someone choose their language without reading
anything at all.

---

Next would be a hosted version, so it can be tried rather than watched, and more
forms. The food bank intake is one wall of many, and the interesting thing about
this approach is that the wall was never really about food.
