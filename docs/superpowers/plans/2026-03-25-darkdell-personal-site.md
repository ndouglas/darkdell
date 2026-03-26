# Darkdell Personal Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Hugo-based blog at darkdell.net with a hand-rolled Python SSG featuring three switchable themes, including a living ant colony pheromone background.

**Architecture:** A single `build.py` script renders markdown content into HTML using a shared template, copies theme assets, and outputs to `public/`. The Consumed theme runs a client-side ACO simulation on a background canvas whose vitality is linked to post recency. Two static themes (Garish, Clean) provide alternatives. Deploy is `aws s3 sync` + CloudFront invalidation.

**Tech Stack:** Python 3 + `markdown` + `pyyaml`, vanilla JS (Canvas 2D API), CSS, AWS CLI, Make.

**Spec:** `docs/superpowers/specs/2026-03-25-darkdell-personal-site-design.md`

---

## File Structure

```
darkdell/
  build.py                          # SSG: globs content, renders markdown, writes HTML
  Makefile                          # build, serve, deploy, new-post targets
  requirements.txt                  # markdown, pyyaml
  templates/
    base.html                       # single HTML template with theme switcher
  themes/
    consumed/
      style.css                     # dark theme + CRT scanlines
      ants.js                       # ACO simulation + canvas pheromone renderer
    garish/
      style.css                     # GeoCities fever dream
    clean/
      style.css                     # readable light theme
    switcher.js                     # theme switching logic (shared across themes)
  content/
    pages/
      index.md                      # landing page
      projects.md                   # projects listing
      reading.md                    # bookshelf
    posts/                          # blog posts (just .md files)
  static/                           # copied as-is to public/
  tests/
    test_build.py                   # build.py unit tests
  public/                           # generated output (gitignored)
```

---

### Task 1: Clean up Hugo and set up project scaffolding

Remove Hugo artifacts and create the new directory structure.

**Files:**
- Remove: `hugo.toml`, `archetypes/`, `layouts/`, `themes/hugo-bearcub/`, `.hugo_build.lock`, `.gitmodules`, `public/`
- Create: `requirements.txt`, `Makefile`, `templates/`, `themes/consumed/`, `themes/garish/`, `themes/clean/`, `content/pages/`, `content/posts/`, `static/`, `tests/`
- Modify: `.gitignore`

- [ ] **Step 1: Remove Hugo files**

```bash
rm -f hugo.toml .hugo_build.lock .gitmodules
rm -rf archetypes/ layouts/ themes/hugo-bearcub/ public/
```

- [ ] **Step 2: Create new directory structure**

```bash
mkdir -p templates themes/consumed themes/garish themes/clean content/pages content/posts static tests
```

- [ ] **Step 3: Create requirements.txt**

```
markdown
pyyaml
```

- [ ] **Step 4: Update .gitignore**

```
.superpowers/
public/
__pycache__/
*.pyc
.venv/
```

- [ ] **Step 5: Create Makefile**

```makefile
.PHONY: build serve deploy new

build:
	python build.py

serve: build
	python -m http.server -d public 8000

deploy: build
	aws s3 sync public/ s3://darkdell.www --delete
	aws cloudfront create-invalidation --distribution-id ERL3QRNQL3Q5K --paths "/*"

new:
	@read -p "Post slug: " slug; \
	touch "content/posts/$$slug.md"; \
	echo "# $$slug" > "content/posts/$$slug.md"; \
	$${EDITOR:-vim} "content/posts/$$slug.md"
```

- [ ] **Step 6: Install dependencies**

```bash
pip install markdown pyyaml
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "Remove Hugo, scaffold new project structure"
```

---

### Task 2: Build the static site generator — content parsing

Core of `build.py`: parse markdown files, extract title/date, handle optional frontmatter.

**Files:**
- Create: `build.py`
- Create: `tests/test_build.py`

- [ ] **Step 1: Write failing tests for content parsing**

```python
# tests/test_build.py
import os
import tempfile
import time
from pathlib import Path

import pytest


def test_extract_title_from_heading():
    """Title comes from first # heading."""
    from build import parse_content
    result = parse_content("# My Great Post\n\nSome content here.")
    assert result["title"] == "My Great Post"


def test_extract_title_from_filename():
    """When no heading, title is derived from filename."""
    from build import parse_content
    result = parse_content("Just some content, no heading.", filename="b-trees-are-neat.md")
    assert result["title"] == "B Trees Are Neat"


def test_frontmatter_overrides_title():
    """YAML frontmatter title takes precedence."""
    from build import parse_content
    content = "---\ntitle: Custom Title\n---\n# Heading Title\n\nBody."
    result = parse_content(content)
    assert result["title"] == "Custom Title"


def test_frontmatter_overrides_date():
    """YAML frontmatter date takes precedence over mtime."""
    from build import parse_content
    content = "---\ndate: 2026-01-15\n---\n# Post\n\nBody."
    result = parse_content(content)
    assert result["date"].year == 2026
    assert result["date"].month == 1
    assert result["date"].day == 15


def test_markdown_renders_to_html():
    """Markdown content is rendered to HTML."""
    from build import parse_content
    result = parse_content("# Title\n\nHello **world**.")
    assert "<strong>world</strong>" in result["html"]


def test_no_frontmatter_works():
    """A bare markdown file with no frontmatter parses fine."""
    from build import parse_content
    result = parse_content("# Simple\n\nJust text.")
    assert result["title"] == "Simple"
    assert "Just text." in result["html"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/nathan/Projects/ndouglas/darkdell
python -m pytest tests/test_build.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `build` module doesn't exist yet.

- [ ] **Step 3: Implement parse_content in build.py**

```python
#!/usr/bin/env python3
"""Static site generator for darkdell.net."""

import re
from datetime import datetime
from pathlib import Path

import markdown
import yaml


def parse_content(raw: str, filename: str = "untitled.md", mtime: float | None = None) -> dict:
    """Parse a markdown file, extracting title, date, and rendered HTML.

    Title priority: frontmatter > first # heading > humanized filename.
    Date priority: frontmatter > mtime > now.
    """
    frontmatter = {}
    body = raw

    # Extract optional YAML frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)", raw, re.DOTALL)
    if fm_match:
        frontmatter = yaml.safe_load(fm_match.group(1)) or {}
        body = fm_match.group(2)

    # Extract title
    title = frontmatter.get("title")
    if not title:
        heading_match = re.match(r"^#\s+(.+)$", body, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
        else:
            title = _humanize_filename(filename)

    # Extract date
    date = None
    if "date" in frontmatter:
        d = frontmatter["date"]
        if isinstance(d, datetime):
            date = d
        else:
            date = datetime.fromisoformat(str(d))
    elif mtime is not None:
        date = datetime.fromtimestamp(mtime)
    else:
        date = datetime.now()

    # Render markdown to HTML
    html = markdown.markdown(body, extensions=["fenced_code", "codehilite", "tables"])

    return {"title": title, "date": date, "html": html, "frontmatter": frontmatter}


def _humanize_filename(filename: str) -> str:
    """Convert 'b-trees-are-neat.md' to 'B Trees Are Neat'."""
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ").title()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_build.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "Add content parser: markdown rendering, frontmatter, title/date extraction"
```

---

### Task 3: Build the static site generator — site assembly

Add the functions that glob content, render pages through templates, and write `public/`.

**Files:**
- Modify: `build.py`
- Modify: `tests/test_build.py`
- Create: `templates/base.html` (minimal, just enough for tests)

- [ ] **Step 1: Write failing tests for site assembly**

Add to `tests/test_build.py`:

```python
def test_build_creates_post_html(tmp_site):
    """Building produces HTML files for posts."""
    from build import build_site
    build_site(tmp_site)
    output = tmp_site / "public" / "blog" / "hello-world" / "index.html"
    assert output.exists()
    assert "Hello World" in output.read_text()


def test_build_creates_blog_index(tmp_site):
    """Building produces a blog index page listing posts."""
    from build import build_site
    build_site(tmp_site)
    index = tmp_site / "public" / "blog" / "index.html"
    assert index.exists()
    content = index.read_text()
    assert "Hello World" in content


def test_build_creates_page_html(tmp_site):
    """Building produces HTML files for pages."""
    from build import build_site
    build_site(tmp_site)
    output = tmp_site / "public" / "index.html"
    assert output.exists()
    assert "Welcome" in output.read_text()


def test_posts_sorted_reverse_chron(tmp_site):
    """Blog index lists posts newest first."""
    from build import build_site
    import time

    # Create two posts with different mtimes
    post_old = tmp_site / "content" / "posts" / "old-post.md"
    post_old.write_text("# Old Post\n\nOld content.")
    time.sleep(0.1)
    post_new = tmp_site / "content" / "posts" / "new-post.md"
    post_new.write_text("# New Post\n\nNew content.")

    build_site(tmp_site)
    index_html = (tmp_site / "public" / "blog" / "index.html").read_text()
    assert index_html.index("New Post") < index_html.index("Old Post")


def test_build_bakes_last_post_date(tmp_site):
    """Built pages contain lastPostDate as a JS variable."""
    from build import build_site
    build_site(tmp_site)
    index = (tmp_site / "public" / "index.html").read_text()
    assert "lastPostDate" in index


def test_build_copies_static_files(tmp_site):
    """Static files are copied to public/ as-is."""
    from build import build_site
    (tmp_site / "static").mkdir(exist_ok=True)
    (tmp_site / "static" / "photo.jpg").write_bytes(b"fake image")
    build_site(tmp_site)
    assert (tmp_site / "public" / "photo.jpg").exists()


def test_build_copies_theme_assets(tmp_site):
    """Theme CSS/JS files are copied to public/themes/."""
    from build import build_site
    build_site(tmp_site)
    assert (tmp_site / "public" / "themes" / "consumed" / "style.css").exists()


@pytest.fixture
def tmp_site(tmp_path):
    """Create a minimal site directory for testing."""
    # Content
    pages = tmp_path / "content" / "pages"
    pages.mkdir(parents=True)
    (pages / "index.md").write_text("# Welcome\n\nThis is the landing page.")

    posts = tmp_path / "content" / "posts"
    posts.mkdir(parents=True)
    (posts / "hello-world.md").write_text("# Hello World\n\nFirst post.")

    # Template
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "base.html").write_text(
        '<html><head><script>var lastPostDate = "${last_post_date}";</script></head>'
        "<body>${nav}${content}</body></html>"
    )

    # Theme stubs
    for theme in ("consumed", "garish", "clean"):
        d = tmp_path / "themes" / theme
        d.mkdir(parents=True)
        (d / "style.css").write_text(f"/* {theme} */")
    (tmp_path / "themes" / "consumed" / "ants.js").write_text("// ants")

    return tmp_path
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_build.py -v
```

Expected: New tests fail — `build_site` doesn't exist yet.

- [ ] **Step 3: Create minimal base.html template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title} — Nathan Douglas</title>
  <script>
    (function() {
      var theme = localStorage.getItem('theme') || 'consumed';
      document.documentElement.setAttribute('data-theme', theme);
      document.write('<link id="theme-css" rel="stylesheet" href="/themes/' + theme + '/style.css">');
    })();
  </script>
  <script>var lastPostDate = "${last_post_date}";</script>
</head>
<body>
  <nav>
    <a href="/" class="site-name">Nathan Douglas</a>
    <div class="nav-links">
      <a href="/blog/">blog</a>
      <a href="/projects/">projects</a>
      <a href="/reading/">reading</a>
    </div>
  </nav>
  <main>
    ${content}
  </main>
  <canvas id="ants-canvas"></canvas>
  <button id="theme-switcher" aria-label="Switch theme">consumed</button>
  <script src="/themes/switcher.js"></script>
  <script src="/themes/consumed/ants.js"></script>
</body>
</html>
```

- [ ] **Step 4: Implement build_site and supporting functions in build.py**

Add to `build.py`:

```python
import shutil
from string import Template


def build_site(site_dir: Path) -> None:
    """Build the complete site from site_dir into site_dir/public/."""
    site_dir = Path(site_dir)
    public = site_dir / "public"

    # Clean output
    if public.exists():
        shutil.rmtree(public)
    public.mkdir()

    # Load template
    template_str = (site_dir / "templates" / "base.html").read_text()

    # Parse all posts
    posts = []
    posts_dir = site_dir / "content" / "posts"
    if posts_dir.exists():
        for md_file in sorted(posts_dir.glob("*.md")):
            raw = md_file.read_text()
            mtime = md_file.stat().st_mtime
            parsed = parse_content(raw, filename=md_file.name, mtime=mtime)
            parsed["slug"] = md_file.stem
            posts.append(parsed)
    posts.sort(key=lambda p: p["date"], reverse=True)

    # Determine last post date
    last_post_date = posts[0]["date"].strftime("%Y-%m-%d") if posts else "1970-01-01"

    # Render each post
    for post in posts:
        post_dir = public / "blog" / post["slug"]
        post_dir.mkdir(parents=True, exist_ok=True)
        html = _render_template(template_str, post["title"], post["html"], last_post_date)
        (post_dir / "index.html").write_text(html)

    # Render blog index
    blog_index_dir = public / "blog"
    blog_index_dir.mkdir(parents=True, exist_ok=True)
    blog_list_html = "<h1>Blog</h1>\n<ul class=\"post-list\">\n"
    for post in posts:
        date_str = post["date"].strftime("%Y-%m-%d")
        blog_list_html += (
            f'  <li><time datetime="{date_str}">{date_str}</time> '
            f'<a href="/blog/{post["slug"]}/">{post["title"]}</a></li>\n'
        )
    blog_list_html += "</ul>"
    html = _render_template(template_str, "Blog", blog_list_html, last_post_date)
    (blog_index_dir / "index.html").write_text(html)

    # Render pages
    pages_dir = site_dir / "content" / "pages"
    if pages_dir.exists():
        for md_file in pages_dir.glob("*.md"):
            raw = md_file.read_text()
            mtime = md_file.stat().st_mtime
            parsed = parse_content(raw, filename=md_file.name, mtime=mtime)
            slug = md_file.stem

            if slug == "index":
                out_dir = public
            else:
                out_dir = public / slug
                out_dir.mkdir(parents=True, exist_ok=True)

            html = _render_template(template_str, parsed["title"], parsed["html"], last_post_date)
            (out_dir / "index.html").write_text(html)

    # Copy static files
    static_dir = site_dir / "static"
    if static_dir.exists():
        for item in static_dir.iterdir():
            dest = public / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    # Copy theme assets
    themes_dir = site_dir / "themes"
    if themes_dir.exists():
        dest_themes = public / "themes"
        shutil.copytree(themes_dir, dest_themes)


def _render_template(template_str: str, title: str, content: str, last_post_date: str) -> str:
    """Render the base template with the given content."""
    return Template(template_str).safe_substitute(
        title=title,
        content=content,
        last_post_date=last_post_date,
        nav="",  # nav is in the template HTML directly
    )


if __name__ == "__main__":
    build_site(Path("."))
    print("Site built to public/")
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_build.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add build.py templates/base.html tests/test_build.py
git commit -m "Add site assembly: template rendering, post/page generation, static copying"
```

---

### Task 4: Theme switcher and CSS — Clean theme

Build the theme switcher JS and the Clean theme first (easiest to verify visually).

**Files:**
- Create: `themes/switcher.js`
- Create: `themes/clean/style.css`

- [ ] **Step 1: Write theme switcher JS**

```javascript
// themes/switcher.js
// Theme switching: cycle through themes, persist in localStorage.

(function () {
  var THEMES = ['consumed', 'garish', 'clean'];
  var btn = document.getElementById('theme-switcher');
  var link = document.getElementById('theme-css');
  var canvas = document.getElementById('ants-canvas');

  function getTheme() {
    return localStorage.getItem('theme') || 'consumed';
  }

  function setTheme(name) {
    localStorage.setItem('theme', name);
    document.documentElement.setAttribute('data-theme', name);
    link.href = '/themes/' + name + '/style.css';
    btn.textContent = name;

    // Start/stop ant simulation
    if (typeof window.antsSimulation !== 'undefined') {
      if (name === 'consumed') {
        window.antsSimulation.start();
        canvas.style.display = '';
      } else {
        window.antsSimulation.stop();
        canvas.style.display = 'none';
      }
    }
  }

  // Cycle on click
  btn.addEventListener('click', function () {
    var current = getTheme();
    var idx = THEMES.indexOf(current);
    var next = THEMES[(idx + 1) % THEMES.length];
    setTheme(next);
  });

  // Apply saved theme on load
  setTheme(getTheme());
})();
```

- [ ] **Step 2: Write Clean theme CSS**

```css
/* themes/clean/style.css */

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #fafafa;
  color: #222;
  line-height: 1.7;
}

nav {
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem 1rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1px solid #e0e0e0;
}

.site-name {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.1rem;
  font-weight: bold;
  color: #222;
  text-decoration: none;
}

.nav-links { display: flex; gap: 1rem; }
.nav-links a { color: #666; text-decoration: none; font-size: 0.9rem; }
.nav-links a:hover { color: #222; }

main {
  max-width: 640px;
  margin: 2rem auto;
  padding: 0 1rem;
}

main h1 { font-family: Georgia, serif; font-size: 1.8rem; margin-bottom: 0.5rem; color: #111; }
main h2 { font-family: Georgia, serif; font-size: 1.4rem; margin: 2rem 0 0.5rem; color: #222; }
main h3 { font-family: Georgia, serif; font-size: 1.1rem; margin: 1.5rem 0 0.5rem; color: #333; }

main p { margin-bottom: 1rem; }
main a { color: #0066cc; }

main code {
  background: #f0f0f0;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

main pre {
  background: #f0f0f0;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 1rem;
}

main pre code { background: none; padding: 0; }

.post-list { list-style: none; }
.post-list li { padding: 0.4rem 0; border-bottom: 1px solid #f0f0f0; }
.post-list time { color: #999; font-size: 0.85rem; margin-right: 0.5rem; }
.post-list a { color: #222; text-decoration: none; }
.post-list a:hover { color: #0066cc; }

#theme-switcher {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background: #e0e0e0;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #666;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}
#theme-switcher:hover { opacity: 1; }

#ants-canvas { display: none; }
```

- [ ] **Step 3: Test manually**

```bash
cd /Users/nathan/Projects/ndouglas/darkdell
echo "# Welcome\n\nThis is darkdell.net." > content/pages/index.md
echo "# Projects\n\nStuff I've built." > content/pages/projects.md
echo "# Reading\n\nWhat I'm reading." > content/pages/reading.md
echo "# Hello World\n\nFirst post. Let's see if this works." > content/posts/hello-world.md
python build.py
python -m http.server -d public 8000
```

Open http://localhost:8000 and verify the Clean theme renders correctly. Check navigation links, blog index, individual post.

- [ ] **Step 4: Commit**

```bash
git add themes/switcher.js themes/clean/style.css content/
git commit -m "Add theme switcher and Clean theme"
```

---

### Task 5: Consumed theme CSS (without ants)

Build the Consumed theme's static CSS — dark background, monospace type, CRT scanlines, phosphor glow. The ant colony JS comes in a later task.

**Files:**
- Create: `themes/consumed/style.css`

- [ ] **Step 1: Write Consumed theme CSS**

```css
/* themes/consumed/style.css */

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  background: #0a0808;
  color: #d4b8a8;
  line-height: 1.9;
}

/* CRT scanlines */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 3px,
    rgba(0, 0, 0, 0.08) 3px,
    rgba(0, 0, 0, 0.08) 4px
  );
  pointer-events: none;
  z-index: 1000;
}

nav {
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem 1rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.site-name {
  font-size: 0.85rem;
  color: #d4b8a8;
  text-decoration: none;
  letter-spacing: 4px;
  text-transform: uppercase;
  text-shadow: 0 0 6px rgba(220, 180, 160, 0.3);
}

.nav-links { display: flex; gap: 1rem; }
.nav-links a {
  color: #7a6858;
  text-decoration: none;
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  transition: color 0.3s, text-shadow 0.3s;
}
.nav-links a:hover {
  color: #d4b8a8;
  text-shadow: 0 0 6px rgba(220, 180, 160, 0.3);
}

main {
  max-width: 640px;
  margin: 2rem auto;
  padding: 0 1rem;
}

main h1 {
  font-size: 1.4rem;
  margin-bottom: 0.5rem;
  color: #d4b8a8;
  text-shadow: 0 0 8px rgba(220, 180, 160, 0.4);
}
main h2 { font-size: 1.2rem; margin: 2rem 0 0.5rem; color: #d4b8a8; }
main h3 { font-size: 1rem; margin: 1.5rem 0 0.5rem; color: #baa090; }

main p { margin-bottom: 1rem; }
main a { color: #c08060; text-decoration: none; border-bottom: 1px solid #5a3828; }
main a:hover { color: #d4b8a8; border-color: #d4b8a8; }

main code {
  background: rgba(255, 255, 255, 0.05);
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

main pre {
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow-x: auto;
  margin-bottom: 1rem;
}

main pre code { background: none; padding: 0; }

.post-list { list-style: none; }
.post-list li { padding: 0.5rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
.post-list time { color: #6a5848; font-size: 0.8rem; margin-right: 0.5rem; }
.post-list a { color: #baa090; text-decoration: none; border-bottom: none; }
.post-list a:hover { color: #d4b8a8; text-shadow: 0 0 6px rgba(220, 180, 160, 0.25); }

#theme-switcher {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-family: inherit;
  font-size: 0.7rem;
  color: #6a5848;
  cursor: pointer;
  letter-spacing: 2px;
  text-transform: uppercase;
  opacity: 0.5;
  transition: opacity 0.3s;
  z-index: 1001;
}
#theme-switcher:hover { opacity: 1; color: #d4b8a8; }

#ants-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
}

/* Reduced motion: hide canvas, show static gradient instead */
@media (prefers-reduced-motion: reduce) {
  #ants-canvas { display: none; }
  body {
    background: #0a0808 radial-gradient(
      ellipse at 50% 50%,
      rgba(100, 15, 30, 0.12) 0%,
      transparent 70%
    );
  }
}
```

- [ ] **Step 2: Test manually — switch between themes**

```bash
python build.py && python -m http.server -d public 8000
```

Open http://localhost:8000, verify Consumed theme renders (dark background, monospace, scanlines). Click the theme switcher to toggle between Consumed and Clean. Verify localStorage persistence by refreshing.

- [ ] **Step 3: Commit**

```bash
git add themes/consumed/style.css
git commit -m "Add Consumed theme CSS: dark monospace with CRT scanlines and phosphor glow"
```

---

### Task 6: Garish theme CSS

The GeoCities fever dream.

**Files:**
- Create: `themes/garish/style.css`

- [ ] **Step 1: Write Garish theme CSS**

```css
/* themes/garish/style.css */

@keyframes rainbow-bg {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
@keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Comic Sans MS', 'Chalkboard SE', cursive;
  background: linear-gradient(135deg, #ff0080, #ff8c00, #ffff00, #00ff00, #00ffff, #8000ff, #ff0080);
  background-size: 400% 400%;
  animation: rainbow-bg 8s ease infinite;
  color: #000;
  line-height: 1.6;
}

nav {
  max-width: 700px;
  margin: 0 auto;
  padding: 1rem;
  text-align: center;
}

.site-name {
  font-size: 2rem;
  color: #fff;
  text-decoration: none;
  text-shadow: 3px 3px 0 #ff00ff, -2px -2px 0 #00ffff;
  display: block;
  margin-bottom: 0.5rem;
}

.site-name::before { content: '★ '; }
.site-name::after { content: ' ★'; }

.nav-links { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; }
.nav-links a {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  text-decoration: none;
  font-weight: bold;
  transform: rotate(-1deg);
}
.nav-links a:nth-child(1) { background: #ff00ff; color: #fff; }
.nav-links a:nth-child(2) { background: #00ff00; color: #000; }
.nav-links a:nth-child(3) { background: #ffff00; color: #000; transform: rotate(2deg); }
.nav-links a:hover { animation: blink 0.3s 2; }

main {
  max-width: 700px;
  margin: 1rem auto;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(4px);
  border: 3px dashed #ff00ff;
  border-radius: 12px;
}

main h1 { font-size: 1.8rem; color: #ff0080; text-align: center; }
main h1::before { content: '🌈 '; }
main h1::after { content: ' 🌈'; }
main h2 { font-size: 1.4rem; margin: 1.5rem 0 0.5rem; color: #8000ff; }
main h3 { font-size: 1.1rem; margin: 1rem 0 0.5rem; color: #0080ff; }

main p { margin-bottom: 1rem; }
main a { color: #ff0080; font-weight: bold; }

main code {
  background: #ffff00;
  color: #000;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'Comic Sans MS', cursive;
}

main pre {
  background: #1a1a2e;
  color: #00ff00;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid #00ffff;
  overflow-x: auto;
  margin-bottom: 1rem;
  font-family: monospace;
}

main pre code { background: none; color: #00ff00; font-family: monospace; }

.post-list { list-style: none; }
.post-list li {
  padding: 0.5rem;
  margin-bottom: 0.3rem;
  background: rgba(255, 255, 255, 0.3);
  border: 2px dashed #00ffff;
  border-radius: 8px;
}
.post-list time { color: #8000ff; font-size: 0.85rem; margin-right: 0.5rem; font-weight: bold; }
.post-list a { color: #ff0080; text-decoration: none; }
.post-list a:hover { text-decoration: underline wavy; }

/* Visitor counter */
main::after {
  content: '🚧 Under Construction!! 🚧  |  Visitors: 000042069  |  Best viewed at 800x600';
  display: block;
  text-align: center;
  margin-top: 2rem;
  padding: 0.5rem;
  font-size: 0.75rem;
  color: #fff;
  background: #000;
  border-radius: 4px;
}

#theme-switcher {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background: #ff00ff;
  border: 3px dashed #00ffff;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-family: 'Comic Sans MS', cursive;
  font-size: 0.8rem;
  color: #fff;
  cursor: pointer;
  font-weight: bold;
  z-index: 1001;
}
#theme-switcher:hover { background: #00ffff; color: #000; }

#ants-canvas { display: none; }
```

- [ ] **Step 2: Test manually**

```bash
python build.py && python -m http.server -d public 8000
```

Switch to Garish theme. Verify rainbow gradient, Comic Sans, neon pills, dashed borders. Revel in the horror.

- [ ] **Step 3: Commit**

```bash
git add themes/garish/style.css
git commit -m "Add Garish theme: GeoCities rainbow nightmare with Comic Sans and marquee energy"
```

---

### Task 7: Ant colony simulation — core engine

The ACO simulation logic: grid, ants, pheromones, food, hive, decay. No rendering yet — just the simulation loop with an exported API.

**Files:**
- Create: `themes/consumed/ants.js`

- [ ] **Step 1: Write the ACO simulation engine**

```javascript
// themes/consumed/ants.js
// Ant Colony Optimization background simulation for the Consumed theme.
// Renders pheromone trails as subtle color gradients on a background canvas.

(function () {
  'use strict';

  // --- Configuration ---
  var GRID_W = 128;
  var GRID_H = 64;
  var CELL_PX = 6;           // pixels per cell on canvas
  var NUM_FOOD_SOURCES = 8;
  var FOOD_PER_SOURCE = 80;
  var DECAY_RATE = 0.4;      // pheromone lost per tick
  var MARK_STRENGTH = 25;    // pheromone deposited per step
  var MAX_PHEROMONE = 255;
  var FOOD_RESPAWN_TICKS = 600;
  var MAX_DAYS = 60;         // vitality decay window

  // Pheromone channel colors (RGBA base, rendered at low alpha)
  var CHANNELS = [
    { r: 197, g: 64, b: 48 },    // vermilion
    { r: 90, g: 16, b: 64 },     // aubergine
    { r: 138, g: 16, b: 32 },    // crimson
  ];

  // --- State ---
  var canvas, ctx;
  var grid;        // [GRID_W * GRID_H * CHANNELS.length] pheromone values
  var ants;
  var hive;        // { x, y }
  var foods;       // [{ x, y, amount }]
  var vitality;
  var antCount;
  var running = false;
  var rafId = null;
  var tickCounter = 0;

  // --- Helpers ---
  function rand(max) { return Math.floor(Math.random() * max); }

  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }

  function wrap(v, max) { return ((v % max) + max) % max; }

  // --- Initialization ---
  function init() {
    canvas = document.getElementById('ants-canvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    // Calculate vitality from lastPostDate
    vitality = calcVitality();
    antCount = Math.round(5 + 95 * vitality); // 5..100

    // Size canvas
    canvas.width = GRID_W * CELL_PX;
    canvas.height = GRID_H * CELL_PX;

    // Init pheromone grid (flat array, 3 channels per cell)
    grid = new Float32Array(GRID_W * GRID_H * CHANNELS.length);

    // Place hive randomly (avoid edges)
    hive = {
      x: 10 + rand(GRID_W - 20),
      y: 5 + rand(GRID_H - 10)
    };

    // Place food sources
    foods = [];
    spawnFoods(NUM_FOOD_SOURCES);

    // Create ants at hive
    ants = [];
    for (var i = 0; i < antCount; i++) {
      ants.push(createAnt());
    }

    tickCounter = 0;
  }

  function createAnt() {
    return {
      x: hive.x + rand(3) - 1,
      y: hive.y + rand(3) - 1,
      dx: rand(3) - 1 || 1,
      dy: rand(3) - 1,
      carrying: false,
      channel: rand(CHANNELS.length)
    };
  }

  function spawnFoods(count) {
    for (var i = 0; i < count; i++) {
      var food = {
        x: rand(GRID_W),
        y: rand(GRID_H),
        amount: FOOD_PER_SOURCE
      };
      // Don't spawn on top of hive
      if (Math.abs(food.x - hive.x) < 5 && Math.abs(food.y - hive.y) < 5) {
        food.x = wrap(food.x + 20, GRID_W);
      }
      foods.push(food);
    }
  }

  function calcVitality() {
    if (typeof lastPostDate === 'undefined' || !lastPostDate || lastPostDate === '1970-01-01') {
      return 0;
    }
    var posted = new Date(lastPostDate);
    var now = new Date();
    var days = (now - posted) / (1000 * 60 * 60 * 24);
    return Math.max(0, 1 - days / MAX_DAYS);
  }

  // --- Simulation Tick ---
  function tick() {
    // Move ants
    for (var i = 0; i < ants.length; i++) {
      stepAnt(ants[i]);
    }

    // Decay pheromones
    var decay = DECAY_RATE * (0.3 + 0.7 * vitality);
    for (var j = 0; j < grid.length; j++) {
      grid[j] = Math.max(0, grid[j] - decay);
    }

    // Respawn food periodically
    tickCounter++;
    var respawnRate = Math.max(2000, FOOD_RESPAWN_TICKS / Math.max(vitality, 0.1));
    if (tickCounter % Math.round(respawnRate) === 0) {
      // Remove depleted, add new
      foods = foods.filter(function (f) { return f.amount > 0; });
      if (foods.length < NUM_FOOD_SOURCES) {
        spawnFoods(1);
      }
    }
  }

  function stepAnt(ant) {
    if (ant.carrying) {
      // Heading home — move toward hive
      var hdx = hive.x - ant.x;
      var hdy = hive.y - ant.y;
      ant.dx = hdx === 0 ? (rand(3) - 1) : (hdx > 0 ? 1 : -1);
      ant.dy = hdy === 0 ? (rand(3) - 1) : (hdy > 0 ? 1 : -1);

      // Add some randomness to avoid straight lines
      if (Math.random() < 0.2) {
        ant.dx = rand(3) - 1;
        ant.dy = rand(3) - 1;
      }

      // Mark pheromone trail
      var idx = (ant.y * GRID_W + ant.x) * CHANNELS.length + ant.channel;
      grid[idx] = Math.min(MAX_PHEROMONE, grid[idx] + MARK_STRENGTH * (0.3 + 0.7 * vitality));

      // Check if home
      if (Math.abs(ant.x - hive.x) <= 1 && Math.abs(ant.y - hive.y) <= 1) {
        ant.carrying = false;
        // Random new direction
        ant.dx = rand(3) - 1 || 1;
        ant.dy = rand(3) - 1;
      }
    } else {
      // Foraging — sense pheromones and food
      var bestPheromone = 0;
      var bestDx = ant.dx;
      var bestDy = ant.dy;

      // Check neighbors for pheromones
      for (var ddx = -1; ddx <= 1; ddx++) {
        for (var ddy = -1; ddy <= 1; ddy++) {
          if (ddx === 0 && ddy === 0) continue;
          var nx = wrap(ant.x + ddx, GRID_W);
          var ny = wrap(ant.y + ddy, GRID_H);
          var nIdx = (ny * GRID_W + nx) * CHANNELS.length + ant.channel;
          if (grid[nIdx] > bestPheromone) {
            bestPheromone = grid[nIdx];
            bestDx = ddx;
            bestDy = ddy;
          }
        }
      }

      // Follow pheromones with some probability, otherwise wander
      if (bestPheromone > 5 && Math.random() < 0.6) {
        ant.dx = bestDx;
        ant.dy = bestDy;
      } else if (Math.random() < 0.3) {
        // Random turn
        ant.dx = rand(3) - 1;
        ant.dy = rand(3) - 1;
      }

      // Check for food at current position
      for (var f = 0; f < foods.length; f++) {
        var food = foods[f];
        if (food.amount > 0 && Math.abs(ant.x - food.x) <= 2 && Math.abs(ant.y - food.y) <= 2) {
          ant.carrying = true;
          food.amount--;
          ant.channel = rand(CHANNELS.length); // pick a random channel for trail color
          break;
        }
      }
    }

    // Move
    if (ant.dx === 0 && ant.dy === 0) ant.dx = 1; // never stall
    ant.x = wrap(ant.x + ant.dx, GRID_W);
    ant.y = wrap(ant.y + ant.dy, GRID_H);
  }

  // --- Rendering ---
  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    var imageData = ctx.createImageData(GRID_W, GRID_H);
    var data = imageData.data;
    var saturation = 0.3 + 0.7 * vitality;

    for (var y = 0; y < GRID_H; y++) {
      for (var x = 0; x < GRID_W; x++) {
        var pIdx = (y * GRID_W + x) * CHANNELS.length;
        var pixIdx = (y * GRID_W + x) * 4;

        var r = 0, g = 0, b = 0, a = 0;
        for (var c = 0; c < CHANNELS.length; c++) {
          var intensity = grid[pIdx + c] / MAX_PHEROMONE;
          r += CHANNELS[c].r * intensity * saturation;
          g += CHANNELS[c].g * intensity * saturation;
          b += CHANNELS[c].b * intensity * saturation;
          a = Math.max(a, intensity);
        }

        data[pixIdx] = clamp(Math.round(r), 0, 255);
        data[pixIdx + 1] = clamp(Math.round(g), 0, 255);
        data[pixIdx + 2] = clamp(Math.round(b), 0, 255);
        data[pixIdx + 3] = clamp(Math.round(a * 180 * saturation), 0, 255);
      }
    }

    // Draw at native grid resolution, then CSS scales up
    ctx.putImageData(imageData, 0, 0);
  }

  // --- Main Loop ---
  var TICKS_PER_FRAME = 3;

  function loop() {
    for (var i = 0; i < TICKS_PER_FRAME; i++) {
      tick();
    }
    render();
    rafId = requestAnimationFrame(loop);
  }

  // --- Public API ---
  window.antsSimulation = {
    start: function () {
      if (running) return;
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      running = true;
      init();
      loop();
    },
    stop: function () {
      running = false;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = null;
    }
  };

  // Auto-start if consumed theme is active
  var theme = localStorage.getItem('theme') || 'consumed';
  if (theme === 'consumed') {
    // Wait for DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        window.antsSimulation.start();
      });
    } else {
      window.antsSimulation.start();
    }
  }
})();
```

- [ ] **Step 2: Add blur filter to consumed CSS**

In `themes/consumed/style.css`, add `filter: blur(10px);` and `image-rendering: pixelated;` to the existing `#ants-canvas` rule from Task 5. The final rule should be:

```css
#ants-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  filter: blur(10px);
  image-rendering: pixelated;
}
```

- [ ] **Step 3: Test manually**

```bash
python build.py && python -m http.server -d public 8000
```

Open http://localhost:8000 with Consumed theme. Verify:
- Background canvas is visible behind content
- Faint color trails emerge over ~10–20 seconds
- Trails fade over time
- Performance is smooth (no jank)

- [ ] **Step 4: Commit**

```bash
git add themes/consumed/ants.js themes/consumed/style.css
git commit -m "Add ant colony pheromone simulation for Consumed theme background"
```

---

### Task 8: Vitality system integration

Verify the vitality system works end-to-end: build.py bakes the date, ants.js reads it, simulation behavior changes.

**Files:**
- Modify: `tests/test_build.py`

- [ ] **Step 1: Write a test verifying lastPostDate is baked in correctly**

Add to `tests/test_build.py`:

```python
def test_last_post_date_is_recent(tmp_site):
    """lastPostDate reflects the most recent post's date."""
    from build import build_site
    from datetime import datetime

    build_site(tmp_site)
    index = (tmp_site / "public" / "index.html").read_text()

    # Should contain today's date (since the test creates files "now")
    today = datetime.now().strftime("%Y-%m-%d")
    assert today in index
```

- [ ] **Step 2: Run test**

```bash
python -m pytest tests/test_build.py::test_last_post_date_is_recent -v
```

Expected: PASS.

- [ ] **Step 3: Manual test — vitality variation**

Test with a post from today (high vitality) vs. modifying the baked date to simulate old post:

```bash
python build.py && python -m http.server -d public 8000
```

Open browser, observe rich ant colony. Then temporarily edit `public/index.html` to set `lastPostDate = "2025-01-01"`, refresh, observe diminished activity.

- [ ] **Step 4: Commit**

```bash
git add tests/test_build.py
git commit -m "Add vitality integration test"
```

---

### Task 9: Content — initial pages and first post

Create the actual content for the landing page, projects page, reading page, and a first blog post.

**Files:**
- Modify: `content/pages/index.md`
- Modify: `content/pages/projects.md`
- Modify: `content/pages/reading.md`
- Create: `content/posts/hello-again.md`

- [ ] **Step 1: Write landing page**

`content/pages/index.md`:

```markdown
# Nathan Douglas

Software engineer. Reader of books. Builder of things.

This is my personal site — a place to think out loud, track what I'm reading, and keep my projects in one place. The background is alive; it's an ant colony optimization simulation that thrives when I write and fades when I don't. Think of it as a digital Tamagotchi.

[Blog](/blog/) · [Projects](/projects/) · [Reading](/reading/)
```

- [ ] **Step 2: Write projects page**

`content/pages/projects.md`:

```markdown
# Projects

A non-exhaustive list of things I've built or am building.

- **[Pinkmaiden](https://pnk.darkdell.net)** — Infinite scrolling image gallery
- **[Goldentooth](https://goldentooth.darkdell.net)** — Homelab infrastructure
- **[Ants](https://github.com/ndouglas/ants)** — Ant colony optimization for the SWARM competition
- **[This site](https://github.com/ndouglas/darkdell)** — Hand-rolled SSG with a living background
```

- [ ] **Step 3: Write reading page**

`content/pages/reading.md`:

```markdown
# Reading

What I'm currently shuffling between. The system: pick 2–3 books, read a pomodoro each, write about what I learned.

## Currently Reading

- *Brain of the Firm* — Stafford Beer
- *Designing Data-Intensive Applications* — Martin Kleppmann
- *Micromotives and Macrobehavior* — Thomas Schelling

## Queue

- *Team Topologies* — Matthew Skelton & Manuel Pais
```

- [ ] **Step 4: Write first blog post**

`content/posts/hello-again.md`:

```markdown
# Hello Again

New site, new start. This is a hand-rolled static site generator — about 200 lines of Python, three CSS themes, and an ant colony optimization simulation painting the background.

The idea is simple: read some stuff in the evening, write about it here. The site is alive — the more I write, the more vibrant the background becomes. Neglect it and the ants die off. It's a Tamagotchi that runs on writing.

Let's see how this goes.
```

- [ ] **Step 5: Build and verify**

```bash
python build.py && python -m http.server -d public 8000
```

Check all pages render, navigation works, blog index shows the post.

- [ ] **Step 6: Commit**

```bash
git add content/
git commit -m "Add initial content: landing page, projects, reading list, first post"
```

---

### Task 10: Final build, deploy, and cleanup

Full build, verify locally, deploy to S3/CloudFront.

**Files:**
- No new files

- [ ] **Step 1: Run full test suite**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 2: Full build**

```bash
python build.py
```

- [ ] **Step 3: Verify locally**

```bash
python -m http.server -d public 8000
```

Checklist:
- [ ] Landing page renders at /
- [ ] Blog index renders at /blog/
- [ ] Individual post renders at /blog/hello-again/
- [ ] Projects page renders at /projects/
- [ ] Reading page renders at /reading/
- [ ] Theme switcher cycles through all three themes
- [ ] Consumed theme shows ant colony background
- [ ] Garish theme shows rainbow horror
- [ ] Clean theme is readable
- [ ] Theme persists across page refresh
- [ ] Navigation links work across all pages

- [ ] **Step 4: Deploy**

```bash
make deploy
```

- [ ] **Step 5: Verify live site**

Open https://darkdell.net and run through the same checklist.

- [ ] **Step 6: Commit any final tweaks**

```bash
git add -A
git commit -m "Final tweaks after deploy"
```

- [ ] **Step 7: Clean up old Hugo references**

Verify no Hugo artifacts remain:

```bash
# Should return nothing Hugo-related
ls hugo.toml archetypes/ layouts/ .hugo_build.lock .gitmodules 2>/dev/null
```
