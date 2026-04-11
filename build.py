#!/usr/bin/env python3
"""Static site generator for darkdell.net."""

import calendar
import re
import shutil
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from string import Template

import markdown
import yaml

MD_EXTENSIONS = ["fenced_code", "codehilite", "tables", "footnotes"]


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
    html = markdown.markdown(body, extensions=MD_EXTENSIONS)

    return {"title": title, "date": date, "html": html, "frontmatter": frontmatter}


def _humanize_filename(filename: str) -> str:
    """Convert 'DD-slug.md' or 'slug.md' to 'Slug' title."""
    stem = Path(filename).stem
    # Strip day prefix if present (e.g. "25-hello-world" -> "hello-world")
    stem = re.sub(r"^\d{2}-", "", stem)
    return stem.replace("-", " ").replace("_", " ").title()


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


def parse_reading_file(raw: str, year: int, month: int) -> list[dict]:
    """Parse a monthly reading file into individual book entries.

    Each ## heading starts a new book. Any leading # heading or intro text is skipped.
    Returns a list of book dicts sorted by position within the file.
    """
    sections = re.split(r"^(?=## )", raw, flags=re.MULTILINE)
    books = []
    for position, section in enumerate(s for s in sections if s.startswith("## ")):
        lines = section.split("\n", 1)
        title = lines[0].removeprefix("## ").strip()
        body = lines[1] if len(lines) > 1 else ""
        html = markdown.markdown(body.strip(), extensions=MD_EXTENSIONS)
        books.append({
            "title": title,
            "html": html,
            "year": year,
            "month": month,
            "position": position,
            "sort_key": (-year, -month, position),
        })
    return books


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

    # Blog sections: (content_dir, url_prefix, index_title)
    blog_sections = [
        ("posts", "blog", "Blog"),
        ("posts-fr", "fr", "Blog (Français)"),
    ]

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
                parsed = parse_content(raw, filename=md_file.name)
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

        # Render each post
        for post in posts:
            post_dir = public / url_prefix / post["slug"]
            post_dir.mkdir(parents=True, exist_ok=True)
            # last_post_date filled in after all sections parsed
            post["_url_prefix"] = url_prefix
            post["_out_dir"] = post_dir

        # Store for index rendering after last_post_date is known
        posts_dir_data = (posts, url_prefix, index_title)
        blog_sections[blog_sections.index((content_subdir, url_prefix, index_title))] = posts_dir_data

    # Determine last post date from all sections
    all_posts.sort(key=lambda p: p["date"], reverse=True)
    last_post_date = all_posts[0]["date"].strftime("%Y-%m-%d") if all_posts else "1970-01-01"

    # Render reading section
    build_reading_section(site_dir, public, template_str, last_post_date)

    # Render ideas section
    build_ideas_section(site_dir, public, template_str, last_post_date)

    # Now render all posts and indexes with last_post_date
    for posts, url_prefix, index_title in blog_sections:
        for post in posts:
            post_dir = post["_out_dir"]
            html = _render_template(template_str, post["title"], post["html"], last_post_date)
            (post_dir / "index.html").write_text(html)

        # Render section index
        index_dir = public / url_prefix
        index_dir.mkdir(parents=True, exist_ok=True)
        blog_list_html = f"<h1>{index_title}</h1>\n<ul class=\"post-list\">\n"
        for post in posts:
            date_str = post["date"].strftime("%Y-%m-%d")
            blog_list_html += (
                f'  <li><time datetime="{date_str}">{date_str}</time> '
                f'<a href="/{url_prefix}/{post["slug"]}/">{post["title"]}</a></li>\n'
            )
        blog_list_html += "</ul>"
        html = _render_template(template_str, index_title, blog_list_html, last_post_date)
        (index_dir / "index.html").write_text(html)

        # Render RSS feed
        feed_descriptions = {
            "blog": "Nathan Douglas's blog",
            "fr": "Le blog de Nathan Douglas (en français)",
        }
        feed_titles = {
            "blog": "Nathan Douglas",
            "fr": "Nathan Douglas (Français)",
        }
        feed_xml = _build_rss_feed(
            posts, url_prefix,
            feed_titles.get(url_prefix, index_title),
            feed_descriptions.get(url_prefix, index_title),
        )
        (index_dir / "feed.xml").write_text(feed_xml)

    # Build recent posts HTML for the index page
    recent_posts_html = _build_recent_posts_html(blog_sections)

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
                parsed["html"] += recent_posts_html
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


def build_reading_section(
    site_dir: Path, public: Path, template_str: str, last_post_date: str
) -> None:
    """Build the /reading/ index and /reading/YYYY/ year pages."""
    reading_dir = site_dir / "content" / "reading"
    if not reading_dir.exists():
        return

    books = []
    for md_file in sorted(reading_dir.rglob("*.md")):
        relative = md_file.relative_to(reading_dir)
        parts = relative.parts
        if len(parts) != 2:
            raise ValueError(
                f"Reading file {relative} doesn't match YYYY/MM.md structure"
            )
        year = int(parts[0])
        month = int(Path(parts[1]).stem)
        books.extend(parse_reading_file(md_file.read_text(), year, month))

    books.sort(key=lambda b: b["sort_key"])

    # Main /reading/ index: recent books + archive links
    content_html = "<h1>Reading</h1>\n"
    for book in books[:10]:
        content_html += f"<h2>{book['title']}</h2>\n{book['html']}\n"

    years = sorted({b["year"] for b in books}, reverse=True)
    content_html += "<h2>Archive</h2>\n<ul>\n"
    for y in years:
        count = sum(1 for b in books if b["year"] == y)
        content_html += (
            f'  <li><a href="/reading/{y}/">{y}</a> ({count} books)</li>\n'
        )
    content_html += "</ul>"

    out_dir = public / "reading"
    out_dir.mkdir(parents=True, exist_ok=True)
    html = _render_template(template_str, "Reading", content_html, last_post_date)
    (out_dir / "index.html").write_text(html)

    # Yearly pages: books grouped by month
    for y in years:
        year_books = [b for b in books if b["year"] == y]
        year_html = f"<h1>Reading: {y}</h1>\n"

        current_month = None
        for book in year_books:
            if book["month"] != current_month:
                current_month = book["month"]
                month_name = calendar.month_name[current_month]
                year_html += f"<h2>{month_name} {y}</h2>\n"
            year_html += f"<h3>{book['title']}</h3>\n{book['html']}\n"

        year_dir = public / "reading" / str(y)
        year_dir.mkdir(parents=True, exist_ok=True)
        page_html = _render_template(
            template_str, f"Reading: {y}", year_html, last_post_date
        )
        (year_dir / "index.html").write_text(page_html)

    # RSS feed
    feed_url = f"{SITE_URL}/reading/feed.xml"
    items = ""
    for book in books[:20]:
        link = f"{SITE_URL}/reading/{book['year']}/"
        date_rfc822 = datetime(book["year"], book["month"], 1, tzinfo=timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )
        items += f"""    <item>
      <title>{escape(book["title"])}</title>
      <link>{link}</link>
      <guid isPermaLink="false">{escape(book["title"])} ({book["year"]}-{book["month"]:02d})</guid>
      <pubDate>{date_rfc822}</pubDate>
      <description>{escape(book["html"])}</description>
    </item>
"""
    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Nathan Douglas — Reading</title>
    <link>{SITE_URL}/reading/</link>
    <description>Books I&#x27;ve been reading</description>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>
{items}  </channel>
</rss>
"""
    (out_dir / "feed.xml").write_text(feed_xml)


def build_ideas_section(
    site_dir: Path, public: Path, template_str: str, last_post_date: str
) -> None:
    """Build the /ideas/ index and /ideas/YYYY/ year pages."""
    ideas_dir = site_dir / "content" / "ideas"
    if not ideas_dir.exists():
        return

    months = []
    for md_file in sorted(ideas_dir.rglob("*.md")):
        relative = md_file.relative_to(ideas_dir)
        parts = relative.parts
        if len(parts) != 2:
            raise ValueError(
                f"Ideas file {relative} doesn't match YYYY/MM.md structure"
            )
        year = int(parts[0])
        month = int(Path(parts[1]).stem)
        raw = md_file.read_text()
        # Strip optional # heading (used for internal organization)
        body = re.sub(r"^#\s+.*\n*", "", raw, count=1)
        html = markdown.markdown(body, extensions=MD_EXTENSIONS)
        months.append({
            "year": year,
            "month": month,
            "html": html,
            "sort_key": (-year, -month),
        })

    months.sort(key=lambda m: m["sort_key"])

    # Main /ideas/ index: recent 3 months + archive links
    content_html = "<h1>Ideas</h1>\n"
    for m in months[:3]:
        month_name = calendar.month_name[m["month"]]
        content_html += f"<h2>{month_name} {m['year']}</h2>\n{m['html']}\n"

    years = sorted({m["year"] for m in months}, reverse=True)
    content_html += "<h2>Archive</h2>\n<ul>\n"
    for y in years:
        content_html += f'  <li><a href="/ideas/{y}/">{y}</a></li>\n'
    content_html += "</ul>"

    out_dir = public / "ideas"
    out_dir.mkdir(parents=True, exist_ok=True)
    html = _render_template(template_str, "Ideas", content_html, last_post_date)
    (out_dir / "index.html").write_text(html)

    # Yearly pages
    for y in years:
        year_months = [m for m in months if m["year"] == y]
        year_html = f"<h1>Ideas: {y}</h1>\n"
        for m in year_months:
            month_name = calendar.month_name[m["month"]]
            year_html += f"<h2>{month_name} {y}</h2>\n{m['html']}\n"

        year_dir = public / "ideas" / str(y)
        year_dir.mkdir(parents=True, exist_ok=True)
        page_html = _render_template(
            template_str, f"Ideas: {y}", year_html, last_post_date
        )
        (year_dir / "index.html").write_text(page_html)


SITE_URL = "https://darkdell.net"


def _build_rss_feed(posts: list, url_prefix: str, title: str, description: str) -> str:
    """Build an RSS 2.0 XML feed for a list of posts."""
    feed_url = f"{SITE_URL}/{url_prefix}/feed.xml"
    items = ""
    for post in posts[:20]:
        date_rfc822 = post["date"].replace(tzinfo=timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )
        link = f"{SITE_URL}/{url_prefix}/{post['slug']}/"
        items += f"""    <item>
      <title>{escape(post["title"])}</title>
      <link>{link}</link>
      <guid>{link}</guid>
      <pubDate>{date_rfc822}</pubDate>
      <description>{escape(post["html"])}</description>
    </item>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(title)}</title>
    <link>{SITE_URL}/{url_prefix}/</link>
    <description>{escape(description)}</description>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>
{items}  </channel>
</rss>
"""


def _build_recent_posts_html(blog_sections: list, max_posts: int = 5) -> str:
    """Build HTML listing recent posts across all blog sections."""
    all_recent = []
    section_labels = {"blog": "EN", "fr": "FR"}
    for posts, url_prefix, _index_title in blog_sections:
        for post in posts:
            all_recent.append((post, url_prefix))
    all_recent.sort(key=lambda pair: pair[0]["date"], reverse=True)
    all_recent = all_recent[:max_posts]

    if not all_recent:
        return ""

    html = '\n<ul class="post-list">\n'
    for post, url_prefix in all_recent:
        date_str = post["date"].strftime("%Y-%m-%d")
        label = section_labels.get(url_prefix, "")
        html += (
            f'  <li><time datetime="{date_str}">{date_str}</time> '
            f'<a href="/{url_prefix}/{post["slug"]}/">{post["title"]}</a>'
            f" ({label})</li>\n"
        )
    html += "</ul>"
    return html


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
