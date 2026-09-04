"""One-off: turn the generated JPGs into web-ready art in static/.

The dove is the mascot and sits on both light and dark backgrounds, so its
white JPG background is knocked out and the image is cropped to the artwork.
"""
from pathlib import Path
from PIL import Image

DOWN = Path.home() / "Downloads"
OUT = Path(__file__).with_name("static")

HAND = DOWN / "Gemini_Generated_Image_72ssex72ssex72ss.jpg"
DOVE = DOWN / "Gemini_Generated_Image_8xnkgw8xnkgw8xnk.jpg"


def transparent(src: Path, dst: Path, pad: int = 12):
    """Keep only the coloured artwork.

    The exported JPG has the transparency checkerboard baked in as real
    pixels, so dropping pure white is not enough. The dove is drawn in
    saturated indigo and amber, while the background (white AND the grey
    checker squares) is neutral and light — so drop every light, neutral pixel.
    """
    im = Image.open(src).convert("RGBA")
    out = []
    for (r, g, b, a) in im.getdata():
        neutral = max(r, g, b) - min(r, g, b) < 40
        light = min(r, g, b) > 140
        out.append((r, g, b, 0) if (neutral and light) else (r, g, b, a))
    im.putdata(out)
    box = im.getbbox()
    if box:
        l, t, r_, b_ = box
        l, t = max(0, l - pad), max(0, t - pad)
        r_, b_ = min(im.width, r_ + pad), min(im.height, b_ + pad)
        im = im.crop((l, t, r_, b_))
    im.thumbnail((512, 512), Image.LANCZOS)
    im.save(dst)
    print(f"{dst.name}: {im.size}")


def icon(src: Path, dst: Path):
    im = Image.open(src).convert("RGBA")
    im.thumbnail((512, 512), Image.LANCZOS)
    im.save(dst)
    print(f"{dst.name}: {im.size}")


def whiten(src: Path, dst: Path):
    """A white silhouette of the mascot, for the PDF's dark header band."""
    im = Image.open(src).convert("RGBA")
    im.putdata([(255, 255, 255, a) for (_, _, _, a) in im.getdata()])
    im.save(dst)
    print(f"{dst.name}: {im.size}")


OUT.mkdir(exist_ok=True)
icon(HAND, OUT / "logo.png")
transparent(DOVE, OUT / "dove.png")
whiten(OUT / "dove.png", OUT / "dove_white.png")
