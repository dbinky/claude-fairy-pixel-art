# Claude-Generated Pixel Art Pipeline

A complete example of using Claude to generate all pixel art assets for a game — from writing the asset spec, to building a Python generator script, to creating a browser-based pixel editor for touch-ups. Every image in [Fairy Frontier](https://github.com/dbinky/FairyFrontier) (a M.U.L.E.-inspired turn-based strategy game built in Flutter) was produced this way, with zero traditional art tools.

## Background

I'm a solo developer working on a fairy-themed economic strategy game. I can't draw. At all. Rather than struggle with AI image generators (which produce inconsistent styles, wrong sizes, and no transparency), I took a different approach: I had Claude write a Python script that draws every asset pixel-by-pixel using Pillow. The result is 163 PNG files with a consistent 8-bit art style, proper alpha channels, exact pixel dimensions, and deterministic output — run the script again, get the same images.

This repo contains the three key files from that process, shared so others can see how it works and adapt the approach for their own games.

## How It Was Made

This pipeline was built across several Claude Code sessions over two days. Here's the actual sequence:

### Step 1: Write the Asset Spec (conversation 1)

I asked Claude to create a comprehensive checklist of every pixel art asset the game would need. I described the game mechanics, the four fairy characters, the resource types, the market system, and so on. Claude produced `graphics-assets.md` — a structured markdown document defining all 163 assets organized into 12 categories, with:

- **File paths** (e.g., `fairies/rose_portrait.png`)
- **Pixel dimensions** (e.g., `48x48`, `128x48` for 4-frame sprite sheets)
- **Descriptive prompts** (e.g., "Pink fairy with rose petal wings and a flower crown, front-facing portrait, 8-bit pixel art, warm expression")
- **A color palette reference** with hex codes for every fairy, resource, and UI element

This document became the single source of truth for the entire art pipeline.

### Step 2: Establish the Art Style (conversation 2, Claude Desktop)

Before generating everything programmatically, I used Claude Desktop's artifact system to create a reference sprite — a 48x48 Rose fairy portrait drawn interactively in a React pixel editor. This established the visual language: dark outlines (`#5C3A4E`), 2-3 shading levels per area, large expressive eyes, cute proportions. The pixel editor (included here as `pixel-editor.jsx`) was built during this step and ships with that reference sprite as its default.

### Step 3: Generate All Assets (conversation 3)

This was the key prompt:

> Build me a python script (scripts/generate-art.py) that will go through the markdown file and generate all of the png files inside of assets/images/. We want super cute 8-bit art appropriate for a cozy game (think stardew valley). Think really hard about how to build the script so that — based on the short descriptions in the md spec file — you can create 8-bit pixel art that is creative, consistently themed, and maximally cute. Don't forget that these are PNGs, too, so character sprites for gameplay, be sure to correctly use the alpha channel.

Claude produced the entire `generate-art.py` script (~2,700 lines) in one session. It generated all 163 assets on the first run.

### Step 4: Integration (conversations 4-5)

Subsequent sessions planned and executed the integration of all 163 assets into the Flutter game, replacing placeholder emoji and colored boxes across every screen and widget.

## What's in This Repo

### `graphics-assets.md` — The Asset Specification

A structured markdown document defining all 163 game assets across 12 categories:

| Category | Count | Examples |
|----------|-------|---------|
| Fairy characters | 35 | Portraits, walk cycles (4-dir sprite sheets), idle, carry, icons |
| Sprites (workers) | 12 | Ghost creatures in various states and resource tints |
| Map tiles | 18 | 3 terrain types x 3 variants, border overlays, market |
| Resource icons | 15 | 5 resources x 3 sizes (16/24/32px) |
| Screens | 8 | Splash, menu, victory/defeat banners, logo |
| Market interior | 9 | Stations, corrals, fortune teller booth |
| Auction UI | 7 | Price ladder, bid/ask markers, trader tokens |
| HUD/UI chrome | 18 | Buttons, panels, timer bars, navigation icons |
| Events | 17 | Personal and grove event illustrations |
| Effects | 14 | Sparkles, particles, glows, countdown numbers |
| Tutorial | 6 | Phase illustrations, resource overview |
| App icons | 4 | 180px through 1024px |

Each asset has a file path, pixel dimensions, and a text description that the generator uses to determine what to draw.

### `generate-art.py` — The Generator Script

A self-contained Python script that reads the markdown spec and generates every PNG. Here's how it's structured:

**Color Palette** (lines 24-97) — 60+ named colors with light/dark variants. Every color in the game is defined here once and referenced by name throughout the script:

```python
PALETTE = {
    'rose':         '#E85D75',
    'rose_light':   '#FF9EAE',
    'rose_dark':    '#C44569',
    # ... 60+ colors
}
```

**Drawing Primitives** (lines 142-245) — Low-level pixel manipulation functions:

- `px()` / `px_rgba()` — set individual pixels by palette name or RGBA tuple
- `fill_rect()`, `draw_ellipse()`, `draw_circle()` — filled shapes
- `outline_rect()`, `outline_ellipse()` — shape outlines
- `draw_line()` — Bresenham's line algorithm
- `draw_dither()` — checkerboard dithering
- `scatter_pixels()` — random pixel placement (seeded for determinism)
- `draw_sparkle()` — 4-pointed star effect
- `mirror_h()` — horizontal flip

**Composite Helpers** (lines 252-452) — Reusable components built from primitives:

- `draw_cute_eyes()` — eyes with white highlights
- `draw_ghost_body()` — the ghost-like sprite workers with wavy bottoms
- `draw_tree_small()`, `draw_flower_small()`, `draw_rock()` — terrain elements
- `draw_water_tile()` — animated-looking water

**11 Category Generators** (lines 454-2601) — Each asset category has a dedicated generator that interprets file names and prompts:

| Function | What It Draws |
|----------|--------------|
| `gen_fairy()` | Routes to portrait/idle/walk/carry/icon sub-generators; uses template + color substitution so all 4 fairy types share body structure but have unique headpieces |
| `gen_sprite()` | Ghost workers with resource-specific tints and accessories |
| `gen_terrain()` | Procedural terrain tiles using seeded random for reproducible variants |
| `gen_resource()` | Resource icons at 3 size tiers |
| `gen_screen()` | Full-screen backgrounds and banners with custom pixel font text |
| `gen_market()` | Market interior stations and trading UI elements |
| `gen_ui()` | Buttons, panels, timer bars (9-slice aware) |
| `gen_event()` | 17 unique event illustrations |
| `gen_effect()` | Sparkles, particles, glow circles, animated poof sheet |
| `gen_tutorial()` | Tutorial illustrations compositing multiple elements |
| `gen_app_icon()` | Renders at 64x64 then scales up with nearest-neighbor to preserve pixel crispness |

**Markdown Parser** (lines 2615-2647) — Extracts assets from the spec using regex, handling dimensions, 9-slice markers, and sprite sheet sizes embedded in prompts.

**Router** (lines 2690-2717) — Maps file path prefixes to generator functions:

```python
def get_generator(file_path, prompt):
    parts = file_path.split('/')
    category = parts[0] if parts else ''
    if category == 'fairies': return gen_fairy
    elif category == 'sprites': return gen_sprite
    # ... 11 categories
```

### `pixel-editor.jsx` — Browser-Based Pixel Editor

A React component ("Pixel Forge") for manual touch-up of generated assets. Features:

- Canvas-based drawing with configurable grid (up to 128x128)
- **Tools**: Draw, Erase, Flood Fill, Color Picker
- **Palettes**: PICO-8 default palette + the game's custom palette with named colors
- Custom color management
- Undo/redo (Ctrl+Z / Ctrl+Shift+Z)
- PNG export at configurable scale with `imageSmoothingEnabled = false`
- Ships pre-loaded with the Rose fairy portrait that established the art style

To use it, drop it into any React project or render it in a tool like [Claude Desktop](https://claude.ai/download) artifacts.

## How to Use It

### Prerequisites

- Python 3.8+
- Pillow (`pip install Pillow`)

### Running the Generator

```bash
# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install Pillow

# Run the generator
python generate-art.py
```

The script expects `graphics-assets.md` to be at `../docs/plans/graphics-assets.md` relative to the script (this is because it lived in `scripts/` in the original project). You'll want to adjust the paths in `main()` for your own project:

```python
def main():
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    md_path = project_dir / 'docs' / 'plans' / 'graphics-assets.md'  # <-- adjust this
    output_dir = project_dir / 'assets' / 'images'                    # <-- and this
```

The script creates all output directories automatically and prints progress as it goes:

```
Parsing asset spec: /path/to/graphics-assets.md
Found 163 assets to generate

  Created: assets/images/fairies/rose_portrait.png
  Created: assets/images/fairies/rose_idle.png
  ...

Done! Generated: 163, Skipped: 0
```

## Adapting This for Your Own Game

The general approach works for any 2D game with pixel art:

1. **Write your asset spec first.** Define every asset you need in a structured document — file path, dimensions, and a short description. This forces you to think through your full asset list before drawing anything, and gives Claude the context it needs to generate coherent code.

2. **Establish your color palette.** Define all your colors in one place with named variants (primary, light, dark). Consistent palette = consistent look.

3. **Start with a reference piece.** Use the pixel editor (or any tool) to manually create one key asset that establishes your style. Show it to Claude when asking for the generator script.

4. **Ask Claude to write the generator.** Give it your asset spec, your color palette, your reference art, and describe the vibe you're going for. The key insight is asking Claude to write *code that draws*, not asking it to *generate images*. Claude is much better at writing precise pixel-placement code than it is at generating images through other means.

5. **Iterate.** The script is deterministic — if you don't like how something looks, you can read the specific generator function, understand the pixel logic, and ask Claude to adjust it. You can also use the pixel editor for manual touch-ups on individual assets.

### Key Design Decisions Worth Copying

- **Palette-by-name**: Reference colors as `'rose_light'` not `'#FF9EAE'`. Change a hex value once, everything updates.
- **Template + color substitution**: The four fairy types share one body template with per-fairy color dictionaries and unique headpiece functions. This keeps characters consistent while allowing variation.
- **Seeded randomness**: Terrain generators use `random.Random(seed)` so the output is reproducible. Same seed = same rocks, same flowers, same tree placement.
- **Nearest-neighbor scaling**: App icons are drawn at a small base size (64x64) and scaled up with `Image.NEAREST` — this preserves the pixel art look at any resolution.
- **RGBA throughout**: Every image uses RGBA mode. Character sprites have transparent backgrounds. This is critical for compositing in a game engine.

## What This Is NOT

This is not an AI image generator. There's no neural network, no diffusion model, no API call. It's a hand-written Python script that places pixels using math and logic. Claude wrote the script, but the script itself is just Pillow `putpixel()` calls, Bresenham's line algorithm, ellipse math, and a lot of carefully chosen coordinates.

The "AI" part is that Claude understood descriptions like "cute ghost-like sprite with tiny golden pollen baskets" and translated them into specific pixel arrangements. Once the script exists, it runs deterministically with no AI involvement.

## License

MIT — see [LICENSE](LICENSE).
