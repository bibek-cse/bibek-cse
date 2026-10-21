"""
Builds dark_mode.svg and light_mode.svg from the PROFILE config below.

Edit the text here, then run:   python build_svg.py
The GitHub Action (today.py) only refreshes the numbers (age, repos, stars,
commits, followers, lines of code); everything else comes from this file.
"""
from xml.sax.saxutils import escape

WIDTH = 60            # characters in each right-hand line (do not change unless you resize the card)
HEADER = "bibek@iitp"

# Each section is a list of rows. A row is (key, value), None for a blank "." line.
# Keys with a dot (e.g. "Research.Forensics") get both parts coloured like the original.
PROFILE = [
    ("OS", "Ubuntu, Windows 11"),
    ("Uptime", "__AGE__"),                     # filled in daily by today.py
    # ("Host", "Indian Institute of Technology Patna"),
    ("Kernel", "Research Scholar, CSE"),
    ("IDE", "VSCode, Jupyter, Vim on SSH"),
    None,
    ("Languages.Programming", "Python, Java"),
    ("Languages.Frameworks", "PyTorch, OpenCV, HF, timm"),
    ("Languages.Real", "English, Hindi, Bengali"),
    None,
    ("Research.Provenance", "Image/Video Watermarking"),
    ("Research.Forensics", "Deepfakes, Biometric"),
    ("Research.Venues", "ICPR, ICONIP, IEEE TBIOM"), 
]

CONTACT = [
    ("Email.Academic", "bibekdas.cse@gmail.com"),         
    ("Kaggle", "bibek.cse"),
    ("LinkedIn", "https://in.linkedin.com/in/bibek6612"),             
    ("Scholar", "Bibek Das"),
]

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff",
                          add="#3fb950", dele="#f85149", cc="#616e7f"),
    "light_mode.svg": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069",
                           add="#1a7f37", dele="#cf222e", cc="#c2cfde"),
}

X_ART, X_INFO, LINE_H, TOP = 15, 390, 20, 30
CARD_W, CARD_H = 985, 530


def key_spans(key):
    parts = key.split(".")
    return ".".join(f'<tspan class="key">{escape(p)}</tspan>' for p in parts)


def row(y, key, value, value_id=None, dots_id=None):
    """'. Key: ....... value' padded to exactly WIDTH characters."""
    n_dots = WIDTH - (2 + len(key) + 1 + len(value) + 2)   # ". " + key + ":" + " ... " spacing
    dots = " " + "." * max(n_dots, 1) + " "
    vid = f' id="{value_id}"' if value_id else ""
    did = f' id="{dots_id}"' if dots_id else ""
    return (f'<tspan x="{X_INFO}" y="{y}" class="cc">. </tspan>{key_spans(key)}:'
            f'<tspan class="cc"{did}>{dots}</tspan><tspan class="value"{vid}>{escape(value)}</tspan>')


def header(y, title):
    pad = WIDTH - len(title) - 5
    return f'<tspan x="{X_INFO}" y="{y}">{escape(title)}</tspan> -{"—" * pad}-—-'


def load_art():
    try:
        lines = [l.rstrip("\n") for l in open("cache/ascii.txt")]
    except FileNotFoundError:
        lines = []
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    rows = (CARD_H - TOP) // LINE_H + 1
    top_pad = max(0, (rows - len(lines)) // 2)
    return [""] * top_pad + lines[:rows]


def build(filename, c, age_placeholder="0 years, 0 months, 0 days"):
    out = [f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" font-family="ConsolasFallback,Consolas,monospace" width="{CARD_W}px" height="{CARD_H}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {c['key']};}}
.value {{fill: {c['value']};}}
.addColor {{fill: {c['add']};}}
.delColor {{fill: {c['dele']};}}
.cc {{fill: {c['cc']};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{CARD_W}px" height="{CARD_H}px" fill="{c['bg']}" rx="15"/>
<text x="{X_ART}" y="{TOP}" fill="{c['text']}" class="ascii">''']
    for i, line in enumerate(load_art()):
        out.append(f'<tspan x="{X_ART}" y="{TOP + i * LINE_H}">{escape(line)}</tspan>')
    out.append('</text>')
    out.append(f'<text x="{X_INFO}" y="{TOP}" fill="{c["text"]}">')

    y = TOP
    out.append(header(y, HEADER))
    for item in PROFILE:
        y += LINE_H
        if item is None:
            out.append(f'<tspan x="{X_INFO}" y="{y}" class="cc">. </tspan>')
        elif item[1] == "__AGE__":
            out.append(row(y, item[0], age_placeholder, "age_data", "age_data_dots"))
        else:
            out.append(row(y, *item))

    y += LINE_H * 2
    out.append(header(y, "- Contact"))
    for k, v in CONTACT:
        y += LINE_H
        out.append(row(y, k, v))

    y += LINE_H * 2
    out.append(header(y, "- GitHub Stats"))
    y += LINE_H
    out.append(f'<tspan x="{X_INFO}" y="{y}" class="cc">. </tspan><tspan class="key">Repos</tspan>:'
               '<tspan class="cc" id="repo_data_dots"> .... </tspan><tspan class="value" id="repo_data">0</tspan> '
               '{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">0</tspan>} | '
               '<tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> ............ </tspan>'
               '<tspan class="value" id="star_data">0</tspan>')
    y += LINE_H
    out.append(f'<tspan x="{X_INFO}" y="{y}" class="cc">. </tspan><tspan class="key">Commits</tspan>:'
               '<tspan class="cc" id="commit_data_dots"> ...................... </tspan><tspan class="value" id="commit_data">0</tspan> | '
               '<tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> ......... </tspan>'
               '<tspan class="value" id="follower_data">0</tspan>')
    y += LINE_H
    out.append(f'<tspan x="{X_INFO}" y="{y}" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:'
               '<tspan class="cc" id="loc_data_dots"> ......... </tspan><tspan class="value" id="loc_data">0</tspan> ( '
               '<tspan class="addColor" id="loc_add">0</tspan><tspan class="addColor">++</tspan>, '
               '<tspan id="loc_del_dots"> ....... </tspan><tspan class="delColor" id="loc_del">0</tspan>'
               '<tspan class="delColor">--</tspan> )')
    out.append('</text>\n</svg>\n')

    # sanity check: card must fit
    if y > CARD_H - 10:
        raise SystemExit(f"Too many rows ({y}px > {CARD_H}px). Remove a line from PROFILE/CONTACT.")
    for item in PROFILE + CONTACT:
        if item and item[1] != "__AGE__" and len(item[0]) + len(item[1]) > WIDTH - 7:
            print(f"WARNING: '{item[0]}: {item[1]}' is too long and will overflow — shorten it.")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    for name, colors in THEMES.items():
        build(name, colors)
        print("wrote", name)
    print("Now run today.py (or push to GitHub) to fill in live stats.")
