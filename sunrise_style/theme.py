"""Project-wide visual theme for Sunrise research artifacts.

The theme is intentionally small: shared color tokens, matplotlib defaults,
and Marp CSS that can be reused by notebooks, scripts, and generated decks.
It is based on the local `sunrise_sample_presentation.pdf`: image-led white
slides, large clean sans typography, warm Sunrise orange/red, cyan accents,
and light technical linework.

The current default aims for an insight-led narrative style: analytical enough
for technical review, but structured so decision makers can read the headline,
scan one visual, and land on the recommendation quickly.
"""

from __future__ import annotations

from textwrap import dedent
from typing import Mapping

CHART_DPI = 180
SANS_STACK = ["Avenir Next", "Source Sans 3", "Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"]

SUNRISE_COLORS: Mapping[str, str] = {
    "orange": "#FF5A1F",
    "orange_dark": "#D64116",
    "coral": "#E84E3C",
    "cyan": "#72C7E7",
    "blue": "#147FB8",
    "green": "#2FB344",
    "yellow": "#F4B740",
    "navy": "#0B1F2A",
    "charcoal": "#232A2F",
    "slate": "#52616B",
    "grid": "#D7DEE2",
    "muted": "#8A969E",
    "paper": "#F7F8F8",
    "white": "#FFFFFF",
}

SUNRISE_PALETTE = [
    SUNRISE_COLORS["orange"],
    SUNRISE_COLORS["cyan"],
    SUNRISE_COLORS["blue"],
    SUNRISE_COLORS["green"],
    SUNRISE_COLORS["coral"],
    SUNRISE_COLORS["yellow"],
    SUNRISE_COLORS["slate"],
]

GROUP_COLORS: Mapping[str, str] = {
    "control": SUNRISE_COLORS["blue"],
    "treatment": SUNRISE_COLORS["orange"],
    "standard": SUNRISE_COLORS["blue"],
    "cuped": SUNRISE_COLORS["green"],
    "sms": SUNRISE_COLORS["cyan"],
    "email": SUNRISE_COLORS["blue"],
    "call": SUNRISE_COLORS["orange_dark"],
    "none": SUNRISE_COLORS["muted"],
}

STATUS_COLORS: Mapping[str, str] = {
    "pass": SUNRISE_COLORS["green"],
    "ok": SUNRISE_COLORS["green"],
    "watch": SUNRISE_COLORS["yellow"],
    "warning": SUNRISE_COLORS["yellow"],
    "stop": SUNRISE_COLORS["coral"],
    "fail": SUNRISE_COLORS["coral"],
}


def color(name: str) -> str:
    """Return a named Sunrise color token."""
    return SUNRISE_COLORS[name]


def group_color(name: str) -> str:
    """Return a stable color for common experiment, method, or channel labels."""
    return GROUP_COLORS.get(name.lower(), SUNRISE_COLORS["slate"])


def status_color(status: str) -> str:
    """Return a stable color for pass/watch/stop style labels."""
    normalized = status.lower().replace(".", " ").replace("_", " ")
    for key, value in STATUS_COLORS.items():
        if key in normalized:
            return value
    return SUNRISE_COLORS["slate"]


def apply_matplotlib_style() -> None:
    """Apply Sunrise defaults to matplotlib for notebooks and scripts."""
    import matplotlib as mpl
    from cycler import cycler

    mpl.rcParams.update(
        {
            "axes.prop_cycle": cycler(color=SUNRISE_PALETTE),
            "figure.facecolor": SUNRISE_COLORS["white"],
            "axes.facecolor": SUNRISE_COLORS["white"],
            "savefig.facecolor": SUNRISE_COLORS["white"],
            "savefig.edgecolor": SUNRISE_COLORS["white"],
            "font.family": "sans-serif",
            "font.sans-serif": SANS_STACK,
            "font.size": 10.5,
            "figure.titlesize": 15,
            "figure.titleweight": "bold",
            "axes.titlesize": 13.5,
            "axes.titleweight": "bold",
            "axes.titlepad": 12,
            "axes.labelsize": 10.5,
            "axes.labelpad": 8,
            "axes.labelcolor": SUNRISE_COLORS["charcoal"],
            "axes.edgecolor": SUNRISE_COLORS["grid"],
            "axes.linewidth": 0.8,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": SUNRISE_COLORS["slate"],
            "ytick.color": SUNRISE_COLORS["slate"],
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "grid.color": SUNRISE_COLORS["grid"],
            "grid.linewidth": 0.8,
            "grid.alpha": 0.55,
            "lines.linewidth": 2.2,
            "lines.markersize": 6,
            "patch.edgecolor": SUNRISE_COLORS["white"],
            "patch.linewidth": 0,
            "legend.frameon": False,
            "legend.fontsize": 9.5,
            "legend.title_fontsize": 10,
            "figure.autolayout": False,
        }
    )


def save_figure(fig, path, dpi: int = CHART_DPI, **kwargs) -> None:
    """Save a figure with the project chart defaults."""
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=SUNRISE_COLORS["white"], **kwargs)


MARP_CSS = dedent(
    f"""
    :root {{
      --sunrise-orange: {SUNRISE_COLORS['orange']};
      --sunrise-coral: {SUNRISE_COLORS['coral']};
      --sunrise-cyan: {SUNRISE_COLORS['cyan']};
      --sunrise-blue: {SUNRISE_COLORS['blue']};
      --sunrise-navy: {SUNRISE_COLORS['navy']};
      --sunrise-charcoal: {SUNRISE_COLORS['charcoal']};
      --sunrise-slate: {SUNRISE_COLORS['slate']};
      --sunrise-grid: {SUNRISE_COLORS['grid']};
      --sunrise-paper: {SUNRISE_COLORS['paper']};
    }}

    section {{
      width: 1280px;
      height: 720px;
      padding: 52px 64px 44px;
      background:
        linear-gradient(180deg, #ffffff 0%, #fbfbfa 100%);
      color: var(--sunrise-charcoal);
      font-family: "Avenir Next", "Source Sans 3", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      font-size: 23px;
      line-height: 1.36;
      letter-spacing: 0;
    }}

    section::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at top right, rgba(114,199,231,0.12), transparent 28%),
        linear-gradient(90deg, rgba(247,248,248,0.6), rgba(247,248,248,0));
      pointer-events: none;
    }}

    section::after {{
      color: var(--sunrise-slate);
      font-size: 12px;
      right: 28px;
      bottom: 18px;
    }}

    h1 {{
      color: var(--sunrise-navy);
      font-size: 44px;
      line-height: 1.06;
      margin: 0 0 18px;
      font-weight: 700;
      max-width: 1020px;
    }}

    h2 {{
      color: var(--sunrise-navy);
      font-size: 28px;
      line-height: 1.16;
      margin: 0 0 12px;
      font-weight: 700;
    }}

    h3 {{
      color: var(--sunrise-charcoal);
      font-size: 22px;
      margin: 16px 0 8px;
    }}

    p, li {{
      line-height: 1.34;
    }}

    ul {{
      padding-left: 1.1em;
    }}

    li {{
      margin: 0.16em 0;
    }}

    strong {{
      color: var(--sunrise-navy);
    }}

    blockquote {{
      margin: 14px 0 18px;
      padding: 14px 18px;
      border-left: 4px solid var(--sunrise-orange);
      background: rgba(247,248,248,0.96);
      border-radius: 0 14px 14px 0;
      color: var(--sunrise-charcoal);
      font-size: 22px;
    }}

    blockquote strong {{
      color: var(--sunrise-orange);
    }}

    a {{
      color: var(--sunrise-blue);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 18px;
      margin-top: 12px;
      box-shadow: 0 10px 24px rgba(11,31,42,0.05);
      border-radius: 12px;
      overflow: hidden;
    }}

    th {{
      background: var(--sunrise-navy);
      color: #fff;
      font-weight: 700;
    }}

    th, td {{
      border: 1px solid var(--sunrise-grid);
      padding: 7px 10px;
    }}

    tr:nth-child(even) td {{
      background: var(--sunrise-paper);
    }}

    img {{
      max-height: 390px;
      object-fit: contain;
      border-radius: 16px;
      box-shadow: 0 18px 36px rgba(11,31,42,0.10);
      background: #fff;
      padding: 6px;
    }}

    header, footer {{
      color: var(--sunrise-slate);
      font-size: 13px;
    }}

    mermaid {{
      text-align: center;
    }}

    code {{
      font-family: "SF Mono", "Menlo", "Consolas", monospace;
      font-size: 0.86em;
      background: rgba(247,248,248,0.95);
      padding: 0.08em 0.28em;
      border-radius: 6px;
    }}

    pre code {{
      display: block;
      padding: 14px 16px;
      line-height: 1.38;
    }}

    section.compact p,
    section.compact li,
    section.compact table {{
      font-size: 20px;
    }}

    .insight {{
      color: var(--sunrise-orange);
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}

    section.lead {{
      background: linear-gradient(112deg, rgba(11,31,42,0.94), rgba(214,65,22,0.78));
      color: #fff;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    section.lead h1,
    section.lead h2,
    section.lead strong,
    section.lead footer,
    section.lead header {{
      color: #fff;
    }}

    section.lead table,
    section.lead td {{
      color: var(--sunrise-charcoal);
    }}

    section.lead th {{
      color: #fff;
    }}

    section.lead::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        repeating-radial-gradient(ellipse at 78% 35%, rgba(255,255,255,0.42) 0 1px, transparent 1px 12px);
      opacity: 0.5;
      pointer-events: none;
    }}
    """
).strip()


def marp_frontmatter(
    *,
    title: str | None = None,
    description: str | None = None,
    paginate: bool = True,
    header: str = "Sunrise Data Science & Analytics",
    footer: str = "Stanislav Babenyshev | Case Study Interview",
) -> str:
    """Return Marp frontmatter with the shared Sunrise presentation style."""
    lines = ["---", "marp: true"]
    if title:
        lines.append(f"title: {title}")
    if description:
        lines.append(f"description: {description}")
    lines.extend(
        [
            f"paginate: {str(paginate).lower()}",
            "theme: default",
            f'header: "{header}"',
            f'footer: "{footer}"',
            "style: |",
        ]
    )
    lines.extend(f"  {line}" if line else "" for line in MARP_CSS.splitlines())
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


MARP_FRONTMATTER = marp_frontmatter()