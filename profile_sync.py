"""
Reads my public GitHub repos and turns them into live card content (cache/profile.json)
plus an auto-written README block. Runs daily in the Action, before build_svg.py.

What it derives
  keywords   research keywords + repo topics, ranked by how recent and how frequent they are
  areas      the four research-signal bars, scored from the keywords
  languages  top languages by bytes of code
  recent     the most recently pushed repos ("currently" + README "fresh from the lab")

To steer it: add GitHub topics to your repos (Settings → About → Topics) or extend VOCAB below.

Usage:   ACCESS_TOKEN=... python profile_sync.py
         python profile_sync.py --fixture some.json      (offline test with saved GraphQL nodes)
"""
import datetime
import json
import math
import os
import re
import sys

USER = os.environ.get("USER_NAME", "bibek-cse")
SKIP_REPOS = {USER}                      # the profile repo itself
HALF_LIFE_DAYS = 120                     # a repo pushed 4 months ago counts half as much
README = "README.md"
START, END = "<!-- LAB:START -->", "<!-- LAB:END -->"

# canonical keyword -> pattern matched against repo name + description + topics
VOCAB = {
    "watermarking":          r"watermark",
    "provenance":            r"provenance|attribution|c2pa|content credential",
    "steganography":         r"stegan",
    "deepfake detection":    r"deep.?fake|face.?swap|faceforensic|dfdc",
    "forgery localization":  r"forg|tamper|splic|copy.?move|manipulat|trufor|casia",
    "media forensics":       r"forensic",
    "adversarial attacks":   r"adversar|attack|robustness|perturb",
    "data poisoning":        r"poison|nightshade|glaze|photoguard",
    "vision-language":       r"\bvlm|vision.?language|llava|qwen.?vl|\bclip\b|multimodal",
    "LLMs":                  r"\bllm|large language|gpt|gemma|llama",
    "diffusion models":      r"diffusion|sdxl|\bflux\b|stable.?diffusion|image.?edit",
    "crowd counting":        r"crowd",
    "audio deepfakes":       r"speech|audio|voice|asvspoof",
    "biometrics":            r"biometric|face recog|re-?id|signature",
    "explainability":        r"explain|grad.?cam|prototype|interpretab",
    "teaching":              r"\bgate\b|quiz|\blab\b|course|lecture|tutorial|dsa",
    "web apps":              r"github.?pages|web.?app|\bsite\b|front.?end|html",
    "computer vision":       r"vision|opencv|image|video",
}

NON_RESEARCH = {"teaching", "web apps"}

# research-signal bars: which keywords feed which bar
AREAS = {
    "watermarking & provenance": ["watermarking", "provenance", "steganography", "adversarial attacks"],
    "deepfake detection":        ["deepfake detection", "audio deepfakes", "biometrics"],
    "forgery localization":      ["forgery localization", "media forensics", "explainability"],
    "vision-language models":    ["vision-language", "LLMs", "diffusion models", "crowd counting"],
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name description url homepageUrl pushedAt stargazerCount isArchived
        primaryLanguage { name }
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
        repositoryTopics(first: 20) { nodes { topic { name } } }
      }
    }
  }
}"""


def fetch_repos():
    import requests
    token = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    r = requests.post("https://api.github.com/graphql", json={"query": QUERY, "variables": {"login": USER}},
                      headers={"Authorization": f"bearer {token}"}, timeout=60)
    r.raise_for_status()
    return r.json()["data"]["user"]["repositories"]["nodes"]


def age_days(iso, now):
    return max(0.0, (now - datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds() / 86400)


def ago(days):
    if days < 1:
        return "today"
    if days < 30:
        return f"{int(days)}d ago"
    if days < 365:
        return f"{int(days // 30)}mo ago"
    return f"{int(days // 365)}y ago"


def analyse(repos, previous=None, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    repos = [r for r in repos if r["name"] not in SKIP_REPOS and not r.get("isArchived")]
    kw_score, kw_repos, langs = {}, {}, {}

    for r in repos:
        topics = [t["topic"]["name"] for t in (r.get("repositoryTopics") or {}).get("nodes", [])]
        text = " ".join([r["name"].replace("_", " ").replace("-", " "), r.get("description") or "", " ".join(topics)]).lower()
        weight = 0.5 ** (age_days(r["pushedAt"], now) / HALF_LIFE_DAYS) + 0.3 * math.log1p(r.get("stargazerCount", 0))

        hits = {k for k, pat in VOCAB.items() if re.search(pat, text)}
        if "teaching" in hits:              # a quiz about LLMs isn't LLM research
            hits &= NON_RESEARCH
        # repo topics that the vocabulary doesn't already cover become keywords of their own
        for t in topics:
            label = t.replace("-", " ")
            if not any(re.search(pat, label) for pat in VOCAB.values()):
                hits.add(label)
        for k in hits:
            kw_score[k] = kw_score.get(k, 0) + weight
            kw_repos[k] = kw_repos.get(k, 0) + 1

        for e in (r.get("languages") or {}).get("edges", []):
            n = e["node"]["name"]
            if n not in ("Jupyter Notebook",):          # notebooks inflate byte counts
                langs[n] = langs.get(n, 0) + e["size"]
        if r.get("primaryLanguage") and r["primaryLanguage"]["name"] == "Jupyter Notebook":
            langs.setdefault("Jupyter", 0)

    prev_kw = {k["k"] for k in (previous or {}).get("keywords", [])}
    ranked = sorted(kw_score.items(), key=lambda kv: (-kv[1], kv[0]))
    # "computer vision" matches nearly everything; keep it out of the top spots
    ranked = [kv for kv in ranked if kv[0] != "computer vision"] + [kv for kv in ranked if kv[0] == "computer vision"]
    keywords = [{"k": k, "score": round(s, 3), "repos": kw_repos[k], "new": bool(prev_kw) and k not in prev_kw}
                for k, s in ranked[:14]]

    areas = {a: round(sum(kw_score.get(k, 0) for k in ks), 3) for a, ks in AREAS.items()}

    recent = []
    for r in repos[:6]:
        recent.append({"name": r["name"], "description": (r.get("description") or "").strip(),
                       "url": r.get("homepageUrl") or r["url"], "repo_url": r["url"],
                       "lang": (r.get("primaryLanguage") or {}).get("name", ""),
                       "pushed": r["pushedAt"][:10], "ago": ago(age_days(r["pushedAt"], now))})

    return {"synced": now.date().isoformat(), "repo_count": len(repos), "keywords": keywords,
            "areas": areas, "languages": sorted(langs.items(), key=lambda kv: -kv[1])[:6], "recent": recent}


def readme_block(p):
    kws = " ".join(f"`{k['k']}`" + (" 🆕" if k["new"] else "") for k in p["keywords"][:12])
    rows = "\n".join(
        f"| [**{r['name']}**]({r['repo_url']}) | {r['description'] or '—'} | {r['lang'] or '—'} | {r['ago']} |"
        for r in p["recent"][:5])
    return (f"{START}\n### 🧪 Fresh from the lab\n\n"
            f"<sub>Auto-generated from my repos on {p['synced']}, so this section changes as I push.</sub>\n\n"
            f"**Trending in my work:** {kws}\n\n"
            f"| Repo | What it is | Lang | Updated |\n|---|---|---|---|\n{rows}\n{END}")


def update_readme(p):
    try:
        s = open(README, encoding="utf-8").read()
    except FileNotFoundError:
        return
    if START in s and END in s:
        s = s[:s.index(START)] + readme_block(p) + s[s.index(END) + len(END):]
        open(README, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    os.makedirs("cache", exist_ok=True)
    try:
        previous = json.load(open("cache/profile.json"))
    except (FileNotFoundError, json.JSONDecodeError):
        previous = None
    if "--fixture" in sys.argv:
        repos = json.load(open(sys.argv[sys.argv.index("--fixture") + 1]))
    else:
        repos = fetch_repos()
    profile = analyse(repos, previous)
    json.dump(profile, open("cache/profile.json", "w"), indent=1)
    update_readme(profile)
    print(f"synced {profile['repo_count']} repos")
    print("keywords:", ", ".join(k["k"] + ("*" if k["new"] else "") for k in profile["keywords"]))
    print("areas:", profile["areas"])
    print("languages:", profile["languages"])
