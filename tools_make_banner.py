"""Build the cover image for the DEV post (1000x420, DEV's recommended size)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
STATIC = HERE / "static"
OUT = HERE / "banner.png"

W, H = 1000, 420
BG = (246, 247, 251)
INDIGO = (55, 48, 196)
MUTED = (107, 114, 128)
AMBER = (245, 165, 36)


def font(size, bold=True):
    for name in (("segoeuib.ttf", "seguisb.ttf") if bold else ("segoeui.ttf",)) + \
                (("arialbd.ttf",) if bold else ("arial.ttf",)):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# A quiet amber rule along the bottom, the app's accent.
d.rectangle([0, H - 7, W, H], fill=AMBER)

# The dove, large on the right.
dove = Image.open(STATIC / "dove.png").convert("RGBA")
dove.thumbnail((330, 330), Image.LANCZOS)
img.paste(dove, (W - dove.width - 70, (H - dove.height) // 2 - 6), dove)

x = 78
# The hand mark, small, above the name. Its own background is a flat off-white
# baked into the source, so drop light neutral pixels or it shows as a tile.
logo = Image.open(STATIC / "logo.png").convert("RGBA")
logo.putdata([
    (r, g, b, 0) if (max(r, g, b) - min(r, g, b) < 40 and min(r, g, b) > 140) else (r, g, b, a)
    for (r, g, b, a) in logo.getdata()
])
logo = logo.crop(logo.getbbox())
logo.thumbnail((74, 74), Image.LANCZOS)
img.paste(logo, (x, 96), logo)

d.text((x, 186), "Amparo", font=font(96), fill=INDIGO)
d.text((x + 4, 296), "Apply for aid entirely by talking —", font=font(27, bold=False), fill=MUTED)
d.text((x + 4, 331), "in your own language.", font=font(27, bold=False), fill=MUTED)

img.save(OUT)
print(f"{OUT.name}: {img.size}")
