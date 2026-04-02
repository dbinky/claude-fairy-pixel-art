#!/usr/bin/env python3
"""Fairy Frontier Pixel Art Generator.

Reads docs/plans/graphics-assets.md and generates all 163 PNG assets
into assets/images/ with cute 8-bit pixel art style.

Usage:
    source scripts/.venv/bin/activate
    python scripts/generate-art.py
"""

import os
import re
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------

# Game palette from spec
PALETTE = {
    # Fairy colors
    'rose':         '#E85D75',
    'rose_light':   '#FF9EAE',
    'rose_dark':    '#C44569',
    'lilypad':      '#5B9BD5',
    'lilypad_light':'#8EC0E8',
    'lilypad_dark': '#3A7BBF',
    'fern':         '#6B8E23',
    'fern_light':   '#8DB33A',
    'fern_dark':    '#4A6310',
    'mushroom':     '#9B59B6',
    'mushroom_light':'#BB84D0',
    'mushroom_dark':'#7D3F9B',

    # Resources
    'nectar':       '#D4A017',
    'nectar_light': '#F0C040',
    'nectar_dark':  '#A07010',
    'dewshine':     '#87CEEB',
    'dewshine_light':'#B0E0F0',
    'dewshine_dark':'#5BA0C8',
    'heartwood':    '#8B4513',
    'heartwood_light':'#A0603A',
    'heartwood_dark':'#5C2E0A',
    'shimmer':      '#DA70D6',
    'shimmer_light':'#EE99EA',
    'shimmer_dark': '#A850A5',
    'coins':        '#FFD700',
    'coins_light':  '#FFE84D',
    'coins_dark':   '#C8A800',

    # UI / Environment
    'bg':           '#F5F0E1',
    'forest':       '#2D5016',
    'forest_light': '#4A7828',
    'forest_dark':  '#1A3008',
    'magic':        '#7B2D8E',
    'magic_light':  '#A050B8',
    'magic_dark':   '#551A68',

    # Common
    'outline':      '#5C3A4E',
    'outline_light':'#7A5A6E',
    'skin':         '#FFDAB9',
    'skin_light':   '#FFE8D0',
    'skin_dark':    '#E8A87C',
    'blush':        '#FFB6C1',
    'white':        '#FFFFFF',
    'cream':        '#F5F0E1',
    'eye_blue':     '#87CEEB',
    'eye_dark':     '#2A1F3D',
    'gold':         '#FFD700',
    'gold_light':   '#FFE84D',
    'gold_dark':    '#C8A800',
    'brown':        '#8B4513',
    'brown_light':  '#A0603A',
    'brown_dark':   '#5C2E0A',
    'gray':         '#9E9E9E',
    'gray_light':   '#C0C0C0',
    'gray_dark':    '#6E6E6E',
    'green_grass':  '#4CAF50',
    'green_light':  '#6ECF72',
    'green_dark':   '#2E7D32',
    'water_blue':   '#4FC3F7',
    'water_light':  '#80D8FF',
    'water_dark':   '#0288D1',
    'red':          '#FF004D',
    'red_dark':     '#CC003E',
    'orange':       '#FFA300',
    'yellow':       '#FFEC27',
    'black':        '#000000',
    'transparent':  None,
}

def hex_to_rgba(hex_color, alpha=255):
    """Convert hex color string to RGBA tuple."""
    if hex_color is None:
        return (0, 0, 0, 0)
    h = hex_color.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)

def c(name, alpha=255):
    """Get RGBA color tuple by palette name."""
    return hex_to_rgba(PALETTE.get(name), alpha)

# Fairy-specific color sets
FAIRY_COLORS = {
    'rose': {
        'primary': 'rose', 'light': 'rose_light', 'dark': 'rose_dark',
        'hair': 'rose', 'hair_light': 'rose_light',
        'wing': 'rose_light', 'wing_dark': 'rose',
        'crown_accent': 'gold', 'crown_green': 'forest',
    },
    'lilypad': {
        'primary': 'lilypad', 'light': 'lilypad_light', 'dark': 'lilypad_dark',
        'hair': 'lilypad', 'hair_light': 'lilypad_light',
        'wing': 'lilypad_light', 'wing_dark': 'lilypad',
        'crown_accent': 'lilypad_light', 'crown_green': 'forest',
    },
    'fern': {
        'primary': 'fern', 'light': 'fern_light', 'dark': 'fern_dark',
        'hair': 'fern', 'hair_light': 'fern_light',
        'wing': 'fern_light', 'wing_dark': 'fern',
        'crown_accent': 'brown', 'crown_green': 'fern_dark',
    },
    'mushroom': {
        'primary': 'mushroom', 'light': 'mushroom_light', 'dark': 'mushroom_dark',
        'hair': 'mushroom', 'hair_light': 'mushroom_light',
        'wing': 'mushroom_light', 'wing_dark': 'mushroom',
        'crown_accent': 'white', 'crown_green': 'mushroom_dark',
    },
}

# ---------------------------------------------------------------------------
# Drawing Helpers
# ---------------------------------------------------------------------------

def new_image(w, h):
    """Create a new RGBA image with transparent background."""
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))

def px(img, x, y, color_name, alpha=255):
    """Set a single pixel by palette color name."""
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c(color_name, alpha))

def px_rgba(img, x, y, rgba):
    """Set a single pixel by RGBA tuple."""
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), rgba)

def fill_rect(img, x, y, w, h, color_name, alpha=255):
    """Fill a rectangle with a palette color."""
    rgba = c(color_name, alpha)
    for dy in range(h):
        for dx in range(w):
            px_rgba(img, x + dx, y + dy, rgba)

def draw_ellipse(img, cx, cy, rx, ry, color_name, alpha=255):
    """Draw a filled ellipse."""
    rgba = c(color_name, alpha)
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            if (dx * dx) / max(rx * rx, 1) + (dy * dy) / max(ry * ry, 1) <= 1.0:
                px_rgba(img, cx + dx, cy + dy, rgba)

def draw_circle(img, cx, cy, r, color_name, alpha=255):
    """Draw a filled circle."""
    draw_ellipse(img, cx, cy, r, r, color_name, alpha)

def outline_rect(img, x, y, w, h, color_name, alpha=255):
    """Draw a rectangle outline (1px border)."""
    rgba = c(color_name, alpha)
    for dx in range(w):
        px_rgba(img, x + dx, y, rgba)
        px_rgba(img, x + dx, y + h - 1, rgba)
    for dy in range(h):
        px_rgba(img, x, y + dy, rgba)
        px_rgba(img, x + w - 1, y + dy, rgba)

def outline_ellipse(img, cx, cy, rx, ry, color_name, alpha=255):
    """Draw an ellipse outline."""
    rgba = c(color_name, alpha)
    for angle in range(360):
        rad = math.radians(angle)
        x = int(cx + rx * math.cos(rad))
        y = int(cy + ry * math.sin(rad))
        px_rgba(img, x, y, rgba)

def draw_line(img, x0, y0, x1, y1, color_name, alpha=255):
    """Draw a line using Bresenham's algorithm."""
    rgba = c(color_name, alpha)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        px_rgba(img, x0, y0, rgba)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def draw_rounded_rect(img, x, y, w, h, color_name, alpha=255):
    """Draw a filled rectangle with 1px rounded corners."""
    fill_rect(img, x + 1, y, w - 2, h, color_name, alpha)
    fill_rect(img, x, y + 1, w, h - 2, color_name, alpha)

def draw_dither(img, x, y, w, h, color1, color2, alpha=255):
    """Fill area with checkerboard dither pattern."""
    for dy in range(h):
        for dx in range(w):
            cn = color1 if (dx + dy) % 2 == 0 else color2
            px(img, x + dx, y + dy, cn, alpha)

def scatter_pixels(img, x, y, w, h, color_name, density=0.15, seed=None):
    """Scatter random pixels in an area."""
    rng = random.Random(seed)
    for dy in range(h):
        for dx in range(w):
            if rng.random() < density:
                px(img, x + dx, y + dy, color_name)

def draw_sparkle(img, cx, cy, color_name='white', size=3):
    """Draw a small 4-pointed sparkle."""
    px(img, cx, cy, color_name)
    for i in range(1, size):
        px(img, cx + i, cy, color_name)
        px(img, cx - i, cy, color_name)
        px(img, cx, cy + i, color_name)
        px(img, cx, cy - i, color_name)

def mirror_h(img):
    """Return a horizontally mirrored copy."""
    return img.transpose(Image.FLIP_LEFT_RIGHT)


# ---------------------------------------------------------------------------
# Composite Drawing Helpers (shared across generators)
# ---------------------------------------------------------------------------

def draw_cute_eyes(img, left_x, right_x, y, size=3):
    """Draw a pair of cute pixel art eyes with highlights."""
    for ex in [left_x, right_x]:
        # Eye white
        fill_rect(img, ex, y, size, size, 'white')
        # Pupil
        px(img, ex + size - 1, y + size - 1, 'eye_dark')
        px(img, ex + size - 2, y + size - 1, 'eye_dark')
        px(img, ex + size - 1, y + size - 2, 'eye_dark')
        # Highlight
        px(img, ex, y, 'eye_blue')

def draw_mouth_smile(img, cx, y):
    """Draw a tiny cute smile."""
    px(img, cx - 1, y, 'outline')
    px(img, cx, y + 1, 'outline')
    px(img, cx + 1, y, 'outline')

def draw_blush(img, left_x, right_x, y):
    """Draw pink blush marks on cheeks."""
    for bx in [left_x, right_x]:
        px(img, bx, y, 'blush', 180)
        px(img, bx + 1, y, 'blush', 180)

def draw_ghost_body(img, cx, cy, w, h, tint='white', outline_c='outline'):
    """Draw a cute ghost/blob body shape (round top, wavy bottom)."""
    # Round top half
    rx = w // 2
    ry = h // 3
    draw_ellipse(img, cx, cy - h // 6, rx, ry, tint)
    # Body rectangle
    fill_rect(img, cx - rx, cy - h // 6, w, h // 2, tint)
    # Wavy bottom
    bottom_y = cy - h // 6 + h // 2
    for dx in range(-rx, rx + 1):
        wave = int(1.5 * math.sin(dx * 1.2))
        px(img, cx + dx, bottom_y + wave, tint)
        px(img, cx + dx, bottom_y + wave + 1, tint)
    # Outline top
    outline_ellipse(img, cx, cy - h // 6, rx, ry, outline_c)

def draw_tree_small(img, x, y, green='green_grass', trunk='brown'):
    """Draw a small 2D pixel art tree for terrain tiles."""
    # Trunk
    fill_rect(img, x + 2, y + 5, 2, 4, trunk)
    fill_rect(img, x + 2, y + 8, 2, 2, 'brown_dark')
    # Canopy (layered circles)
    draw_circle(img, x + 3, y + 3, 3, green)
    draw_circle(img, x + 2, y + 2, 2, 'green_light')
    px(img, x + 1, y + 1, 'green_light')

def draw_flower_small(img, x, y, petal='rose_light', center='gold'):
    """Draw a tiny flower."""
    px(img, x, y, center)
    px(img, x - 1, y, petal)
    px(img, x + 1, y, petal)
    px(img, x, y - 1, petal)
    px(img, x, y + 1, petal)

def draw_rock(img, x, y, size=3):
    """Draw a small rock."""
    fill_rect(img, x, y, size, size - 1, 'gray')
    fill_rect(img, x, y + size - 2, size, 1, 'gray_dark')
    px(img, x, y, 'gray_light')

def draw_water_tile(img, x, y, w, h, seed=0):
    """Fill an area with water pattern."""
    rng = random.Random(seed)
    fill_rect(img, x, y, w, h, 'water_blue')
    for dy in range(h):
        for dx in range(w):
            if rng.random() < 0.1:
                px(img, x + dx, y + dy, 'water_light')
            elif rng.random() < 0.05:
                px(img, x + dx, y + dy, 'water_dark')


# ---------------------------------------------------------------------------
# PLACEHOLDER: Generator functions will be added in subsequent edits
# ---------------------------------------------------------------------------

# Each generate_* function takes (width, height, variant_info) and returns an Image.
# The asset router maps file paths to these functions.

GENERATORS = {}  # Populated by generator functions below


# ===================================================================
# 1. FAIRY CHARACTER GENERATORS
# ===================================================================

def _draw_fairy_base_portrait(img, fc):
    """Draw base fairy portrait (48x48) - shared body, face, then caller adds unique features."""
    W, H = img.size
    cx = W // 2

    # --- Wings (behind body) ---
    for side in [-1, 1]:
        wing_x = cx + side * 10
        # Upper wing
        draw_ellipse(img, wing_x, 20, 7, 10, fc['wing'])
        outline_ellipse(img, wing_x, 20, 7, 10, fc['wing_dark'])
        # Lower wing
        draw_ellipse(img, wing_x + side * 2, 30, 5, 7, fc['wing'])
        outline_ellipse(img, wing_x + side * 2, 30, 5, 7, fc['wing_dark'])
        # Wing veins
        draw_line(img, cx + side * 5, 18, wing_x, 13, fc['wing_dark'])
        draw_line(img, cx + side * 5, 22, wing_x + side * 3, 28, fc['wing_dark'])

    # --- Hair (behind face) ---
    draw_ellipse(img, cx, 14, 10, 11, fc['hair'])
    # Hair highlights
    draw_ellipse(img, cx - 3, 10, 4, 4, fc['hair_light'])

    # --- Head ---
    draw_ellipse(img, cx, 16, 8, 9, 'skin')
    # Forehead highlight
    fill_rect(img, cx - 4, 10, 8, 3, 'skin_light')

    # --- Face ---
    draw_cute_eyes(img, cx - 5, cx + 3, 15, size=3)
    draw_mouth_smile(img, cx, 22)
    draw_blush(img, cx - 6, cx + 4, 20)

    # --- Body/Dress ---
    # Neck
    fill_rect(img, cx - 2, 25, 4, 2, 'skin')
    # Dress top
    draw_ellipse(img, cx, 30, 6, 4, fc['primary'])
    # Dress skirt
    for dy in range(6):
        half_w = 6 + dy
        fill_rect(img, cx - half_w, 32 + dy, half_w * 2, 1, fc['primary'])
    # Dress highlight
    fill_rect(img, cx - 3, 29, 3, 4, fc['light'])

    # --- Arms ---
    fill_rect(img, cx - 8, 28, 2, 6, 'skin')
    fill_rect(img, cx + 6, 28, 2, 6, 'skin')

    # --- Tiny legs/feet ---
    fill_rect(img, cx - 4, 38, 2, 3, 'skin')
    fill_rect(img, cx + 2, 38, 2, 3, 'skin')
    # Shoes
    fill_rect(img, cx - 5, 40, 3, 2, fc['dark'])
    fill_rect(img, cx + 2, 40, 3, 2, fc['dark'])


def _draw_rose_crown(img, fc):
    """Draw rose fairy's flower crown."""
    cx = img.width // 2
    # Green leaf base
    fill_rect(img, cx - 7, 6, 14, 2, fc['crown_green'])
    # Gold accents
    for x in [cx - 5, cx - 1, cx + 3]:
        px(img, x, 5, fc['crown_accent'])
        px(img, x + 1, 5, fc['crown_accent'])
        px(img, x, 4, fc['crown_accent'])
    # Rose petals on crown
    draw_flower_small(img, cx - 3, 4, 'rose_light', 'gold')
    draw_flower_small(img, cx + 3, 4, 'rose_light', 'gold')
    px(img, cx, 3, 'rose')


def _draw_lilypad_hat(img, fc):
    """Draw lilypad fairy's lilypad hat."""
    cx = img.width // 2
    # Lilypad disc
    draw_ellipse(img, cx, 6, 8, 3, 'forest')
    draw_ellipse(img, cx, 6, 6, 2, 'forest_light')
    # V-notch in lilypad
    px(img, cx, 4, 'transparent')
    px(img, cx + 1, 5, 'transparent')
    # Little flower on hat
    px(img, cx - 2, 4, 'lilypad_light')
    px(img, cx - 3, 3, 'white')


def _draw_fern_crown(img, fc):
    """Draw fern fairy's twig crown."""
    cx = img.width // 2
    # Twigs
    draw_line(img, cx - 6, 7, cx - 3, 3, 'brown')
    draw_line(img, cx + 6, 7, cx + 3, 3, 'brown')
    draw_line(img, cx - 1, 7, cx, 2, 'brown')
    # Tiny leaves on twigs
    for x in [cx - 4, cx + 4, cx]:
        px(img, x - 1, 3, 'fern_light')
        px(img, x + 1, 3, 'fern_light')


def _draw_mushroom_cap(img, fc):
    """Draw mushroom fairy's mushroom cap hat."""
    cx = img.width // 2
    # Cap
    draw_ellipse(img, cx, 6, 9, 5, 'mushroom')
    draw_ellipse(img, cx, 5, 7, 3, 'mushroom_light')
    # Spots
    for sx, sy in [(cx - 4, 4), (cx + 3, 5), (cx, 3), (cx + 5, 6)]:
        px(img, sx, sy, 'white')


def gen_fairy(w, h, file_path, prompt):
    """Generate a fairy character asset."""
    fname = Path(file_path).stem  # e.g. 'rose_portrait', 'lilypad_walk_e'

    # Determine fairy type
    fairy_type = None
    for ft in ['rose', 'lilypad', 'fern', 'mushroom', 'unicorn']:
        if ft in fname:
            fairy_type = ft
            break
    if not fairy_type:
        fairy_type = 'rose'  # fallback

    # Determine asset variant
    if 'portrait' in fname:
        return _gen_fairy_portrait(w, h, fairy_type)
    elif 'icon' in fname:
        return _gen_fairy_icon(w, h, fairy_type)
    elif 'idle' in fname:
        return _gen_fairy_idle(w, h, fairy_type)
    elif 'walk' in fname:
        direction = fname.split('_')[-1]  # e, w, n, s
        return _gen_fairy_walk(w, h, fairy_type, direction)
    elif 'carry' in fname:
        return _gen_fairy_carry(w, h, fairy_type)
    else:
        return _gen_fairy_portrait(w, h, fairy_type)


def _get_fc(fairy_type):
    """Get fairy color dict, handling unicorn."""
    if fairy_type == 'unicorn':
        return {
            'primary': 'white', 'light': 'cream', 'dark': 'gray',
            'hair': 'shimmer_light', 'hair_light': 'shimmer',
            'wing': 'gold_light', 'wing_dark': 'gold',
            'crown_accent': 'shimmer', 'crown_green': 'gold',
        }
    return FAIRY_COLORS.get(fairy_type, FAIRY_COLORS['rose'])


def _gen_fairy_portrait(w, h, fairy_type):
    """Generate 48x48 front-facing fairy portrait."""
    img = new_image(w, h)
    fc = _get_fc(fairy_type)

    if fairy_type == 'unicorn':
        return _gen_unicorn_portrait(img)

    _draw_fairy_base_portrait(img, fc)

    # Add unique headpiece
    crown_funcs = {
        'rose': _draw_rose_crown,
        'lilypad': _draw_lilypad_hat,
        'fern': _draw_fern_crown,
        'mushroom': _draw_mushroom_cap,
    }
    crown_func = crown_funcs.get(fairy_type)
    if crown_func:
        crown_func(img, fc)

    return img


def _gen_unicorn_portrait(img):
    """Generate unicorn portrait."""
    W, H = img.size
    cx = W // 2

    # Body
    draw_ellipse(img, cx, 24, 12, 14, 'white')
    draw_ellipse(img, cx, 22, 10, 10, 'cream')

    # Head
    draw_ellipse(img, cx, 16, 9, 8, 'white')
    draw_ellipse(img, cx - 2, 14, 5, 5, 'cream')

    # Horn
    draw_line(img, cx, 8, cx, 2, 'gold')
    draw_line(img, cx - 1, 6, cx, 2, 'gold_light')
    px(img, cx, 1, 'gold_light')

    # Rainbow mane
    mane_colors = ['red', 'orange', 'yellow', 'green_grass', 'dewshine', 'mushroom']
    for i, mc in enumerate(mane_colors):
        y = 10 + i * 2
        fill_rect(img, cx + 6, y, 4, 2, mc)
        if i < 3:
            px(img, cx + 5, y, mc)

    # Eyes
    draw_cute_eyes(img, cx - 5, cx + 2, 15, size=3)
    draw_blush(img, cx - 6, cx + 4, 19)

    # Nose
    px(img, cx - 1, 20, 'blush')

    # Ears
    fill_rect(img, cx - 6, 9, 2, 4, 'white')
    fill_rect(img, cx + 5, 9, 2, 4, 'white')
    px(img, cx - 5, 10, 'blush')
    px(img, cx + 5, 10, 'blush')

    # Legs
    for lx in [cx - 6, cx - 2, cx + 2, cx + 5]:
        fill_rect(img, lx, 34, 2, 8, 'white')
        fill_rect(img, lx, 40, 2, 2, 'gray')

    # Sparkles
    draw_sparkle(img, 5, 5, 'gold_light', 2)
    draw_sparkle(img, W - 6, 8, 'shimmer_light', 2)

    return img


def _gen_fairy_icon(w, h, fairy_type):
    """Generate 24x24 tiny fairy head icon."""
    img = new_image(w, h)
    fc = _get_fc(fairy_type)
    cx, cy = w // 2, h // 2

    if fairy_type == 'unicorn':
        # Unicorn mini head
        draw_ellipse(img, cx, cy + 2, 7, 7, 'white')
        draw_cute_eyes(img, cx - 4, cx + 1, cy, size=2)
        draw_line(img, cx, cy - 5, cx, cy - 9, 'gold')
        px(img, cx, cy - 9, 'gold_light')
        # Rainbow streak
        for i, mc in enumerate(['red', 'orange', 'yellow']):
            px(img, cx + 5, cy - 2 + i, mc)
        return img

    # Fairy head
    draw_ellipse(img, cx, cy + 1, 7, 8, fc['hair'])
    draw_ellipse(img, cx, cy + 2, 6, 6, 'skin')
    # Hair highlight
    draw_ellipse(img, cx - 2, cy - 2, 3, 3, fc['hair_light'])
    # Eyes (tiny)
    px(img, cx - 3, cy + 1, 'eye_dark')
    px(img, cx + 2, cy + 1, 'eye_dark')
    px(img, cx - 3, cy, 'white')
    px(img, cx + 2, cy, 'white')
    # Blush
    px(img, cx - 4, cy + 2, 'blush')
    px(img, cx + 3, cy + 2, 'blush')
    # Smile
    px(img, cx - 1, cy + 4, 'outline')
    px(img, cx, cy + 4, 'outline')

    # Mini crown hint
    if fairy_type == 'rose':
        px(img, cx, cy - 6, 'gold')
        px(img, cx - 1, cy - 5, 'rose_light')
        px(img, cx + 1, cy - 5, 'rose_light')
    elif fairy_type == 'lilypad':
        fill_rect(img, cx - 3, cy - 6, 6, 2, 'forest')
    elif fairy_type == 'fern':
        px(img, cx, cy - 6, 'brown')
        px(img, cx - 2, cy - 5, 'fern_light')
        px(img, cx + 2, cy - 5, 'fern_light')
    elif fairy_type == 'mushroom':
        draw_ellipse(img, cx, cy - 5, 4, 2, 'mushroom')
        px(img, cx - 1, cy - 6, 'white')

    return img


def _gen_fairy_idle(w, h, fairy_type):
    """Generate 32x48 fairy idle pose (side view, hovering)."""
    img = new_image(w, h)
    fc = _get_fc(fairy_type)
    cx = w // 2

    if fairy_type == 'unicorn':
        # Simple unicorn side view
        draw_ellipse(img, cx, 28, 8, 10, 'white')
        draw_ellipse(img, cx - 4, 18, 6, 6, 'white')
        draw_line(img, cx - 6, 14, cx - 8, 8, 'gold')
        px(img, cx - 7, 16, 'eye_dark')
        for lx in [cx - 5, cx - 1, cx + 3, cx + 6]:
            fill_rect(img, lx, 36, 2, 6, 'white')
        return img

    # Wing behind
    draw_ellipse(img, cx + 6, 18, 5, 8, fc['wing'])
    outline_ellipse(img, cx + 6, 18, 5, 8, fc['wing_dark'])

    # Hair
    draw_ellipse(img, cx - 2, 14, 7, 8, fc['hair'])

    # Head
    draw_ellipse(img, cx - 2, 16, 6, 7, 'skin')

    # Eye (side view - one eye)
    fill_rect(img, cx - 4, 15, 2, 2, 'white')
    px(img, cx - 4, 16, 'eye_dark')
    px(img, cx - 4, 15, 'eye_blue')

    # Blush
    px(img, cx - 6, 18, 'blush')

    # Body/dress
    draw_ellipse(img, cx - 1, 28, 5, 6, fc['primary'])
    for dy in range(5):
        hw = 5 + dy
        fill_rect(img, cx - 1 - hw // 2, 30 + dy, hw, 1, fc['primary'])
    fill_rect(img, cx - 3, 26, 3, 3, fc['light'])

    # Arm
    fill_rect(img, cx - 6, 26, 2, 5, 'skin')

    # Legs
    fill_rect(img, cx - 3, 35, 2, 3, 'skin')
    fill_rect(img, cx + 1, 35, 2, 3, 'skin')

    # Hover sparkles
    draw_sparkle(img, cx - 2, 42, fc['light'], 1)
    draw_sparkle(img, cx + 2, 44, fc['light'], 1)

    return img


def _gen_fairy_walk(w, h, fairy_type, direction):
    """Generate 128x48 4-frame walk sprite sheet."""
    img = new_image(w, h)
    fc = _get_fc(fairy_type)
    frame_w = w // 4

    for frame_idx in range(4):
        fx = frame_idx * frame_w
        frame = new_image(frame_w, h)
        cx = frame_w // 2

        if fairy_type == 'unicorn':
            bob = [0, -1, 0, 1][frame_idx]
            draw_ellipse(frame, cx, 26 + bob, 8, 10, 'white')
            draw_ellipse(frame, cx - 4, 16 + bob, 6, 6, 'white')
            draw_line(frame, cx - 6, 12 + bob, cx - 8, 6 + bob, 'gold')
            px(frame, cx - 7, 14 + bob, 'eye_dark')
            leg_offsets = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            lo = leg_offsets[frame_idx]
            for i, lx in enumerate([cx - 5, cx - 1, cx + 3, cx + 6]):
                adj = lo[0] if i % 2 == 0 else lo[1]
                fill_rect(frame, lx, 34 + adj, 2, 6, 'white')
            img.paste(frame, (fx, 0), frame)
            continue

        bob = [0, -2, 0, 2][frame_idx]

        # Wing
        wing_side = 1 if direction in ['e', 's'] else -1
        if direction != 'n':
            wx = cx + wing_side * 6
            draw_ellipse(frame, wx, 16 + bob, 5, 7, fc['wing'])

        # Hair
        draw_ellipse(frame, cx, 12 + bob, 6, 7, fc['hair'])
        # Head
        draw_ellipse(frame, cx, 14 + bob, 5, 6, 'skin')

        if direction == 'n':
            # Back view - just hair, no face
            draw_ellipse(frame, cx, 12 + bob, 6, 8, fc['hair'])
        elif direction == 's':
            # Front view
            draw_cute_eyes(frame, cx - 4, cx + 1, 13 + bob, size=2)
            draw_mouth_smile(frame, cx, 18 + bob)
        else:
            # Side view - one eye
            eye_x = cx - 3 if direction == 'w' else cx + 1
            fill_rect(frame, eye_x, 13 + bob, 2, 2, 'white')
            px(frame, eye_x, 14 + bob, 'eye_dark')

        # Body
        draw_ellipse(frame, cx, 24 + bob, 4, 5, fc['primary'])
        for dy in range(4):
            hw = 4 + dy
            fill_rect(frame, cx - hw // 2, 26 + dy + bob, hw, 1, fc['primary'])

        # Walk animation legs
        leg_anim = [(-1, 1), (0, 0), (1, -1), (0, 0)]
        la = leg_anim[frame_idx]
        fill_rect(frame, cx - 3, 30 + bob + la[0], 2, 4, 'skin')
        fill_rect(frame, cx + 1, 30 + bob + la[1], 2, 4, 'skin')

        img.paste(frame, (fx, 0), frame)

    return img


def _gen_fairy_carry(w, h, fairy_type):
    """Generate 32x48 fairy carrying a sprite."""
    img = _gen_fairy_idle(w, h, fairy_type)
    # Add a small ghost sprite following
    draw_ghost_body(img, 24, 18, 8, 10, 'cream', 'outline_light')
    # Ghost eyes
    px(img, 22, 16, 'eye_dark')
    px(img, 25, 16, 'eye_dark')
    return img


# ===================================================================
# 2. SPRITE WORKER GENERATORS
# ===================================================================

def gen_sprite(w, h, file_path, prompt):
    """Generate a sprite (ghost worker) asset."""
    fname = Path(file_path).stem
    img = new_image(w, h)
    cx, cy = w // 2, h // 2

    # Determine sprite type/state
    if fname == 'following':
        return _gen_sprite_following(img, cx, cy)

    # Base ghost body color
    tint_map = {
        'nectar': ('nectar_light', 'nectar', 'nectar_dark'),
        'dewshine': ('dewshine_light', 'dewshine', 'dewshine_dark'),
        'heartwood': ('heartwood_light', 'heartwood', 'heartwood_dark'),
        'shimmer': ('shimmer_light', 'shimmer', 'shimmer_dark'),
        'working_nectar': ('nectar_light', 'nectar', 'nectar_dark'),
        'working_dewshine': ('dewshine_light', 'dewshine', 'dewshine_dark'),
        'working_heartwood': ('heartwood_light', 'heartwood', 'heartwood_dark'),
        'working_shimmer': ('shimmer_light', 'shimmer', 'shimmer_dark'),
    }
    colors = tint_map.get(fname, ('white', 'cream', 'gray_light'))
    body_c, mid_c, dark_c = colors

    # Draw ghost body
    _draw_ghost(img, cx, cy - 1, w, h, body_c, mid_c, dark_c)

    # Draw face
    _draw_ghost_face(img, cx, cy - 3, fname)

    # Draw accessory based on type
    _draw_sprite_accessory(img, cx, cy, fname)

    return img


def _draw_ghost(img, cx, cy, w, h, body_c, mid_c, dark_c):
    """Draw a cute ghost body shape."""
    rx = w // 3
    ry = h // 3

    # Main body (rounded top)
    draw_ellipse(img, cx, cy - 2, rx, ry, body_c)
    fill_rect(img, cx - rx, cy - 2, rx * 2 + 1, ry, body_c)

    # Highlight on top
    draw_ellipse(img, cx - 1, cy - 4, rx - 2, ry - 3, mid_c)

    # Wavy bottom edge
    bottom = cy - 2 + ry
    for dx in range(-rx, rx + 1):
        wave = int(1.5 * math.sin(dx * 0.8 + 1.0))
        for dy_off in range(3):
            py = bottom + wave - dy_off
            if 0 <= py < img.height:
                a = 255 - dy_off * 50
                px(img, cx + dx, py, body_c, max(a, 100))

    # Shadow at bottom
    for dx in range(-rx + 1, rx):
        wave = int(1.5 * math.sin(dx * 0.8 + 1.0))
        px(img, cx + dx, bottom + wave, dark_c, 150)

    # Outline
    outline_ellipse(img, cx, cy - 2, rx, ry, 'outline_light')


def _draw_ghost_face(img, cx, cy, sprite_type):
    """Draw ghost face appropriate for state."""
    if 'sleeping' in sprite_type:
        # Closed eyes (^_^)
        draw_line(img, cx - 4, cy, cx - 2, cy - 1, 'outline')
        draw_line(img, cx - 2, cy - 1, cx - 1, cy, 'outline')
        draw_line(img, cx + 1, cy, cx + 3, cy - 1, 'outline')
        draw_line(img, cx + 3, cy - 1, cx + 4, cy, 'outline')
        # Zzz
        for i, (zx, zy) in enumerate([(cx + 5, cy - 6), (cx + 7, cy - 9), (cx + 9, cy - 12)]):
            sz = 3 - i
            if sz > 0:
                fill_rect(img, zx, zy, sz, 1, 'dewshine')
                px(img, zx + sz - 1, zy + 1, 'dewshine')
                fill_rect(img, zx, zy + 2, sz, 1, 'dewshine')
        return

    if 'working' in sprite_type:
        # Determined face (> <)
        px(img, cx - 3, cy, 'outline')
        px(img, cx - 4, cy - 1, 'outline')
        px(img, cx - 4, cy + 1, 'outline')
        px(img, cx + 3, cy, 'outline')
        px(img, cx + 4, cy - 1, 'outline')
        px(img, cx + 4, cy + 1, 'outline')
        px(img, cx, cy + 2, 'outline')  # mouth
        return

    # Default cute eyes
    px(img, cx - 3, cy, 'eye_dark')
    px(img, cx - 3, cy - 1, 'white')
    px(img, cx + 2, cy, 'eye_dark')
    px(img, cx + 2, cy - 1, 'white')
    # Smile
    px(img, cx - 1, cy + 2, 'outline')
    px(img, cx, cy + 3, 'outline')
    px(img, cx + 1, cy + 2, 'outline')


def _draw_sprite_accessory(img, cx, cy, sprite_type):
    """Draw tool/accessory for sprite type."""
    if sprite_type == 'nectar':
        # Tiny golden pollen baskets
        fill_rect(img, cx - 6, cy - 2, 2, 3, 'gold')
        fill_rect(img, cx + 5, cy - 2, 2, 3, 'gold')
        # Flower antennae
        draw_line(img, cx - 2, cy - 7, cx - 4, cy - 10, 'outline_light')
        draw_line(img, cx + 2, cy - 7, cx + 4, cy - 10, 'outline_light')
        draw_flower_small(img, cx - 4, cy - 11, 'nectar_light', 'gold')
        draw_flower_small(img, cx + 4, cy - 11, 'nectar_light', 'gold')
    elif sprite_type == 'dewshine':
        # Prism lens on head
        fill_rect(img, cx - 1, cy - 9, 3, 3, 'dewshine_light')
        outline_rect(img, cx - 1, cy - 9, 3, 3, 'dewshine')
        # Sun collector dish
        fill_rect(img, cx + 4, cy - 4, 4, 2, 'gray')
        px(img, cx + 5, cy - 5, 'gray_light')
    elif sprite_type == 'heartwood':
        # Tiny axe
        fill_rect(img, cx + 5, cy - 6, 1, 7, 'brown')
        fill_rect(img, cx + 4, cy - 6, 3, 2, 'gray')
        # Backpack
        fill_rect(img, cx - 7, cy - 3, 3, 5, 'brown')
        fill_rect(img, cx - 7, cy - 3, 3, 1, 'brown_light')
    elif sprite_type == 'shimmer':
        # Crystal wand
        fill_rect(img, cx + 5, cy - 5, 1, 6, 'brown')
        px(img, cx + 5, cy - 6, 'shimmer_light')
        px(img, cx + 4, cy - 7, 'shimmer')
        px(img, cx + 6, cy - 7, 'shimmer')
        px(img, cx + 5, cy - 8, 'white')
        # Sparkle net
        draw_line(img, cx - 6, cy - 3, cx - 6, cy + 3, 'outline_light')
        draw_line(img, cx - 6, cy - 3, cx - 3, cy - 3, 'outline_light')
    elif sprite_type == 'installing':
        # Wrench
        fill_rect(img, cx + 4, cy - 3, 1, 5, 'gray')
        fill_rect(img, cx + 3, cy - 4, 3, 2, 'gray_light')
    elif 'working' in sprite_type:
        # Action lines
        for i in range(3):
            px(img, cx + 7 + i, cy - 3 + i, 'gold_light')
            px(img, cx - 7 - i, cy - 3 + i, 'gold_light')


def _gen_sprite_following(img, cx, cy):
    """Generate 16x16 tiny following sprite."""
    # Mini ghost
    draw_ellipse(img, cx, cy - 1, 4, 5, 'cream')
    fill_rect(img, cx - 4, cy - 1, 9, 5, 'cream')
    outline_ellipse(img, cx, cy - 1, 4, 5, 'outline_light')
    # Tiny eyes
    px(img, cx - 2, cy - 2, 'eye_dark')
    px(img, cx + 1, cy - 2, 'eye_dark')
    # Smile
    px(img, cx, cy + 1, 'outline_light')
    return img


# ===================================================================
# 3. TERRAIN TILE GENERATORS
# ===================================================================

def gen_terrain(w, h, file_path, prompt):
    """Generate a terrain tile or overlay."""
    fname = Path(file_path).stem
    img = new_image(w, h)

    if 'border_' in fname:
        return _gen_border(img, fname)
    elif 'taken_overlay' in fname:
        return _gen_taken_overlay(img)
    elif 'shimmer_deposit' in fname:
        return _gen_shimmer_deposit(img)
    elif 'tree_grove' in fname:
        variant = 0
        if '_v2' in fname:
            variant = 1
        elif '_v3' in fname:
            variant = 2
        return _gen_tree_grove(img, variant)
    elif 'stoney' in fname:
        variant = 0
        if '_v2' in fname:
            variant = 1
        elif '_v3' in fname:
            variant = 2
        return _gen_stoney_clearing(img, variant)
    elif 'babbling' in fname:
        variant = 0
        if '_v2' in fname:
            variant = 1
        elif '_v3' in fname:
            variant = 2
        return _gen_babbling_brook(img, variant)
    elif 'mushroom_market' in fname:
        return _gen_mushroom_market_tile(img)
    return img


def _gen_tree_grove(img, variant=0):
    """Generate 64x64 forest tile."""
    W, H = img.size
    rng = random.Random(42 + variant)

    # Ground base
    fill_rect(img, 0, 0, W, H, 'forest_dark')
    # Mossy patches
    for _ in range(80):
        x, y = rng.randint(0, W - 2), rng.randint(0, H - 2)
        fill_rect(img, x, y, 2, 2, 'forest' if rng.random() > 0.5 else 'forest_light')

    # Trees - varied placement per variant
    tree_positions = [
        [(10, 10), (30, 8), (50, 12), (15, 35), (42, 30), (55, 42)],
        [(8, 15), (28, 5), (48, 18), (20, 40), (38, 35), (52, 48)],
        [(12, 8), (35, 14), (18, 28), (45, 22), (8, 45), (50, 38)],
    ][variant]

    for tx, ty in tree_positions:
        draw_tree_small(img, tx, ty, 'green_grass' if rng.random() > 0.3 else 'forest_light', 'brown')

    # Small flowers
    for _ in range(5):
        fx, fy = rng.randint(2, W - 3), rng.randint(2, H - 3)
        petal_c = rng.choice(['rose_light', 'gold_light', 'dewshine_light'])
        draw_flower_small(img, fx, fy, petal_c, 'gold')

    # Mushrooms (variant 0)
    if variant == 0:
        for mx, my in [(22, 48), (45, 50)]:
            fill_rect(img, mx, my + 2, 2, 3, 'cream')
            draw_ellipse(img, mx + 1, my + 1, 3, 2, 'red')
            px(img, mx, my, 'white')

    # Fallen log (variant 2)
    if variant == 2:
        fill_rect(img, 5, 50, 20, 3, 'brown')
        fill_rect(img, 5, 50, 20, 1, 'brown_light')
        # Wildflowers around log
        for fx in range(8, 23, 4):
            draw_flower_small(img, fx, 48, rng.choice(['rose_light', 'gold_light']), 'gold')

    return img


def _gen_stoney_clearing(img, variant=0):
    """Generate 64x64 rocky clearing tile."""
    W, H = img.size
    rng = random.Random(100 + variant)

    # Sandy/grassy ground
    fill_rect(img, 0, 0, W, H, 'bg')
    for _ in range(120):
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        px(img, x, y, rng.choice(['green_light', 'cream', 'bg']))

    # Sunlight patches
    for _ in range(3):
        sx, sy = rng.randint(10, W - 10), rng.randint(10, H - 10)
        draw_circle(img, sx, sy, 5, 'gold_light', 60)

    # Rocks
    rock_positions = [
        [(8, 12, 5), (25, 8, 7), (45, 15, 4), (15, 40, 6), (50, 45, 5), (35, 50, 4)],
        [(12, 10, 6), (38, 6, 5), (52, 20, 7), (10, 48, 4), (30, 42, 5), (48, 50, 6)],
        [(18, 8, 5), (40, 12, 6), (8, 30, 7), (50, 35, 4), (25, 50, 5), (42, 48, 5)],
    ][variant]

    for rx, ry, rs in rock_positions:
        draw_ellipse(img, rx, ry, rs, rs - 1, 'gray')
        draw_ellipse(img, rx - 1, ry - 1, rs - 1, rs - 2, 'gray_light')
        # Shadow
        for dx in range(-rs + 1, rs):
            px(img, rx + dx, ry + rs - 1, 'gray_dark', 120)

    # Sparse grass tufts
    for _ in range(8):
        gx, gy = rng.randint(3, W - 3), rng.randint(3, H - 3)
        px(img, gx, gy - 1, 'green_grass')
        px(img, gx - 1, gy, 'green_grass')
        px(img, gx + 1, gy, 'green_grass')

    # Crystal formations (variant 1)
    if variant == 1:
        for cx_off, cy_off in [(20, 25), (44, 30)]:
            fill_rect(img, cx_off, cy_off - 4, 2, 5, 'shimmer_light')
            fill_rect(img, cx_off + 2, cy_off - 2, 2, 3, 'shimmer')
            px(img, cx_off, cy_off - 5, 'white')

    # Mossy boulders (variant 2)
    if variant == 2:
        for bx, by in [(20, 25), (42, 35)]:
            draw_ellipse(img, bx, by, 6, 5, 'gray')
            # Moss on top
            for dx in range(-4, 5):
                if rng.random() > 0.4:
                    px(img, bx + dx, by - 4, 'forest_light')
                    px(img, bx + dx, by - 3, 'green_grass')

    return img


def _gen_babbling_brook(img, variant=0):
    """Generate 64x64 stream tile."""
    W, H = img.size
    rng = random.Random(200 + variant)

    # Water base
    draw_water_tile(img, 0, 0, W, H, seed=200 + variant)

    # Banks (top and bottom)
    for y in range(8):
        for x in range(W):
            if rng.random() < 0.7 - y * 0.08:
                px(img, x, y, rng.choice(['forest_dark', 'brown', 'forest']))
            if rng.random() < 0.7 - y * 0.08:
                px(img, x, H - 1 - y, rng.choice(['forest_dark', 'brown', 'forest']))

    # Pebbles in water
    for _ in range(10):
        px_x, px_y = rng.randint(5, W - 5), rng.randint(12, H - 12)
        draw_rock(img, px_x, px_y, 2)

    # Lily pads
    for _ in range(3):
        lx, ly = rng.randint(10, W - 10), rng.randint(15, H - 15)
        draw_ellipse(img, lx, ly, 4, 2, 'forest')
        draw_ellipse(img, lx, ly, 3, 1, 'forest_light')

    # Water sparkles
    for _ in range(5):
        sx, sy = rng.randint(5, W - 5), rng.randint(10, H - 10)
        px(img, sx, sy, 'white')

    # Waterfall cascade (variant 1)
    if variant == 1:
        for y in range(0, 20):
            fill_rect(img, 25, y, 14, 1, 'water_light')
            if y % 3 == 0:
                px(img, 28 + rng.randint(-2, 2), y, 'white')
        # Foam at base
        for x in range(22, 42):
            if rng.random() > 0.3:
                px(img, x, 20, 'white')
                px(img, x, 21, 'water_light')

    # Stepping stones (variant 2)
    if variant == 2:
        for sx in [15, 28, 42]:
            draw_ellipse(img, sx, 32, 4, 2, 'gray')
            draw_ellipse(img, sx, 31, 3, 1, 'gray_light')

    return img


def _gen_mushroom_market_tile(img):
    """Generate 64x64 mushroom market building tile."""
    W, H = img.size

    # Ground
    fill_rect(img, 0, 0, W, H, 'forest_dark')
    scatter_pixels(img, 0, 0, W, H, 'forest', 0.3, seed=300)

    # Giant mushroom building
    cx = W // 2

    # Stem
    fill_rect(img, cx - 6, 30, 12, 20, 'cream')
    fill_rect(img, cx - 5, 30, 2, 20, 'white', 120)  # highlight
    fill_rect(img, cx + 3, 30, 2, 20, 'brown_light', 80)  # shadow

    # Cap
    draw_ellipse(img, cx, 25, 20, 12, 'red')
    draw_ellipse(img, cx, 22, 18, 8, 'red')
    # Spots on cap
    for sx, sy in [(cx - 10, 20), (cx + 8, 22), (cx - 3, 16), (cx + 5, 18), (cx - 8, 26)]:
        draw_circle(img, sx, sy, 2, 'white')

    # Door
    fill_rect(img, cx - 3, 40, 6, 10, 'brown')
    fill_rect(img, cx - 2, 40, 4, 1, 'brown_light')
    px(img, cx + 1, 45, 'gold')  # doorknob

    # Windows
    for wx in [cx - 8, cx + 6]:
        fill_rect(img, wx, 34, 3, 3, 'gold_light')
        outline_rect(img, wx, 34, 3, 3, 'brown')

    # Tiny awnings
    for ax in [cx - 14, cx + 10]:
        fill_rect(img, ax, 32, 6, 2, 'red')
        fill_rect(img, ax, 34, 6, 1, 'red_dark')

    return img


def _gen_border(img, fname):
    """Generate 64x64 transparent border overlay."""
    W, H = img.size
    inset = 3

    color_map = {
        'border_rose': 'rose',
        'border_lilypad': 'lilypad',
        'border_fern': 'fern',
        'border_mushroom': 'mushroom',
        'border_selected': 'gold',
        'border_human': 'gold',
    }
    border_color = color_map.get(fname, 'white')

    # Draw inset border
    alpha = 200 if fname != 'border_selected' else 230
    for t in range(2):
        outline_rect(img, inset + t, inset + t, W - (inset + t) * 2, H - (inset + t) * 2, border_color, alpha)

    # Selected gets pulsing dots at corners
    if fname == 'border_selected':
        for cx_off, cy_off in [(inset + 1, inset + 1), (W - inset - 2, inset + 1),
                              (inset + 1, H - inset - 2), (W - inset - 2, H - inset - 2)]:
            px(img, cx_off, cy_off, 'white')

    # Human border gets glow effect
    if fname == 'border_human':
        for t in range(3):
            outline_rect(img, inset - 1 + t, inset - 1 + t,
                        W - (inset - 1 + t) * 2, H - (inset - 1 + t) * 2,
                        'gold_light', 100 - t * 30)

    return img


def _gen_taken_overlay(img):
    """Generate 64x64 semi-transparent red TAKEN overlay."""
    W, H = img.size
    fill_rect(img, 0, 0, W, H, 'red', 80)
    # Pixelated "X"
    for i in range(min(W, H) // 4):
        px(img, W // 4 + i, H // 4 + i, 'white', 180)
        px(img, 3 * W // 4 - i, H // 4 + i, 'white', 180)
    return img


def _gen_shimmer_deposit(img):
    """Generate 16x16 tiny crystal deposit."""
    cx, cy = img.width // 2, img.height // 2
    # Crystal shape
    fill_rect(img, cx - 1, cy - 3, 3, 6, 'shimmer')
    fill_rect(img, cx - 2, cy - 1, 5, 3, 'shimmer')
    # Highlights
    px(img, cx - 1, cy - 2, 'shimmer_light')
    px(img, cx, cy - 3, 'white')
    # Glow
    for angle in range(0, 360, 45):
        dx = int(4 * math.cos(math.radians(angle)))
        dy = int(4 * math.sin(math.radians(angle)))
        px(img, cx + dx, cy + dy, 'shimmer_light', 100)
    return img


# ===================================================================
# 4. RESOURCE ICON GENERATORS
# ===================================================================

def gen_resource(w, h, file_path, prompt):
    """Generate a resource icon."""
    fname = Path(file_path).stem
    img = new_image(w, h)
    cx, cy = w // 2, h // 2

    if 'nectar' in fname:
        _draw_nectar_icon(img, cx, cy, w)
    elif 'dewshine' in fname:
        _draw_dewshine_icon(img, cx, cy, w)
    elif 'heartwood' in fname:
        _draw_heartwood_icon(img, cx, cy, w)
    elif 'shimmer' in fname:
        _draw_shimmer_icon(img, cx, cy, w)
    elif 'coin' in fname:
        _draw_coin_icon(img, cx, cy, w)

    return img


def _draw_nectar_icon(img, cx, cy, size):
    """Golden nectar droplet with flower petal accent."""
    r = size // 3
    # Droplet shape
    draw_ellipse(img, cx, cy + 1, r, r + 1, 'nectar')
    draw_ellipse(img, cx, cy - 1, r - 1, r - 1, 'nectar_light')
    # Droplet tip
    for i in range(r):
        px(img, cx, cy - r - i, 'nectar')
    px(img, cx, cy - r - r + 1, 'nectar_light')
    # Highlight
    px(img, cx - 1, cy - 1, 'gold_light')
    # Petal accent
    if size >= 24:
        px(img, cx + r, cy - r, 'rose_light')
        px(img, cx + r + 1, cy - r - 1, 'rose_light')
        px(img, cx + r - 1, cy - r - 1, 'rose_light')


def _draw_dewshine_icon(img, cx, cy, size):
    """Glowing blue dewdrop."""
    r = size // 3
    draw_ellipse(img, cx, cy + 1, r, r + 1, 'dewshine')
    draw_ellipse(img, cx, cy - 1, r - 1, r, 'dewshine_light')
    for i in range(r):
        px(img, cx, cy - r - i, 'dewshine')
    px(img, cx - 1, cy - 1, 'white')
    # Sparkle
    if size >= 24:
        draw_sparkle(img, cx + r, cy - r, 'white', 2)
    if size >= 32:
        # Sun rays
        for angle in [30, 60]:
            dx = int(r * 1.5 * math.cos(math.radians(angle)))
            dy = int(r * 1.5 * math.sin(math.radians(angle)))
            draw_line(img, cx + dx, cy - dy, cx + dx + 2, cy - dy - 2, 'gold_light')


def _draw_heartwood_icon(img, cx, cy, size):
    """Cross-section of magical tree log."""
    r = size // 3
    # Log circle
    draw_circle(img, cx, cy, r, 'heartwood')
    draw_circle(img, cx, cy, r - 1, 'heartwood_light')
    # Growth rings
    for ring_r in range(2, r - 1, 2):
        outline_ellipse(img, cx, cy, ring_r, ring_r, 'heartwood')
    # Heart-shaped center (for 24+ sizes)
    if size >= 24:
        px(img, cx, cy, 'nectar_light')
        px(img, cx - 1, cy - 1, 'nectar_light')
        px(img, cx + 1, cy - 1, 'nectar_light')
    # Glow
    if size >= 32:
        draw_circle(img, cx, cy, 2, 'gold_light')
    # Outline
    outline_ellipse(img, cx, cy, r, r, 'heartwood_dark')


def _draw_shimmer_icon(img, cx, cy, size):
    """Faceted purple crystal."""
    r = size // 3
    # Crystal body (hexagonal-ish)
    for dy in range(-r, r + 1):
        half_w = r - abs(dy) // 2
        fill_rect(img, cx - half_w, cy + dy, half_w * 2 + 1, 1, 'shimmer')
    # Facet highlight
    for dy in range(-r + 1, 0):
        hw = r - abs(dy) // 2 - 1
        fill_rect(img, cx - hw, cy + dy, hw, 1, 'shimmer_light')
    # Tip
    px(img, cx, cy - r, 'white')
    # Sparkles
    if size >= 24:
        draw_sparkle(img, cx + r, cy - r + 1, 'white', 2)
    if size >= 32:
        draw_sparkle(img, cx - r, cy + r - 2, 'shimmer_light', 2)
        draw_sparkle(img, cx + r + 1, cy + 1, 'white', 1)


def _draw_coin_icon(img, cx, cy, size):
    """Gold coin with fairy wing stamp."""
    r = size // 3
    # Coin body
    draw_circle(img, cx, cy, r, 'coins')
    draw_circle(img, cx, cy, r - 1, 'coins_light')
    # Rim
    outline_ellipse(img, cx, cy, r, r, 'coins_dark')
    if r > 3:
        outline_ellipse(img, cx, cy, r - 2, r - 2, 'coins_dark')
    # Wing stamp (tiny V shape)
    if size >= 16:
        draw_line(img, cx - 2, cy - 1, cx, cy + 1, 'coins_dark')
        draw_line(img, cx, cy + 1, cx + 2, cy - 1, 'coins_dark')
    # Shine highlight
    px(img, cx - r // 2, cy - r // 2, 'white')


# ===================================================================
# 5. SCREEN GENERATORS
# ===================================================================

def gen_screen(w, h, file_path, prompt):
    """Generate screen backgrounds and banners."""
    fname = Path(file_path).stem
    img = new_image(w, h)

    if fname == 'logo':
        return _gen_logo(img)
    elif fname == 'splash_bg':
        return _gen_splash_bg(img)
    elif fname == 'menu_bg':
        return _gen_menu_bg(img)
    elif 'victory' in fname:
        return _gen_banner(img, 'VICTORY', 'gold', 'gold_light')
    elif 'defeat' in fname:
        return _gen_banner(img, 'DEFEAT', 'gray', 'gray_dark')
    elif 'struggle' in fname:
        return _gen_banner(img, 'STRUGGLE', 'nectar', 'nectar_dark')
    return img


def _draw_pixel_char(img, x, y, char, color_name, scale=1):
    """Draw a single pixel font character (5x7 grid)."""
    # Minimal 5x7 pixel font for key characters
    FONT = {
        'F': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
        'A': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'I': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],
        'R': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
        'Y': [[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
        'O': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'T': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
        'E': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
        'V': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0]],
        'C': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,1,0]],
        'D': [[1,1,1,0,0],[1,0,0,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,1,0],[1,1,1,0,0]],
        'S': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        'U': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        'G': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        'L': [[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
        'P': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
        'K': [[1,0,0,0,1],[1,0,0,1,0],[1,0,1,0,0],[1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
        'H': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'W': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,0,0,0,1]],
        'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
        'B': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
        '!': [[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0]],
        ' ': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        '3': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
        '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,1,1,1,1]],
        '1': [[0,0,1,0,0],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0]],
    }

    glyph = FONT.get(char.upper(), FONT.get(' '))
    if glyph:
        for row_i, row in enumerate(glyph):
            for col_i, on in enumerate(row):
                if on:
                    fill_rect(img, x + col_i * scale, y + row_i * scale, scale, scale, color_name)


def _draw_pixel_text(img, x, y, text, color_name, scale=1):
    """Draw text using pixel font."""
    cursor_x = x
    for ch in text:
        _draw_pixel_char(img, cursor_x, y, ch, color_name, scale)
        cursor_x += 6 * scale  # 5px char + 1px spacing


def _gen_logo(img):
    """Generate 256x64 game title logo."""
    W, H = img.size
    # Background vine decoration
    for x in range(0, W, 12):
        draw_line(img, x, H - 4, x + 8, H - 8, 'forest')
        px(img, x + 4, H - 9, 'forest_light')

    # "FAIRY" text
    _draw_pixel_text(img, 8, 10, 'FAIRY', 'forest', scale=3)
    # "FRONTIER" text
    _draw_pixel_text(img, 8, 35, 'FRONTIER', 'gold', scale=3)

    # Decorative flowers
    draw_flower_small(img, 3, 8, 'rose_light', 'gold')
    draw_flower_small(img, W - 5, 12, 'rose_light', 'gold')
    draw_flower_small(img, W - 8, 38, 'dewshine_light', 'white')

    # Ivy
    for i in range(0, 6):
        px(img, 2 + i, 14 + i * 3, 'forest_light')
        px(img, 3 + i, 15 + i * 3, 'forest')

    return img


def _gen_splash_bg(img):
    """Generate 360x640 enchanted forest splash background."""
    W, H = img.size

    # Sky gradient (dark at top, lighter at bottom)
    for y in range(H):
        ratio = y / H
        if ratio < 0.4:
            fill_rect(img, 0, y, W, 1, 'forest_dark')
        elif ratio < 0.7:
            fill_rect(img, 0, y, W, 1, 'forest')
        else:
            fill_rect(img, 0, y, W, 1, 'forest_light')

    rng = random.Random(42)

    # Trees (silhouettes in background)
    for tx in range(0, W, 20):
        tree_h = rng.randint(80, 200)
        tree_w = rng.randint(15, 30)
        trunk_x = tx + tree_w // 2 - 2
        # Trunk
        fill_rect(img, trunk_x, H - tree_h, 4, tree_h // 2, 'brown_dark')
        # Canopy
        for cy_off in range(tree_h // 2):
            spread = int(tree_w * (1 - cy_off / (tree_h / 2)) * 0.7)
            fill_rect(img, tx + tree_w // 2 - spread, H - tree_h + cy_off, spread * 2, 1,
                      'forest_dark' if rng.random() > 0.3 else 'forest')

    # Light rays
    for ray_x in [W // 4, W // 2, 3 * W // 4]:
        for y in range(H // 3):
            spread = y // 4
            fill_rect(img, ray_x - spread, y * 2, spread * 2 + 2, 2, 'gold_light', 30)

    # Fireflies
    for _ in range(15):
        fx, fy = rng.randint(10, W - 10), rng.randint(50, H - 100)
        px(img, fx, fy, 'gold_light')
        px(img, fx + 1, fy, 'gold_light', 150)

    # Mushrooms at base
    for mx in range(10, W - 10, 40):
        my = H - 20
        fill_rect(img, mx, my, 3, 8, 'cream')
        draw_ellipse(img, mx + 1, my - 2, 5, 3, 'red')
        px(img, mx - 1, my - 3, 'white')

    # Ground
    fill_rect(img, 0, H - 10, W, 10, 'brown_dark')
    scatter_pixels(img, 0, H - 10, W, 10, 'forest_dark', 0.3, seed=42)

    return img


def _gen_menu_bg(img):
    """Generate 360x640 menu background."""
    # Similar to splash but with mushroom house
    img = _gen_splash_bg(img)
    W, H = img.size

    # Path
    for y in range(H // 2, H - 10):
        path_w = 20 + (y - H // 2) // 3
        cx_p = W // 2
        fill_rect(img, cx_p - path_w // 2, y, path_w, 1, 'brown')
        if y % 3 == 0:
            px(img, cx_p - path_w // 4, y, 'brown_light')

    # Giant mushroom house
    mcx = W // 2
    fill_rect(img, mcx - 15, H // 2 - 20, 30, 60, 'cream')
    draw_ellipse(img, mcx, H // 2 - 30, 35, 20, 'red')
    draw_ellipse(img, mcx, H // 2 - 35, 30, 14, 'red')
    for sx, sy in [(mcx - 15, H // 2 - 35), (mcx + 12, H // 2 - 30), (mcx, H // 2 - 40)]:
        draw_circle(img, sx, sy, 4, 'white')
    # Door
    fill_rect(img, mcx - 8, H // 2 + 10, 16, 30, 'brown')
    px(img, mcx + 5, H // 2 + 25, 'gold')

    # Butterflies
    for bx, by in [(50, 200), (300, 180), (150, 250)]:
        px(img, bx, by, 'rose_light')
        px(img, bx - 2, by - 1, 'rose')
        px(img, bx + 2, by - 1, 'rose')

    return img


def _gen_banner(img, text, color_name, dark_color):
    """Generate result banner with text."""
    W, H = img.size

    # Banner background (parchment scroll shape)
    draw_rounded_rect(img, 4, 8, W - 8, H - 16, 'cream')
    draw_rounded_rect(img, 8, 12, W - 16, H - 24, 'bg')
    # Border
    outline_rect(img, 4, 8, W - 8, H - 16, color_name)
    outline_rect(img, 6, 10, W - 12, H - 20, dark_color)

    # Text
    text_w = len(text) * 12
    text_x = (W - text_w) // 2
    _draw_pixel_text(img, text_x, H // 2 - 6, text, color_name, scale=2)

    # Decorations based on type
    if 'VICTORY' in text:
        # Sparkles
        draw_sparkle(img, 15, 15, 'gold_light', 3)
        draw_sparkle(img, W - 16, 15, 'gold_light', 3)
        draw_sparkle(img, W // 2, 12, 'white', 2)
    elif 'DEFEAT' in text:
        # Rain drops
        for rx in range(20, W - 20, 15):
            draw_line(img, rx, 5, rx - 2, 12, 'dewshine')

    return img


# ===================================================================
# 6. MARKET INTERIOR GENERATORS
# ===================================================================

def gen_market(w, h, file_path, prompt):
    """Generate market interior assets."""
    fname = Path(file_path).stem
    img = new_image(w, h)

    if fname == 'interior_bg':
        return _gen_market_interior_bg(img)
    elif 'station_' in fname:
        resource = fname.replace('station_', '')
        return _gen_market_station(img, resource)
    elif fname == 'sprite_corral':
        return _gen_sprite_corral(img)
    elif fname == 'sparkle_sensing':
        return _gen_sparkle_sensing(img)
    elif fname == 'luck_lounge':
        return _gen_luck_lounge(img)
    elif fname == 'exit_door':
        return _gen_exit_door(img)
    elif fname == 'price_ladder_bg':
        return _gen_price_ladder(img)
    elif fname == 'bid_marker':
        return _gen_bid_ask_marker(img, 'bid')
    elif fname == 'ask_marker':
        return _gen_bid_ask_marker(img, 'ask')
    elif fname == 'mm_buy_line':
        return _gen_mm_line(img, 'green_grass')
    elif fname == 'mm_sell_line':
        return _gen_mm_line(img, 'red')
    elif fname == 'trader_buyer':
        return _gen_trader_icon(img, 'buyer')
    elif fname == 'trader_seller':
        return _gen_trader_icon(img, 'seller')
    return img


def _gen_market_interior_bg(img):
    """Generate 320x480 mushroom market interior."""
    W, H = img.size

    # Warm wood walls
    fill_rect(img, 0, 0, W, H, 'brown')
    for y in range(0, H, 3):
        fill_rect(img, 0, y, W, 1, 'brown_light' if y % 6 < 3 else 'brown_dark')

    # Curved ceiling (inside of mushroom cap)
    for y in range(80):
        ratio = y / 80
        fill_rect(img, 0, y, W, 1, 'red_dark' if ratio < 0.5 else 'brown')
    draw_ellipse(img, W // 2, -20, W // 2 + 20, 60, 'red_dark')

    # Shelves
    for sy in [120, 200, 280]:
        fill_rect(img, 10, sy, W - 20, 4, 'brown_dark')
        fill_rect(img, 10, sy, W - 20, 2, 'brown_light')

    # Warm lighting
    draw_circle(img, W // 2, 90, 15, 'gold_light', 40)

    # Counter at bottom
    fill_rect(img, 0, H - 60, W, 60, 'brown_dark')
    fill_rect(img, 0, H - 60, W, 3, 'brown_light')

    # Floor
    fill_rect(img, 0, H - 20, W, 20, 'brown_dark')
    for x in range(0, W, 8):
        fill_rect(img, x, H - 20, 4, 20, 'brown')

    return img


def _gen_market_station(img, resource):
    """Generate 48x48 market stall for a resource."""
    W, H = img.size
    color_map = {
        'nectar': ('nectar', 'nectar_light', 'nectar_dark'),
        'dewshine': ('dewshine', 'dewshine_light', 'dewshine_dark'),
        'heartwood': ('heartwood', 'heartwood_light', 'heartwood_dark'),
        'shimmer': ('shimmer', 'shimmer_light', 'shimmer_dark'),
    }
    colors = color_map.get(resource, ('gray', 'gray_light', 'gray_dark'))
    main_c, light_c, dark_c = colors

    # Stall frame
    fill_rect(img, 4, 20, W - 8, H - 24, 'brown')
    fill_rect(img, 4, 20, W - 8, 2, 'brown_light')

    # Awning
    fill_rect(img, 2, 14, W - 4, 8, main_c)
    fill_rect(img, 2, 14, W - 4, 3, light_c)
    # Awning scallops
    for x in range(4, W - 4, 6):
        draw_ellipse(img, x + 3, 21, 3, 2, main_c)

    # Contents based on resource
    if resource == 'nectar':
        # Barrels and honey jars
        for bx in [10, 22, 34]:
            fill_rect(img, bx, 28, 6, 8, 'nectar_dark')
            fill_rect(img, bx, 28, 6, 2, 'nectar')
        # Flower garlands
        for x in range(6, W - 6, 5):
            draw_flower_small(img, x, 16, 'gold_light', 'nectar')
    elif resource == 'dewshine':
        # Prisms
        for bx in [12, 24, 36]:
            fill_rect(img, bx, 26, 4, 8, 'dewshine_light')
            px(img, bx + 1, 25, 'white')
        # Blue crystals
        for cx_off in [8, 20, 32]:
            fill_rect(img, cx_off, 30, 3, 6, 'dewshine')
    elif resource == 'heartwood':
        # Stacked logs
        for ly in range(28, 38, 3):
            for lx in range(8, W - 8, 7):
                fill_rect(img, lx, ly, 6, 3, 'heartwood')
                fill_rect(img, lx, ly, 6, 1, 'heartwood_light')
    elif resource == 'shimmer':
        # Glowing crystals on velvet
        fill_rect(img, 6, 30, W - 12, 8, 'mushroom_dark')
        for cx_off in [12, 24, 36]:
            fill_rect(img, cx_off - 1, 26, 3, 6, 'shimmer_light')
            px(img, cx_off, 25, 'white')

    # Sign post
    fill_rect(img, W // 2 - 1, 4, 2, 12, 'brown')
    draw_rounded_rect(img, W // 2 - 8, 2, 16, 10, main_c)
    outline_rect(img, W // 2 - 8, 2, 16, 10, dark_c)

    return img


def _gen_sprite_corral(img):
    """Generate 48x48 sprite pen."""
    W, H = img.size
    # Fence
    fill_rect(img, 4, 16, W - 8, 2, 'brown')
    fill_rect(img, 4, H - 8, W - 8, 2, 'brown')
    fill_rect(img, 4, 16, 2, H - 24, 'brown')
    fill_rect(img, W - 6, 16, 2, H - 24, 'brown')
    # Fence posts
    for fx in [4, W // 2, W - 6]:
        fill_rect(img, fx, 14, 2, H - 20, 'brown_dark')

    # Ghost sprites inside
    for sx, sy in [(15, 28), (28, 25), (36, 32)]:
        draw_circle(img, sx, sy, 3, 'cream')
        px(img, sx - 1, sy - 1, 'eye_dark')
        px(img, sx + 1, sy - 1, 'eye_dark')

    # Sign
    draw_rounded_rect(img, W // 2 - 12, 2, 24, 12, 'brown')
    _draw_pixel_text(img, W // 2 - 10, 4, 'SP', 'cream', scale=1)

    return img


def _gen_sparkle_sensing(img):
    """Generate 48x48 fortune teller booth."""
    W, H = img.size
    # Curtain backdrop
    for x in range(W):
        stripe_c = 'magic_dark' if (x // 4) % 2 == 0 else 'magic'
        fill_rect(img, x, 0, 1, H, stripe_c)

    # Crystal ball
    cx, cy = W // 2, H // 2
    draw_circle(img, cx, cy, 8, 'shimmer_light')
    draw_circle(img, cx - 2, cy - 2, 3, 'white', 150)
    outline_ellipse(img, cx, cy, 8, 8, 'shimmer_dark')
    # Velvet cushion
    draw_ellipse(img, cx, cy + 10, 10, 3, 'magic')

    # Stars in curtain
    for sx, sy in [(5, 5), (W - 6, 8), (10, H - 8), (W - 10, H - 5)]:
        draw_sparkle(img, sx, sy, 'gold_light', 2)

    return img


def _gen_luck_lounge(img):
    """Generate 48x48 cozy lounge area."""
    W, H = img.size
    # Background
    fill_rect(img, 0, 0, W, H, 'brown')
    fill_rect(img, 0, 0, W, H // 3, 'brown_dark')

    # Toadstool chair
    cx = W // 2
    fill_rect(img, cx - 3, H // 2, 6, 12, 'cream')
    draw_ellipse(img, cx, H // 2 - 2, 8, 5, 'red')
    px(img, cx - 3, H // 2 - 3, 'white')
    px(img, cx + 2, H // 2 - 4, 'white')

    # Teapot
    draw_ellipse(img, cx + 14, H // 2 + 4, 4, 3, 'cream')
    fill_rect(img, cx + 17, H // 2 + 2, 3, 1, 'cream')  # spout
    px(img, cx + 14, H // 2, 'brown')  # lid

    # Sparkles
    for sx, sy in [(8, 10), (W - 10, 15), (cx, 8)]:
        draw_sparkle(img, sx, sy, 'gold_light', 2)

    return img


def _gen_exit_door(img):
    """Generate 48x48 exit door."""
    W, H = img.size
    # Wall background
    fill_rect(img, 0, 0, W, H, 'brown')

    # Arched door
    fill_rect(img, 12, 16, 24, 28, 'brown_dark')
    draw_ellipse(img, 24, 16, 12, 10, 'brown_dark')

    # Daylight through door
    fill_rect(img, 14, 18, 20, 26, 'gold_light')
    draw_ellipse(img, 24, 18, 10, 8, 'gold_light')
    # Brighter center
    fill_rect(img, 18, 24, 12, 16, 'cream')

    # EXIT sign
    draw_rounded_rect(img, 14, 4, 20, 10, 'forest')
    _draw_pixel_text(img, 16, 6, 'EXIT', 'cream', scale=1)

    return img


def _gen_price_ladder(img):
    """Generate 80x400 vertical price ladder."""
    W, H = img.size
    # Wooden post
    fill_rect(img, W // 2 - 4, 0, 8, H, 'brown')
    fill_rect(img, W // 2 - 3, 0, 2, H, 'brown_light')

    # Price notches
    for y in range(10, H - 10, 15):
        fill_rect(img, W // 2 - 10, y, 20, 2, 'brown_dark')
        fill_rect(img, W // 2 - 9, y, 18, 1, 'brown_light')

    return img


def _gen_bid_ask_marker(img, marker_type):
    """Generate 24x12 bid or ask marker."""
    W, H = img.size
    color = 'green_grass' if marker_type == 'bid' else 'red'
    dark = 'green_dark' if marker_type == 'bid' else 'red_dark'

    # Leaf shape
    draw_ellipse(img, W // 2, H // 2, W // 2 - 2, H // 2 - 1, color)
    # Arrow point
    if marker_type == 'bid':
        for i in range(H // 2):
            px(img, W - 2 - i, H // 2 - i, color)
            px(img, W - 2 - i, H // 2 + i, color)
    else:
        for i in range(H // 2):
            px(img, 1 + i, H // 2 - i, color)
            px(img, 1 + i, H // 2 + i, color)

    # Text
    label = 'BID' if marker_type == 'bid' else 'ASK'
    _draw_pixel_text(img, 3, 3, label[0], 'white', scale=1)

    return img


def _gen_mm_line(img, color):
    """Generate 80x4 dotted line."""
    W, H = img.size
    for x in range(0, W, 4):
        fill_rect(img, x, H // 2 - 1, 2, 2, color)
    return img


def _gen_trader_icon(img, trader_type):
    """Generate 16x16 tiny trader icon."""
    W, H = img.size
    cx, cy = W // 2, H // 2

    tint = 'green_grass' if trader_type == 'buyer' else 'red'

    # Fairy silhouette
    draw_circle(img, cx, cy - 2, 3, tint)
    fill_rect(img, cx - 2, cy + 1, 5, 5, tint)

    # Coin or basket
    if trader_type == 'buyer':
        draw_circle(img, cx + 4, cy + 3, 2, 'gold')
    else:
        fill_rect(img, cx - 5, cy + 1, 3, 4, 'brown')

    return img


# ===================================================================
# 7. UI / HUD GENERATORS
# ===================================================================

def gen_ui(w, h, file_path, prompt):
    """Generate UI elements."""
    fname = Path(file_path).stem
    img = new_image(w, h)

    if 'btn_play' in fname:
        pressed = 'pressed' in fname
        return _gen_button(img, 'PLAY', 'forest', 'forest_light', 'forest_dark', pressed)
    elif 'btn_generic' in fname:
        pressed = 'pressed' in fname
        return _gen_button(img, '', 'forest', 'forest_light', 'forest_dark', pressed)
    elif 'btn_small' in fname:
        pressed = 'pressed' in fname
        return _gen_button(img, '', 'forest', 'forest_light', 'forest_dark', pressed, small=True)
    elif 'card_frame' in fname:
        if 'selected' in fname:
            return _gen_card_frame(img, 'gold')
        elif 'locked' in fname:
            return _gen_card_frame(img, 'gray')
        return _gen_card_frame(img, 'forest')
    elif fname == 'panel_bg':
        return _gen_panel(img, 'brown', 'brown_light', 'brown_dark')
    elif fname == 'panel_dark':
        return _gen_panel(img, 'brown_dark', 'brown', 'black')
    elif fname == 'stats_box':
        return _gen_panel(img, 'cream', 'bg', 'forest')
    elif 'timer_bar_bg' in fname:
        return _gen_timer_bar_bg(img)
    elif 'timer_bar_fill' in fname:
        color = 'green_grass' if 'green' in fname else ('orange' if 'orange' in fname else 'red')
        fill_rect(img, 0, 0, w, h, color)
        return img
    elif fname == 'divider_h':
        return _gen_divider(img)
    elif fname == 'phase_banner':
        return _gen_phase_banner(img)
    elif 'icon_' in fname:
        return _gen_ui_icon(img, fname)
    return img


def _gen_button(img, text, color, light, dark, pressed=False, small=False):
    """Generate a pixel art button."""
    W, H = img.size
    bg_c = dark if pressed else color
    top_c = color if pressed else light
    bot_c = 'brown_dark' if pressed else dark

    # Button body
    draw_rounded_rect(img, 2, 2, W - 4, H - 4, bg_c)
    # Top highlight
    fill_rect(img, 3, 2, W - 6, 2, top_c)
    # Bottom shadow
    fill_rect(img, 3, H - 4, W - 6, 2, bot_c)
    # Vine border
    outline_rect(img, 1, 1, W - 2, H - 2, 'forest_dark')
    # Leaf corners
    for cx_off, cy_off in [(3, 3), (W - 4, 3), (3, H - 4), (W - 4, H - 4)]:
        px(img, cx_off, cy_off, 'forest_light')

    if text:
        text_w = len(text) * 6 * 2
        tx = (W - text_w) // 2
        ty = H // 2 - 5 + (2 if pressed else 0)
        _draw_pixel_text(img, tx, ty, text, 'white', scale=2)

    return img


def _gen_card_frame(img, border_color):
    """Generate 120x160 card frame."""
    W, H = img.size
    # Ornate border
    outline_rect(img, 2, 2, W - 4, H - 4, border_color)
    outline_rect(img, 4, 4, W - 8, H - 8, border_color)

    # Vine corners
    for cx_off, cy_off in [(6, 6), (W - 7, 6), (6, H - 7), (W - 7, H - 7)]:
        draw_circle(img, cx_off, cy_off, 3, 'forest_light')
        px(img, cx_off, cy_off, 'forest')

    # Mushroom accents at top corners
    for mx in [10, W - 11]:
        fill_rect(img, mx, 6, 2, 3, 'cream')
        draw_ellipse(img, mx + 1, 5, 3, 2, 'red')

    if border_color == 'gold':
        # Gold glow effect
        for t in range(3):
            outline_rect(img, 2 - t, 2 - t, W - 4 + t * 2, H - 4 + t * 2, 'gold_light', 80 - t * 25)

    if border_color == 'gray':
        # Lock icon
        cx_off = W // 2
        fill_rect(img, cx_off - 3, H // 2 - 2, 6, 6, 'gray')
        outline_rect(img, cx_off - 3, H // 2 - 2, 6, 6, 'gray_dark')
        draw_ellipse(img, cx_off, H // 2 - 5, 3, 3, 'gray')
        fill_rect(img, cx_off - 1, H // 2 - 4, 2, 2, 'transparent')

    return img


def _gen_panel(img, bg, highlight, border):
    """Generate 9-slice panel."""
    W, H = img.size
    # Fill
    fill_rect(img, 2, 2, W - 4, H - 4, bg)
    # Border
    outline_rect(img, 0, 0, W, H, border)
    outline_rect(img, 1, 1, W - 2, H - 2, border)
    # Inner highlight
    fill_rect(img, 2, 2, W - 4, 2, highlight)
    # Mushroom corner accents
    for cx_off, cy_off in [(4, 4), (W - 5, 4), (4, H - 5), (W - 5, H - 5)]:
        px(img, cx_off, cy_off, 'red')
        px(img, cx_off, cy_off - 1, 'red')
    return img


def _gen_timer_bar_bg(img):
    """Generate timer bar background frame."""
    W, H = img.size
    outline_rect(img, 0, 0, W, H, 'forest')
    fill_rect(img, 1, 1, W - 2, H - 2, 'brown_dark')
    # Vine decoration at ends
    for vx in [2, W - 5]:
        px(img, vx, 2, 'forest_light')
        px(img, vx + 1, 3, 'forest_light')
        px(img, vx + 2, 2, 'forest_light')
    return img


def _gen_divider(img):
    """Generate horizontal vine divider."""
    W, H = img.size
    cy = H // 2
    # Branch
    fill_rect(img, 0, cy, W, 1, 'brown')
    fill_rect(img, 0, cy + 1, W, 1, 'brown_dark')
    # Leaves
    for x in range(4, W - 4, 8):
        px(img, x, cy - 1, 'forest_light')
        px(img, x + 1, cy - 1, 'forest')
    return img


def _gen_phase_banner(img):
    """Generate scroll/parchment phase banner."""
    W, H = img.size
    # Parchment body
    draw_rounded_rect(img, 4, 4, W - 8, H - 8, 'cream')
    draw_rounded_rect(img, 6, 6, W - 12, H - 12, 'bg')
    # Scroll rolls at ends
    for ex in [4, W - 8]:
        fill_rect(img, ex, 4, 4, H - 8, 'cream')
        fill_rect(img, ex, 4, 4, 2, 'white', 120)
    # Border
    outline_rect(img, 4, 4, W - 8, H - 8, 'brown')
    return img


def _gen_ui_icon(img, fname):
    """Generate 24x24 UI icons."""
    W, H = img.size
    cx, cy = W // 2, H // 2

    if fname == 'icon_back':
        # Left arrow on leaf
        draw_ellipse(img, cx, cy, 8, 8, 'forest')
        draw_line(img, cx + 3, cy - 3, cx - 2, cy, 'white')
        draw_line(img, cx - 2, cy, cx + 3, cy + 3, 'white')
    elif fname == 'icon_settings':
        # Gear from mushroom parts
        draw_circle(img, cx, cy, 6, 'brown')
        draw_circle(img, cx, cy, 3, 'brown_dark')
        for angle in range(0, 360, 45):
            dx = int(7 * math.cos(math.radians(angle)))
            dy = int(7 * math.sin(math.radians(angle)))
            draw_circle(img, cx + dx, cy + dy, 2, 'brown')
    elif fname == 'icon_music_on':
        # Notes from flower
        draw_flower_small(img, cx - 4, cy + 4, 'forest_light', 'gold')
        draw_circle(img, cx + 2, cy - 2, 2, 'outline')
        draw_circle(img, cx + 6, cy, 2, 'outline')
        draw_line(img, cx + 4, cy - 2, cx + 4, cy - 6, 'outline')
        draw_line(img, cx + 8, cy, cx + 8, cy - 4, 'outline')
        draw_line(img, cx + 4, cy - 6, cx + 8, cy - 4, 'outline')
    elif fname == 'icon_music_off':
        _gen_ui_icon(img, 'icon_music_on')
        draw_line(img, 4, 4, W - 4, H - 4, 'red')
        draw_line(img, 5, 4, W - 3, H - 4, 'red')
        return img
    elif fname == 'icon_sound_on':
        # Speaker
        fill_rect(img, cx - 4, cy - 3, 4, 6, 'outline')
        draw_line(img, cx, cy - 5, cx + 3, cy - 5, 'outline')
        draw_line(img, cx, cy + 5, cx + 3, cy + 5, 'outline')
        # Sound waves
        for r in [4, 6]:
            for dy in range(-r, r + 1):
                dx = int(math.sqrt(max(0, r * r - dy * dy)))
                px(img, cx + 4 + dx, cy + dy, 'outline_light')
    elif fname == 'icon_sound_off':
        _gen_ui_icon(img, 'icon_sound_on')
        draw_line(img, 4, 4, W - 4, H - 4, 'red')
        draw_line(img, 5, 4, W - 3, H - 4, 'red')
        return img
    elif fname == 'icon_pause':
        # Two toadstool pillars
        for px_off in [cx - 4, cx + 2]:
            fill_rect(img, px_off, cy - 2, 3, 10, 'cream')
            draw_ellipse(img, px_off + 1, cy - 3, 3, 2, 'red')
    elif fname == 'icon_fast_forward':
        # Leaf arrows
        for offset in [0, 6]:
            draw_line(img, cx - 4 + offset, cy - 4, cx + 2 + offset, cy, 'forest')
            draw_line(img, cx + 2 + offset, cy, cx - 4 + offset, cy + 4, 'forest')
    elif fname == 'icon_info':
        # Glowing question mark mushroom
        draw_ellipse(img, cx, cy - 2, 6, 4, 'mushroom')
        px(img, cx - 2, cy - 3, 'white')
        fill_rect(img, cx - 1, cy + 2, 2, 4, 'cream')
        _draw_pixel_char(img, cx - 2, cy - 5, '?', 'gold_light', scale=1)

    return img


# ===================================================================
# 8. EVENT GENERATORS
# ===================================================================

def gen_event(w, h, file_path, prompt):
    """Generate 64x64 event illustrations."""
    fname = Path(file_path).stem
    img = new_image(w, h)
    W, H = img.size
    rng = random.Random(hash(fname) % 10000)

    # Background based on tone
    if any(t in prompt.lower() for t in ['gold', 'warm', 'sunny', 'bright', 'friendly', 'generous', 'peaceful']):
        _fill_warm_bg(img, rng)
    elif any(t in prompt.lower() for t in ['dark', 'night', 'mischiev', 'raid']):
        _fill_dark_bg(img, rng)
    elif any(t in prompt.lower() for t in ['blue', 'dew', 'rain', 'shower']):
        _fill_cool_bg(img, rng)
    else:
        _fill_neutral_bg(img, rng)

    # Event-specific content
    if fname == 'friendly_bees':
        _draw_bees(img, rng)
    elif fname == 'hidden_dewdrops':
        _draw_dewdrops_event(img, rng)
    elif fname == 'generous_woodpecker':
        _draw_woodpecker(img, rng)
    elif fname == 'shimmer_dust':
        _draw_shimmer_dust(img, rng)
    elif fname == 'hungry_caterpillars':
        _draw_caterpillars(img, rng)
    elif fname == 'static_storm':
        _draw_storm(img, rng)
    elif fname == 'termites':
        _draw_termites(img, rng)
    elif fname == 'mischievous_pixies':
        _draw_pixies(img, rng)
    elif fname == 'dew_shower':
        _draw_rain(img, rng)
    elif fname == 'sunbeam_blessing':
        _draw_sunbeams(img, rng)
    elif fname == 'root_tremor':
        _draw_tremor(img, rng)
    elif fname == 'caterpillar_swarm':
        _draw_swarm(img, rng)
    elif fname == 'falling_star':
        _draw_falling_star(img, rng)
    elif fname == 'sprite_wanders':
        _draw_wandering_sprite(img, rng)
    elif fname == 'market_mishap':
        _draw_market_mishap(img, rng)
    elif fname == 'pixie_raid':
        _draw_pixie_raid(img, rng)
    elif fname == 'peaceful_day':
        _draw_peaceful_day(img, rng)

    return img


def _fill_warm_bg(img, rng):
    W, H = img.size
    fill_rect(img, 0, 0, W, H, 'bg')
    scatter_pixels(img, 0, 0, W, H, 'gold_light', 0.05, seed=rng.randint(0, 9999))
    fill_rect(img, 0, H - 10, W, 10, 'forest_dark')

def _fill_dark_bg(img, rng):
    W, H = img.size
    fill_rect(img, 0, 0, W, H, 'magic_dark')
    scatter_pixels(img, 0, 0, W, H, 'magic', 0.05, seed=rng.randint(0, 9999))
    fill_rect(img, 0, H - 10, W, 10, 'forest_dark')

def _fill_cool_bg(img, rng):
    W, H = img.size
    fill_rect(img, 0, 0, W, H, 'dewshine')
    scatter_pixels(img, 0, 0, W, H, 'dewshine_light', 0.08, seed=rng.randint(0, 9999))
    fill_rect(img, 0, H - 10, W, 10, 'forest_dark')

def _fill_neutral_bg(img, rng):
    W, H = img.size
    fill_rect(img, 0, 0, W, H, 'forest')
    scatter_pixels(img, 0, 0, W, H, 'forest_light', 0.08, seed=rng.randint(0, 9999))
    fill_rect(img, 0, H - 10, W, 10, 'forest_dark')

def _draw_bees(img, rng):
    for _ in range(5):
        bx, by = rng.randint(10, 54), rng.randint(10, 44)
        fill_rect(img, bx, by, 4, 3, 'gold')
        fill_rect(img, bx + 1, by, 1, 3, 'brown_dark')
        px(img, bx + 2, by - 1, 'cream', 180)  # wing
        px(img, bx + 1, by - 1, 'cream', 180)
    # Golden pollen trail
    for _ in range(8):
        px(img, rng.randint(5, 59), rng.randint(5, 50), 'gold_light')

def _draw_dewdrops_event(img, rng):
    for _ in range(8):
        dx, dy = rng.randint(8, 56), rng.randint(15, 48)
        draw_circle(img, dx, dy, 2, 'dewshine_light')
        px(img, dx - 1, dy - 1, 'white')
    # Leaves
    for lx in [10, 30, 50]:
        fill_rect(img, lx, rng.randint(12, 20), 8, 2, 'forest')

def _draw_woodpecker(img, rng):
    cx = 32
    # Tree trunk
    fill_rect(img, 25, 5, 8, 54, 'brown')
    fill_rect(img, 25, 5, 3, 54, 'brown_light')
    # Bird
    draw_ellipse(img, 38, 20, 5, 4, 'red')
    draw_ellipse(img, 42, 20, 3, 3, 'cream')
    px(img, 45, 20, 'gold')  # beak
    px(img, 42, 19, 'eye_dark')
    # Logs falling
    for ly in [35, 42, 50]:
        fill_rect(img, 15 + rng.randint(-5, 5), ly, 8, 3, 'heartwood')

def _draw_shimmer_dust(img, rng):
    for _ in range(20):
        sx, sy = rng.randint(5, 59), rng.randint(5, 50)
        px(img, sx, sy, rng.choice(['shimmer', 'shimmer_light', 'white']))
    draw_circle(img, 32, 25, 10, 'shimmer', 60)
    draw_circle(img, 32, 25, 6, 'shimmer_light', 40)

def _draw_caterpillars(img, rng):
    for _ in range(4):
        cx = rng.randint(10, 50)
        cy = rng.randint(20, 50)
        for seg in range(5):
            draw_circle(img, cx + seg * 3, cy, 2, 'green_grass')
        px(img, cx, cy - 1, 'eye_dark')
    # Eaten petals
    for _ in range(5):
        px(img, rng.randint(5, 59), rng.randint(5, 35), 'rose_light')

def _draw_storm(img, rng):
    for _ in range(5):
        sx, sy = rng.randint(10, 54), rng.randint(5, 30)
        draw_line(img, sx, sy, sx + rng.randint(-3, 3), sy + rng.randint(5, 12), 'gold')
        px(img, sx, sy, 'white')
    # Dewdrops zapped
    for _ in range(4):
        dx, dy = rng.randint(10, 54), rng.randint(30, 50)
        draw_circle(img, dx, dy, 2, 'dewshine', 120)

def _draw_termites(img, rng):
    # Log pile
    for ly in range(30, 55, 4):
        fill_rect(img, 15, ly, 35, 3, 'heartwood')
        fill_rect(img, 15, ly, 35, 1, 'heartwood_light')
    # Termites
    for _ in range(8):
        tx, ty = rng.randint(16, 48), rng.randint(30, 54)
        px(img, tx, ty, 'brown_dark')
        px(img, tx + 1, ty, 'brown_dark')

def _draw_pixies(img, rng):
    for _ in range(4):
        px_x, py = rng.randint(10, 50), rng.randint(10, 40)
        draw_circle(img, px_x, py, 3, 'magic_dark')
        px(img, px_x - 1, py - 1, 'shimmer_light')
        px(img, px_x + 1, py - 1, 'shimmer_light')
        # Stolen crystal
        px(img, px_x, py + 5, 'shimmer')
        px(img, px_x, py + 6, 'shimmer')

def _draw_rain(img, rng):
    for _ in range(30):
        rx, ry = rng.randint(0, 63), rng.randint(0, 55)
        draw_line(img, rx, ry, rx - 1, ry + 3, 'dewshine_light')
    for _ in range(5):
        draw_circle(img, rng.randint(10, 54), rng.randint(40, 55), 2, 'dewshine', 100)

def _draw_sunbeams(img, rng):
    for ray_x in [15, 32, 50]:
        for y in range(0, 45):
            spread = y // 5
            fill_rect(img, ray_x - spread, y, spread * 2 + 1, 1, 'gold_light', 60)
    for _ in range(6):
        draw_flower_small(img, rng.randint(5, 59), rng.randint(40, 58), 'gold_light', 'nectar')

def _draw_tremor(img, rng):
    # Cracked ground
    fill_rect(img, 0, 35, 64, 29, 'brown')
    for cx_off in [20, 35, 48]:
        draw_line(img, cx_off, 35, cx_off + rng.randint(-5, 5), 63, 'brown_dark')
    # Falling leaves
    for _ in range(6):
        px(img, rng.randint(5, 59), rng.randint(5, 30), 'forest_light')
    # Shaking roots
    for rx in range(5, 60, 10):
        draw_line(img, rx, 35, rx + 3, 30, 'brown')

def _draw_swarm(img, rng):
    # Vegetation being eaten
    fill_rect(img, 0, 30, 64, 34, 'forest')
    fill_rect(img, 0, 30, 64, 5, 'forest_light')
    # Caterpillars swarming
    for _ in range(10):
        cx = rng.randint(5, 55)
        cy = rng.randint(25, 55)
        for seg in range(4):
            draw_circle(img, cx + seg * 2, cy, 1, 'green_grass')

def _draw_falling_star(img, rng):
    # Star trail
    draw_line(img, 55, 5, 20, 40, 'gold')
    draw_line(img, 56, 5, 21, 40, 'gold_light')
    # Sparkle burst
    for _ in range(10):
        dx, dy = rng.randint(-8, 8), rng.randint(-8, 8)
        px(img, 20 + dx, 40 + dy, rng.choice(['gold_light', 'shimmer_light', 'white']))
    draw_sparkle(img, 20, 40, 'white', 3)

def _draw_wandering_sprite(img, rng):
    cx = 32
    # Ghost sprite
    draw_circle(img, cx, 28, 6, 'cream')
    fill_rect(img, cx - 6, 28, 13, 10, 'cream')
    px(img, cx - 3, 26, 'eye_dark')
    px(img, cx + 2, 26, 'eye_dark')
    # Question marks
    _draw_pixel_char(img, cx - 10, 12, '?', 'gold', scale=1)
    _draw_pixel_char(img, cx + 8, 15, '?', 'gold', scale=1)

def _draw_market_mishap(img, rng):
    # Market stall
    fill_rect(img, 10, 20, 44, 30, 'brown')
    fill_rect(img, 10, 20, 44, 3, 'brown_light')
    # Knocked over barrels
    draw_ellipse(img, 20, 42, 5, 3, 'brown')
    draw_ellipse(img, 35, 45, 4, 3, 'brown')
    # Spilled goods
    for _ in range(8):
        px(img, rng.randint(15, 50), rng.randint(40, 55), rng.choice(['nectar', 'dewshine', 'gold']))

def _draw_pixie_raid(img, rng):
    # Dark scene with pixies
    for _ in range(5):
        px_x, py = rng.randint(8, 56), rng.randint(8, 40)
        draw_circle(img, px_x, py, 3, 'magic')
        px(img, px_x - 1, py - 1, 'white')
        px(img, px_x + 1, py - 1, 'white')
    # Mushroom market outline
    fill_rect(img, 20, 35, 24, 20, 'brown_dark')
    draw_ellipse(img, 32, 32, 15, 8, 'red_dark')

def _draw_peaceful_day(img, rng):
    # Butterflies
    for _ in range(4):
        bx, by = rng.randint(10, 54), rng.randint(10, 35)
        px(img, bx, by, rng.choice(['rose_light', 'dewshine_light', 'shimmer_light']))
        px(img, bx - 2, by - 1, rng.choice(['rose', 'dewshine', 'shimmer']))
        px(img, bx + 2, by - 1, rng.choice(['rose', 'dewshine', 'shimmer']))
    # Flowers
    for _ in range(6):
        draw_flower_small(img, rng.randint(5, 59), rng.randint(40, 58),
                         rng.choice(['rose_light', 'gold_light', 'dewshine_light']), 'gold')
    # Soft sunlight
    draw_circle(img, 50, 10, 8, 'gold_light', 50)


# ===================================================================
# 9. EFFECT / PARTICLE GENERATORS
# ===================================================================

def gen_effect(w, h, file_path, prompt):
    """Generate effects and particles."""
    fname = Path(file_path).stem
    img = new_image(w, h)
    cx, cy = w // 2, h // 2

    if fname == 'sparkle_1':
        draw_sparkle(img, cx, cy, 'white', min(w, h) // 2)
        px(img, cx, cy, 'gold_light')
    elif fname == 'sparkle_2':
        # Rotated 45 degrees
        s = min(w, h) // 2
        for i in range(1, s):
            px(img, cx + i, cy + i, 'white')
            px(img, cx - i, cy - i, 'white')
            px(img, cx + i, cy - i, 'white')
            px(img, cx - i, cy + i, 'white')
        px(img, cx, cy, 'gold_light')
    elif fname == 'sparkle_3':
        px(img, cx, cy, 'white')
        px(img, cx + 1, cy, 'white', 180)
        px(img, cx - 1, cy, 'white', 180)
        px(img, cx, cy + 1, 'white', 180)
        px(img, cx, cy - 1, 'white', 180)
    elif 'particle_' in fname:
        resource = fname.replace('particle_', '')
        color_map = {'nectar': 'nectar', 'dewshine': 'dewshine',
                     'heartwood': 'heartwood', 'shimmer': 'shimmer'}
        pc = color_map.get(resource, 'white')
        draw_circle(img, cx, cy, 2, pc)
        px(img, cx - 1, cy - 1, pc + '_light' if pc + '_light' in PALETTE else 'white')
    elif fname == 'glow_gold':
        _draw_glow(img, cx, cy, 'gold', 'gold_light')
    elif fname == 'glow_white':
        _draw_glow(img, cx, cy, 'white', 'cream')
    elif fname == 'poof':
        return _gen_poof(w, h)
    elif 'countdown_' in fname:
        char = fname.replace('countdown_', '').upper()
        if char == 'PICK':
            _draw_pixel_text(img, 4, h // 2 - 5, 'PICK!', 'gold', scale=2)
            draw_sparkle(img, 8, 8, 'gold_light', 3)
            draw_sparkle(img, w - 9, h - 9, 'gold_light', 3)
        else:
            _draw_pixel_char(img, w // 2 - 5, h // 2 - 7, char, 'forest', scale=3)
            # Vine decoration
            for vx in range(4, w - 4, 8):
                px(img, vx, 4, 'forest_light')
                px(img, vx, h - 5, 'forest_light')

    return img


def _draw_glow(img, cx, cy, inner, outer):
    """Draw a soft circular glow."""
    r = min(img.width, img.height) // 2
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= r:
                alpha = int(150 * (1 - dist / r) ** 2)
                if alpha > 5:
                    color = inner if dist < r * 0.4 else outer
                    px(img, cx + dx, cy + dy, color, alpha)


def _gen_poof(w, h):
    """Generate 128x32 4-frame poof animation."""
    img = new_image(w, h)
    frame_w = w // 4

    for i in range(4):
        fx = i * frame_w
        cx = fx + frame_w // 2
        cy = h // 2

        if i == 0:
            # Small burst
            draw_circle(img, cx, cy, 4, 'cream')
            draw_circle(img, cx, cy, 2, 'white')
        elif i == 1:
            # Expanding
            draw_circle(img, cx, cy, 8, 'cream', 200)
            draw_circle(img, cx, cy, 5, 'white', 180)
            scatter_pixels(img, cx - 10, cy - 10, 20, 20, 'gold_light', 0.1, seed=i)
        elif i == 2:
            # Full cloud
            draw_circle(img, cx, cy, 10, 'cream', 150)
            draw_circle(img, cx - 4, cy - 2, 6, 'white', 120)
            draw_circle(img, cx + 3, cy + 1, 5, 'white', 120)
            scatter_pixels(img, cx - 12, cy - 12, 24, 24, 'gold_light', 0.08, seed=i)
        elif i == 3:
            # Fading
            draw_circle(img, cx, cy, 12, 'cream', 60)
            scatter_pixels(img, cx - 14, cy - 14, 28, 28, 'gold_light', 0.05, seed=i)

    return img


# ===================================================================
# 10. TUTORIAL GENERATORS
# ===================================================================

def gen_tutorial(w, h, file_path, prompt):
    """Generate 128x128 tutorial illustrations."""
    fname = Path(file_path).stem
    img = new_image(w, h)
    W, H = img.size
    rng = random.Random(hash(fname) % 10000)

    if fname == 'phase_land_claim':
        # Bird's eye grid with fairies
        fill_rect(img, 0, 0, W, H, 'forest_dark')
        for row in range(5):
            for col in range(5):
                tx = 10 + col * 22
                ty = 10 + row * 22
                terrain_c = rng.choice(['forest', 'gray', 'water_blue'])
                fill_rect(img, tx, ty, 20, 20, terrain_c)
                outline_rect(img, tx, ty, 20, 20, 'forest_dark')
        # Fairy indicators
        for fc_name, fx, fy in [('rose', 20, 16), ('lilypad', 60, 38), ('fern', 82, 60), ('mushroom', 38, 82)]:
            draw_circle(img, fx, fy, 4, fc_name)

    elif fname == 'phase_outfitting':
        # Market interior with fairy
        fill_rect(img, 0, 0, W, H, 'brown')
        draw_ellipse(img, W // 2, 20, W // 2, 25, 'red_dark')
        # Shelves
        for sy in [50, 75, 100]:
            fill_rect(img, 10, sy, W - 20, 3, 'brown_light')
        # Fairy
        draw_circle(img, W // 2, 90, 6, 'rose')
        draw_circle(img, W // 2, 84, 5, 'skin')
        # Sprite
        draw_circle(img, W // 2 + 15, 85, 4, 'cream')

    elif fname == 'phase_tending':
        # Tiles with sparkle effects
        fill_rect(img, 0, 0, W, H, 'forest_dark')
        for row in range(3):
            for col in range(3):
                tx = 15 + col * 34
                ty = 15 + row * 34
                fill_rect(img, tx, ty, 30, 30, 'forest')
                # Sprite on tile
                draw_circle(img, tx + 15, ty + 15, 4, 'cream')
                # Sparkles
                draw_sparkle(img, tx + 8, ty + 5, 'gold_light', 2)

    elif fname == 'phase_market':
        # Vertical auction board
        fill_rect(img, 0, 0, W, H, 'bg')
        # Price ladder
        fill_rect(img, W // 2 - 3, 10, 6, H - 20, 'brown')
        for y in range(15, H - 15, 10):
            fill_rect(img, W // 2 - 8, y, 16, 2, 'brown_dark')
        # Fairy markers
        draw_circle(img, W // 3, 40, 5, 'rose')
        draw_circle(img, 2 * W // 3, 80, 5, 'lilypad')

    elif fname == 'phase_events':
        # Split scene: rain and sun
        fill_rect(img, 0, 0, W // 2, H, 'dewshine')
        fill_rect(img, W // 2, 0, W // 2, H, 'bg')
        # Rain side
        for _ in range(15):
            rx, ry = rng.randint(5, W // 2 - 5), rng.randint(5, H - 15)
            draw_line(img, rx, ry, rx - 1, ry + 4, 'dewshine_light')
        # Sun side
        draw_circle(img, 3 * W // 4, 20, 12, 'gold_light')
        for angle in range(0, 360, 30):
            dx = int(18 * math.cos(math.radians(angle)))
            dy = int(18 * math.sin(math.radians(angle)))
            draw_line(img, 3 * W // 4, 20, 3 * W // 4 + dx, 20 + dy, 'gold', 120)
        # Ground
        fill_rect(img, 0, H - 15, W, 15, 'forest_dark')

    elif fname == 'resource_overview':
        # 4 resources labeled
        fill_rect(img, 0, 0, W, H, 'bg')
        resources = [
            ('nectar', 'NECTAR', 20, 30),
            ('dewshine', 'DEW', 90, 30),
            ('heartwood', 'WOOD', 20, 80),
            ('shimmer', 'SHIM', 90, 80),
        ]
        for res_c, label, rx, ry in resources:
            draw_circle(img, rx, ry, 8, res_c)
            draw_circle(img, rx - 2, ry - 2, 3, res_c + '_light' if res_c + '_light' in PALETTE else 'white')
            _draw_pixel_text(img, rx - 10, ry + 12, label, 'outline', scale=1)

    return img


# ===================================================================
# 11. APP ICON GENERATOR
# ===================================================================

def gen_app_icon(w, h, file_path, prompt):
    """Generate app icon at various sizes."""
    # Generate at target size (will be pixel art scaled up)
    # Base design at 64x64, then scale
    base_size = 64
    base = new_image(base_size, base_size)

    # Forest green background
    fill_rect(base, 0, 0, base_size, base_size, 'forest')
    draw_rounded_rect(base, 2, 2, base_size - 4, base_size - 4, 'forest_dark')
    fill_rect(base, 4, 4, base_size - 8, base_size - 8, 'forest')

    # Mushroom
    cx = base_size // 2
    fill_rect(base, cx - 3, 35, 6, 18, 'cream')
    draw_ellipse(base, cx, 32, 14, 8, 'red')
    draw_ellipse(base, cx, 30, 12, 6, 'red')
    px(base, cx - 5, 28, 'white')
    px(base, cx + 4, 30, 'white')
    px(base, cx, 27, 'white')

    # Fairy silhouette
    draw_circle(base, cx, 18, 6, 'rose_light')
    draw_circle(base, cx, 14, 5, 'rose')
    # Wings
    draw_ellipse(base, cx - 8, 16, 4, 6, 'rose_light', 180)
    draw_ellipse(base, cx + 8, 16, 4, 6, 'rose_light', 180)

    # Sparkles
    draw_sparkle(base, 10, 10, 'gold_light', 2)
    draw_sparkle(base, base_size - 11, 12, 'gold_light', 2)
    draw_sparkle(base, 15, base_size - 12, 'shimmer_light', 2)
    draw_sparkle(base, base_size - 16, base_size - 10, 'shimmer_light', 2)

    # Scale up to target size using nearest neighbor (preserves pixel art)
    img = base.resize((w, h), Image.NEAREST)
    return img


def save_asset(img, output_path):
    """Save image to the output path, creating directories as needed."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"  Created: {output_path}")


# ---------------------------------------------------------------------------
# Markdown Parser
# ---------------------------------------------------------------------------

def parse_assets(md_path):
    """Parse graphics-assets.md and return list of (file_path, width, height, prompt)."""
    assets = []
    with open(md_path) as f:
        content = f.read()

    # Find all table rows with asset definitions
    # Pattern: | `path/file.png` | WxH | description |
    pattern = r'\|\s*`([^`]+\.png)`\s*\|\s*([^|]+)\|\s*([^|]+)\|'
    for m in re.finditer(pattern, content):
        file_path = m.group(1).strip()
        size_str = m.group(2).strip()
        prompt = m.group(3).strip()

        # Parse size - handle "WxH", "9-slice", sprite sheets
        w, h = 32, 32  # default
        if '9-slice' in size_str.lower():
            w, h = 48, 48  # reasonable 9-slice base
        else:
            size_match = re.search(r'(\d+)\s*x\s*(\d+)', size_str)
            if size_match:
                w = int(size_match.group(1))
                h = int(size_match.group(2))

        # Check for sprite sheet (e.g., "4-frame sprite sheet (128x48)")
        sheet_match = re.search(r'(\d+)-frame.*\((\d+)x(\d+)\)', prompt)
        if sheet_match:
            w = int(sheet_match.group(2))
            h = int(sheet_match.group(3))

        assets.append((file_path, w, h, prompt))

    return assets


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    md_path = project_dir / 'docs' / 'plans' / 'graphics-assets.md'
    output_dir = project_dir / 'assets' / 'images'

    if not md_path.exists():
        print(f"Error: {md_path} not found")
        return 1

    print(f"Parsing asset spec: {md_path}")
    assets = parse_assets(str(md_path))
    print(f"Found {len(assets)} assets to generate\n")

    generated = 0
    skipped = 0

    for file_path, w, h, prompt in assets:
        out_path = output_dir / file_path
        gen_func = get_generator(file_path, prompt)
        if gen_func:
            try:
                img = gen_func(w, h, file_path, prompt)
                save_asset(img, str(out_path))
                generated += 1
            except Exception as e:
                print(f"  ERROR generating {file_path}: {e}")
                skipped += 1
        else:
            print(f"  SKIP (no generator): {file_path}")
            skipped += 1

    print(f"\nDone! Generated: {generated}, Skipped: {skipped}")
    return 0


def get_generator(file_path, prompt):
    """Route a file path to its generator function."""
    parts = file_path.split('/')
    category = parts[0] if parts else ''

    if category == 'fairies':
        return gen_fairy
    elif category == 'sprites':
        return gen_sprite
    elif category == 'terrain':
        return gen_terrain
    elif category == 'resources':
        return gen_resource
    elif category == 'screens':
        return gen_screen
    elif category == 'market':
        return gen_market
    elif category == 'ui':
        return gen_ui
    elif category == 'events':
        return gen_event
    elif category == 'effects':
        return gen_effect
    elif category == 'tutorial':
        return gen_tutorial
    elif category == 'app_icon':
        return gen_app_icon
    return None


if __name__ == '__main__':
    exit(main())
