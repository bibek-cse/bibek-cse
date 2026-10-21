"""
Turn any image into ASCII art for the profile card.

Usage:
    pip install pillow
    python ascii_art.py my_photo.jpg            # writes cache/ascii.txt
    python build_svg.py                         # rebuilds both SVGs with the new art

Tips: a tightly cropped, high-contrast face photo on a plain background works best.
"""
import sys
from PIL import Image, ImageOps, ImageEnhance

COLS, ROWS = 36, 25          # fits the left panel of the card (wider overlaps the text)
RAMP = " .'`^\",:;Il!i~+_-?][}{1)(|tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def image_to_ascii(path, cols=COLS, rows=ROWS, invert=False):
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = img.resize((cols, rows))
    if invert:
        img = ImageOps.invert(img)
    px = img.load()
    lines = []
    for y in range(rows):
        line = ""
        for x in range(cols):
            # bright pixels -> dense characters (looks right on the dark card)
            line += RAMP[int(px[x, y] / 255 * (len(RAMP) - 1))]
        lines.append(line.rstrip())
    return lines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    art = image_to_ascii(sys.argv[1], invert="--invert" in sys.argv)
    with open("cache/ascii.txt", "w") as f:
        f.write("\n".join(art) + "\n")
    print("\n".join(art))
    print("\nSaved to cache/ascii.txt — now run: python build_svg.py")
