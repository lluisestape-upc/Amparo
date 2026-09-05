---
title: "Amparo: applying for food aid without reading a single word"
published: false
tags: weekendchallenge, ai, accessibility, gemini
---

Every year, an enormous amount of aid money goes unclaimed. Not because it runs
out, and not because nobody needs it — but because of something much stupider.

The form is the wall.

If you are blind, if you never learned to read well, or if you arrived last
month and don't yet speak the language the form is printed in, then the help you
are entitled to is sitting behind a document you cannot fill in. You need a
neighbour, a caseworker, or a volunteer to sit down with you. So you wait. Or you
don't apply at all.

I wanted to see if the wall could just be removed.

## What I Built

**Amparo** is a web app that completes a real aid application **entirely by
talking**. No reading. No typing. No form.

It asks you a few simple questions out loud. You answer in your own words, in
whatever language you speak. It fills in the application for you, reads back what
it understood so you can catch mistakes, and hands you a finished PDF to take to
your local food bank.

The part I care most about is that it accepts answers the way people actually
give them. You don't say "household size: four". You say:

> "We're me, my mum and two little kids."

And Amparo works out that there are **4 people in the household, 2 of them
children**, and moves on to the next question. It does the paperwork thinking so
the person doesn't have to.

You can also correct it at any time, about anything, however long ago you said
it — *"no, I said three, not four"* — and it changes that field and carries on.
That mattered more than I expected: a voice interface without a correction path
is a trap, because you can't see what it wrote down.

## Demo

<!-- TODO: embed the 90-second demo video here -->

<!-- TODO: screenshot — the conversation on the left, the form filling itself on the right -->

<!-- TODO: screenshot — the completed PDF -->

The moment worth watching: one messy spoken sentence, and three fields fill
themselves in on the right.

## Code

{% embed https://github.com/lluisestape-upc/Amparo %}

MIT licensed. `form_schema.py` defines the one form being filled — swap the
fields there and the whole app targets a different aid program without another
line changing.

## How I Built It

Two models, each doing the thing it's genuinely good at.

**Google Gemini is the brain.** It isn't transcribing — it's conducting an
interview. It reads the blank form, decides what to ask next, one field at a
time, and extracts structured values out of unstructured human speech. Each turn
it returns strict JSON: the complete state of the form, what to say next, and
which language the person is speaking. Returning the *whole* form state rather
than a diff is what makes corrections work — a corrected value simply replaces
the old one, with no ambiguity about what changed.

**ElevenLabs is the voice.** `eleven_multilingual_v2` speaks every question in a
warm human voice, in whatever language Gemini detected. The opening greeting is
spoken in several languages at once, so there is no language menu to read before
you can start — you just answer in yours, and everything follows.

A Flask backend holds it together, and the front end is a single accessible HTML
page.

### The decisions I'd defend

- **It reads back every value it records.** The person can't see the screen, so
  a value that isn't spoken aloud is a value they can't check.
- **Errors are spoken, never silent text.** An accessibility tool that reports
  its failures in writing has failed twice.
- **When the browser can't understand you, Gemini listens instead.** Browser
  speech recognition is weakest on accented and hesitant speech — precisely the
  people this is for. So every answer is recorded alongside it, and when it gives
  up, the audio goes to Gemini, which transcribes it directly. Recordings are
  re-encoded to 16 kHz WAV in the browser rather than trusting container support.
- **Nothing is kept.** Answers include income and home address. They're deleted
  the moment the PDF is downloaded, and abandoned sessions expire within the
  hour. A tool that asks vulnerable people for their address should be able to
  say exactly how long it keeps it.
- **You never lose your place.** Answers survive a reload or a dropped
  connection, and it welcomes you back where you left off.

## Prize Categories

**Google AI** — Gemini runs the entire conversation: choosing questions,
extracting structured data from natural speech, detecting language, applying
corrections, and transcribing audio when the browser fails.

**ElevenLabs** — every word the app speaks, multilingual, including the opening
that lets someone pick their language without reading anything.

## What I'd do next

A hosted version, so it can be tried rather than watched. And more forms — the
food bank intake is one wall of many, and the interesting thing about this
approach is that the wall was never really about food.

---

*Built for the DEV Weekend Challenge: Generosity Edition.*
