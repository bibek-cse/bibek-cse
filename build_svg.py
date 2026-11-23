"""
Builds dark_mode.svg and light_mode.svg: a "forensic report" profile card.

The card treats the profile itself as a piece of media under analysis:
  - the binary portrait (0s and 1s that spell out my bio) gets a face-detection box, an authenticity heat-map and a sweeping scan line
  - research areas show up as "signals", live GitHub numbers as "telemetry"
  - a 40-bit invisible watermark is hidden in the bottom edge of the card (payload below)

Dynamic: if cache/profile.json exists (written daily by profile_sync.py from my repos), the research
bars, KEYWORDS, STACK languages, CURRENTLY and the text hidden in the portrait all come from it.
Without it, the static config below is used.

Edit the config, then run:   python build_svg.py
today.py (GitHub Action) then fills in the live numbers (repos, stars, commits, followers, LOC).
"""
import datetime
import hashlib
import json
from xml.sax.saxutils import escape

# ----------------------------------------------------------------------------- config
USER = "bibek-cse"
CASE_ID = "IITP-CSE-2026"
BIRTHDAY = datetime.date(2001, 1, 12)          # keep in sync with today.py
WATERMARK = "BIBEK"                            # hidden payload, 5 ASCII chars = 40 bits

SUBJECT = [
    ("name", "Bibek Das"),
    ("role", "Research Scholar, CSE @ IIT Patna"),
    ("uptime", "__AGE__"),
    ("env", "Ubuntu · Windows 11 · Vim over SSH"),
    ("compute", "Param Rudra HPC · local GPU server"),
    ("speaks", "English · Hindi · Bengali"),
]

# (label, bar fill 0..1). The bars are a visual of focus, not a measured number.
SIGNALS = [
    ("watermarking & provenance", 0.95),
    ("deepfake detection", 0.88),
    ("forgery localization", 0.78),
    ("vision-language models", 0.66),
]

CURRENTLY = [
    "stress-testing image watermarks against new attack families",
    "building AI GATE Quest: AI & GATE concepts as a game",
    "teaching Java & DSA labs at IIT Patna",
]

STACK = "Python · Java · PyTorch · OpenCV · Hugging Face · timm · Jupyter"   # fallback
FRAMEWORKS = ["PyTorch", "OpenCV", "Hugging Face", "timm"]                       # appended to live languages
CURRENTLY_PINNED = []        # lines always shown first; the rest are filled from recently pushed repos
FALLBACK_KEYWORDS = ["watermarking", "provenance", "deepfake detection", "forgery localization",
                     "adversarial attacks", "vision-language", "media forensics", "teaching"]

# text hidden in the portrait's 0s and 1s; live keywords and latest repo are appended to it
BIO = ("Bibek Das | Research Scholar, CSE, IIT Patna | image & video watermarking, provenance, "
       "deepfake detection, forgery localization, VLMs | ICPR, ICONIP, IEEE TBIOM | "
       "github.com/bibek-cse | kaggle.com/bibekcse")

CONTACT = [
    ("mail", "bibekdas.cse@gmail.com"),
    ("kaggle", "bibekcse"),
    ("linkedin", "bibek6612"),
]

VERIFY_LINE = "✓ watermark intact  ✓ no manipulation  ✓ caffeine nominal  → AUTHENTIC"

# Placeholder numbers shown until the Action runs (last known values).
LIVE_DEFAULTS = dict(repo_data="7", contrib_data="7", star_data="1", commit_data="232",
                     follower_data="0", loc_data="14,248", loc_add="72,473", loc_del="58,225")

THEMES = {
    "dark_mode.svg": dict(bg="#0d1117", panel="#161b22", border="#30363d", text="#e6edf3",
                          dim="#7d8590", accent="#39c5cf", ok="#3fb950", warn="#f0883e",
                          bad="#f85149", track="#21262d", wm_on="#0e1319", mode="dark", ink="#dbe7ee"),
    "light_mode.svg": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", text="#1f2328",
                           dim="#656d76", accent="#0a7ea4", ok="#1a7f37", warn="#bc4c00",
                           bad="#cf222e", track="#eaeef2", wm_on="#fcfcfc", mode="light", ink="#1f2328"),
}

W = 985
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


# ----------------------------------------------------------------------------- helpers
def age_string(today=None):
    today = today or datetime.date.today()
    y = today.year - BIRTHDAY.year
    m = today.month - BIRTHDAY.month
    d = today.day - BIRTHDAY.day
    if d < 0:
        m -= 1
        prev = (today.replace(day=1) - datetime.timedelta(days=1))
        d += prev.day
    if m < 0:
        y -= 1
        m += 12
    p = lambda n, u: f"{n} {u}{'' if n == 1 else 's'}"
    return f"{p(y, 'year')}, {p(m, 'month')}, {p(d, 'day')}"


def load_portrait():
    try:
        return json.load(open("cache/portrait.json", encoding="utf-8"))
    except FileNotFoundError:
        print("no cache/portrait.json: run binary_portrait.py photo.jpg first")
        return None


def payload_bits(text, n):
    stream = "".join(f"{b:08b}" for b in text.encode("ascii", "replace"))
    return (stream * (n // len(stream) + 1))[:n]


def portrait_svg(P, c, cell, x0, y0, payload):
    """One <text> per (row, brightness class); each digit placed by its own x so any font lines up."""
    levels = "abcdefghij"
    css, groups = [], {}
    for i in range(10):
        t = (i + .5) / 10
        op = (.13 + .87 * t ** 2.1) if c["mode"] == "dark" else (.05 + .95 * (1 - t) ** 1.7)
        css.append(f".p{i}{{fill-opacity:{op:.2f}}}")
        # background cells (uppercase in the grid): toned down so the face stays the focus
        bop = op * (.75 if c["mode"] == "dark" else .38)
        css.append(f".b{i}{{fill-opacity:{bop:.2f}}}")
    css.append(".pb{fill-opacity:.045}")
    out = [f'<style>.bp{{fill:{c["ink"]};font-size:7.6px;font-weight:800}}{"".join(css)}</style><g class="bp" text-anchor="middle">']
    bits = payload_bits(payload, P["cols"] * P["rows"])
    for r, line in enumerate(P["cells"]):
        y = y0 + r * cell + cell * .8
        row = {}
        for col, ch in enumerate(line):
            if ch == ".":
                cls = "pb"
            elif ch.isupper():
                cls = f"b{levels.index(ch.lower())}"
            else:
                cls = f"p{levels.index(ch)}"
            row.setdefault(cls, ([], []))
            row[cls][0].append(f"{x0 + col * cell + cell / 2:g}")
            row[cls][1].append(bits[r * P["cols"] + col])
        for cls, (xs, ds) in row.items():
            out.append(f'<text class="{cls}" y="{y:g}" x="{" ".join(xs)}">{"".join(ds)}</text>')
    out.append("</g>")
    return "\n".join(out)


def load_profile():
    try:
        return json.load(open("cache/profile.json", encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def live_content(LP):
    """Everything on the card that can change with my GitHub activity."""
    if not LP:
        return dict(signals=SIGNALS, keywords=[{"k": k, "new": False} for k in FALLBACK_KEYWORDS],
                    stack=STACK, currently=CURRENTLY, synced=None, repo_count=None, payload=BIO + " | ")
    top = max(LP["areas"].values()) or 1
    signals = [(a, .28 + .67 * v / top) for a, v in LP["areas"].items()]
    langs = [l for l, _ in LP["languages"][:4]]
    stack = ""
    for item in dict.fromkeys(langs + FRAMEWORKS):          # add items while the line still fits
        nxt = f"{stack} · {item}" if stack else item
        if len(nxt) > 68:
            break
        stack = nxt
    currently = list(CURRENTLY_PINNED)
    for r in LP["recent"]:
        if len(currently) >= 3:
            break
        tail = f" · {r['ago']}"
        desc = r["description"] or r["lang"] or "new repo"
        line = f"{r['name']}: {desc}"
        room = 62 - len(tail)
        currently.append((line if len(line) <= room else line[:room - 1].rstrip() + "…") + tail)
    kws = [k["k"] for k in LP["keywords"][:8]]
    latest = LP["recent"][0]["name"] if LP["recent"] else "-"
    payload = f"{BIO} | now: {', '.join(kws)} | latest: {latest} | synced {LP['synced']} | "
    return dict(signals=signals, keywords=LP["keywords"][:12], stack=stack, currently=currently or CURRENTLY,
                synced=LP["synced"], repo_count=LP["repo_count"], payload=payload)


def chips(y, items, c, x_start=396, x_end=965):
    """Keyword chips, wrapped onto as many rows as needed. Returns (svg, last_baseline_y)."""
    out, x, cw = [], x_start, 7.2
    for i, it in enumerate(items):
        label = it["k"] + (" ✦" if it.get("new") else "")
        w = len(label) * cw + 16
        if x + w > x_end:
            x, y = x_start, y + 26
        strong = i < 3
        fill = c["accent"] if strong else "none"
        txt = c["bg"] if strong else c["text"]
        stroke = c["accent"] if strong else c["border"]
        out.append(f'<rect x="{x:.0f}" y="{y - 14}" width="{w:.0f}" height="20" rx="10" fill="{fill}" stroke="{stroke}"/>'
                   f'<text x="{x + w / 2:.0f}" y="{y}" text-anchor="middle" font-size="12px" fill="{txt}"'
                   f'{" font-weight=\"700\"" if strong else ""}>{escape(label)}</text>')
        x += w + 8
    return "".join(out), y


def watermark_bits(payload):
    return "".join(f"{ord(ch):08b}" for ch in payload)


def section(y, num, title, c, note=""):
    s = (f'<text x="380" y="{y}" class="sec"><tspan fill="{c["accent"]}">[{num}]</tspan> {escape(title)}'
         + (f'<tspan class="dim" font-size="11px">  {escape(note)}</tspan>' if note else "")
         + '</text>')
    return s + f'<line x1="380" y1="{y + 8}" x2="965" y2="{y + 8}" stroke="{c["border"]}" stroke-dasharray="2 4"/>'


def kv(y, k, v, vid=None, x_val=490):
    idattr = f' id="{vid}"' if vid else ""
    return (f'<text x="396" y="{y}" class="dim">{escape(k)}</text>'
            f'<text x="{x_val}" y="{y}" class="val"{idattr}>{escape(v)}</text>')


# ----------------------------------------------------------------------------- card
def build(filename, c, LP=None):
    live = live_content(LP)
    P = load_portrait()

    # ---------------- right column (built first: its height decides the card height)
    r = []
    y = 80
    r.append(section(y, "01", "SUBJECT", c))
    for k, v in SUBJECT:
        y += 21
        r.append(kv(y, k, age_string() if v == "__AGE__" else v, "age_data" if v == "__AGE__" else None))

    y += 31
    r.append(section(y, "02", "RESEARCH SIGNALS", c, f"from {live['repo_count']} repos" if live["repo_count"] else ""))
    bar_x, bar_w = 640, 320
    for i, (label, frac) in enumerate(sorted(live["signals"], key=lambda s: -s[1])):
        y += 22
        full = bar_w * min(frac, 1)
        r.append(f'<text x="396" y="{y}" class="val">{escape(label)}</text>'
                 f'<rect x="{bar_x}" y="{y - 10}" width="{bar_w}" height="10" rx="2" fill="{c["track"]}"/>'
                 f'<rect x="{bar_x}" y="{y - 10}" width="{full:.0f}" height="10" rx="2" fill="{c["accent"]}" opacity="{1 - i * 0.15:.2f}">'
                 f'<animate attributeName="width" from="0" to="{full:.0f}" dur="1.4s" begin="{0.2 + i * 0.15:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>')

    y += 31
    r.append(section(y, "03", "KEYWORDS", c, "auto-extracted from my repos · ✦ new" if live["synced"] else ""))
    chip_svg, y = chips(y + 24, live["keywords"], c)
    r.append(chip_svg)

    y += 31
    r.append(section(y, "04", "STACK", c))
    y += 22
    r.append(f'<text x="396" y="{y}" class="val">{escape(live["stack"])}</text>')

    y += 31
    r.append(section(y, "05", "TELEMETRY", c, "live · refreshed daily"))
    d = LIVE_DEFAULTS
    cols = [396, 586, 776]
    y += 22
    for x, (k, vid) in zip(cols, [("repos", "repo_data"), ("contributed", "contrib_data"), ("stars", "star_data")]):
        r.append(f'<text x="{x}" y="{y}"><tspan class="dim">{k} </tspan><tspan class="val" font-weight="700" id="{vid}">{d[vid]}</tspan></text>')
    y += 21
    for x, (k, vid) in zip(cols, [("commits", "commit_data"), ("followers", "follower_data"), ("loc", "loc_data")]):
        r.append(f'<text x="{x}" y="{y}"><tspan class="dim">{k} </tspan><tspan class="val" font-weight="700" id="{vid}">{d[vid]}</tspan></text>')
    y += 21
    r.append(f'<text x="396" y="{y}"><tspan class="dim">diff  </tspan>'
             f'<tspan class="ok" id="loc_add">{d["loc_add"]}</tspan><tspan class="ok">++</tspan>  '
             f'<tspan fill="{c["bad"]}" id="loc_del">{d["loc_del"]}</tspan><tspan fill="{c["bad"]}">--</tspan></text>')

    y += 31
    r.append(section(y, "06", "CHANNELS", c))
    y += 22
    r.append(f'<text x="396" y="{y}">' + "   ".join(
        f'<tspan class="dim">{escape(k)} </tspan><tspan class="val">{escape(v)}</tspan>' for k, v in CONTACT) + '</text>')

    y += 31
    r.append(section(y, "07", "CURRENTLY", c, "latest pushes" if live["synced"] else ""))
    for item in live["currently"]:
        y += 21
        r.append(f'<text x="396" y="{y}"><tspan fill="{c["accent"]}">▸ </tspan><tspan class="val">{escape(item)}</tspan></text>')

    # ---------------- geometry
    panel_h = y + 16 - 64
    term_y = 64 + panel_h + 18
    H = term_y + 46 + 26

    # ---------------- left panel: binary portrait under analysis
    l = [f'<rect x="20" y="64" width="330" height="{panel_h}" rx="10" fill="{c["panel"]}" stroke="{c["border"]}"/>',
         '<g clip-path="url(#panelclip)">']
    if P:
        cell = 5
        x0 = 185 - P["cols"] * cell / 2
        y0 = 64 + max(14, (panel_h - P["rows"] * cell - 80) // 2)
        l.append(portrait_svg(P, c, cell, x0, y0, live["payload"]))
        fx, fy, fw, fh = P["face"]
        bx, by, bw, bh = x0 + fx * cell, y0 + fy * cell, fw * cell, fh * cell
        art_bottom = y0 + P["rows"] * cell
    else:
        bx, by, bw, bh, art_bottom = 70, 100, 222, 290, 490
    l.append(f'<rect class="scan" x="20" y="22" width="330" height="60" fill="url(#beam)"/>')
    l.append('</g>')
    L, br = 16, c["accent"]
    for (x, yy, dx, dy) in [(bx, by, 1, 1), (bx + bw, by, -1, 1), (bx, by + bh, 1, -1), (bx + bw, by + bh, -1, -1)]:
        l.append(f'<path d="M{x:.0f} {yy + dy * L:.0f} V{yy:.0f} H{x + dx * L:.0f}" fill="none" stroke="{br}" stroke-width="2"/>')
    l.append(f'<rect x="{bx:.0f}" y="{by - 20:.0f}" width="150" height="17" rx="3" fill="{br}"/>'
             f'<text x="{bx + 6:.0f}" y="{by - 7:.0f}" font-size="11px" fill="{c["bg"]}" font-weight="700">face_0 · REAL · 0.997</text>')
    digest = hashlib.sha256(live["payload"].encode()).hexdigest()
    n_bits = P["cols"] * P["rows"] if P else 0
    reps = n_bits / (8 * len(live["payload"]))
    cap = [("pixels", f'<tspan class="val">{P["cols"]}×{P["rows"]} → {n_bits:,} bits</tspan>' if P else ""),
           ("payload", f'<tspan class="val">bio + live keywords, ×{reps:.1f}</tspan>'),
           ("sha256", f'<tspan class="val">{digest[:12]}…{digest[-6:]}</tspan>'),
           ("wm", '<tspan class="ok">✓ 40-bit watermark embedded</tspan>')]
    for i, (k, v) in enumerate(cap):
        l.append(f'<text x="36" y="{art_bottom + 22 + i * 16:.0f}" font-size="11px"><tspan class="dim">{k:<9}</tspan>{v}</text>')

    # ---------------- header, top bar, terminal, watermark
    o = [f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" font-size="14px">
<title>Forensic report: {USER}</title>
<desc>Profile card for Bibek Das, styled as a media-forensics analysis report. Regenerated daily from my GitHub repos. Contains a hidden 40-bit watermark.</desc>
<style>
text, tspan {{ white-space: pre; }}
.dim {{ fill: {c['dim']}; }}
.val {{ fill: {c['text']}; }}
.sec {{ fill: {c['text']}; font-weight: 700; letter-spacing: 1px; font-size: 13px; }}
.ok  {{ fill: {c['ok']}; }}
.scan {{ animation: scan 4.5s cubic-bezier(.45,0,.55,1) infinite; }}
.pulse {{ animation: pulse 1.6s ease-in-out infinite; }}
@keyframes scan {{ 0% {{ transform: translateY(0); opacity: 0; }} 8% {{ opacity: 1; }} 92% {{ opacity: 1; }} 100% {{ transform: translateY({panel_h - 10}px); opacity: 0; }} }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
@media (prefers-reduced-motion: reduce) {{ .scan, .pulse {{ animation: none; }} .scan {{ opacity: 0; }} }}
</style>
<defs>
  <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{c['accent']}" stop-opacity="0"/>
    <stop offset=".85" stop-color="{c['accent']}" stop-opacity=".22"/>
    <stop offset="1" stop-color="{c['accent']}" stop-opacity=".9"/>
  </linearGradient>
  <clipPath id="panelclip"><rect x="20" y="64" width="330" height="{panel_h}" rx="10"/></clipPath>
  <clipPath id="typeclip"><rect x="40" y="{term_y + 10}" height="30" width="0">
    <animate attributeName="width" values="0;905;905;0" keyTimes="0;.55;.95;1" dur="9s" repeatCount="indefinite"/>
  </rect></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{c['bg']}" stroke="{c['border']}"/>''']
    synced = f"synced {live['synced']} · " if live["synced"] else ""
    o.append(f'<circle cx="32" cy="30" r="5" fill="{c["bad"]}" class="pulse"/>'
             f'<text x="46" y="35" class="sec">FORENSIC REPORT <tspan class="dim" font-weight="400" letter-spacing="0">· subject </tspan>'
             f'<tspan fill="{c["accent"]}" letter-spacing="0">{USER}</tspan></text>'
             f'<text x="965" y="35" text-anchor="end" class="dim" font-size="12px">case #{CASE_ID} · {synced}status '
             f'<tspan class="ok" font-weight="700">VERIFIED</tspan></text>'
             f'<line x1="20" y1="50" x2="965" y2="50" stroke="{c["border"]}"/>')
    o += l + r
    o.append(f'<rect x="20" y="{term_y}" width="945" height="46" rx="8" fill="{c["panel"]}" stroke="{c["border"]}"/>')
    o.append(f'<text x="36" y="{term_y + 28}" font-size="13px"><tspan fill="{c["accent"]}">$</tspan>'
             f'<tspan class="val"> verify --provenance {USER}</tspan></text>')
    o.append(f'<g clip-path="url(#typeclip)"><text x="310" y="{term_y + 28}" font-size="13px" class="ok">{escape(VERIFY_LINE)}</text></g>')

    bits = watermark_bits(WATERMARK)
    x0 = (W - len(bits) * 6) // 2
    cells = "".join(f'<rect x="{x0 + i * 6}" y="{H - 17}" width="4" height="4" fill="{c["wm_on"]}"/>'
                    for i, b in enumerate(bits) if b == "1")
    o.append(f'<g id="wm" data-hint="40 cells, MSB first, 8 bits per char">{cells}</g>')
    o.append('</svg>\n')
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


if __name__ == "__main__":
    LP = load_profile()
    print("live profile:", f"synced {LP['synced']}" if LP else "none (static config)")
    for name, colors in THEMES.items():
        build(name, colors, LP)
        print("wrote", name)
