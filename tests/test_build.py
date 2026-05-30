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
    result = parse_content("Just some content, no heading.", filename="25-hello-world.md")
    assert result["title"] == "Hello World"


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


def test_render_title_html_renders_italic():
    """Inline markdown in a title renders to HTML without a wrapping <p>."""
    from build import render_title_html
    assert render_title_html("_Wizardry VI_") == "<em>Wizardry VI</em>"
    assert render_title_html("**Bold** and `code`") == "<strong>Bold</strong> and <code>code</code>"


def test_strip_title_markdown_removes_markers():
    """Plain-text title strips italic/bold/code markers."""
    from build import strip_title_markdown
    assert strip_title_markdown("_Wizardry VI: Bane of the Cosmic Forge_") == (
        "Wizardry VI: Bane of the Cosmic Forge"
    )
    assert strip_title_markdown("**Bold** and `code`") == "Bold and code"
    assert strip_title_markdown("No formatting here") == "No formatting here"


def test_blog_index_renders_markdown_in_titles(tmp_site):
    """Blog index link text renders italic from a markdown title."""
    md = tmp_site / "content" / "posts" / "2026" / "03" / "26-italic.md"
    md.write_text("# _Italicized Title_\n\nBody.")
    from build import build_site
    build_site(tmp_site)
    index = (tmp_site / "public" / "blog" / "index.html").read_text()
    assert "<em>Italicized Title</em>" in index
    assert "_Italicized Title_" not in index


def test_rss_feed_title_is_plain(tmp_site):
    """RSS feed item title strips markdown markers."""
    md = tmp_site / "content" / "posts" / "2026" / "03" / "26-italic.md"
    md.write_text("# _Italicized Title_\n\nBody.")
    from build import build_site
    build_site(tmp_site)
    feed = (tmp_site / "public" / "blog" / "feed.xml").read_text()
    assert "<title>Italicized Title</title>" in feed
    assert "_Italicized Title_" not in feed


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

    old_dir = tmp_site / "content" / "posts" / "2026" / "01"
    old_dir.mkdir(parents=True, exist_ok=True)
    (old_dir / "01-old-post.md").write_text("# Old Post\n\nOld content.")

    new_dir = tmp_site / "content" / "posts" / "2026" / "04"
    new_dir.mkdir(parents=True, exist_ok=True)
    (new_dir / "01-new-post.md").write_text("# New Post\n\nNew content.")

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

    # Should contain the date from the nested directory structure (2026-03-25)
    assert "2026-03-25" in index


def test_build_finds_nested_posts(tmp_site):
    """Building discovers posts in YYYY/MM/DD-slug.md structure."""
    from build import build_site
    build_site(tmp_site)
    output = tmp_site / "public" / "blog" / "hello-world" / "index.html"
    assert output.exists()
    assert "Hello World" in output.read_text()


def test_intro_renders_on_section_index(tmp_site):
    """An _intro.md in a section dir renders above the post list."""
    (tmp_site / "content" / "posts" / "_intro.md").write_text(
        "These are my posts about stuff."
    )
    from build import build_site
    build_site(tmp_site)
    index_html = (tmp_site / "public" / "blog" / "index.html").read_text()
    assert "These are my posts about stuff." in index_html
    # Intro appears before the post list
    assert index_html.index("These are my posts about stuff.") < index_html.index(
        'class="post-list"'
    )


def test_intro_not_rendered_as_post(tmp_site):
    """An _intro.md is not treated as a post (no individual page, not in list)."""
    (tmp_site / "content" / "posts" / "_intro.md").write_text("Intro prose.")
    from build import build_site
    build_site(tmp_site)
    assert not (tmp_site / "public" / "blog" / "_intro").exists()
    index_html = (tmp_site / "public" / "blog" / "index.html").read_text()
    # Intro body shouldn't show up inside the <ul> post list
    list_start = index_html.index('<ul class="post-list">')
    list_end = index_html.index("</ul>", list_start)
    assert "Intro prose." not in index_html[list_start:list_end]


def test_build_errors_on_slug_collision(tmp_site):
    """Building fails with clear error if two posts produce the same slug."""
    colliding = tmp_site / "content" / "posts" / "2026" / "04"
    colliding.mkdir(parents=True)
    (colliding / "10-hello-world.md").write_text("# Hello World Again\n\nDuplicate slug.")

    from build import build_site
    with pytest.raises(ValueError, match="Duplicate post slug"):
        build_site(tmp_site)


def test_date_from_directory_structure():
    """Date is extracted from YYYY/MM/DD-slug.md path components."""
    from build import extract_post_date_and_slug
    date, slug = extract_post_date_and_slug(Path("2026/03/25-hello-world.md"))
    assert date.year == 2026
    assert date.month == 3
    assert date.day == 25
    assert slug == "hello-world"


def test_parse_monthly_files_strips_h1(tmp_path):
    """The optional # heading is stripped from monthly files."""
    from build import _parse_monthly_files
    d = tmp_path / "2026"
    d.mkdir()
    (d / "03.md").write_text("# March 2026\n\n- Item one\n- Item two\n")
    months = _parse_monthly_files(tmp_path)
    assert len(months) == 1
    assert "March 2026" not in months[0]["html"]
    assert "Item one" in months[0]["html"]


def test_parse_monthly_files_sort_order(tmp_path):
    """Monthly files sort newest-first."""
    from build import _parse_monthly_files
    d = tmp_path / "2026"
    d.mkdir()
    for m in ("01", "06"):
        (d / f"{m}.md").write_text(f"- Month {m}\n")
    months = _parse_monthly_files(tmp_path)
    assert months[0]["month"] == 6
    assert months[1]["month"] == 1


def test_build_creates_reading_index(tmp_site):
    """Building produces a /reading/ index page with rendered markdown."""
    from build import build_site
    build_site(tmp_site)
    index = tmp_site / "public" / "reading" / "index.html"
    assert index.exists()
    content = index.read_text()
    assert "Book Alpha" in content
    assert "<em>Book Alpha</em>" in content
    assert "Archive" in content


def test_build_creates_reading_year_page(tmp_site):
    """Building produces yearly /reading/YYYY/ pages."""
    from build import build_site
    build_site(tmp_site)
    year_page = tmp_site / "public" / "reading" / "2026" / "index.html"
    assert year_page.exists()
    content = year_page.read_text()
    assert "Reading: 2026" in content
    assert "Book Alpha" in content
    assert "March 2026" in content


def test_reading_months_ordered_recent_first(tmp_site):
    """Reading index shows most recent months first."""
    from build import build_site
    old = tmp_site / "content" / "reading" / "2026" / "01.md"
    old.write_text("- Old book\n")

    build_site(tmp_site)
    index = (tmp_site / "public" / "reading" / "index.html").read_text()
    assert index.index("Book Alpha") < index.index("Old book")


def test_reading_year_page_groups_by_month(tmp_site):
    """Year pages group entries under month subheadings."""
    from build import build_site
    jan = tmp_site / "content" / "reading" / "2026" / "01.md"
    jan.write_text("- January book\n")

    build_site(tmp_site)
    year_page = (tmp_site / "public" / "reading" / "2026" / "index.html").read_text()
    assert "March 2026" in year_page
    assert "January 2026" in year_page
    assert year_page.index("March 2026") < year_page.index("January 2026")


def test_build_creates_ideas_index(tmp_site):
    """Building produces an /ideas/ index page."""
    from build import build_site
    build_site(tmp_site)
    index = tmp_site / "public" / "ideas" / "index.html"
    assert index.exists()
    content = index.read_text()
    assert "Idea one" in content
    assert "Idea two" in content
    assert "Archive" in content


def test_build_creates_ideas_year_page(tmp_site):
    """Building produces yearly /ideas/YYYY/ pages."""
    from build import build_site
    build_site(tmp_site)
    year_page = tmp_site / "public" / "ideas" / "2026" / "index.html"
    assert year_page.exists()
    content = year_page.read_text()
    assert "Ideas: 2026" in content
    assert "April 2026" in content


def test_ideas_months_ordered_recent_first(tmp_site):
    """Ideas index shows most recent months first."""
    from build import build_site
    jan = tmp_site / "content" / "ideas" / "2026" / "01.md"
    jan.write_text("- Old idea\n")

    build_site(tmp_site)
    index = (tmp_site / "public" / "ideas" / "index.html").read_text()
    assert index.index("Idea one") < index.index("Old idea")


def test_ideas_index_limits_to_3_months(tmp_site):
    """The /ideas/ index shows at most 3 months."""
    from build import build_site
    for m in ("01", "02", "03"):
        (tmp_site / "content" / "ideas" / "2026" / f"{m}.md").write_text(
            f"- Idea from month {m}\n"
        )
    # Now we have 4 months: 01, 02, 03, 04
    build_site(tmp_site)
    index = (tmp_site / "public" / "ideas" / "index.html").read_text()
    # April (04), March (03), February (02) should be shown; January (01) should not
    assert "Idea from month 03" in index
    assert "Idea from month 01" not in index
    # But the year page has all of them
    year_page = (tmp_site / "public" / "ideas" / "2026" / "index.html").read_text()
    assert "Idea from month 01" in year_page


def test_index_page_has_recent_reading(tmp_site):
    """Homepage includes recent reading."""
    from build import build_site
    build_site(tmp_site)
    index = (tmp_site / "public" / "index.html").read_text()
    assert "Recent Reading" in index
    assert "Book Alpha" in index


def test_index_page_has_recent_ideas(tmp_site):
    """Homepage includes recent ideas."""
    from build import build_site
    build_site(tmp_site)
    index = (tmp_site / "public" / "index.html").read_text()
    assert "Recent Ideas" in index
    assert "Idea one" in index


@pytest.fixture
def tmp_site(tmp_path):
    """Create a minimal site directory for testing."""
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

    reading = tmp_path / "content" / "reading" / "2026"
    reading.mkdir(parents=True)
    (reading / "03.md").write_text(
        "# March 2026\n\n"
        "- *Book Alpha*, Author A: Alpha content.\n"
        "- *Book Beta*, Author B: Beta content.\n"
    )

    ideas = tmp_path / "content" / "ideas" / "2026"
    ideas.mkdir(parents=True)
    (ideas / "04.md").write_text("- Idea one\n- Idea two\n")

    return tmp_path
