#!/usr/bin/env python3
"""Generate two LIGHT-theme cover variants per user feedback:

  L1 = combo (#1 asymmetric dim) + (#2 magnifier inset on each screenshot)
  L2 = combo (#1 asymmetric dim) + (#3 single screenshot + big pull-out card)

Both are 1280x800 PNG-embedded SVGs.
"""
import base64
import io
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))


# ---- helpers ---------------------------------------------------------------

def png_b64_from_path(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def crop_b64(src_path, box):
    """PIL crop -> base64 PNG string."""
    img = Image.open(src_path)
    cropped = img.crop(box)
    buf = io.BytesIO()
    cropped.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ---- shared visual atoms ---------------------------------------------------

SPARKLE_PATH = "M12 0 L14.8 9.2 L24 12 L14.8 14.8 L12 24 L9.2 14.8 L0 12 L9.2 9.2 Z"


def sparkle_cluster(x, y, color, scale=1.0):
    return f'''
    <g transform="translate({x},{y}) scale({scale})" fill="{color}">
      <path d="{SPARKLE_PATH}"/>
      <path d="M38 12 L39.8 18 L46 20 L39.8 22 L38 28 L36.2 22 L30 20 L36.2 18 Z" opacity="0.85"/>
      <path d="M6 30 L7 33 L10 34 L7 35 L6 38 L5 35 L2 34 L5 33 Z" opacity="0.7"/>
    </g>'''


def title_block(title_color, accent_color, sub_color, accent_color_dim):
    """Top hero text block — same on L1 & L2."""
    return f'''
  <text x="640" y="68" text-anchor="middle"
        font-family="Goldman, 'Arial Black', sans-serif"
        font-size="60" fill="{title_color}" letter-spacing="-1.5">YouTube <tspan fill="{accent_color}">Summarizer</tspan></text>
  <text x="640" y="106" text-anchor="middle"
        font-family="Inter, 'Helvetica Neue', sans-serif"
        font-size="20" font-weight="500" fill="{sub_color}" letter-spacing="0.2">Understand any YouTube video in seconds — without watching it.</text>
  {sparkle_cluster(905, 26, accent_color_dim, 1.0)}
'''


def screenshot_with_dim(img_b64, x, y, w, h, radius=18,
                       dim_color="#000000", dim_opacity=0.22, dim_id_suffix="a"):
    """Renders a screenshot with an asymmetric darkening overlay on its
    LEFT ~45%, fading to transparent. Pure vector, no SVG filters.
    """
    grad_id = f"dimGrad_{dim_id_suffix}"
    return f'''
    <g transform="translate({x},{y})">
      <rect x="4" y="9" width="{w}" height="{h}" rx="{radius}" fill="#000000" fill-opacity="0.22"/>
      <rect width="{w}" height="{h}" rx="{radius}" fill="#FFFFFF"/>
      <clipPath id="clip_{dim_id_suffix}">
        <rect width="{w}" height="{h}" rx="{radius}"/>
      </clipPath>
      <g clip-path="url(#clip_{dim_id_suffix})">
        <image href="data:image/png;base64,{img_b64}"
               x="0" y="0" width="{w}" height="{h}"
               preserveAspectRatio="xMidYMid slice"/>
        <rect width="{w}" height="{h}" fill="url(#{grad_id})"/>
      </g>
      <rect width="{w}" height="{h}" rx="{radius}" fill="none"
            stroke="#0000001E" stroke-width="1.5"/>
    </g>'''


def dim_gradient_def(grad_id, dim_color="#000000", dim_opacity=0.28):
    """Linear gradient from dim_opacity at left → transparent ~50% across.
    Used inside <defs>."""
    return f'''
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{dim_color}" stop-opacity="{dim_opacity}"/>
      <stop offset="35%" stop-color="{dim_color}" stop-opacity="{dim_opacity * 0.55}"/>
      <stop offset="55%" stop-color="{dim_color}" stop-opacity="0"/>
    </linearGradient>'''


# ---- Variant L1 ------------------------------------------------------------

def variant_l1_light(yt3_b64, yt4_b64, zoom_yt3_b64, zoom_yt4_b64):
    # Layout
    sw, sh = 440, 481
    gap = 60
    pad_x = (1280 - sw * 2 - gap) // 2  # = 170
    y_shot = 145

    # Magnifier cards
    mw, mh = 440, 138
    y_mag = 645

    accent = "#E50914"
    accent_dim = "#FF6E76"
    title_color = "#171717"
    sub_color = "#5C5C5C"

    # Connection: a small triangular "tab" pointing UP from magnifier to screenshot,
    # plus a hint rect inside screenshot showing source area.

    def magnifier(mx, my, zoom_b64, label_text, label_icon):
        # Small upward-pointing triangle at top center to suggest origin
        tri = f'<path d="M{mw // 2 - 10} -2 L{mw // 2} -14 L{mw // 2 + 10} -2 Z" fill="#FFFFFF" stroke="{accent}" stroke-width="1.5"/>'
        return f'''
    <g transform="translate({mx},{my})">
      <!-- soft drop shadow rect -->
      <rect x="3" y="9" width="{mw}" height="{mh}" rx="16" fill="#000000" fill-opacity="0.18"/>
      {tri}
      <!-- card body -->
      <rect width="{mw}" height="{mh}" rx="16" fill="#FFFFFF"/>
      <!-- zoomed image (image already pre-cropped, just stretch into available area) -->
      <clipPath id="zoomClip_{mx}_{my}">
        <rect x="0" y="0" width="{mw}" height="{mh - 38}" rx="16"/>
      </clipPath>
      <g clip-path="url(#zoomClip_{mx}_{my})">
        <image href="data:image/png;base64,{zoom_b64}"
               x="0" y="0" width="{mw}" height="{mh - 38}"
               preserveAspectRatio="xMidYMid slice"/>
      </g>
      <!-- divider -->
      <line x1="0" y1="{mh - 38}" x2="{mw}" y2="{mh - 38}" stroke="#E5091420" stroke-width="1"/>
      <!-- footer: icon + label -->
      <g transform="translate(16,{mh - 28})">{label_icon}</g>
      <text x="50" y="{mh - 14}" font-family="Inter, sans-serif"
            font-weight="700" font-size="14" fill="{accent}" letter-spacing="0.4">{label_text}</text>
      <!-- card border -->
      <rect width="{mw}" height="{mh}" rx="16" fill="none" stroke="{accent}" stroke-width="2" stroke-opacity="0.55"/>
    </g>'''

    # Source-area hints inside screenshots — subtle rounded outline highlighting
    # the widget portion that the magnifier zooms into.
    # Native crop region for each was (460, 160) → (1240, 360) in 1280×1400
    # Display scale: 440/1280 = 0.34375
    def source_hint(sx_offset_x, sx_offset_y):
        # source rect in native: x=460..1240 (780w), y=160..360 (200h)
        scale = sw / 1280
        rx = 460 * scale
        ry = 160 * scale
        rw = 780 * scale
        rh = 200 * scale
        return f'''
    <g transform="translate({sx_offset_x},{sx_offset_y})">
      <rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}"
            rx="6" fill="none" stroke="{accent}" stroke-width="2"
            stroke-opacity="0.85" stroke-dasharray="4 3"/>
    </g>'''

    list_icon = (f'<g fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round">'
                 f'<circle cx="3" cy="4" r="1.6" fill="{accent}"/><line x1="10" y1="4" x2="22" y2="4"/>'
                 f'<circle cx="3" cy="11" r="1.6" fill="{accent}"/><line x1="10" y1="11" x2="22" y2="11"/>'
                 f'<circle cx="3" cy="18" r="1.6" fill="{accent}"/><line x1="10" y1="18" x2="22" y2="18"/></g>')
    chat_icon = (f'<g fill="{accent}" stroke="{accent}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">'
                 f'<path d="M2 4 H22 V16 H10 L4 21 V16 H2 Z" fill="{accent}" fill-opacity="0.18"/></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFF7F4"/>
      <stop offset="50%" stop-color="#FAF0EE"/>
      <stop offset="100%" stop-color="#F4E6E6"/>
    </linearGradient>
    <radialGradient id="halo1" cx="20%" cy="40%" r="40%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="halo2" cx="80%" cy="65%" r="40%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    {dim_gradient_def("dimGrad_l1a")}
    {dim_gradient_def("dimGrad_l1b")}
  </defs>

  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#halo1)"/>
  <rect width="1280" height="800" fill="url(#halo2)"/>

  {title_block(title_color, accent, sub_color, accent_dim)}

  <!-- Left screenshot -->
  {screenshot_with_dim(yt3_b64, pad_x, y_shot, sw, sh, dim_id_suffix="l1a")}
  {source_hint(pad_x, y_shot)}

  <!-- Right screenshot -->
  {screenshot_with_dim(yt4_b64, pad_x + sw + gap, y_shot, sw, sh, dim_id_suffix="l1b")}
  {source_hint(pad_x + sw + gap, y_shot)}

  <!-- Magnifier 1 — Timestamped summary -->
  {magnifier(pad_x, y_mag, zoom_yt3_b64, "TIMESTAMPED SUMMARY", list_icon)}

  <!-- Magnifier 2 — Q&A -->
  {magnifier(pad_x + sw + gap, y_mag, zoom_yt4_b64, "ASK ANY QUESTION", chat_icon)}
</svg>'''
    return svg


# ---- Variant L2 ------------------------------------------------------------

def variant_l2_light(yt3_b64):
    """Single screenshot (left) + big AI summary card (right).

    Card mimics the look of the actual widget output but at LARGE
    readable typography so the user instantly sees what the product
    produces.
    """
    accent = "#E50914"
    accent_dim = "#FF6E76"
    title_color = "#171717"
    sub_color = "#5C5C5C"
    card_bg = "#FFFFFF"

    sw, sh = 470, 514
    sx, sy = 76, 140
    qx, qy = 590, 140
    qw, qh = 614, 540

    # Caption chip below the screenshot
    cap_x, cap_y, cap_w, cap_h = sx, sy + sh + 32, sw, 54

    # Right-side "what you get" card content — three timestamped entries
    entries = [
        ("00:00", "Sleep & reproductive health", "Why deprivation hurts testosterone"),
        ("04:36", "Memory consolidation", "How deep sleep transfers memories"),
        ("07:28", "Sleep loss & physical health", "Cardiovascular and immune effects"),
    ]

    # Build entry rows — start at qy + 90 (after card header), step 130
    rows_svg = []
    for i, (ts, head, sub) in enumerate(entries):
        row_y = qy + 110 + i * 130
        rows_svg.append(f'''
    <!-- entry {i + 1} -->
    <g transform="translate({qx + 28},{row_y})">
      <rect width="92" height="40" rx="20" fill="{accent}"/>
      <text x="46" y="27" text-anchor="middle"
            font-family="'JetBrains Mono', 'SF Mono', monospace"
            font-weight="700" font-size="16" fill="#FFFFFF">{ts}</text>
      <text x="116" y="22" font-family="Inter, sans-serif" font-weight="700"
            font-size="22" fill="#171717" letter-spacing="-0.2">{head}</text>
      <text x="116" y="50" font-family="Inter, sans-serif" font-weight="500"
            font-size="16" fill="#6A6A6A">{sub}</text>
    </g>''')

        # Divider between rows
        if i < len(entries) - 1:
            rows_svg.append(f'''
    <line x1="{qx + 28}" y1="{row_y + 92}" x2="{qx + qw - 28}"
          y2="{row_y + 92}" stroke="#0000000F" stroke-width="1"/>''')

    list_icon = (f'<g fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round">'
                 f'<circle cx="3" cy="4" r="1.6" fill="{accent}"/><line x1="10" y1="4" x2="22" y2="4"/>'
                 f'<circle cx="3" cy="11" r="1.6" fill="{accent}"/><line x1="10" y1="11" x2="22" y2="11"/>'
                 f'<circle cx="3" cy="18" r="1.6" fill="{accent}"/><line x1="10" y1="18" x2="22" y2="18"/></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFF7F4"/>
      <stop offset="50%" stop-color="#FAF0EE"/>
      <stop offset="100%" stop-color="#F4E6E6"/>
    </linearGradient>
    <radialGradient id="halo1" cx="15%" cy="50%" r="35%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="halo2" cx="80%" cy="55%" r="40%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    {dim_gradient_def("dimGrad_l2", dim_opacity=0.28)}
  </defs>

  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#halo1)"/>
  <rect width="1280" height="800" fill="url(#halo2)"/>

  {title_block(title_color, accent, sub_color, accent_dim)}

  <!-- Screenshot YT3 with asymmetric dim -->
  {screenshot_with_dim(yt3_b64, sx, sy, sw, sh, dim_id_suffix="l2")}

  <!-- Caption chip under screenshot -->
  <g transform="translate({cap_x + (cap_w - 320) // 2},{cap_y})">
    <rect width="320" height="{cap_h}" rx="{cap_h // 2}" fill="{accent}"/>
    <g transform="translate(22,15)">{list_icon}</g>
    <text x="60" y="35" font-family="Inter, sans-serif" font-weight="700"
          font-size="18" fill="#FFFFFF" letter-spacing="0.2">Real screenshot — works inside YouTube</text>
  </g>

  <!-- Right: big "what you get" card -->
  <g>
    <rect x="{qx + 4}" y="{qy + 10}" width="{qw}" height="{qh}" rx="22" fill="#000000" fill-opacity="0.14"/>
    <rect x="{qx}" y="{qy}" width="{qw}" height="{qh}" rx="22" fill="{card_bg}"/>
    <rect x="{qx}" y="{qy}" width="{qw}" height="{qh}" rx="22" fill="none" stroke="{accent}" stroke-opacity="0.35" stroke-width="1.5"/>

    <!-- Card header -->
    <rect x="{qx}" y="{qy}" width="{qw}" height="76" rx="22" fill="{accent}"/>
    <rect x="{qx}" y="{qy + 38}" width="{qw}" height="38" fill="{accent}"/>
    <g transform="translate({qx + 26},{qy + 26})">
      <g fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round">
        <circle cx="3" cy="4" r="1.8" fill="#FFFFFF"/><line x1="10" y1="4" x2="26" y2="4"/>
        <circle cx="3" cy="13" r="1.8" fill="#FFFFFF"/><line x1="10" y1="13" x2="26" y2="13"/>
        <circle cx="3" cy="22" r="1.8" fill="#FFFFFF"/><line x1="10" y1="22" x2="26" y2="22"/>
      </g>
    </g>
    <text x="{qx + 70}" y="{qy + 47}" font-family="Inter, sans-serif"
          font-weight="700" font-size="22" fill="#FFFFFF" letter-spacing="-0.2">What you get — instantly</text>
    {sparkle_cluster(qx + qw - 80, qy + 22, "#FFFFFF", 0.9)}

    <!-- Entries -->
    {''.join(rows_svg)}
  </g>
</svg>'''
    return svg


# ---- main ------------------------------------------------------------------

if __name__ == "__main__":
    yt3_path = os.path.join(ROOT, "yt3_s.png")
    yt4_path = os.path.join(ROOT, "yt4_s.png")

    # Pre-crop magnifier zoom regions from the FULL-RES versions for crispness.
    # Then the SVG embeds them and stretches to magnifier-card size.
    zoom_box = (460, 160, 1240, 360)  # 780×200 in native 1280×1400

    zoom_yt3_b64 = crop_b64(os.path.join(ROOT, "yt3_light.png"), zoom_box)
    zoom_yt4_b64 = crop_b64(os.path.join(ROOT, "yt4_light.png"), zoom_box)

    yt3_b64 = png_b64_from_path(yt3_path)
    yt4_b64 = png_b64_from_path(yt4_path)

    out = {
        "cover_variantL1_light.svg": variant_l1_light(yt3_b64, yt4_b64,
                                                      zoom_yt3_b64, zoom_yt4_b64),
        "cover_variantL2_light.svg": variant_l2_light(yt3_b64),
    }
    for name, svg in out.items():
        path = os.path.join(ROOT, name)
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {name}: {os.path.getsize(path) / 1024:.0f} KB")
