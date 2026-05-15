#!/usr/bin/env python3
"""Generate 4 CWS main promo tiles (1280x800) for YouTube Summarizer.

Variant A — "Hero top, dual screenshots below"
Variant B — "Title left, screenshots right"

Each in dark and light themes.
"""
import base64
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))

def b64(fname):
    with open(os.path.join(ROOT, fname), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

YT1 = b64("yt1_s.png")  # dark, summary mode (1280x1600)
YT2 = b64("yt2_s.png")  # dark, Q&A mode (1280x1600)
YT3 = b64("yt3_s.png")  # light, summary mode (1280x1400)
YT4 = b64("yt4_s.png")  # light, Q&A mode (1280x1400)
# Cropped-to-1400 versions of dark — match light aspect for consistent display
YT1C = b64("yt1_s2.png")  # dark cropped 1280x1400
YT2C = b64("yt2_s2.png")  # dark cropped 1280x1400

# --- shared chunks -----------------------------------------------------------

# Simple 4-point sparkle path (for AI symbol). Rescale via transform.
SPARKLE = 'M12 0 L14.8 9.2 L24 12 L14.8 14.8 L12 24 L9.2 14.8 L0 12 L9.2 9.2 Z'


def sparkle_cluster(x, y, color="#FFFFFF", scale=1.0):
    """Three sparkles — big, medium, small — universal AI symbol."""
    return f'''
    <g transform="translate({x},{y}) scale({scale})" fill="{color}">
      <path d="{SPARKLE}"/>
      <path d="M38 12 L39.8 18 L46 20 L39.8 22 L38 28 L36.2 22 L30 20 L36.2 18 Z" opacity="0.85"/>
      <path d="M6 30 L7 33 L10 34 L7 35 L6 38 L5 35 L2 34 L5 33 Z" opacity="0.7"/>
    </g>'''


def tilted_screenshot(img_b64, x, y, w, h, angle_deg, ratio, stroke="#00000020", radius=16):
    """Tilted screenshot with rounded corners & stroke, no filter (Figma-friendly)."""
    # We emulate shadow by an offset darker rect below
    dx, dy = 6, 14
    return f'''
    <g transform="translate({x},{y}) rotate({angle_deg})">
      <rect x="{dx}" y="{dy}" width="{w}" height="{h}" rx="{radius}" fill="#000000" fill-opacity="0.28"/>
      <rect x="0" y="0" width="{w}" height="{h}" rx="{radius}" fill="#FFFFFF"/>
      <image href="data:image/png;base64,{img_b64}"
             x="0" y="0" width="{w}" height="{h}"
             preserveAspectRatio="xMidYMid slice"/>
      <rect x="0" y="0" width="{w}" height="{h}" rx="{radius}"
            fill="none" stroke="{stroke}" stroke-width="1.5"/>
    </g>'''


def tilted_screenshot_dim(img_b64, x, y, w, h, suffix, stroke="#0000001E",
                          radius=20):
    """Same screenshot card, but with two pure-vector overlays inside the
    clipPath:

      • asymmetric dim — linear gradient that darkens the left ~55% of the
        image (the YouTube video / sidebar area) and fades to transparent
        before the widget panel begins, so the widget reads at full
        brightness;
      • warm spotlight — radial red tint ~8% over the widget area, giving
        the right side a subtle "lit" feel for cinematic contrast.

    All filters avoided — Figma-safe.
    """
    dx, dy = 6, 14
    return f'''
    <g transform="translate({x},{y})">
      <rect x="{dx}" y="{dy}" width="{w}" height="{h}" rx="{radius}"
            fill="#000000" fill-opacity="0.28"/>
      <rect x="0" y="0" width="{w}" height="{h}" rx="{radius}" fill="#FFFFFF"/>
      <clipPath id="a3clip_{suffix}">
        <rect width="{w}" height="{h}" rx="{radius}"/>
      </clipPath>
      <g clip-path="url(#a3clip_{suffix})">
        <image href="data:image/png;base64,{img_b64}"
               x="0" y="0" width="{w}" height="{h}"
               preserveAspectRatio="xMidYMid slice"/>
        <rect width="{w}" height="{h}" fill="url(#a3_dim)"/>
        <rect width="{w}" height="{h}" fill="url(#a3_dim_btm)"/>
      </g>
      <rect width="{w}" height="{h}" rx="{radius}"
            fill="none" stroke="{stroke}" stroke-width="1.5"/>
    </g>'''


# --- Variant A: hero-top, twin screenshots below ---------------------------

def variant_a(img_left_b64, img_right_b64, theme):
    """1280x800 — big title on top, two screenshots beneath, side-by-side.

    Screenshot box: 420 x 525 (keeping 4:5 dark or close for light).
    Two boxes centered → total width 420*2 + gap 40 = 880 → start x = 200.
    Title zone y = 40..160.
    """
    if theme == "dark":
        bg_grad_stops = '<stop offset="0%" stop-color="#1A0606"/><stop offset="60%" stop-color="#0B0B0B"/><stop offset="100%" stop-color="#050505"/>'
        glow_color = "#FF2323"
        glow_opacity_0 = 0.55
        glow_opacity_1 = 0.10
        title_color = "#F5F5F5"
        accent_color = "#FF2D2D"
        subtitle_color = "#C8C8C8"
        pill_bg = "#FF23231F"
        pill_stroke = "#FF2323AA"
        pill_text = "#FFB3B3"
        stroke_color = "#FFFFFF20"
    else:
        bg_grad_stops = '<stop offset="0%" stop-color="#FFF4F4"/><stop offset="50%" stop-color="#F9EEEE"/><stop offset="100%" stop-color="#F4E6E6"/>'
        glow_color = "#FF2D2D"
        glow_opacity_0 = 0.28
        glow_opacity_1 = 0.05
        title_color = "#171717"
        accent_color = "#E50914"
        subtitle_color = "#5C5C5C"
        pill_bg = "#E5091414"
        pill_stroke = "#E50914AA"
        pill_text = "#B00710"
        stroke_color = "#0000001A"

    # image sizes for screenshots (dark 4:5 or light 4:4.375)
    if theme == "dark":
        sw, sh = 400, 500
    else:
        # light screenshots are 1280×1400 (10:10.9375) ~ 1:1.094
        sw, sh = 400, 437

    # horizontal layout under title
    gap = 40
    total_w = sw * 2 + gap
    start_x = (1280 - total_w) // 2
    y_shots = 220 if theme == "dark" else 240  # vertical position

    left_screenshot = tilted_screenshot(img_left_b64, start_x, y_shots, sw, sh, -3, ratio=sw / sh, stroke=stroke_color)
    right_screenshot = tilted_screenshot(img_right_b64, start_x + sw + gap, y_shots + 20, sw, sh, 3, ratio=sw / sh, stroke=stroke_color)

    sparkles = sparkle_cluster(930, 60, color=accent_color, scale=1.2)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{bg_grad_stops}</linearGradient>
    <radialGradient id="glowL" cx="18%" cy="25%" r="55%">
      <stop offset="0%" stop-color="{glow_color}" stop-opacity="{glow_opacity_0}"/>
      <stop offset="60%" stop-color="{glow_color}" stop-opacity="{glow_opacity_1}"/>
      <stop offset="100%" stop-color="{glow_color}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowR" cx="85%" cy="85%" r="45%">
      <stop offset="0%" stop-color="{glow_color}" stop-opacity="{glow_opacity_0 * 0.7}"/>
      <stop offset="60%" stop-color="{glow_color}" stop-opacity="{glow_opacity_1}"/>
      <stop offset="100%" stop-color="{glow_color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#glowL)"/>
  <rect width="1280" height="800" fill="url(#glowR)"/>

  <!-- Title block -->
  <text x="640" y="108" text-anchor="middle" font-family="Goldman, 'Arial Black', sans-serif" font-size="72" fill="{title_color}" letter-spacing="-1.5">YouTube <tspan fill="{accent_color}">Summarizer</tspan></text>
  <text x="640" y="162" text-anchor="middle" font-family="Inter, 'Helvetica Neue', sans-serif" font-size="22" font-weight="500" fill="{subtitle_color}" letter-spacing="0.3">AI-powered summaries &amp; Q&amp;A for any video</text>

  {sparkles}

  <!-- Feature pill strip -->
  <g transform="translate(340, 192)">
    <g>
      <rect width="180" height="34" rx="17" fill="{pill_bg}" stroke="{pill_stroke}" stroke-width="1"/>
      <text x="90" y="22" text-anchor="middle" font-family="Inter, sans-serif" font-weight="600" font-size="13" fill="{pill_text}" letter-spacing="0.3">Timestamped summary</text>
    </g>
    <g transform="translate(200,0)">
      <rect width="130" height="34" rx="17" fill="{pill_bg}" stroke="{pill_stroke}" stroke-width="1"/>
      <text x="65" y="22" text-anchor="middle" font-family="Inter, sans-serif" font-weight="600" font-size="13" fill="{pill_text}" letter-spacing="0.3">Ask the video</text>
    </g>
    <g transform="translate(350,0)">
      <rect width="230" height="34" rx="17" fill="{pill_bg}" stroke="{pill_stroke}" stroke-width="1"/>
      <text x="115" y="22" text-anchor="middle" font-family="Inter, sans-serif" font-weight="600" font-size="13" fill="{pill_text}" letter-spacing="0.3">Any language &#8226; Any length</text>
    </g>
  </g>

  <!-- Screenshots -->
  {left_screenshot}
  {right_screenshot}
</svg>'''
    return svg


# --- Variant B: title-left, screenshots-right ------------------------------

def variant_b(img_left_b64, img_right_b64, theme):
    """1280x800 — title + features on left (560), two screenshots stacked on right.

    Right zone: x=620..1240. Two screenshots slightly overlapping.
    """
    if theme == "dark":
        bg_start = "#1A0606"
        bg_mid = "#0B0B0B"
        bg_end = "#050505"
        glow_color = "#FF2323"
        glow_o_0 = 0.55
        glow_o_1 = 0.10
        title_color = "#F5F5F5"
        accent_color = "#FF2D2D"
        subtitle_color = "#B8B8B8"
        bullet_color = "#D8D8D8"
        pill_bg = "#FF23231F"
        pill_stroke = "#FF2323AA"
        pill_text = "#FFB3B3"
        stroke_color = "#FFFFFF20"
        yt_chip_bg = "#FFFFFF0F"
    else:
        bg_start = "#FFF4F4"
        bg_mid = "#F9EEEE"
        bg_end = "#F4E6E6"
        glow_color = "#FF2D2D"
        glow_o_0 = 0.28
        glow_o_1 = 0.05
        title_color = "#171717"
        accent_color = "#E50914"
        subtitle_color = "#5C5C5C"
        bullet_color = "#3A3A3A"
        pill_bg = "#E5091414"
        pill_stroke = "#E50914AA"
        pill_text = "#B00710"
        stroke_color = "#0000001A"
        yt_chip_bg = "#0000000A"

    if theme == "dark":
        sw, sh = 480, 600
    else:
        sw, sh = 480, 525

    # Right zone: two screenshots offset
    # First (left-tilt, front), at (720, 140). Second (right-tilt, behind), at (780, 170), scaled smaller.
    sw2, sh2 = int(sw * 0.85), int(sh * 0.85)
    s1 = tilted_screenshot(img_left_b64, 600, 180, sw, sh, -4, ratio=sw / sh, stroke=stroke_color)
    s2 = tilted_screenshot(img_right_b64, 820, 120, sw2, sh2, 5, ratio=sw2 / sh2, stroke=stroke_color)

    sparkles = sparkle_cluster(300, 140, color=accent_color, scale=1.4)

    bullet = f'<circle cx="0" cy="0" r="4" fill="{accent_color}"/>'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{bg_start}"/>
      <stop offset="60%" stop-color="{bg_mid}"/>
      <stop offset="100%" stop-color="{bg_end}"/>
    </linearGradient>
    <radialGradient id="glowTL" cx="5%" cy="15%" r="50%">
      <stop offset="0%" stop-color="{glow_color}" stop-opacity="{glow_o_0}"/>
      <stop offset="70%" stop-color="{glow_color}" stop-opacity="{glow_o_1}"/>
      <stop offset="100%" stop-color="{glow_color}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowBR" cx="92%" cy="90%" r="50%">
      <stop offset="0%" stop-color="{glow_color}" stop-opacity="{glow_o_0 * 0.7}"/>
      <stop offset="70%" stop-color="{glow_color}" stop-opacity="{glow_o_1}"/>
      <stop offset="100%" stop-color="{glow_color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#glowTL)"/>
  <rect width="1280" height="800" fill="url(#glowBR)"/>

  <!-- Right zone: stacked screenshots (rendered BEHIND if z-order wanted) -->
  {s2}
  {s1}

  <!-- Left zone: title + features -->
  <g transform="translate(60, 210)">
    <!-- "works inside YouTube" chip -->
    <g>
      <rect width="200" height="34" rx="17" fill="{yt_chip_bg}" stroke="{pill_stroke}" stroke-width="1"/>
      <g transform="translate(12, 9)"><rect width="18" height="14" rx="4" fill="{accent_color}"/><path d="M7 4 L14 7 L7 10 Z" fill="#FFFFFF"/></g>
      <text x="38" y="22" font-family="Inter, sans-serif" font-weight="600" font-size="13" fill="{pill_text}" letter-spacing="0.3">Works inside YouTube</text>
    </g>
  </g>

  <text x="60" y="320" font-family="Goldman, 'Arial Black', sans-serif" font-size="72" fill="{title_color}" letter-spacing="-1.5">YouTube</text>
  <text x="60" y="388" font-family="Goldman, 'Arial Black', sans-serif" font-size="72" fill="{accent_color}" letter-spacing="-1.5">Summarizer</text>

  <text x="60" y="440" font-family="Inter, sans-serif" font-size="20" font-weight="500" fill="{subtitle_color}" letter-spacing="0.2">Understand any video in seconds.</text>

  <!-- Bullets -->
  <g transform="translate(68, 486)">
    <g>
      <g transform="translate(0, -5)">{bullet}</g>
      <text x="18" y="0" font-family="Inter, sans-serif" font-size="18" font-weight="600" fill="{bullet_color}">Timestamped summaries</text>
    </g>
    <g transform="translate(0, 34)">
      <g transform="translate(0, -5)">{bullet}</g>
      <text x="18" y="0" font-family="Inter, sans-serif" font-size="18" font-weight="600" fill="{bullet_color}">Ask questions about the video</text>
    </g>
    <g transform="translate(0, 68)">
      <g transform="translate(0, -5)">{bullet}</g>
      <text x="18" y="0" font-family="Inter, sans-serif" font-size="18" font-weight="600" fill="{bullet_color}">Works in any language</text>
    </g>
  </g>

  {sparkles}
</svg>'''
    return svg


# --- Variant A v2: bigger screenshots, no pills, captions ------------------

def variant_a2(img_left_b64, img_right_b64, theme):
    """1280x800 — refined Variant A.

    Key changes vs A:
      - screenshots scaled up from 400x500 to ~540x591 (35% bigger)
      - pill row removed (was competing with screenshots for attention)
      - caption chip BELOW each screenshot with an icon + 1-line label
      - dark screenshots are pre-cropped to 1280x1400 so both themes use
        identical display geometry
      - soft red glow placed under each screenshot — radiates around it
        without obscuring the widget itself
      - subtitle becomes punchier 1-liner
    """
    if theme == "dark":
        bg_grad_stops = '<stop offset="0%" stop-color="#1A0606"/><stop offset="60%" stop-color="#0B0B0B"/><stop offset="100%" stop-color="#050505"/>'
        glow_color = "#FF2323"
        glow_o_0 = 0.55
        glow_o_1 = 0.10
        title_color = "#F5F5F5"
        accent_color = "#FF2D2D"
        subtitle_color = "#C8C8C8"
        cap_bg = "#FF23231F"
        cap_stroke = "#FF2323AA"
        cap_text = "#FFB3B3"
        stroke_color = "#FFFFFF22"
        halo_color = "#FF2323"
        halo_opacity = 0.42
    else:
        bg_grad_stops = '<stop offset="0%" stop-color="#FFF7F4"/><stop offset="50%" stop-color="#FAF0EE"/><stop offset="100%" stop-color="#F4E6E6"/>'
        glow_color = "#FF2D2D"
        glow_o_0 = 0.28
        glow_o_1 = 0.05
        title_color = "#171717"
        accent_color = "#E50914"
        subtitle_color = "#5C5C5C"
        cap_bg = "#E5091416"
        cap_stroke = "#E50914AA"
        cap_text = "#A4070F"
        stroke_color = "#0000001E"
        halo_color = "#E50914"
        halo_opacity = 0.22

    # Screenshot display: width 494, native ratio 1280/1400 = 0.9143
    sw, sh = 494, 540  # both themes use the cropped-to-1400 source

    # Title
    title_y = 60
    sub_y = 100

    # Centred pair: 494 + gap 42 + 494 = 1030 → padding 125
    gap = 42
    total_w = sw * 2 + gap
    pad_x = (1280 - total_w) // 2
    y_shot = 124

    # Halo behind each screenshot (offset down-right slightly so it reads
    # like a soft glow lifting the screenshot off the bg)
    def halo(cx, cy, rx, ry):
        return f'''
    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{halo_color}" opacity="{halo_opacity}"/>'''

    # Sparkle decoration top-right of title
    sparkles = sparkle_cluster(890, 36, color=accent_color, scale=1.15)

    # Caption chip generator — placed below each screenshot.
    # Wider, taller, solid accent fill — high-contrast read at 2 second glance.
    def cap(cx, cy, label, icon):
        cw = 320
        ch = 54
        return f'''
    <g transform="translate({cx - cw // 2}, {cy})">
      <rect width="{cw}" height="{ch}" rx="{ch // 2}" fill="{accent_color}"/>
      <g transform="translate(22, 15)">{icon}</g>
      <text x="60" y="35" font-family="Inter, sans-serif" font-weight="700" font-size="18" fill="#FFFFFF" letter-spacing="0.2">{label}</text>
    </g>'''

    # Icons rendered WHITE-on-accent (chip is solid accent now)
    list_icon = '<g fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"><circle cx="3" cy="4" r="1.6" fill="#FFFFFF"/><line x1="10" y1="4" x2="24" y2="4"/><circle cx="3" cy="12" r="1.6" fill="#FFFFFF"/><line x1="10" y1="12" x2="24" y2="12"/><circle cx="3" cy="20" r="1.6" fill="#FFFFFF"/><line x1="10" y1="20" x2="24" y2="20"/></g>'
    chat_icon = '<g fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M2 4 H24 V17 H11 L4 23 V17 H2 Z" fill="#FFFFFF" fill-opacity="0.25" stroke="#FFFFFF"/></g>'

    # Centres of each screenshot for caption alignment
    cx_left = pad_x + sw // 2
    cx_right = pad_x + sw + gap + sw // 2
    cap_y = y_shot + sh + 26  # leaves 6px gap below screenshot, chip ends at 744

    # Straight side-by-side — better readability for hero shot
    s_left = tilted_screenshot(img_left_b64, pad_x, y_shot, sw, sh, 0, ratio=sw / sh, stroke=stroke_color, radius=20)
    s_right = tilted_screenshot(img_right_b64, pad_x + sw + gap, y_shot, sw, sh, 0, ratio=sw / sh, stroke=stroke_color, radius=20)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{bg_grad_stops}</linearGradient>
    <radialGradient id="glowBgL" cx="15%" cy="20%" r="50%">
      <stop offset="0%" stop-color="{glow_color}" stop-opacity="{glow_o_0 * 0.6}"/>
      <stop offset="70%" stop-color="{glow_color}" stop-opacity="{glow_o_1}"/>
      <stop offset="100%" stop-color="{glow_color}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowBgR" cx="88%" cy="80%" r="45%">
      <stop offset="0%" stop-color="{glow_color}" stop-opacity="{glow_o_0 * 0.5}"/>
      <stop offset="70%" stop-color="{glow_color}" stop-opacity="{glow_o_1}"/>
      <stop offset="100%" stop-color="{glow_color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#glowBgL)"/>
  <rect width="1280" height="800" fill="url(#glowBgR)"/>

  <!-- Halos behind each screenshot to lift them off the bg -->
  {halo(cx_left, y_shot + sh // 2 + 15, 330, 220)}
  {halo(cx_right, y_shot + sh // 2 + 15, 330, 220)}

  <!-- Title -->
  <text x="640" y="{title_y}" text-anchor="middle" font-family="Goldman, 'Arial Black', sans-serif" font-size="62" fill="{title_color}" letter-spacing="-1.5">YouTube <tspan fill="{accent_color}">Summarizer</tspan></text>
  <text x="640" y="{sub_y}" text-anchor="middle" font-family="Inter, 'Helvetica Neue', sans-serif" font-size="20" font-weight="500" fill="{subtitle_color}" letter-spacing="0.2">Understand any YouTube video in seconds — without watching it.</text>

  {sparkles}

  <!-- Screenshots -->
  {s_left}
  {s_right}

  <!-- Captions under each screenshot -->
  {cap(cx_left, cap_y, "Timestamped summary", list_icon)}
  {cap(cx_right, cap_y, "Ask anything about it", chat_icon)}
</svg>'''
    return svg


# --- Variant A3 light: A2 layout + cinematic dim + warm spotlight ----------

def variant_a3_light(img_left_b64, img_right_b64):
    """A2 light layout, but each screenshot has cinematic dim+spotlight:
      • left ~55% darkened by linear gradient (YouTube zone fades to shadow)
      • right ~45% lit by warm red radial spotlight (widget glows subtly)

    Result: eye is funneled to the widget without losing the YouTube
    context.
    """
    accent_color = "#E50914"
    title_color = "#171717"
    subtitle_color = "#5C5C5C"
    halo_color = "#E50914"

    sw, sh = 494, 540
    gap = 42
    pad_x = (1280 - sw * 2 - gap) // 2
    y_shot = 124

    cx_left = pad_x + sw // 2
    cx_right = pad_x + sw + gap + sw // 2
    cap_y = y_shot + sh + 26

    sparkles = sparkle_cluster(890, 36, color=accent_color, scale=1.15)

    list_icon = '<g fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"><circle cx="3" cy="4" r="1.6" fill="#FFFFFF"/><line x1="10" y1="4" x2="24" y2="4"/><circle cx="3" cy="12" r="1.6" fill="#FFFFFF"/><line x1="10" y1="12" x2="24" y2="12"/><circle cx="3" cy="20" r="1.6" fill="#FFFFFF"/><line x1="10" y1="20" x2="24" y2="20"/></g>'
    chat_icon = '<g fill="#FFFFFF" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M2 4 H24 V17 H11 L4 23 V17 H2 Z" fill="#FFFFFF" fill-opacity="0.25" stroke="#FFFFFF"/></g>'

    def cap(cx, cy_, label, icon):
        cw, ch = 320, 54
        return f'''
    <g transform="translate({cx - cw // 2}, {cy_})">
      <rect width="{cw}" height="{ch}" rx="{ch // 2}" fill="{accent_color}"/>
      <g transform="translate(22, 15)">{icon}</g>
      <text x="60" y="35" font-family="Inter, sans-serif" font-weight="700" font-size="18" fill="#FFFFFF" letter-spacing="0.2">{label}</text>
    </g>'''

    s_left = tilted_screenshot_dim(img_left_b64, pad_x, y_shot, sw, sh,
                                   suffix="L")
    s_right = tilted_screenshot_dim(img_right_b64, pad_x + sw + gap, y_shot,
                                    sw, sh, suffix="R")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"  stop-color="#FFF7F4"/>
      <stop offset="50%" stop-color="#FAF0EE"/>
      <stop offset="100%" stop-color="#F4E6E6"/>
    </linearGradient>
    <radialGradient id="glowBgL" cx="15%" cy="20%" r="50%">
      <stop offset="0%"   stop-color="{accent_color}" stop-opacity="0.18"/>
      <stop offset="70%"  stop-color="{accent_color}" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowBgR" cx="88%" cy="80%" r="45%">
      <stop offset="0%"   stop-color="{accent_color}" stop-opacity="0.14"/>
      <stop offset="70%"  stop-color="{accent_color}" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
    <!-- Asymmetric dim — left side only (YouTube video zone).
         Gentler than before, ends well before the widget panel boundary
         (widget starts ~36% of the screenshot width). -->
    <linearGradient id="a3_dim" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="#0E1422" stop-opacity="0.22"/>
      <stop offset="20%" stop-color="#0E1422" stop-opacity="0.16"/>
      <stop offset="34%" stop-color="#0E1422" stop-opacity="0.05"/>
      <stop offset="42%" stop-color="#0E1422" stop-opacity="0"/>
    </linearGradient>
    <!-- Bottom dim — light vertical fade, kicks in at the bottom 30%
         where the recommendations / video thumbnails distract the eye. -->
    <linearGradient id="a3_dim_btm" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#0E1422" stop-opacity="0"/>
      <stop offset="65%"  stop-color="#0E1422" stop-opacity="0"/>
      <stop offset="82%"  stop-color="#0E1422" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#0E1422" stop-opacity="0.20"/>
    </linearGradient>
  </defs>

  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#glowBgL)"/>
  <rect width="1280" height="800" fill="url(#glowBgR)"/>

  <!-- Halos behind each screenshot -->
  <ellipse cx="{cx_left}" cy="{y_shot + sh // 2 + 15}" rx="330" ry="220" fill="{halo_color}" opacity="0.20"/>
  <ellipse cx="{cx_right}" cy="{y_shot + sh // 2 + 15}" rx="330" ry="220" fill="{halo_color}" opacity="0.20"/>

  <!-- Title -->
  <text x="640" y="60" text-anchor="middle" font-family="Goldman, 'Arial Black', sans-serif" font-size="62" fill="{title_color}" letter-spacing="-1.5">YouTube <tspan fill="{accent_color}">Summarizer</tspan></text>
  <text x="640" y="100" text-anchor="middle" font-family="Inter, 'Helvetica Neue', sans-serif" font-size="20" font-weight="500" fill="{subtitle_color}" letter-spacing="0.2">Understand any YouTube video in seconds — without watching it.</text>

  {sparkles}

  <!-- Screenshots with cinematic dim + spotlight -->
  {s_left}
  {s_right}

  <!-- Captions under each screenshot -->
  {cap(cx_left, cap_y, "Timestamped summary", list_icon)}
  {cap(cx_right, cap_y, "Ask anything about it", chat_icon)}
</svg>'''
    return svg


# --- one-screenshot dark variants (A4/A5/A6) -------------------------------
#
# Goal: at 280×175 thumbnail size in the Chrome Web Store, the viewer must
# see in 1 second that this is YouTube + a side-panel summary tool. So we
# show only the timestamped-summary screenshot, oversized, with the widget
# clearly the focal point. The YouTube video pane stays partly visible
# (left edge) so the context reads instantly.

# Shared dark-theme palette for A4/A5/A6 — re-uses A2 dark values exactly,
# so the three new variants slot in with the existing brand system.
_DARK = dict(
    bg_grad_stops='<stop offset="0%" stop-color="#1A0606"/><stop offset="60%" stop-color="#0B0B0B"/><stop offset="100%" stop-color="#050505"/>',
    glow_color="#FF2323",
    title_color="#F5F5F5",
    accent_color="#FF2D2D",
    subtitle_color="#C8C8C8",
    stroke_color="#FFFFFF22",
)


def _shot_cropped(img_b64, x, y, w, h, suffix, align="xMaxYMid",
                  stroke="#FFFFFF22", radius=20, rotate=0,
                  widget_spotlight=True, video_dim=True):
    """Screenshot card with optional crop alignment + widget spotlight.

    align="xMaxYMid" keeps the right side of the source pinned (the widget
    column) and crops the YouTube video pane on the left — that lets us
    show the widget at full width while keeping just enough of the video
    column for instant YouTube recognition.

    widget_spotlight: warm radial highlight over the right ~60% (the
    widget). video_dim: gentle left-side darkening so the eye lands on
    the widget first.
    """
    dx, dy = 8, 18
    rot = f' rotate({rotate})' if rotate else ''
    spot = ''
    dim = ''
    if widget_spotlight:
        spot = f'<rect width="{w}" height="{h}" fill="url(#wspot_{suffix})"/>'
    if video_dim:
        dim = f'<rect width="{w}" height="{h}" fill="url(#vdim_{suffix})"/>'
    return f'''
    <g transform="translate({x},{y}){rot}">
      <rect x="{dx}" y="{dy}" width="{w}" height="{h}" rx="{radius}" fill="#000000" fill-opacity="0.45"/>
      <rect x="0" y="0" width="{w}" height="{h}" rx="{radius}" fill="#0A0A0A"/>
      <defs>
        <clipPath id="clip_{suffix}">
          <rect width="{w}" height="{h}" rx="{radius}"/>
        </clipPath>
        <radialGradient id="wspot_{suffix}" cx="78%" cy="38%" r="55%">
          <stop offset="0%"   stop-color="#FF2D2D" stop-opacity="0.18"/>
          <stop offset="55%"  stop-color="#FF2D2D" stop-opacity="0.04"/>
          <stop offset="100%" stop-color="#FF2D2D" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="vdim_{suffix}" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%"  stop-color="#000000" stop-opacity="0.25"/>
          <stop offset="20%" stop-color="#000000" stop-opacity="0.12"/>
          <stop offset="40%" stop-color="#000000" stop-opacity="0.03"/>
          <stop offset="52%" stop-color="#000000" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <g clip-path="url(#clip_{suffix})">
        <image href="data:image/png;base64,{img_b64}"
               x="0" y="0" width="{w}" height="{h}"
               preserveAspectRatio="{align} slice"/>
        {dim}
        {spot}
      </g>
      <rect x="0" y="0" width="{w}" height="{h}" rx="{radius}"
            fill="none" stroke="{stroke}" stroke-width="1.5"/>
    </g>'''


def _yt_logo(x, y, scale=1.0, color="#FF0000"):
    """Compact YouTube play-button logo — pure SVG, no font dependency."""
    return f'''
    <g transform="translate({x},{y}) scale({scale})">
      <rect width="44" height="30" rx="8" fill="{color}"/>
      <path d="M17 9 L31 15 L17 21 Z" fill="#FFFFFF"/>
    </g>'''


def _feature_chip(x, y, label, accent):
    """Solid-accent feature chip with list-bullet icon."""
    cw, ch = 320, 56
    icon = '<g fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"><circle cx="3" cy="4" r="1.6" fill="#FFFFFF"/><line x1="10" y1="4" x2="24" y2="4"/><circle cx="3" cy="12" r="1.6" fill="#FFFFFF"/><line x1="10" y1="12" x2="24" y2="12"/><circle cx="3" cy="20" r="1.6" fill="#FFFFFF"/><line x1="10" y1="20" x2="24" y2="20"/></g>'
    return f'''
    <g transform="translate({x},{y})">
      <rect width="{cw}" height="{ch}" rx="{ch//2}" fill="{accent}"/>
      <g transform="translate(24,16)">{icon}</g>
      <text x="62" y="36" font-family="Inter, sans-serif" font-weight="700" font-size="19" fill="#FFFFFF" letter-spacing="0.2">{label}</text>
    </g>'''


# --- Variant A4: hero screenshot left, text right --------------------------

def variant_a4_dark(img_b64):
    """1280x800 — single large screenshot on the left (cropped to keep the
    widget pinned right), big text block on the right.

    Reads at thumbnail: massive widget panel + sliver of YouTube video on
    the far left for context. The right-column text states what the
    product does in 3 lines max.
    """
    d = _DARK
    sw, sh = 660, 720
    sx, sy = 40, 40

    shot = _shot_cropped(img_b64, sx, sy, sw, sh, suffix="A4",
                         align="xMaxYMid", stroke=d["stroke_color"],
                         radius=22)

    # Right column starts at x=750
    tx = 740
    title_y = 200
    sub_y = 348
    chip_y = 460

    yt = _yt_logo(tx, 120, scale=1.1)
    chip = _feature_chip(tx, chip_y, "Timestamped summary", d["accent_color"])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{d["bg_grad_stops"]}</linearGradient>
    <radialGradient id="glowL" cx="20%" cy="50%" r="55%">
      <stop offset="0%" stop-color="{d["glow_color"]}" stop-opacity="0.50"/>
      <stop offset="60%" stop-color="{d["glow_color"]}" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="{d["glow_color"]}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowR" cx="90%" cy="80%" r="50%">
      <stop offset="0%" stop-color="{d["glow_color"]}" stop-opacity="0.32"/>
      <stop offset="70%" stop-color="{d["glow_color"]}" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="{d["glow_color"]}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#glowL)"/>
  <rect width="1280" height="800" fill="url(#glowR)"/>

  <!-- Halo behind the screenshot (focuses eye on widget side) -->
  <ellipse cx="{sx + sw - 140}" cy="{sy + sh//2}" rx="320" ry="280"
           fill="{d["accent_color"]}" opacity="0.32"/>

  {shot}

  <!-- Right column: YT logo + title + subtitle + chip -->
  {yt}
  <text x="{tx + 56}" y="146" font-family="Inter, sans-serif" font-weight="600" font-size="18" fill="{d["subtitle_color"]}" letter-spacing="0.4">FOR YOUTUBE</text>

  <text x="{tx}" y="{title_y}" font-family="Goldman, 'Arial Black', sans-serif" font-size="72" fill="{d["title_color"]}" letter-spacing="-1.5">YouTube</text>
  <text x="{tx}" y="{title_y + 70}" font-family="Goldman, 'Arial Black', sans-serif" font-size="72" fill="{d["accent_color"]}" letter-spacing="-1.5">Summarizer</text>

  <text x="{tx}" y="{sub_y}" font-family="Inter, sans-serif" font-size="22" font-weight="500" fill="{d["subtitle_color"]}" letter-spacing="0.2">Get an AI-generated, timestamped</text>
  <text x="{tx}" y="{sub_y + 30}" font-family="Inter, sans-serif" font-size="22" font-weight="500" fill="{d["subtitle_color"]}" letter-spacing="0.2">summary of any video — in seconds.</text>

  {chip}

  <text x="{tx}" y="{chip_y + 100}" font-family="Inter, sans-serif" font-size="15" font-weight="500" fill="#888888" letter-spacing="0.3">Works in any language · Any length</text>
</svg>'''


# --- Variant A5: tilted hero, centered -------------------------------------

def variant_a5_dark(img_b64):
    """1280x800 — single tilted screenshot centered as hero. Title above,
    chip below. Dramatic spotlight on the widget. The slight tilt + halo
    sells "product shot" energy.
    """
    d = _DARK
    sw, sh = 880, 540
    sx = (1280 - sw) // 2
    sy = 130

    shot = _shot_cropped(img_b64, sx, sy, sw, sh, suffix="A5",
                         align="xMaxYMid", stroke=d["stroke_color"],
                         radius=22, rotate=-2)

    chip_y = sy + sh + 28
    chip = _feature_chip((1280 - 320) // 2, chip_y,
                         "Timestamped summary", d["accent_color"])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{d["bg_grad_stops"]}</linearGradient>
    <radialGradient id="glowC" cx="50%" cy="55%" r="60%">
      <stop offset="0%" stop-color="{d["glow_color"]}" stop-opacity="0.45"/>
      <stop offset="55%" stop-color="{d["glow_color"]}" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="{d["glow_color"]}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#glowC)"/>

  <!-- Title -->
  <text x="640" y="76" text-anchor="middle" font-family="Goldman, 'Arial Black', sans-serif" font-size="56" fill="{d["title_color"]}" letter-spacing="-1.3">YouTube <tspan fill="{d["accent_color"]}">Summarizer</tspan></text>
  <text x="640" y="116" text-anchor="middle" font-family="Inter, sans-serif" font-size="19" font-weight="500" fill="{d["subtitle_color"]}" letter-spacing="0.2">Get a timestamped summary of any video — without watching it.</text>

  <!-- Halo behind tilted screenshot -->
  <ellipse cx="{sx + sw - 200}" cy="{sy + sh//2 + 20}" rx="420" ry="280"
           fill="{d["accent_color"]}" opacity="0.30"/>

  {shot}

  {chip}
</svg>'''


# --- Variant A6: browser-mockup frame --------------------------------------

def variant_a6_dark(img_b64):
    """1280x800 — Chrome-style browser frame with a youtube.com URL pill,
    the screenshot fills the content area. Maximum YouTube recognition
    because the frame literally says "you are on youtube.com".

    Title sits on top of the dark canvas above the browser; chip below.
    """
    d = _DARK
    # Browser frame
    bx, by, bw, bh = 60, 130, 1160, 560
    tab_h = 38
    url_h = 40

    # Content area inside frame
    cx_, cy_ = bx, by + tab_h + url_h
    cw_, ch_ = bw, bh - tab_h - url_h

    # Screenshot fills content area, anchored right (widget visible in full)
    shot = _shot_cropped(img_b64, cx_, cy_, cw_, ch_, suffix="A6",
                         align="xMaxYMid", stroke="#00000000",
                         radius=0, widget_spotlight=True, video_dim=False)

    chip = _feature_chip((1280 - 320) // 2, by + bh + 22,
                         "Timestamped summary", d["accent_color"])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{d["bg_grad_stops"]}</linearGradient>
    <radialGradient id="glowTop" cx="50%" cy="0%" r="55%">
      <stop offset="0%" stop-color="{d["glow_color"]}" stop-opacity="0.40"/>
      <stop offset="60%" stop-color="{d["glow_color"]}" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="{d["glow_color"]}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowBR" cx="85%" cy="85%" r="50%">
      <stop offset="0%" stop-color="{d["glow_color"]}" stop-opacity="0.28"/>
      <stop offset="70%" stop-color="{d["glow_color"]}" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="{d["glow_color"]}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="browserClip">
      <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="16"/>
    </clipPath>
  </defs>
  <rect width="1280" height="800" fill="url(#bg)"/>
  <rect width="1280" height="800" fill="url(#glowTop)"/>
  <rect width="1280" height="800" fill="url(#glowBR)"/>

  <!-- Title -->
  <text x="640" y="76" text-anchor="middle" font-family="Goldman, 'Arial Black', sans-serif" font-size="52" fill="{d["title_color"]}" letter-spacing="-1.3">YouTube <tspan fill="{d["accent_color"]}">Summarizer</tspan></text>
  <text x="640" y="108" text-anchor="middle" font-family="Inter, sans-serif" font-size="18" font-weight="500" fill="{d["subtitle_color"]}" letter-spacing="0.2">A side-panel summary for every video you watch.</text>

  <!-- Browser shell -->
  <g>
    <!-- shadow -->
    <rect x="{bx + 6}" y="{by + 14}" width="{bw}" height="{bh}" rx="16" fill="#000000" fill-opacity="0.5"/>
    <!-- frame body -->
    <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="16" fill="#1F1F1F" stroke="#2A2A2A" stroke-width="1"/>
    <g clip-path="url(#browserClip)">
      <!-- tab bar -->
      <rect x="{bx}" y="{by}" width="{bw}" height="{tab_h}" fill="#2A2A2A"/>
      <circle cx="{bx + 22}" cy="{by + tab_h//2}" r="6" fill="#FF5F57"/>
      <circle cx="{bx + 42}" cy="{by + tab_h//2}" r="6" fill="#FEBC2E"/>
      <circle cx="{bx + 62}" cy="{by + tab_h//2}" r="6" fill="#28C840"/>
      <!-- active tab pill -->
      <rect x="{bx + 96}" y="{by + 8}" width="240" height="{tab_h - 8}" rx="10" fill="#1F1F1F"/>
      <rect x="{bx + 108}" y="{by + 16}" width="14" height="14" rx="3" fill="#FF0000"/>
      <path d="M{bx + 113} {by + 21} L{bx + 119} {by + 23} L{bx + 113} {by + 25} Z" fill="#FFFFFF"/>
      <text x="{bx + 130}" y="{by + 27}" font-family="Inter, sans-serif" font-weight="600" font-size="12" fill="#E0E0E0">The skill of self-confidence | Dr. Iv...</text>

      <!-- url bar -->
      <rect x="{bx}" y="{by + tab_h}" width="{bw}" height="{url_h}" fill="#1F1F1F"/>
      <rect x="{bx + 16}" y="{by + tab_h + 6}" width="{bw - 32}" height="{url_h - 12}" rx="14" fill="#101010" stroke="#2E2E2E" stroke-width="1"/>
      <g transform="translate({bx + 30}, {by + tab_h + 14})">
        <path d="M0 4 a4 4 0 0 1 8 0 v4 H0 Z" fill="none" stroke="#7BD88F" stroke-width="1.6"/>
        <rect x="-2" y="7" width="12" height="9" rx="2" fill="none" stroke="#7BD88F" stroke-width="1.6"/>
      </g>
      <text x="{bx + 56}" y="{by + tab_h + url_h//2 + 5}" font-family="Inter, sans-serif" font-size="13" font-weight="500" fill="#C8C8C8" letter-spacing="0.3">youtube.com/watch?v=… <tspan fill="#666666">— enhanced by Summarizer</tspan></text>
    </g>

    <!-- screenshot inside content area -->
    {shot}
  </g>

  {chip}
</svg>'''


# --- write files ---------------------------------------------------------

out = {
    "cover_variantA_dark.svg":  variant_a(YT1, YT2, "dark"),
    "cover_variantA_light.svg": variant_a(YT3, YT4, "light"),
    "cover_variantB_dark.svg":  variant_b(YT1, YT2, "dark"),
    "cover_variantB_light.svg": variant_b(YT3, YT4, "light"),
    "cover_variantA2_dark.svg":  variant_a2(YT1C, YT2C, "dark"),
    "cover_variantA2_light.svg": variant_a2(YT3, YT4, "light"),
    "cover_variantA3_light.svg": variant_a3_light(YT3, YT4),
    "cover_variantA4_dark.svg":  variant_a4_dark(YT1C),
    "cover_variantA5_dark.svg":  variant_a5_dark(YT1C),
    "cover_variantA6_dark.svg":  variant_a6_dark(YT1C),
}
for name, svg in out.items():
    path = os.path.join(ROOT, name)
    with open(path, "w") as f:
        f.write(svg)
    print(f"wrote {name}: {os.path.getsize(path)/1024:.0f} KB")
