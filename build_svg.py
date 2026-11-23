"""
Builds dark_mode.svg and light_mode.svg: a "forensic report" profile card.

The card treats the profile itself as a piece of media under analysis:
  - the ASCII portrait gets a face-detection box, an authenticity heat-map and a sweeping scan line
  - research areas show up as "signals", live GitHub numbers as "telemetry"
  - a 40-bit invisible watermark is hidden in the bottom edge of the card (payload below)

Edit the config, then run:   python build_svg.py
today.py (GitHub Action) only refreshes the ids listed in LIVE_IDS; everything else comes from here.
"""
import datetime
import hashlib
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

STACK = "Python · Java · PyTorch · OpenCV · Hugging Face · timm · Jupyter"

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
                          bad="#f85149", track="#21262d", wm_on="#0e1319"),
    "light_mode.svg": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", text="#1f2328",
                           dim="#656d76", accent="#0a7ea4", ok="#1a7f37", warn="#bc4c00",
                           bad="#cf222e", track="#eaeef2", wm_on="#fcfcfc"),
}

W, H = 985, 640
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


def load_art():
    try:
        lines = [l.rstrip("\n") for l in open("cache/ascii.txt", encoding="utf-8")]
    except FileNotFoundError:
        lines = []
    while lines and not lines[-1].strip():
        lines.pop()
    return lines[:25]


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
def build(filename, c):
    o = []
    o.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" font-size="14px">
<title>Forensic report: {USER}</title>
<desc>Profile card for Bibek Das, styled as a media-forensics analysis report. Contains a hidden 40-bit watermark.</desc>
<style>
text, tspan {{ white-space: pre; }}
.dim {{ fill: {c['dim']}; }}
.val {{ fill: {c['text']}; }}
.sec {{ fill: {c['text']}; font-weight: 700; letter-spacing: 1px; font-size: 13px; }}
.art {{ fill: {c['dim']}; font-size: 13px; }}
.ok  {{ fill: {c['ok']}; }}
.scan {{ animation: scan 4.5s cubic-bezier(.45,0,.55,1) infinite; }}
.pulse {{ animation: pulse 1.6s ease-in-out infinite; }}
@keyframes scan {{ 0% {{ transform: translateY(0); opacity: 0; }} 8% {{ opacity: 1; }} 92% {{ opacity: 1; }} 100% {{ transform: translateY(452px); opacity: 0; }} }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
@media (prefers-reduced-motion: reduce) {{ .scan, .pulse {{ animation: none; }} .scan {{ opacity: 0; }} }}
</style>
<defs>
  <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{c['accent']}" stop-opacity="0"/>
    <stop offset=".85" stop-color="{c['accent']}" stop-opacity=".22"/>
    <stop offset="1" stop-color="{c['accent']}" stop-opacity=".9"/>
  </linearGradient>
  <radialGradient id="heat" cx=".5" cy=".45" r=".55">
    <stop offset="0" stop-color="{c['ok']}" stop-opacity=".22"/>
    <stop offset=".6" stop-color="{c['ok']}" stop-opacity=".08"/>
    <stop offset="1" stop-color="{c['ok']}" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="panelclip"><rect x="20" y="64" width="330" height="470" rx="10"/></clipPath>
  <clipPath id="typeclip"><rect x="40" y="566" height="30" width="0">
    <animate attributeName="width" values="0;905;905;0" keyTimes="0;.55;.95;1" dur="9s" repeatCount="indefinite"/>
  </rect></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{c['bg']}" stroke="{c['border']}"/>
''')

    # --- top bar
    o.append(f'<circle cx="32" cy="30" r="5" fill="{c["bad"]}" class="pulse"/>'
             f'<text x="46" y="35" class="sec">FORENSIC REPORT <tspan class="dim" font-weight="400" letter-spacing="0">· subject </tspan>'
             f'<tspan fill="{c["accent"]}" letter-spacing="0">{USER}</tspan></text>'
             f'<text x="965" y="35" text-anchor="end" class="dim" font-size="12px">case #{CASE_ID} · status '
             f'<tspan class="ok" font-weight="700">VERIFIED</tspan></text>'
             f'<line x1="20" y1="50" x2="965" y2="50" stroke="{c["border"]}"/>')

    # --- left panel: portrait under analysis
    o.append(f'<rect x="20" y="64" width="330" height="470" rx="10" fill="{c["panel"]}" stroke="{c["border"]}"/>')
    o.append('<g clip-path="url(#panelclip)">')
    o.append('<ellipse cx="185" cy="250" rx="140" ry="190" fill="url(#heat)"/>')
    o.append('<text class="art">')
    for i, line in enumerate(load_art()):
        o.append(f'<tspan x="38" y="{106 + i * 15.6:.1f}">{escape(line)}</tspan>')
    o.append('</text>')
    o.append(f'<rect class="scan" x="20" y="22" width="330" height="60" fill="url(#beam)"/>')
    o.append('</g>')
    # face-detection brackets
    bx, by, bw, bh, L = 70, 100, 222, 290, 18
    br = c["accent"]
    for (x, y, dx, dy) in [(bx, by, 1, 1), (bx + bw, by, -1, 1), (bx, by + bh, 1, -1), (bx + bw, by + bh, -1, -1)]:
        o.append(f'<path d="M{x} {y + dy * L} V{y} H{x + dx * L}" fill="none" stroke="{br}" stroke-width="2"/>')
    o.append(f'<rect x="{bx}" y="{by - 20}" width="150" height="17" rx="3" fill="{br}"/>'
             f'<text x="{bx + 6}" y="{by - 7}" font-size="11px" fill="{c["bg"]}" font-weight="700">face_0 · REAL · 0.997</text>')
    digest = hashlib.sha256(USER.encode()).hexdigest()
    o.append(f'<text x="36" y="508" font-size="11px" class="dim">sha256  <tspan class="val">{digest[:12]}…{digest[-6:]}</tspan></text>'
             f'<text x="36" y="524" font-size="11px" class="dim">wm      <tspan class="ok">✓ 40-bit payload embedded</tspan></text>')

    # --- right column
    y = 80
    o.append(section(y, "01", "SUBJECT", c))
    age = age_string()
    for k, v in SUBJECT:
        y += 21
        o.append(kv(y, k, age if v == "__AGE__" else v, "age_data" if v == "__AGE__" else None))

    y += 31
    o.append(section(y, "02", "RESEARCH SIGNALS", c))
    bar_x, bar_w = 640, 320
    for i, (label, frac) in enumerate(SIGNALS):
        y += 22
        full = bar_w * frac
        o.append(f'<text x="396" y="{y}" class="val">{escape(label)}</text>'
                 f'<rect x="{bar_x}" y="{y - 10}" width="{bar_w}" height="10" rx="2" fill="{c["track"]}"/>'
                 f'<rect x="{bar_x}" y="{y - 10}" width="{full:.0f}" height="10" rx="2" fill="{c["accent"]}" opacity="{1 - i * 0.15:.2f}">'
                 f'<animate attributeName="width" from="0" to="{full:.0f}" dur="1.4s" begin="{0.2 + i * 0.15:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>')

    y += 31
    o.append(section(y, "03", "STACK", c))
    y += 22
    o.append(f'<text x="396" y="{y}" class="val">{escape(STACK)}</text>')

    y += 31
    o.append(section(y, "04", "TELEMETRY", c, "live · refreshed daily"))
    d = LIVE_DEFAULTS
    cols = [396, 586, 776]
    y += 22
    for x, (k, vid) in zip(cols, [("repos", "repo_data"), ("contributed", "contrib_data"), ("stars", "star_data")]):
        o.append(f'<text x="{x}" y="{y}"><tspan class="dim">{k} </tspan><tspan class="val" font-weight="700" id="{vid}">{d[vid]}</tspan></text>')
    y += 21
    for x, (k, vid) in zip(cols, [("commits", "commit_data"), ("followers", "follower_data"), ("loc", "loc_data")]):
        o.append(f'<text x="{x}" y="{y}"><tspan class="dim">{k} </tspan><tspan class="val" font-weight="700" id="{vid}">{d[vid]}</tspan></text>')
    y += 21
    o.append(f'<text x="396" y="{y}"><tspan class="dim">diff  </tspan>'
             f'<tspan class="ok" id="loc_add">{d["loc_add"]}</tspan><tspan class="ok">++</tspan>  '
             f'<tspan fill="{c["bad"]}" id="loc_del">{d["loc_del"]}</tspan><tspan fill="{c["bad"]}">--</tspan></text>')

    y += 31
    o.append(section(y, "05", "CHANNELS", c))
    y += 22
    o.append(f'<text x="396" y="{y}">' + "   ".join(
        f'<tspan class="dim">{escape(k)} </tspan><tspan class="val">{escape(v)}</tspan>' for k, v in CONTACT) + '</text>')
    if y > 538:
        raise SystemExit(f"right column overflows ({y}px); remove a row")

    # --- bottom: verification terminal
    o.append(f'<rect x="20" y="556" width="945" height="46" rx="8" fill="{c["panel"]}" stroke="{c["border"]}"/>')
    o.append(f'<text x="36" y="584" font-size="13px"><tspan fill="{c["accent"]}">$</tspan>'
             f'<tspan class="val"> verify --provenance {USER}</tspan></text>')
    o.append(f'<g clip-path="url(#typeclip)"><text x="310" y="584" font-size="13px" class="ok">{escape(VERIFY_LINE)}</text></g>')

    # --- hidden watermark: 40 cells, 1-bits a hair off the background colour
    bits = watermark_bits(WATERMARK)
    x0 = (W - len(bits) * 6) // 2
    cells = "".join(f'<rect x="{x0 + i * 6}" y="{H - 22}" width="4" height="4" fill="{c["wm_on"]}"/>'
                    for i, b in enumerate(bits) if b == "1")
    o.append(f'<g id="wm" data-hint="40 cells, MSB first, 8 bits per char">{cells}</g>')

    o.append('</svg>\n')
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


if __name__ == "__main__":
    for name, colors in THEMES.items():
        build(name, colors)
        print("wrote", name)
