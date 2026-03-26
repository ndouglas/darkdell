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


def test_last_post_date_is_recent(tmp_site):
    """lastPostDate reflects the most recent post's date."""
    from build import build_site
    from datetime import datetime

    build_site(tmp_site)
    index = (tmp_site / "public" / "index.html").read_text()

    # Should contain today's date (since the test creates files "now")
    today = datetime.now().strftime("%Y-%m-%d")
    assert today in index


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
