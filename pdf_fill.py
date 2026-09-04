"""Render the collected answers into a simple, real-looking filled PDF."""

import io
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from form_schema import FIELDS, FORM_TITLE


def build_pdf(answers: dict) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 3 * cm

    c.setFont("Helvetica-Bold", 18)
    c.drawString(2.5 * cm, y, FORM_TITLE)
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    c.setFillGray(0.4)
    c.drawString(2.5 * cm, y, f"Completed with Amparo (by voice) — {date.today().isoformat()}")
    c.setFillGray(0)
    y -= 1.4 * cm

    for f in FIELDS:
        value = str(answers.get(f["id"], "")).strip() or "—"
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2.5 * cm, y, f'{f["label"]}:')
        c.setFont("Helvetica", 11)
        c.drawString(8 * cm, y, value)
        y -= 0.5 * cm
        c.setStrokeGray(0.85)
        c.line(8 * cm, y, width - 2.5 * cm, y)
        y -= 0.8 * cm

    c.showPage()
    c.save()
    return buf.getvalue()
