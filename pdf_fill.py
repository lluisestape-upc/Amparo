"""Render the collected answers into the completed application PDF.

This is the one thing the applicant walks away with, and they may hand it to a
caseworker, so it should look like a real form rather than a printout.
"""

import io
from datetime import date
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from form_schema import FIELDS, FORM_TITLE

INDIGO = HexColor("#3730c4")
AMBER = HexColor("#f5a524")
INK = HexColor("#1a1a2e")
MUTED = HexColor("#6b7280")
RULE = HexColor("#d8dbe6")

LOGO = Path(__file__).with_name("static") / "dove_white.png"


def build_pdf(answers: dict) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # --- Header band -------------------------------------------------------
    band = 3.4 * cm
    c.setFillColor(INDIGO)
    c.rect(0, height - band, width, band, stroke=0, fill=1)
    c.setFillColor(AMBER)
    c.rect(0, height - band - 4, width, 4, stroke=0, fill=1)

    if LOGO.exists():
        try:
            c.drawImage(str(LOGO), width - 4.4 * cm, height - band + 0.7 * cm,
                        width=2.6 * cm, height=2.1 * cm, mask="auto")
        except Exception:
            pass                                   # the form matters, not the mark

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(2.2 * cm, height - 1.9 * cm, FORM_TITLE)
    c.setFont("Helvetica", 10)
    c.drawString(2.2 * cm, height - 2.6 * cm, "Completed with Amparo — by voice")

    # --- Fields ------------------------------------------------------------
    y = height - band - 2.2 * cm
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(2.2 * cm, y, "APPLICANT DETAILS")
    y -= 0.9 * cm

    for f in FIELDS:
        value = str(answers.get(f["id"], "")).strip() or "—"
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(2.2 * cm, y, f["label"])
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(8.4 * cm, y - 0.05 * cm, value)
        y -= 0.55 * cm
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.line(2.2 * cm, y, width - 2.2 * cm, y)
        y -= 0.95 * cm

    # --- Signature line ----------------------------------------------------
    y -= 0.8 * cm
    c.setStrokeColor(RULE)
    c.line(2.2 * cm, y, 9 * cm, y)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(2.2 * cm, y - 0.5 * cm, "Applicant signature")
    c.drawString(11 * cm, y - 0.5 * cm, f"Date completed: {date.today().isoformat()}")

    # --- Footer ------------------------------------------------------------
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawString(2.2 * cm, 1.6 * cm,
                 "Completed by spoken conversation. The applicant's answers were "
                 "read back and confirmed aloud before this form was produced.")

    c.showPage()
    c.save()
    return buf.getvalue()
