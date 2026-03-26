# Darkdell Personal Site — Design Spec

## Overview

Replace the current Hugo-based blog at darkdell.net with a hand-rolled personal site powered by a minimal Python static site generator. The site features three switchable themes, the flagship being "Consumed" — a dark, living theme whose background runs an ant colony optimization simulation that renders pheromone trails as subtle color gradients. The site's visual vitality is linked to how recently it's been posted to, making it a kind of digital Tamagotchi fed by writing.

**Audience:** The author (Nathan). No one else is expected to read this. The blog exists as a tool for processing and internalizing evening learning sessions — pomodoro-sized chunks of reading (Stafford Beer, Kleppmann, MathAcademy, etc.) followed by reflective writing. The tone is unhinged and personal.

**Deployment target:** S3 bucket `darkdell.www` → CloudFront distribution `ERL3QRNQL3Q5K` → `darkdell.net` / `www.darkdell.net`.

## 1. Static Site Generator (`build.py`)

A single Python script, approximately 150–200 lines. One external dependency: `markdown` (for rendering). Everything else is stdlib.

### What it does

1. Globs `content/posts/*.md` and `content/pages/*.md`
2. For each file:
   - Extracts the title from the first `# heading` (falls back to a humanized filename)
   - Gets the date from the file's mtime
   - Renders markdown to HTML
   - Wraps the result in `templates/base.html` using Python string templating
3. Sorts posts reverse-chronologically by mtime
4. Generates the blog index page (`/blog/index.html`)
5. Generates page-level routes (`/index.html`, `/projects/index.html`, `/reading/index.html`)
6. Bakes `lastPostDate` (ISO 8601) into every page as a `<meta>` tag or JS variable — used by the living background for vitality calculation
7. Copies `static/` contents to `public/` as-is
8. Copies theme assets (CSS, JS) to `public/themes/`
9. Writes all output to `public/`

### Content authoring

- Posts are markdown files in `content/posts/`. No frontmatter required.
- Title: first `# heading` in the file. If absent, derived from filename (`b-trees.md` → "B Trees").
- Date: file mtime. No manual date entry.
- Optional YAML frontmatter supported but never required. Can override `title` and `date` if desired.
- Pages work identically but live in `content/pages/`.

### Templates

A single `templates/base.html` containing:
- HTML boilerplate, `<head>` with theme CSS link
- Navigation (site name + links to blog, projects, reading)
- Content block (replaced per page)
- Theme switcher widget
- Theme JS (switcher logic + Consumed's `ants.js`)
- The `lastPostDate` baked in as a JS variable

## 2. Theme System

Three themes, switchable via a small toggle in the bottom corner of every page. Current theme persisted in localStorage. Consumed is the default.

### Consumed (living theme)

The flagship. Dark background, monospace typography, CRT-inspired aesthetic with a living ant colony simulation painting the background.

**Typography:**
- Monospace font stack: `'SF Mono', 'Fira Code', 'Cascadia Code', monospace`
- Warm neutral text color (parchment-like, ~`#d4b8a8`) that stays readable against any background state
- Subtle phosphor glow on headings via `text-shadow`
- Navigation: small, uppercase, letter-spaced, muted until hovered

**Background:**
- Near-black base (`#0a0808`)
- Optional subtle CRT scanlines via CSS `repeating-linear-gradient` (2–4px pitch, very low opacity)
- The ant colony canvas renders behind all content (see Section 3)

**Layout:**
- Single column, generous margins
- Max content width ~640px, centered
- Lots of vertical whitespace between elements

### Garish (GeoCities fever dream)

Static theme — no living background.

- Comic Sans MS as primary font
- Rainbow gradient background (animated CSS `background-size` cycling)
- Marquee tags for announcements
- Visitor counter (localStorage-based)
- Neon colored navigation pills
- Dashed borders, border-radius everywhere
- "Under construction" energy
- Emoji flourishes

### Clean (readable)

Static theme — no living background.

- Serif headings (Georgia), sans-serif body (system font stack)
- Light background (`#fafafa`), dark text (`#222`)
- Minimal decoration — just typography and whitespace
- Thin rule separators
- The "I need to find something I wrote at 2am" theme

### Switcher widget

- Fixed position, bottom corner
- Shows current theme name or a small icon
- Click to cycle: Consumed → Garish → Clean → Consumed
- On switch: updates `<link>` href to new theme CSS, saves to localStorage, starts/stops ant simulation as needed
- On page load: reads localStorage, applies saved theme before first paint (inline `<script>` in `<head>` to avoid flash)

## 3. Living Background — Ant Colony Pheromone Renderer

A simplified ant colony optimization simulation running on a `<canvas>` element behind the page content. Consumed theme only.

### Simulation

- **Grid:** ~128×64 cells mapped to the viewport
- **Ants:** 50–100 invisible agents (count varies with vitality)
- **Hive:** One invisible hive location, randomized per page load
- **Food sources:** Several invisible food locations, randomized per page load. When depleted, trails to them fade. New sources spawn slowly over time.
- **Pheromone channels:** 2–3 channels, each mapped to a color from the palette (vermilion, aubergine, deep indigo, crimson). Pheromone values 0–255 per cell per channel.
- **Pheromone decay:** Linear (subtract fixed amount per tick), matching the ants project's model. Trails fade over ~30–60 seconds of real time.
- **Ant behavior:** Simple foraging loop — wander randomly, sense food, pick up, follow pheromones home, deposit, mark trail. No complex VM — just a few behavioral states.

### Rendering

- Full-viewport `<canvas>` with `position: fixed; z-index: -1`
- Each cell's pheromone intensity → pixel color at low alpha
- CSS `filter: blur(8–12px)` on the canvas for soft glow effect
- Colors are from a warm palette: vermilion (`#c54030`), aubergine (`#5a1040`), deep indigo (`#1a0040`), crimson (`#8a1020`) — but rendered at very low opacity so they appear as subtle glows
- `requestAnimationFrame` loop, targeting ~30fps for simulation ticks
- Canvas resolution can be lower than viewport (e.g., 1 cell = 4–8px) for performance

### Vitality system

The site's "health" affects the simulation's behavior:

- `build.py` bakes `lastPostDate` into every page
- On page load, JS calculates vitality: `v = max(0, 1 - daysSinceLastPost / maxDays)` where `maxDays` is ~60 (tunable)
- Vitality controls:
  - **Ant count:** 100 at v=1.0, down to ~5 at v=0.0
  - **Pheromone intensity cap:** Full range at v=1.0, muted at low vitality
  - **Color saturation:** Rich at v=1.0, near-grayscale at v=0.0
  - **Food spawn rate:** Active at v=1.0, near-zero at v=0.0
- The site is never fully dead — even at v=0.0, a few ants wander with dim trails. A single ember.
- Visitor "nourishment": each page view could give a small temporary vitality boost (localStorage counter, decays over time). No server-side tracking.

### Performance constraints

- 50–100 ants on 128×64 grid is trivially cheap — no Web Workers or WebGL needed
- Plain Canvas 2D API
- CSS blur handles the glow (GPU-accelerated on modern browsers)
- `prefers-reduced-motion` media query: disable animation entirely, show a static subtle gradient instead
- Mobile: reduce ant count and grid resolution

## 4. Site Structure

### URL structure

```
darkdell.net/                  → landing page
darkdell.net/blog/             → reverse-chron post list
darkdell.net/blog/some-post/   → individual post
darkdell.net/projects/         → project list
darkdell.net/reading/          → bookshelf / current reading
```

### Source layout

```
darkdell/
  content/
    pages/
      index.md              → landing page content
      projects.md           → projects page
      reading.md            → bookshelf
    posts/
      *.md                  → blog posts (just write, no frontmatter)
  templates/
    base.html               → single HTML template
  themes/
    consumed/
      style.css             → consumed theme styles
      ants.js               → ACO simulation + canvas renderer
    garish/
      style.css             → garish theme styles
    clean/
      style.css             → clean theme styles
  static/                   → images, fonts, etc. (copied as-is to public/)
  build.py                  → static site generator
  Makefile                  → build + deploy targets
  public/                   → generated output (gitignored)
```

### What gets removed

- `hugo.toml`
- `themes/hugo-bearcub/` (already empty)
- `archetypes/`
- `layouts/` (Hugo overrides)
- Hugo as a dependency entirely

## 5. Build & Deploy

### Makefile targets

```makefile
build:        python build.py
serve:        python -m http.server -d public 8000
deploy:       build + s3 sync + cloudfront invalidation
new:          create a new post file, open in $EDITOR (optional convenience)
```

### Deploy command

```bash
python build.py
aws s3 sync public/ s3://darkdell.www --delete
aws cloudfront create-invalidation --distribution-id ERL3QRNQL3Q5K --paths "/*"
```

### Dependencies

- Python 3.x
- `markdown` Python package (pip install)
- AWS CLI (already configured)
- No Node.js, no npm, no Hugo, no framework

## Non-goals

- SEO, analytics, social sharing, comments, RSS (can add RSS later if wanted)
- Server-side anything
- Mobile-specific design (responsive is fine, but no native app thinking)
- Perfect cross-browser support for IE/legacy
- Professional polish — this is a personal playground
