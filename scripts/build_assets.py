"""Generate the SVG panels used by the profile README.

Edit the data near the top of this file, then run:

    python3 scripts/build_assets.py                      # card, pipeline, progress
    python3 scripts/build_assets.py --icons <dir>        # also rebuild tool tiles

<dir> is the `icons/` folder of the simple-icons npm package (CC0), e.g. after
`npm pack simple-icons && tar xzf simple-icons-*.tgz` it is `package/icons`.
"""

from __future__ import annotations

import argparse
import re
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
SANS = "Arial, Helvetica, 'Segoe UI', sans-serif"
MONO = "Consolas, 'DejaVu Sans Mono', Menlo, 'Courier New', monospace"

# ---------------------------------------------------------------- content
NAME = "Saadat Ahmed"
TAGLINE = "AI and data builder · RAG, NLP, analytics"
CARD_ROWS = [
    ("FOCUS", "RAG, multi-agent systems, NLP"),
    ("BUILDING", "Cross-jurisdiction Shariah RAG"),
    ("SHIPPED", "ScanHalal, live ingredient scanner"),
    ("BEST MODEL", "BERT NER, ingredient F1 0.967"),
    ("TEAM BUILDS", "ShipSentry, VoxelSort"),
    ("DATA", "Python, SQL, Power BI dashboards"),
]
STATUS = ("Currently building", "Shariah RAG · Phase 1")

# (label, done fraction or None, status text, colour)
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


def text(x: float, y: float, s: str, size: int, fill: str, *, weight: str = "", anchor: str = "",
         spacing: str = "", font: str = SANS) -> str:
    attrs = f'x="{x:g}" y="{y:g}" font-family="{font}" font-size="{size}" fill="{fill}"'
    if weight:
        attrs += f' font-weight="{weight}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    return f"<text {attrs}>{escape(s)}</text>"


def frame(w: int, h: int, label: str, style: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label, {chr(34): "&quot;"})}"><style>{style}</style>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{BG}"/>{body}'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="none" '
        f'stroke="{BORDER}" stroke-width="1.5"/></svg>'
    )


FADE = (
    ".t{opacity:0;animation:in .5s ease-out forwards}@keyframes in{to{opacity:1}}"
    ".dot{animation:pl 2s ease-in-out infinite}@keyframes pl{50%{opacity:.35}}"
)


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
    style = FADE + "@media (prefers-reduced-motion:reduce){.t{animation:none;opacity:1}.dot{animation:none}}"
    return frame(640, 620, label, style, "".join(body))


def box(x: float, y: float, w: float, h: float, title: str, sub: str = "", *,
        accent: str = BORDER, fill: str = PANEL, title_fill: str = TEXT) -> str:
    out = f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="10" fill="{fill}" stroke="{accent}" stroke-width="1.2"/>'
    cx = x + w / 2
    if sub:
        out += text(cx, y + h / 2 - 3, title, 16, title_fill, weight="700", anchor="middle")
        out += text(cx, y + h / 2 + 16, sub, 12.5, MUTED, anchor="middle")
    else:
        out += text(cx, y + h / 2 + 5.5, title, 16, title_fill, weight="700", anchor="middle")
    return out


def pipeline() -> str:
    flow = f'class="fl" stroke="{GOLD}" stroke-width="2" fill="none"'
    body = [
        text(40, 62, "HOW MY RAG ANSWERS", 13, MUTED, weight="700", spacing="1.4"),
        text(40, 94, "Shariah Compliance RAG", 26, TEXT, weight="700"),
        box(80, 124, 480, 46, "Question or term sheet", accent=BORDER),
        box(80, 196, 480, 58, "Input security gate", "PII redaction · injection firewall · BiDi strip", accent="#6B5317"),
        box(80, 280, 480, 46, "Router agent", accent=BORDER),
    ]
    for i, name in enumerate(("Extractor", "Checker", "Verifier")):
        body.append(box(80 + 166 * i, 352, 148, 46, name, accent=BORDER))
    body.append(f'<rect x="80" y="424" width="480" height="74" rx="10" fill="{PANEL}" stroke="#6B5317" stroke-width="1.2"/>')
    body.append(text(320, 450, "Stratified retrieval", 16, TEXT, weight="700", anchor="middle"))
    for i, auth in enumerate(("BNM", "SAC", "AAOIFI")):
        x = 170 + 110 * i
        body.append(f'<rect x="{x}" y="466" width="90" height="22" rx="11" fill="{BG}" stroke="{BORDER}"/>')
        body.append(text(x + 45, 481.5, auth, 12.5, GOLD, weight="700", anchor="middle"))
    body.append(box(80, 524, 232, 46, "Cited answer", accent=GOLD, fill="#2A2310", title_fill=GOLD))
    body.append(box(328, 524, 232, 46, "Escalate to committee", accent=TEAL, fill="#0E2A28", title_fill=TEAL))
    # connectors with marching dashes
    for y1, y2 in ((170, 196), (254, 280), (398, 424)):
        body.append(f'<path {flow} d="M320 {y1}V{y2}"/>')
    body.append(f'<path {flow} d="M320 326V339H154V352M320 339V352M320 339H486V352"/>')
    body.append(f'<path {flow} d="M320 498V511H196V524M320 511H444V524"/>')
    body.append(text(320, 600, "Every claim cites a retrieved clause, or the system abstains.", 13.5, MUTED, anchor="middle"))
    label = ("Pipeline of the Shariah Compliance RAG: question or term sheet, input security gate, router agent, "
             "extractor, checker and verifier agents, stratified retrieval over BNM, SAC and AAOIFI, then a cited "
             "answer or escalation to a Shariah committee.")
    style = (
        ".fl{stroke-dasharray:4 5;animation:m 1.1s linear infinite}@keyframes m{to{stroke-dashoffset:-18}}"
        "@media (prefers-reduced-motion:reduce){.fl{animation:none}}"
    )
    return frame(640, 620, label, style, "".join(body))


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
        # chips stay static so the text never jumps
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
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "card.svg").write_text(card(), encoding="utf-8")
    (ASSETS / "pipeline.svg").write_text(pipeline(), encoding="utf-8")
    (ASSETS / "progress.svg").write_text(progress(), encoding="utf-8")
    if args.icons:
        tiles(args.icons)


if __name__ == "__main__":
    main()
