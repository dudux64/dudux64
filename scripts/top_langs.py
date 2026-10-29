"""Gera assets/top-langs.svg com as linguagens mais usadas nos repositórios públicos."""
import json
import os
import urllib.request

USER = "dudux64"
COUNT = 6
IGNORE = {"Makefile", "Dockerfile", "Shell", "Batchfile", "PowerShell"}
COLORS = {
    "HTML": "#e34c26", "CSS": "#663399", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Python": "#3572A5", "C": "#555555", "C#": "#178600", "C++": "#f34b7d",
    "Java": "#b07219", "PHP": "#4F5D95", "SQL": "#e38c00", "TSQL": "#e38c00",
}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


totals = {}
for repo in get(f"https://api.github.com/users/{USER}/repos?per_page=100"):
    if repo["fork"]:
        continue
    for lang, size in get(repo["languages_url"]).items():
        if lang not in IGNORE:
            totals[lang] = totals.get(lang, 0) + size

top = sorted(totals.items(), key=lambda t: -t[1])[:COUNT]
total = sum(size for _, size in top)

W, PAD = 490, 25
bar_w = W - 2 * PAD
rows = (len(top) + 1) // 2
H = 92 + rows * 28

bar, x = [], PAD
for i, (lang, size) in enumerate(top):
    w = bar_w - (x - PAD) if i == len(top) - 1 else round(bar_w * size / total)
    bar.append(f'<rect x="{x}" y="58" width="{w}" height="8" fill="{COLORS.get(lang, "#8b949e")}"/>')
    x += w

items = []
for i, (lang, size) in enumerate(top):
    cx = PAD + (i % 2) * (bar_w // 2)
    cy = 94 + (i // 2) * 28
    items.append(
        f'<circle cx="{cx + 5}" cy="{cy - 5}" r="5" fill="{COLORS.get(lang, "#8b949e")}"/>'
        f'<text x="{cx + 18}" y="{cy}" class="lang">{lang} <tspan class="pct">{100 * size / total:.1f}%</tspan></text>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    text {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; }}
    .bg {{ fill: #ffffff; stroke: #d0d7de; }}
    .title {{ fill: #2563eb; font-size: 18px; font-weight: 700; }}
    .lang {{ fill: #1f2328; font-size: 14px; }}
    .pct {{ fill: #59636e; }}
    @media (prefers-color-scheme: dark) {{
      .bg {{ fill: #151b23; stroke: #3d444d; }}
      .title {{ fill: #60a5fa; }}
      .lang {{ fill: #f0f6fc; }}
      .pct {{ fill: #9198a1; }}
    }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" class="bg"/>
  <text x="{PAD}" y="38" class="title">Linguagens mais usadas</text>
  <clipPath id="r"><rect x="{PAD}" y="58" width="{bar_w}" height="8" rx="4"/></clipPath>
  <g clip-path="url(#r)">{"".join(bar)}</g>
  {"".join(items)}
</svg>
'''

os.makedirs("assets", exist_ok=True)
with open("assets/top-langs.svg", "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(top)
