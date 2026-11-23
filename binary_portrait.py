"""
Turn a photo into the card's binary portrait.

Each cell of the grid becomes a single 0 or 1. Brightness only controls how strongly the digit
is drawn, so the face reads like a photo, while the digits themselves (row by row, left to right)
spell out PAYLOAD as 8-bit ASCII, repeated to fill the grid.

Usage:
    pip install opencv-python numpy
    python binary_portrait.py photo.jpg       # writes cache/portrait.json (the photo itself is NOT stored)
    python build_svg.py

Tips: a head-and-shoulders photo, face lit from the front, works best. The background is removed
automatically (GrabCut) only if KEEP_BACKGROUND = False; keep the person roughly centred.
"""
import json
import sys

import cv2
import numpy as np

COLS = 62                      # 62 x 5px = 310px wide, fits the left panel
CROP_X = 0.14                  # trim this fraction of width from each side (removes empty background)
KEEP_BACKGROUND = True         # False = cut the person out (GrabCut) and leave the background blank
LEVELS = 10                    # brightness levels stored per cell (0 = dark, 9 = bright)

PAYLOAD = ("Bibek Das | Research Scholar, CSE, IIT Patna | "
           "image & video watermarking, provenance, deepfake detection, forgery localization, VLMs | "
           "ICPR, ICONIP, IEEE TBIOM | github.com/bibek-cse | kaggle.com/bibekcse | ")


def person_mask(img):
    """GrabCut seeded for a head-and-shoulders shot: head in the centre, shoulders along the bottom."""
    h, w = img.shape[:2]
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    cv2.ellipse(mask, (w // 2, int(h * .45)), (int(w * .26), int(h * .30)), 0, 0, 360, cv2.GC_PR_FGD, -1)
    mask[int(h * .72):, int(w * .04):int(w * .96)] = cv2.GC_PR_FGD          # shoulders / shirt
    cv2.ellipse(mask, (w // 2, int(h * .48)), (int(w * .12), int(h * .14)), 0, 0, 360, cv2.GC_FGD, -1)
    mask[:int(h * .08), :] = cv2.GC_BGD                                       # top strip
    mask[:int(h * .55), :int(w * .06)] = cv2.GC_BGD                           # upper side strips
    mask[:int(h * .55), int(w * .94):] = cv2.GC_BGD
    bgm, fgm = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(img, mask, None, bgm, fgm, 10, cv2.GC_INIT_WITH_MASK)
    body = (mask == 1) | (mask == 3)
    # second pass with a plain rectangle catches dark hair that the seeded pass can miss
    rmask = np.zeros((h, w), np.uint8)
    cv2.grabCut(img, rmask, (int(w * .05), 2, int(w * .9), h - 2), np.zeros((1, 65)), np.zeros((1, 65)), 8,
                cv2.GC_INIT_WITH_RECT)
    head = ((rmask == 1) | (rmask == 3))
    head[int(h * .7):] = False
    m = (body | head).astype(np.float32)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return cv2.GaussianBlur(m, (7, 7), 0)


def face_box(img):
    """Largest face via OpenCV's Haar cascade; falls back to a centred head-shot guess."""
    h, w = img.shape[:2]
    try:
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(40, 40))
        if len(faces):
            return max(faces, key=lambda f: f[2] * f[3]).tolist()
    except (cv2.error, AttributeError):
        pass
    # fallback: largest skin-coloured blob in the upper part of the frame
    ycc = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    skin = cv2.inRange(ycc, (40, 135, 85), (255, 180, 135))
    skin[int(h * .8):] = 0
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, _, stats, _ = cv2.connectedComponentsWithStats(skin)
    if n > 1:
        x, y, bw, bh, _ = stats[1:][stats[1:, 4].argmax()]
        return [int(x), int(y), int(bw), int(bh)]
    return [int(w * .19), int(h * .17), int(w * .64), int(h * .52)]


def bits_of(text, n):
    stream = "".join(f"{b:08b}" for b in text.encode("ascii"))
    return (stream * (n // len(stream) + 1))[:n]


def build(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"could not read {path}")
    cut = int(img.shape[1] * CROP_X)
    img = img[:, cut:img.shape[1] - cut]
    h, w = img.shape[:2]
    rows = round(COLS * h / w)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(6, 6)).apply(gray)
    lum = cv2.resize(gray, (COLS, rows), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    lum = (lum - lum.min()) / max(1e-6, lum.max() - lum.min())
    pm = cv2.resize(person_mask(img), (COLS, rows), interpolation=cv2.INTER_AREA)
    if KEEP_BACKGROUND:
        mask = np.ones_like(pm)
    else:
        mask = pm

    fade = np.clip((rows - 1 - np.arange(rows)) / (rows * .12), 0, 1)[:, None]   # soften the bottom edge
    if not KEEP_BACKGROUND:
        lum = lum * (0.35 + 0.65 * fade)
    if not KEEP_BACKGROUND:
        mask = mask * np.where(fade > 0.05, 1, 0)
    bits = bits_of(PAYLOAD, COLS * rows)
    cells = []
    for r in range(rows):
        line = ""
        for c in range(COLS):
            lvl = min(LEVELS - 1, int(lum[r, c] * LEVELS))
            if mask[r, c] < 0.5:
                line += "."                                     # background removed
            elif KEEP_BACKGROUND and pm[r, c] < 0.5:
                line += "ABCDEFGHIJ"[lvl]                       # background kept (uppercase = not the person)
            else:
                line += "abcdefghij"[lvl]
        cells.append(line)

    face = face_box(img)
    if face:  # pixels -> cell units
        sx = COLS / w
        face = [round(v * sx, 1) for v in face]                 # in cell units

    out = dict(cols=COLS, rows=rows, cells=cells, bits=bits, face=face, payload_len=len(PAYLOAD))
    with open("cache/portrait.json", "w") as f:
        json.dump(out, f)
    print(f"{COLS}x{rows} cells, {COLS * rows} bits, face={face}")
    for line in cells:                                          # quick terminal preview
        print("".join(" .:-=+*#%@"["abcdefghij".index(ch.lower())] if ch != "." else " " for ch in line))
    print("\nSaved cache/portrait.json — now run: python build_svg.py")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    build(sys.argv[1])
