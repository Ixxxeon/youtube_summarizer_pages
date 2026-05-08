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


# --- write files ---------------------------------------------------------

out = {
    "cover_variantA_dark.svg":  variant_a(YT1, YT2, "dark"),
    "cover_variantA_light.svg": variant_a(YT3, YT4, "light"),
    "cover_variantB_dark.svg":  variant_b(YT1, YT2, "dark"),
    "cover_variantB_light.svg": variant_b(YT3, YT4, "light"),
    "cover_variantA2_dark.svg":  variant_a2(YT1C, YT2C, "dark"),
    "cover_variantA2_light.svg": variant_a2(YT3, YT4, "light"),
    "cover_variantA3_light.svg": variant_a3_light(YT3, YT4),
}
for name, svg in out.items():
    path = os.path.join(ROOT, name)
    with open(path, "w") as f:
        f.write(svg)
    print(f"wrote {name}: {os.path.getsize(path)/1024:.0f} KB")
