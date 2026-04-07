# Post Directory Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize blog post source files from `content/posts/YYYY-MM-DD-slug.md` to `content/posts/YYYY/MM/DD-slug.md` (and same for `posts-fr/`), keeping output URLs unchanged.

**Architecture:** Update `build.py` to recursively glob for `.md` files in post directories, extract dates from the directory path + filename (`YYYY/MM/DD-slug.md`), and detect slug collisions at build time. Move existing content files to the new structure. Update the `Makefile` `new` target. Update tests.

**Tech Stack:** Python, pytest

---

### Task 1: Update build.py to support nested post directories

**Files:**
- Modify: `build.py:70-115` (build_site function)
- Modify: `build.py:14-59` (parse_content function)
- Modify: `build.py:62-67` (_humanize_filename function)
- Test: `tests/test_build.py`

- [ ] **Step 1: Write failing test for nested directory post discovery**

Add to `tests/test_build.py`:

```python
def test_build_finds_nested_posts(tmp_site_nested):
    """Building discovers posts in YYYY/MM/DD-slug.md structure."""
    from build import build_site
    build_site(tmp_site_nested)
    output = tmp_site_nested / "public" / "blog" / "hello-world" / "index.html"
    assert output.exists()
    assert "Hello World" in output.read_text()
```

And the fixture:

```python
@pytest.fixture
def tmp_site_nested(tmp_path):
    """Create a minimal site with nested post directories."""
    pages = tmp_path / "content" / "pages"
    pages.mkdir(parents=True)
    (pages / "index.md").write_text("# Welcome\n\nThis is the landing page.")

    posts = tmp_path / "content" / "posts" / "2026" / "03"
    posts.mkdir(parents=True)
    (posts / "25-hello-world.md").write_text("# Hello World\n\nFirst post.")

    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "base.html").write_text(
        '<html><head><script>var lastPostDate = "${last_post_date}";</script></head>'
        "<body>${nav}${content}</body></html>"
    )

    for theme in ("consumed", "garish", "clean"):
        d = tmp_path / "themes" / theme
        d.mkdir(parents=True)
        (d / "style.css").write_text(f"/* {theme} */")
    (tmp_path / "themes" / "consumed" / "ants.js").write_text("// ants")

    return tmp_path
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_build.py::test_build_finds_nested_posts -v`
Expected: FAIL — no posts found because `glob("*.md")` doesn't recurse.

- [ ] **Step 3: Write failing test for slug collision detection**

Add to `tests/test_build.py`:

```python
def test_build_errors_on_slug_collision(tmp_site_nested):
    """Building fails with clear error if two posts produce the same slug."""
    # Add a second post with the same slug in a different month
    colliding = tmp_site_nested / "content" / "posts" / "2026" / "04"
    colliding.mkdir(parents=True)
    (colliding / "10-hello-world.md").write_text("# Hello World Again\n\nDuplicate slug.")

    from build import build_site
    with pytest.raises(ValueError, match="Duplicate post slug"):
        build_site(tmp_site_nested)
```

- [ ] **Step 4: Run test to verify it fails**

Run: `pytest tests/test_build.py::test_build_errors_on_slug_collision -v`
Expected: FAIL — no collision detection exists yet.

- [ ] **Step 5: Write failing test for date extraction from directory path**

Add to `tests/test_build.py`:

```python
def test_date_from_directory_structure():
    """Date is extracted from YYYY/MM/DD-slug.md path components."""
    from build import extract_post_date_and_slug
    date, slug = extract_post_date_and_slug(Path("2026/03/25-hello-world.md"))
    assert date.year == 2026
    assert date.month == 3
    assert date.day == 25
    assert slug == "hello-world"
```

You'll need to add `from pathlib import Path` at the top of the test file if not already there.

- [ ] **Step 6: Run test to verify it fails**

Run: `pytest tests/test_build.py::test_date_from_directory_structure -v`
Expected: FAIL — `extract_post_date_and_slug` doesn't exist.

- [ ] **Step 7: Implement `extract_post_date_and_slug` in build.py**

Add this function after `_humanize_filename`:

```python
def extract_post_date_and_slug(relative_path: Path) -> tuple[datetime, str]:
    """Extract date and slug from a nested post path like 2026/03/25-hello-world.md.

    Expected structure: YYYY/MM/DD-slug.md
    Returns (datetime, slug_string).
    """
    parts = relative_path.parts
    if len(parts) != 3:
        raise ValueError(
            f"Post {relative_path} doesn't match expected YYYY/MM/DD-slug.md structure"
        )
    year, month, filename = parts
    stem = Path(filename).stem
    day_match = re.match(r"^(\d{2})-(.+)$", stem)
    if not day_match:
        raise ValueError(
            f"Post filename {filename} doesn't match expected DD-slug format"
        )
    day = day_match.group(1)
    slug = day_match.group(2)
    date = datetime.fromisoformat(f"{year}-{month}-{day}")
    return date, slug
```

- [ ] **Step 8: Run the date extraction test to verify it passes**

Run: `pytest tests/test_build.py::test_date_from_directory_structure -v`
Expected: PASS

- [ ] **Step 9: Update `build_site` to use recursive globbing, `extract_post_date_and_slug`, and collision detection**

In `build.py`, replace the post-discovery loop (lines ~91-101) with:

```python
    all_posts = []  # collect all posts for vitality calculation
    for content_subdir, url_prefix, index_title in blog_sections:
        posts = []
        posts_dir = site_dir / "content" / content_subdir
        if posts_dir.exists():
            seen_slugs: dict[str, Path] = {}
            for md_file in sorted(posts_dir.rglob("*.md")):
                relative = md_file.relative_to(posts_dir)
                date, slug = extract_post_date_and_slug(relative)
                raw = md_file.read_text()
                parsed = parse_content(raw, filename=md_file.name, mtime=md_file.stat().st_mtime)
                parsed["date"] = date
                parsed["slug"] = slug
                if slug in seen_slugs:
                    raise ValueError(
                        f"Duplicate post slug '{slug}': "
                        f"{seen_slugs[slug]} and {md_file.relative_to(site_dir)}"
                    )
                seen_slugs[slug] = md_file.relative_to(site_dir)
                posts.append(parsed)
        posts.sort(key=lambda p: p["date"], reverse=True)
        all_posts.extend(posts)
```

This replaces the old `glob("*.md")` with `rglob("*.md")`, uses `extract_post_date_and_slug` for date/slug, and adds collision detection.

- [ ] **Step 10: Run all new tests to verify they pass**

Run: `pytest tests/test_build.py::test_build_finds_nested_posts tests/test_build.py::test_build_errors_on_slug_collision tests/test_build.py::test_date_from_directory_structure -v`
Expected: all PASS

- [ ] **Step 11: Update existing tests to use nested directory structure**

Update the `tmp_site` fixture to use the new directory structure:

```python
@pytest.fixture
def tmp_site(tmp_path):
    """Create a minimal site directory for testing."""
    # Content
    pages = tmp_path / "content" / "pages"
    pages.mkdir(parents=True)
    (pages / "index.md").write_text("# Welcome\n\nThis is the landing page.")

    posts = tmp_path / "content" / "posts" / "2026" / "03"
    posts.mkdir(parents=True)
    (posts / "25-hello-world.md").write_text("# Hello World\n\nFirst post.")

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

Update `test_posts_sorted_reverse_chron` to use nested dirs:

```python
def test_posts_sorted_reverse_chron(tmp_site):
    """Blog index lists posts newest first."""
    from build import build_site

    old_dir = tmp_site / "content" / "posts" / "2026" / "01"
    old_dir.mkdir(parents=True, exist_ok=True)
    (old_dir / "01-old-post.md").write_text("# Old Post\n\nOld content.")

    new_dir = tmp_site / "content" / "posts" / "2026" / "04"
    new_dir.mkdir(parents=True, exist_ok=True)
    (new_dir / "01-new-post.md").write_text("# New Post\n\nNew content.")

    build_site(tmp_site)
    index_html = (tmp_site / "public" / "blog" / "index.html").read_text()
    assert index_html.index("New Post") < index_html.index("Old Post")
```

- [ ] **Step 12: Run all tests**

Run: `pytest tests/test_build.py -v`
Expected: all PASS

- [ ] **Step 13: Remove `tmp_site_nested` fixture and deduplicate**

Since `tmp_site` now uses the nested structure, update `test_build_finds_nested_posts` and `test_build_errors_on_slug_collision` to use `tmp_site` instead of `tmp_site_nested`, then delete the `tmp_site_nested` fixture.

- [ ] **Step 14: Run all tests again**

Run: `pytest tests/test_build.py -v`
Expected: all PASS

- [ ] **Step 15: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "feat: support nested YYYY/MM/DD-slug.md post structure with collision detection"
```

---

### Task 2: Move existing content files to new structure

**Files:**
- Move: all files in `content/posts/` and `content/posts-fr/`

- [ ] **Step 1: Move English posts**

```bash
cd content/posts
for f in ????-??-??-*.md; do
  year="${f:0:4}"
  month="${f:5:2}"
  day_slug="${f:8}"
  mkdir -p "$year/$month"
  git mv "$f" "$year/$month/$day_slug"
done
cd ../..
```

This transforms e.g. `2026-03-25-hello-again.md` → `2026/03/25-hello-again.md`.

- [ ] **Step 2: Move French posts**

```bash
cd content/posts-fr
for f in ????-??-??-*.md; do
  year="${f:0:4}"
  month="${f:5:2}"
  day_slug="${f:8}"
  mkdir -p "$year/$month"
  git mv "$f" "$year/$month/$day_slug"
done
cd ../..
```

- [ ] **Step 3: Verify build works with moved files**

Run: `make build`
Expected: "Site built to public/" with no errors.

- [ ] **Step 4: Verify output URLs are unchanged**

Check that the public directory still has the same slug-based URLs:

```bash
find public/blog -name index.html | sort
find public/fr -name index.html | sort
```

Expected output should show paths like `public/blog/hello-again/index.html`, not date-nested paths.

- [ ] **Step 5: Commit**

```bash
git add content/posts content/posts-fr
git commit -m "refactor: move posts to YYYY/MM/DD-slug.md directory structure"
```

---

### Task 3: Update Makefile `new` target

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Update the `new` target to create files in nested directories**

Replace the current `new` target:

```makefile
new:
	@read -p "Post slug: " slug; \
	dir="content/posts/$$(date +%Y)/$$(date +%m)"; \
	mkdir -p "$$dir"; \
	file="$$dir/$$(date +%d)-$$slug.md"; \
	echo "# $$slug" > "$$file"; \
	$${EDITOR:-vim} "$$file"
```

- [ ] **Step 2: Test the target manually (optional)**

Run: `make new` and verify it creates a file in the right location.

- [ ] **Step 3: Commit**

```bash
git add Makefile
git commit -m "update: Makefile new target for nested post directory structure"
```

---

### Task 4: Clean up unused code paths

**Files:**
- Modify: `build.py:48-50` (old date-from-filename logic in parse_content)
- Modify: `build.py:62-67` (_humanize_filename)

- [ ] **Step 1: Remove the date-from-filename fallback in `parse_content`**

In `parse_content`, the date extraction block (lines ~48-50) has a fallback that parses `YYYY-MM-DD-` from the filename. Since `build_site` now always sets the date from the directory structure via `extract_post_date_and_slug`, and `parse_content` is still used for pages (which don't have date prefixes), this fallback is now dead code for posts. However, `parse_content` is a general function — keep it working for non-post use cases but the `YYYY-MM-DD-` filename pattern is no longer used. Remove the date-from-filename fallback:

```python
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
```

Also simplify `_humanize_filename` since filenames now look like `25-hello-world.md` not `2026-03-25-hello-world.md`:

```python
def _humanize_filename(filename: str) -> str:
    """Convert 'DD-slug.md' or 'slug.md' to 'Slug' title."""
    stem = Path(filename).stem
    # Strip day prefix if present (e.g. "25-hello-world" -> "hello-world")
    stem = re.sub(r"^\d{2}-", "", stem)
    return stem.replace("-", " ").replace("_", " ").title()
```

- [ ] **Step 2: Update the filename humanization test**

Update `test_extract_title_from_filename` in `tests/test_build.py`:

```python
def test_extract_title_from_filename():
    """When no heading, title is derived from filename."""
    from build import parse_content
    result = parse_content("Just some content, no heading.", filename="25-hello-world.md")
    assert result["title"] == "Hello World"
```

- [ ] **Step 3: Run all tests**

Run: `pytest tests/test_build.py -v`
Expected: all PASS

- [ ] **Step 4: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "cleanup: remove old flat-file date extraction, update humanize for DD-slug format"
```
