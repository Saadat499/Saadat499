"""Generate the SVG panels used by the profile README.

Edit the data near the top of this file, then run:

    python3 scripts/build_assets.py                      # all panels
    python3 scripts/build_assets.py --icons <dir>        # also rebuild tool tiles

<dir> is the `icons/` folder of the simple-icons npm package (CC0), e.g. after
`npm pack simple-icons && tar xzf simple-icons-*.tgz` it is `package/icons`.
"""

from __future__ import annotations

import argparse
import re
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ---------------------------------------------------------------- palette
BG = "#0D1117"
PANEL = "#161B22"
BORDER = "#30363D"
TEXT = "#E6EDF3"
SOFT = "#C9D1D9"
MUTED = "#7D8590"
GOLD = "#F2C14E"
TEAL = "#3DD6C6"
BLUE = "#58A6FF"
ROSE = "#F778BA"
SANS = "Arial, Helvetica, 'Segoe UI', sans-serif"
MONO = "Consolas, 'DejaVu Sans Mono', Menlo, 'Courier New', monospace"

# ---------------------------------------------------------------- profile card
NAME = "Saadat Ahmed"
TAGLINE = "AI and data builder · NLP, document AI, analytics"
CARD_ROWS = [
    ("FOCUS", "AI, NLP and data analytics"),
    ("SHIPPED", "ScanHalal, ShipSentry (both live)"),
    ("HACKATHONS", "Averis x Monash, Dormathon 2026"),
    ("BEST MODEL", "BERT NER, ingredient F1 0.967"),
    ("DATA", "Python, SQL, Power BI dashboards"),
    ("BUILDING", "Shariah compliance RAG"),
]
STATUS = ("Currently building", "Shariah RAG · Phase 1")

# ---------------------------------------------------------------- terminal: project map
# (group heading, [(folder, description, tag or "")])
TERMINAL = [
    ("AI · NLP", [
        ("scanhalal/", "OCR + BERT NER halal checker", "live"),
        ("voxelsort/", "chest X-ray worklist triage", "team"),
        ("shariah-rag/", "cited RAG: BNM, SAC, AAOIFI", "wip"),
    ]),
    ("DOCUMENT AUTOMATION", [
        ("shipsentry/", "SI vs BL mismatch checker", "live"),
    ]),
    ("DATA ANALYTICS", [
        ("food-prices/", "festive price moves, MY", ""),
        ("shopping-bi/", "SQL + Power BI retail study", ""),
    ]),
    ("FOUNDATIONS", [
        ("java-oop/", "student mgmt, password check", ""),
    ]),
]
TAG_COLOURS = {"live": TEAL, "team": BLUE, "wip": GOLD}

# ---------------------------------------------------------------- by the numbers
# (number, what it measures, project, colour)
STATS = [
    ("0.967", "ingredient F1, BERT NER", "ScanHalal", TEAL),
    ("181,970", "sentences fine-tuned on", "ScanHalal", TEAL),
    ("1,560", "emails scored, 3 test sets", "ShipSentry", BLUE),
    ("20 / 520", "emails left for a human", "ShipSentry", BLUE),
    ("0.811", "AUROC, any urgent finding", "VoxelSort (team)", ROSE),
    ("957", "price combinations tested", "Malaysia Food Prices", GOLD),
    ("10", "business questions in SQL", "Customer Behavior", GOLD),
    ("3", "languages: AR, EN, MS", "Shariah RAG", TEXT),
]

# ---------------------------------------------------------------- project cards
PROJECTS = [
    {
        "file": "scanhalal", "title": "ScanHalal", "domain": "AI · NLP", "status": "LIVE", "colour": TEAL,
        "desc": "Point a camera at an ingredient label and get a halal, haram or syubhah verdict per "
                "ingredient, with the evidence behind it. Unknown inputs default to needs review.",
        "metric": ("0.967", "ingredient F1, vs 0.954 BiLSTM-CRF"),
        "stack": ["PyTorch", "Transformers", "Tesseract", "Streamlit"],
    },
    {
        "file": "shipsentry", "title": "ShipSentry", "domain": "DOCUMENT AI", "status": "LIVE · TEAM OF 5",
        "colour": BLUE,
        "desc": "Checks that a Shipping Instruction and a draft Bill of Lading describe the same shipment. "
                "I coordinated the team and worked on verification and comparison.",
        "metric": ("100%", "on 3 test sets, 1,560 emails"),
        "stack": ["Python", "pdfplumber", "Gemini", "Firebase"],
    },
    {
        "file": "voxelsort", "title": "VoxelSort", "domain": "HEALTH AI", "status": "TEAM · DORMATHON 2026",
        "colour": ROSE,
        "desc": "Chest X-ray worklist prioritiser that moves urgent scans up the queue. Decision support "
                "only: a clinician reads every scan.",
        "metric": ("4.7 min", "simulated urgent wait, from 11.2"),
        "stack": ["FastAPI", "DenseNet121", "ONNX", "React"],
    },
    {
        "file": "shariah-rag", "title": "Shariah Compliance RAG", "domain": "ISLAMIC FINANCE AI",
        "status": "IN PROGRESS", "colour": GOLD,
        "desc": "Answers compliance questions from BNM, SAC and AAOIFI with clause-level citations, and "
                "shows where authorities disagree instead of blending them.",
        "metric": ("Phase 1", "of 5, security baseline done"),
        "stack": ["Python", "Pydantic", "pdfplumber", "uv"],
    },
    {
        "file": "food-prices", "title": "Malaysia Food Prices", "domain": "DATA ANALYTICS", "status": "OPEN DATA",
        "colour": GOLD,
        "desc": "How staple food prices move around Chinese New Year, Raya and Deepavali, by state and "
                "premise type, using PriceCatcher open data.",
        "metric": ("957", "state and premise combinations"),
        "stack": ["Python", "SQL", "DuckDB", "Power BI"],
    },
    {
        "file": "customer-behavior", "title": "Customer Behavior", "domain": "DATA ANALYTICS",
        "status": "END TO END", "colour": GOLD,
        "desc": "Retail analytics from raw CSV to dashboard: cleaned in pandas, explored in PostgreSQL, "
                "presented in an interactive Power BI report.",
        "metric": ("10", "business questions answered in SQL"),
        "stack": ["pandas", "PostgreSQL", "SQLAlchemy", "Power BI"],
    },
]

# ---------------------------------------------------------------- journey
JOURNEY = [
    ("NOV 2024", "Joined GitHub", "bio: \"just a newbie\""),
    ("APR 2025", "Java OOP", "student mgmt, password check"),
    ("AUG 2026", "ScanHalal", "OCR + NER, now live"),
    ("SEP 2026", "ShipSentry", "Averis x Monash hackathon"),
    ("OCT 2026", "Data analytics", "retail BI, food prices"),
    ("OCT 2026", "VoxelSort", "Dormathon 2026 team build"),
    ("NOW", "Shariah RAG", "building in phases"),
]

# ---------------------------------------------------------------- Shariah RAG progress
PHASES = [
    ("Phase 0 · Security baseline", 1.0, "Done", GOLD),
    ("Phase 1 · Ingestion, clauses", 7 / 9, "7 of 9 tasks", TEAL),
    ("Phase 2 · Eval, red-team", None, "Up next", MUTED),
    ("Phase 3 · Hybrid retrieval", None, "Planned", MUTED),
    ("Phase 4 · Guarded Q&A", None, "Planned", MUTED),
    ("Phase 5 · Contract review", None, "Planned", MUTED),
]
CAPABILITIES = [
    "Clause-level citations",
    "Conflict surfacing",
    "Point-in-time rules",
    "Arabic · English · Malay",
    "Red-team evaluation",
    "Signed corpus",
]

# ---------------------------------------------------------------- tool tiles
# (file stem, label, simple-icons slug or None for a drawn glyph, colour)
TILES = [
    ("pytorch", "PyTorch", "pytorch", "#EE4C2C"),
    ("huggingface", "Hugging Face", "huggingface", "#FFD21E"),
    ("scikit-learn", "scikit-learn", "scikitlearn", "#F7931E"),
    ("tesseract", "Tesseract", None, "#5FB3F9"),
    ("rag", "RAG", None, GOLD),
    ("streamlit", "Streamlit", "streamlit", "#FF4B4B"),
    ("claude", "Claude", "claude", "#D97757"),
    ("pandas", "pandas", "pandas", "#B39DDB"),
    ("numpy", "NumPy", "numpy", "#4DABCF"),
    ("jupyter", "Jupyter", "jupyter", "#F37626"),
    ("postgresql", "PostgreSQL", "postgresql", "#6C9EEB"),
    ("duckdb", "DuckDB", "duckdb", "#FFF000"),
    ("sqlalchemy", "SQLAlchemy", "sqlalchemy", "#E85B4A"),
    ("sql", "SQL", None, "#4FA3D8"),
    ("power-bi", "Power BI", None, "#F2C811"),
    ("pydantic", "Pydantic", "pydantic", "#E92063"),
    ("pytest", "pytest", "pytest", "#0A9EDC"),
    ("ruff", "Ruff", "ruff", "#D7FF64"),
    ("uv", "uv", "uv", "#DE5FE9"),
    ("pre-commit", "pre-commit", "precommit", "#FAB040"),
    ("secret-scan", "gitleaks", None, TEAL),
    ("github-actions", "Actions", "githubactions", "#2088FF"),
    ("python", "Python", "python", "#4B8BBE"),
    ("java", "Java", "openjdk", "#E76F00"),
    ("fastapi", "FastAPI", "fastapi", "#05A08F"),
    ("git", "Git", "git", "#F05032"),
    ("github", "GitHub", "github", "#E6EDF3"),
]

# Stroke glyphs on a 24x24 grid for tools without a simple-icons logo.
GLYPHS = {
    "tesseract": '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M8 9h8M8 12h8M8 15h5"/>',
    "rag": '<path d="M6 3h8l4 4v6"/><path d="M14 3v4h4"/><path d="M6 3v18h6"/><circle cx="17" cy="17" r="3"/><path d="M19.2 19.2 22 22"/>',
    "sql": '<ellipse cx="12" cy="5.5" rx="7" ry="2.5"/><path d="M5 5.5v13c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-13"/><path d="M5 12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5"/>',
    "power-bi": '<path d="M5 20V13M10 20V9M15 20V5M20 20V11"/><path d="M3 20.5h18"/>',
    "secret-scan": '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>',
}


def text(x: float, y: float, s: str, size: float, fill: str, *, weight: str = "", anchor: str = "",
         spacing: str = "", font: str = SANS, cls: str = "", style: str = "") -> str:
    attrs = f'x="{x:g}" y="{y:g}" font-family="{font}" font-size="{size:g}" fill="{fill}"'
    if weight:
        attrs += f' font-weight="{weight}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    if cls:
        attrs += f' class="{cls}"'
    if style:
        attrs += f' style="{style}"'
    return f"<text {attrs}>{escape(s)}</text>"


def frame(w: int, h: int, label: str, style: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label, {chr(34): "&quot;"})}"><style>{style}</style>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{BG}"/>{body}'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="none" '
        f'stroke="{BORDER}" stroke-width="1.5"/></svg>'
    )


def pill(x: float, y: float, label: str, colour: str, *, size: float = 11.5, bold: bool = True,
         anchor_end: bool = False) -> tuple[str, float]:
    """A rounded label; returns (svg, width). Width is estimated from the character count."""
    w = len(label) * size * (0.68 if bold else 0.6) + 20
    if anchor_end:
        x -= w
    svg = (f'<rect x="{x:g}" y="{y:g}" width="{w:.0f}" height="{size + 11:g}" rx="{(size + 11) / 2:g}" '
           f'fill="{PANEL}" stroke="{colour if bold else BORDER}" stroke-opacity="{.6 if bold else 1}"/>'
           + text(x + w / 2, y + size + 4.5, label, size, colour, weight="700" if bold else "",
                  anchor="middle", spacing=".6" if bold else ""))
    return svg, w


FADE = ".t{opacity:0;animation:in .5s ease-out forwards}@keyframes in{to{opacity:1}}"
PULSE = ".dot{animation:pl 2s ease-in-out infinite}@keyframes pl{50%{opacity:.35}}"
CALM = "@media (prefers-reduced-motion:reduce){.t{animation:none;opacity:1}.dot,.cur{animation:none}}"


def card() -> str:
    body = [
        text(40, 74, NAME, 34, TEXT, weight="700"),
        text(40, 106, TAGLINE, 18, MUTED),
        f'<rect x="40" y="128" width="560" height="1" fill="{BORDER}"/>',
    ]
    for i, (label, value) in enumerate(CARD_ROWS):
        y = 178 + 50 * i
        body.append(
            f'<g class="t" style="animation-delay:{0.2 + 0.15 * i:.2f}s">'
            + text(40, y, label, 13, MUTED, weight="700", spacing="1.4")
            + text(184, y, value, 20, TEXT)
            + "</g>"
        )
    lead, detail = STATUS
    body.append(
        f'<g class="t" style="animation-delay:{0.2 + 0.15 * len(CARD_ROWS):.2f}s">'
        f'<rect x="40" y="484" width="560" height="64" rx="10" fill="#2A2310" stroke="#6B5317"/>'
        f'<circle class="dot" cx="66" cy="516" r="6" fill="{GOLD}"/>'
        + text(84, 522, lead, 18, GOLD, weight="700")
        + text(580, 522, detail, 16, SOFT, anchor="end")
        + "</g>"
    )
    label = f"{NAME}, {TAGLINE}. " + ". ".join(f"{k.title()}: {v}" for k, v in CARD_ROWS)
    return frame(640, 620, label, FADE + PULSE + CALM, "".join(body))


def terminal() -> str:
    body = [
        f'<path d="M1 13a12 12 0 0 1 12-12h614a12 12 0 0 1 12 12v31H1z" fill="{PANEL}"/>',
        f'<rect x="1" y="44" width="638" height="1" fill="{BORDER}"/>',
        '<circle cx="28" cy="23" r="6.5" fill="#FF5F57"/><circle cx="50" cy="23" r="6.5" fill="#FEBC2E"/>'
        '<circle cx="72" cy="23" r="6.5" fill="#28C840"/>',
        text(320, 28, "saadat@dev: ~/projects", 14, MUTED, anchor="middle", font=MONO),
        text(36, 88, "saadat@dev:~$", 16, GOLD, weight="700", font=MONO)
        + text(176, 88, "ls projects --by-domain", 16, TEXT, font=MONO),
    ]
    y, step = 130, 0
    for heading, rows in TERMINAL:
        body.append(f'<g class="t" style="animation-delay:{0.25 + 0.12 * step:.2f}s">'
                    + text(36, y, heading, 13, MUTED, weight="700", spacing="1.4", font=MONO) + "</g>")
        y += 35
        step += 1
        for folder, desc, tag in rows:
            g = text(56, y, folder, 15.5, BLUE, weight="700", font=MONO) + text(198, y, desc, 15.5, SOFT, font=MONO)
            if tag:
                svg, _ = pill(604, y - 16, tag, TAG_COLOURS[tag], size=11.5, anchor_end=True)
                g += svg
            body.append(f'<g class="t" style="animation-delay:{0.25 + 0.12 * step:.2f}s">{g}</g>')
            y += 35
            step += 1
        y += 12
    body.append(
        f'<g class="t" style="animation-delay:{0.25 + 0.12 * step:.2f}s">'
        + text(36, y + 6, "saadat@dev:~$", 16, GOLD, weight="700", font=MONO)
        + f'<rect class="cur" x="176" y="{y - 9:g}" width="10" height="19" fill="{GOLD}"/></g>'
    )
    label = "Terminal listing of Saadat's projects by domain. " + "; ".join(
        f"{h}: " + ", ".join(f"{f.rstrip('/')} ({d})" for f, d, _ in rows) for h, rows in TERMINAL)
    style = FADE + ".cur{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}" + CALM
    return frame(640, 620, label, style, "".join(body))


def stats() -> str:
    w, h = 1000, 300
    body = []
    for i, (num, what, proj, colour) in enumerate(STATS):
        col, row = i % 4, i // 4
        x, y = 24 + col * 241, 24 + row * 134
        body.append(
            f'<g class="t" style="animation-delay:{0.1 + 0.1 * i:.2f}s">'
            f'<rect x="{x}" y="{y}" width="227" height="118" rx="10" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<rect x="{x}" y="{y + 18}" width="3" height="82" rx="1.5" fill="{colour}"/>'
            + text(x + 22, y + 50, num, 32, colour, weight="700")
            + text(x + 22, y + 77, what, 14.5, TEXT)
            + text(x + 22, y + 99, proj, 12.5, MUTED, weight="700", spacing=".4")
            + "</g>"
        )
    label = "By the numbers. " + "; ".join(f"{n} {wt} ({p})" for n, wt, p, _ in STATS)
    return frame(w, h, label, FADE + CALM, "".join(body))


def project_card(p: dict) -> str:
    w, h, colour = 480, 290, p["colour"]
    body = [f'<rect x="14" y="1" width="{w - 28}" height="3" rx="1.5" fill="{colour}" fill-opacity=".9"/>']
    svg, pw = pill(28, 26, p["domain"], colour)
    body.append(svg)
    body.append(pill(28 + pw + 8, 26, p["status"], MUTED, bold=False, size=11)[0])
    body.append(text(28, 92, p["title"], 25, TEXT, weight="700"))
    lines = textwrap.wrap(p["desc"], 60)
    if len(lines) > 3:
        raise SystemExit(f'{p["title"]}: description needs {len(lines)} lines, the card fits 3')
    for i, line in enumerate(lines):
        body.append(text(28, 124 + 22 * i, line, 14.5, SOFT))
    num, what = p["metric"]
    body.append(f'<rect x="28" y="196" width="{w - 56}" height="1" fill="{BORDER}"/>')
    body.append(text(28, 232, num, 24, colour, weight="700"))
    body.append(text(28 + len(num) * 14 + 12, 231, what, 14, MUTED))
    x = 28.0
    for s in p["stack"]:
        svg, sw = pill(x, 248, s, SOFT, size=11.5, bold=False)
        body.append(svg)
        x += sw + 8
    label = f'{p["title"]}. {p["domain"].title()}, {p["status"].lower()}. {p["desc"]} {num} {what}.'
    return frame(w, h, label, "", "".join(body))


def journey() -> str:
    w, h = 1000, 250
    xs = [110 + 130 * i for i in range(len(JOURNEY))]
    body = [f'<rect class="line" x="{xs[0]}" y="124" width="{xs[-1] - xs[0]}" height="2" fill="{BORDER}"/>',
            f'<rect class="line" x="{xs[0]}" y="124" width="{xs[-1] - xs[0]}" height="2" fill="url(#gl)"/>']
    for i, ((when, what, sub), x) in enumerate(zip(JOURNEY, xs)):
        last = i == len(JOURNEY) - 1
        colour = GOLD if last else TEAL
        top = i % 2 == 0
        dy = (60, 82, 102) if top else (172, 194, 214)
        node = f'<circle cx="{x}" cy="125" r="7" fill="{BG}" stroke="{colour}" stroke-width="2.5"/>'
        if last:
            node += f'<circle class="dot" cx="{x}" cy="125" r="3.5" fill="{GOLD}"/>'
        stem = f'<rect x="{x - .5}" y="{106 if top else 133}" width="1" height="11" fill="{BORDER}"/>'
        body.append(
            f'<g class="t" style="animation-delay:{0.2 + 0.15 * i:.2f}s">{stem}{node}'
            + text(x, dy[0], when, 12.5, colour, weight="700", anchor="middle", spacing="1", font=MONO)
            + text(x, dy[1], what, 16, TEXT, weight="700", anchor="middle")
            + text(x, dy[2], sub, 12.5, MUTED, anchor="middle")
            + "</g>"
        )
    defs = (f'<defs><linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity=".2"/>'
            f'<stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>')
    style = (FADE + PULSE + ".line{transform-box:fill-box;transform-origin:left;animation:g 1.6s ease-out both}"
             "@keyframes g{from{transform:scaleX(0)}}" + CALM.replace(".t{", ".line{animation:none}.t{"))
    label = "Journey: " + "; ".join(f"{a}, {b} ({c})" for a, b, c in JOURNEY)
    return frame(w, h, label, style, defs + "".join(body))


def progress() -> str:
    w, h = 1000, 330
    bar_x, bar_w = 286, 340
    body = []
    for i, (label, frac, status, colour) in enumerate(PHASES):
        y = 46 + 40 * i
        body.append(text(40, y + 15, label, 16.5, TEXT))
        body.append(f'<rect x="{bar_x}" y="{y}" width="{bar_w}" height="20" rx="10" fill="{PANEL}" stroke="{BORDER}"/>')
        if frac:
            body.append(
                f'<rect class="bar" style="animation-delay:{0.15 * i:.2f}s" x="{bar_x}" y="{y}" '
                f'width="{max(20, bar_w * frac):.0f}" height="20" rx="10" fill="{colour}" fill-opacity=".85"/>'
            )
        body.append(text(bar_x + bar_w + 18, y + 15, status, 15, colour, weight="700"))
    body.append(text(790, 44, "CAPABILITIES", 12, MUTED, weight="700", spacing="1.3"))
    for i, cap in enumerate(CAPABILITIES):
        y = 58 + 34 * i
        body.append(f'<rect x="790" y="{y}" width="176" height="24" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')
        body.append(text(878, y + 16.5, cap, 13, SOFT, anchor="middle"))
    body.append(text(40, 300, "Phase 6 (cloud deployment) stays locked until the whole system passes localhost testing.", 14, MUTED))
    label = "Shariah Compliance RAG build progress. " + ". ".join(f"{p[0]}: {p[2]}" for p in PHASES) + "."
    style = (
        ".bar{transform-box:fill-box;transform-origin:left;animation:g 1.4s cubic-bezier(.2,.8,.2,1) both}"
        "@keyframes g{from{transform:scaleX(0)}}@media (prefers-reduced-motion:reduce){.bar{animation:none}}"
    )
    return frame(w, h, label, style, "".join(body))


def tile(label: str, inner: str) -> str:
    size = "10.5" if len(label) <= 9 else "9.5"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 72 72" role="img" '
        f'aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f'<rect x=".75" y=".75" width="70.5" height="70.5" rx="12" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>'
        f'<g transform="translate(22 12) scale(1.17)">{inner}</g>'
        f'<text x="36" y="61" text-anchor="middle" font-family="{SANS}" font-size="{size}" fill="#9DA7B3">{escape(label)}</text></svg>'
    )


def tiles(icons: Path) -> None:
    out = ASSETS / "tools"
    out.mkdir(parents=True, exist_ok=True)
    for stem, label, slug, colour in TILES:
        if slug:
            src = (icons / f"{slug}.svg").read_text(encoding="utf-8")
            d = re.search(r'<path d="([^"]+)"', src).group(1)  # type: ignore[union-attr]
            inner = f'<path fill="{colour}" d="{d}"/>'
        else:
            inner = (f'<g fill="none" stroke="{colour}" stroke-width="1.7" stroke-linecap="round" '
                     f'stroke-linejoin="round">{GLYPHS[stem]}</g>')
        (out / f"{stem}.svg").write_text(tile(label, inner), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--icons", type=Path, help="simple-icons icons/ directory; rebuilds tool tiles")
    args = parser.parse_args()
    (ASSETS / "projects").mkdir(parents=True, exist_ok=True)
    panels = {"card": card(), "terminal": terminal(), "stats": stats(), "journey": journey(), "progress": progress()}
    for name, svg in panels.items():
        (ASSETS / f"{name}.svg").write_text(svg, encoding="utf-8")
    for p in PROJECTS:
        (ASSETS / "projects" / f'{p["file"]}.svg').write_text(project_card(p), encoding="utf-8")
    if args.icons:
        tiles(args.icons)


if __name__ == "__main__":
    main()
