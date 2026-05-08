#!/usr/bin/env python3
"""L3 variants — single screenshot + big pull-out card.

L3a — 2 timestamp blocks in card, connected to screenshot by hairline curve.
L3b — 1 timestamp block (large) in card, magnifier-lens marker on screenshot.

Both light theme. No paint-like red outlines: card is white with soft
drop-shadow, 1px hairline border, accent expressed only by a 4px red bar
on the inner-left edge.
"""
import base64
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def b64(fname):
    with open(os.path.join(ROOT, fname), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


SPARKLE_PATH = "M12 0 L14.8 9.2 L24 12 L14.8 14.8 L12 24 L9.2 14.8 L0 12 L9.2 9.2 Z"


def sparkles(x, y, color, scale=1.0):
    return f'''
    <g transform="translate({x},{y}) scale({scale})" fill="{color}">
      <path d="{SPARKLE_PATH}"/>
      <path d="M38 12 L39.8 18 L46 20 L39.8 22 L38 28 L36.2 22 L30 20 L36.2 18 Z" opacity="0.85"/>
      <path d="M6 30 L7 33 L10 34 L7 35 L6 38 L5 35 L2 34 L5 33 Z" opacity="0.7"/>
    </g>'''


def wrap_lines(text, max_chars):
    """Greedy word-wrap to a max char width. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def screenshot_with_dim(img_b64, x, y, w, h, suffix, radius=20):
    """Screenshot with asymmetric dim overlay. Pure vector."""
    return f'''
    <g transform="translate({x},{y})">
      <rect x="4" y="9" width="{w}" height="{h}" rx="{radius}"
            fill="#000000" fill-opacity="0.20"/>
      <rect width="{w}" height="{h}" rx="{radius}" fill="#FFFFFF"/>
      <clipPath id="clip_{suffix}">
        <rect width="{w}" height="{h}" rx="{radius}"/>
      </clipPath>
      <g clip-path="url(#clip_{suffix})">
        <image href="data:image/png;base64,{img_b64}"
               x="0" y="0" width="{w}" height="{h}"
               preserveAspectRatio="xMidYMid slice"/>
        <rect width="{w}" height="{h}" fill="url(#dimGrad_{suffix})"/>
      </g>
      <rect width="{w}" height="{h}" rx="{radius}" fill="none"
            stroke="#0000001A" stroke-width="1"/>
    </g>'''


def dim_gradient(grad_id, opacity=0.30):
    return f'''
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="#000000" stop-opacity="{opacity}"/>
      <stop offset="35%" stop-color="#000000" stop-opacity="{opacity * 0.55}"/>
      <stop offset="55%" stop-color="#000000" stop-opacity="0"/>
    </linearGradient>'''


def card_chrome(cx, cy, cw, ch, accent="#E50914"):
    """White card with: soft drop-shadow, 1px hairline border, 4px accent
    bar on inner-left, optional rounded corners."""
    return f'''
    <!-- soft drop shadow -->
    <rect x="{cx + 6}" y="{cy + 14}" width="{cw}" height="{ch}" rx="22"
          fill="#000000" fill-opacity="0.10"/>
    <rect x="{cx + 3}" y="{cy + 7}" width="{cw}" height="{ch}" rx="22"
          fill="#000000" fill-opacity="0.06"/>
    <!-- card body -->
    <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="22"
          fill="#FFFFFF"/>
    <!-- inner-left accent bar -->
    <rect x="{cx}" y="{cy}" width="4" height="{ch}" rx="2" fill="{accent}"/>
    <!-- hairline border -->
    <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="22"
          fill="none" stroke="#0000001A" stroke-width="1"/>'''


def title_block(accent="#E50914", title_color="#171717", sub_color="#5C5C5C"):
    return f'''
  <text x="640" y="68" text-anchor="middle"
        font-family="Goldman, 'Arial Black', sans-serif"
        font-size="58" fill="{title_color}" letter-spacing="-1.5">YouTube <tspan fill="{accent}">Summarizer</tspan></text>
  <text x="640" y="104" text-anchor="middle"
        font-family="Inter, 'Helvetica Neue', sans-serif"
        font-size="19" font-weight="500" fill="{sub_color}" letter-spacing="0.2">Understand any YouTube video in seconds — without watching it.</text>
  {sparkles(913, 26, "#FF6E76", 1.0)}
'''


def magnifier_lens(cx, cy, r, accent="#E50914"):
    """Decorative magnifier-glass marker. Used in L3b."""
    return f'''
    <g transform="translate({cx},{cy})">
      <!-- soft shadow -->
      <circle cx="2" cy="4" r="{r + 1}" fill="#000000" fill-opacity="0.18"/>
      <!-- white lens body -->
      <circle cx="0" cy="0" r="{r}" fill="#FFFFFF"/>
      <!-- accent ring -->
      <circle cx="0" cy="0" r="{r - 2}" fill="none" stroke="{accent}"
              stroke-width="1.5" stroke-opacity="0.55"/>
      <!-- magnifier glass icon inside -->
      <circle cx="-3" cy="-3" r="{r * 0.42:.1f}" fill="none"
              stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
      <line x1="{r * 0.18:.1f}" y1="{r * 0.18:.1f}"
            x2="{r * 0.55:.1f}" y2="{r * 0.55:.1f}"
            stroke="{accent}" stroke-width="3.5" stroke-linecap="round"/>
    </g>'''


def hairline_curve(x1, y1, x2, y2, accent="#E50914"):
    """Subtle curved hairline connecting two points. Two anchor dots at the
    endpoints."""
    cx1 = x1 + (x2 - x1) * 0.55
    cx2 = x2 - (x2 - x1) * 0.55
    return f'''
    <path d="M{x1} {y1} C {cx1} {y1}, {cx2} {y2}, {x2} {y2}"
          fill="none" stroke="{accent}" stroke-opacity="0.35"
          stroke-width="1.5" stroke-dasharray="0"/>
    <circle cx="{x1}" cy="{y1}" r="3.5" fill="{accent}" fill-opacity="0.85"/>
    <circle cx="{x2}" cy="{y2}" r="3.5" fill="{accent}" fill-opacity="0.85"/>'''


# ---------------------------------------------------------------------------
# L3a — 2 timestamp blocks + hairline connection
# ---------------------------------------------------------------------------

def variant_l3a_light(yt3_b64):
    accent = "#E50914"
    sx, sy, sw, sh = 80, 150, 460, 503
    cx, cy, cw, ch = 580, 150, 620, 503

    entries = [
        ("00:00", "The speaker discusses the impact of sleep on "
                  "reproductive health and testosterone levels, and "
                  "emphasizes the importance of sleep for brain functions "
                  "like learning and memory."),
        ("04:36", "Deep sleep stages, characterized by brainwaves and "
                  "sleep spindles, facilitate memory consolidation by "
                  "transferring memories from short-term to long-term "
                  "storage."),
    ]

    # Card header
    header_y = cy + 44
    # Two-entry layout
    block_h = 200
    e1_top = cy + 76
    e2_top = e1_top + block_h + 30

    # Body text wrapping (Inter 19pt, body width ~430 → ~50 chars per line)
    rows = []
    for i, (ts, body) in enumerate(entries):
        top = e1_top if i == 0 else e2_top
        lines = wrap_lines(body, 50)
        line_h = 30
        # Timestamp pill
        pill = f'''
      <rect x="{cx + 28}" y="{top}" width="92" height="40" rx="20" fill="{accent}"/>
      <text x="{cx + 74}" y="{top + 27}" text-anchor="middle"
            font-family="'JetBrains Mono', 'SF Mono', 'Menlo', monospace"
            font-weight="700" font-size="16" fill="#FFFFFF">{ts}</text>'''
        # Body lines
        body_x = cx + 140
        body_top = top + 24
        body_tspans = "".join(
            f'<tspan x="{body_x}" dy="{line_h if k > 0 else 0}">{line}</tspan>'
            for k, line in enumerate(lines)
        )
        body_text = f'''
      <text x="{body_x}" y="{body_top}" font-family="Inter, sans-serif"
            font-weight="500" font-size="19" fill="#1F1F1F"
            letter-spacing="-0.1">{body_tspans}</text>'''
        rows.append(pill + body_text)

        # Subtle divider between entries
        if i == 0:
            rows.append(f'''
      <line x1="{cx + 28}" y1="{top + block_h + 4}"
            x2="{cx + cw - 28}" y2="{top + block_h + 4}"
            stroke="#0000000F" stroke-width="1"/>''')

    # Hairline curve from screenshot's right widget edge to card's left
    # Entry midpoint vertically aligns with first card entry
    # Native widget sits at right ~60% of screenshot. Pick a y that maps
    # to the first summary entry (y=180..360 native; native_h=1400, displayed
    # at 503 → scale=0.359; entry mid native y=270 → display y_off=97; absolute
    # y = sy + 97 = 247).
    line_x1 = sx + sw - 4
    line_y1 = 247
    line_x2 = cx + 4
    line_y2 = e1_top + 20  # near top of first entry

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"  stop-color="#FFF7F4"/>
      <stop offset="50%" stop-color="#FAF0EE"/>
      <stop offset="100%" stop-color="#F4E6E6"/>
    </linearGradient>
    <radialGradient id="haloLeft" cx="15%" cy="50%" r="35%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="haloRight" cx="80%" cy="55%" r="40%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.13"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    {dim_gradient("dimGrad_l3a")}
  </defs>

  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#haloLeft)"/>
  <rect width="1280" height="800" fill="url(#haloRight)"/>

  {title_block(accent)}

  <!-- Single screenshot YT3 -->
  {screenshot_with_dim(yt3_b64, sx, sy, sw, sh, "l3a")}

  <!-- Pull-out card -->
  {card_chrome(cx, cy, cw, ch, accent)}

  <!-- Card header -->
  <g transform="translate({cx + 28},{header_y - 18})">
    <g fill="none" stroke="{accent}" stroke-width="2.2" stroke-linecap="round">
      <circle cx="3" cy="4" r="1.6" fill="{accent}"/><line x1="10" y1="4" x2="22" y2="4"/>
      <circle cx="3" cy="12" r="1.6" fill="{accent}"/><line x1="10" y1="12" x2="22" y2="12"/>
      <circle cx="3" cy="20" r="1.6" fill="{accent}"/><line x1="10" y1="20" x2="22" y2="20"/>
    </g>
  </g>
  <text x="{cx + 60}" y="{header_y}"
        font-family="Inter, sans-serif" font-weight="700"
        font-size="14" fill="{accent}" letter-spacing="1.5">FROM YOUR SCREEN</text>
  {sparkles(cx + cw - 56, header_y - 26, accent, 0.75)}
  <line x1="{cx + 28}" y1="{header_y + 12}" x2="{cx + cw - 28}" y2="{header_y + 12}"
        stroke="#0000000F" stroke-width="1"/>

  {''.join(rows)}

  <!-- Hairline connection screenshot ↔ card -->
  {hairline_curve(line_x1, line_y1, line_x2, line_y2, accent)}
</svg>'''
    return svg


# ---------------------------------------------------------------------------
# L3b — single timestamp block (LARGE) + magnifier-lens marker
# ---------------------------------------------------------------------------

def variant_l3b_light(yt3_b64):
    accent = "#E50914"
    sx, sy, sw, sh = 80, 150, 460, 503
    cx, cy, cw, ch = 580, 150, 620, 503

    ts = "00:00"
    body = ("The speaker discusses the significant impact of sleep on "
            "reproductive health and testosterone levels in men, "
            "highlighting that sleep deprivation can affect health, "
            "and emphasizes the importance of sleep for brain functions "
            "like learning and memory.")

    header_y = cy + 44
    pill_top = cy + 100
    body_x = cx + 28
    body_top = cy + 200

    # Wrap long body — 24pt Inter wider chars; 580 width → ~36 chars/line
    lines = wrap_lines(body, 36)
    line_h = 38
    body_tspans = "".join(
        f'<tspan x="{body_x}" dy="{line_h if k > 0 else 0}">{line}</tspan>'
        for k, line in enumerate(lines)
    )

    # Lens marker on screenshot — over first summary entry source
    # Native source y=180..360 (mid 270); display scale 0.359 → mid y_off=97
    # Native source x=460..1240 (mid 850); scale 460/1280=0.359 → mid x_off=305
    # Using sw=460: actual scale = 460/1280=0.359
    lens_x = sx + 285
    lens_y = sy + 105

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"  stop-color="#FFF7F4"/>
      <stop offset="50%" stop-color="#FAF0EE"/>
      <stop offset="100%" stop-color="#F4E6E6"/>
    </linearGradient>
    <radialGradient id="haloLeft" cx="15%" cy="50%" r="35%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="haloRight" cx="80%" cy="55%" r="40%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.13"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    {dim_gradient("dimGrad_l3b")}
  </defs>

  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#haloLeft)"/>
  <rect width="1280" height="800" fill="url(#haloRight)"/>

  {title_block(accent)}

  <!-- Single screenshot YT3 -->
  {screenshot_with_dim(yt3_b64, sx, sy, sw, sh, "l3b")}

  <!-- Magnifier lens marker on screenshot first entry -->
  {magnifier_lens(lens_x, lens_y, 30, accent)}

  <!-- Pull-out card -->
  {card_chrome(cx, cy, cw, ch, accent)}

  <!-- Card header -->
  <g transform="translate({cx + 28},{header_y - 18})">
    <g fill="none" stroke="{accent}" stroke-width="2.2" stroke-linecap="round">
      <circle cx="3" cy="4" r="1.6" fill="{accent}"/><line x1="10" y1="4" x2="22" y2="4"/>
      <circle cx="3" cy="12" r="1.6" fill="{accent}"/><line x1="10" y1="12" x2="22" y2="12"/>
      <circle cx="3" cy="20" r="1.6" fill="{accent}"/><line x1="10" y1="20" x2="22" y2="20"/>
    </g>
  </g>
  <text x="{cx + 60}" y="{header_y}"
        font-family="Inter, sans-serif" font-weight="700"
        font-size="14" fill="{accent}" letter-spacing="1.5">FROM YOUR SCREEN</text>
  {sparkles(cx + cw - 56, header_y - 26, accent, 0.75)}
  <line x1="{cx + 28}" y1="{header_y + 12}" x2="{cx + cw - 28}" y2="{header_y + 12}"
        stroke="#0000000F" stroke-width="1"/>

  <!-- Big timestamp pill -->
  <rect x="{cx + 28}" y="{pill_top}" width="124" height="52" rx="26" fill="{accent}"/>
  <text x="{cx + 90}" y="{pill_top + 35}" text-anchor="middle"
        font-family="'JetBrains Mono', 'SF Mono', 'Menlo', monospace"
        font-weight="700" font-size="22" fill="#FFFFFF">{ts}</text>

  <!-- Body text -->
  <text x="{body_x}" y="{body_top}" font-family="Inter, sans-serif"
        font-weight="500" font-size="23" fill="#171717"
        letter-spacing="-0.2">{body_tspans}</text>
</svg>'''
    return svg


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    yt3 = b64("yt3_s.png")
    out = {
        "cover_variantL3a_light.svg": variant_l3a_light(yt3),
        "cover_variantL3b_light.svg": variant_l3b_light(yt3),
    }
    for name, svg in out.items():
        path = os.path.join(ROOT, name)
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {name}: {os.path.getsize(path) / 1024:.0f} KB")
