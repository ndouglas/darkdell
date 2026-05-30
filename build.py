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
SITE_URL = "https://darkdell.net"


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
    stem = re.sub(r"^\d{2}-", "", stem)
    return stem.replace("-", " ").replace("_", " ").title()


def render_title_html(title: str) -> str:
    """Render a title's inline markdown to HTML, without the wrapping <p>."""
    html = markdown.markdown(title).strip()
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4]
    return html


_INLINE_MD_PATTERNS = [
    (re.compile(r"\*\*(.+?)\*\*"), r"\1"),
    (re.compile(r"__(.+?)__"), r"\1"),
    (re.compile(r"(?<!\w)\*([^*\s].*?)\*(?!\w)"), r"\1"),
    (re.compile(r"(?<!\w)_([^_\s].*?)_(?!\w)"), r"\1"),
    (re.compile(r"`([^`]+)`"), r"\1"),
]


def strip_title_markdown(title: str) -> str:
    """Strip inline markdown markers from a title for plain-text contexts."""
    s = title
    for pattern, repl in _INLINE_MD_PATTERNS:
        s = pattern.sub(repl, s)
    return s


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


def _parse_monthly_files(content_dir: Path) -> list[dict]:
    """Discover and parse YYYY/MM.md files into sorted monthly entries.

    Each file's optional # heading is stripped before rendering.
    Returns entries sorted newest-first.
    """
    months = []
    for md_file in sorted(content_dir.rglob("*.md")):
        relative = md_file.relative_to(content_dir)
        parts = relative.parts
        if len(parts) != 2:
            raise ValueError(
                f"File {relative} doesn't match YYYY/MM.md structure"
            )
        year = int(parts[0])
        month = int(Path(parts[1]).stem)
        raw = md_file.read_text()
        body = re.sub(r"^#\s+.*\n*", "", raw, count=1)
        html = markdown.markdown(body, extensions=MD_EXTENSIONS)
        months.append({
            "year": year,
            "month": month,
            "raw_body": body,
            "html": html,
            "sort_key": (-year, -month),
        })
    months.sort(key=lambda m: m["sort_key"])
    return months


MAX_TITLE_CHARS = 120


def _cap_title(s: str) -> str:
    """Cap a candidate title at MAX_TITLE_CHARS, preferring a word boundary."""
    s = s.strip()
    if len(s) <= MAX_TITLE_CHARS:
        return s
    prefix = s[:MAX_TITLE_CHARS]
    last_space = prefix.rfind(" ")
    if last_space > MAX_TITLE_CHARS // 2:
        return prefix[:last_space].rstrip(",;:- ") + "…"
    return prefix.rstrip() + "…"


def _extract_bullet_title(bullet: str) -> str:
    """Derive a concise title from a bullet's markdown.

    Cases handled (in order):
    - Starts with `**Bold**` or `*Italic*` or `_Italic_`: use the emphasised text.
    - Otherwise: use the first sentence (up to '.', '?', '!'), capped.
    - As a final fallback: use the full bullet, capped.
    All results are run through `_cap_title` so titles stay under 120 chars.
    """
    s = bullet.strip()
    # Check double-asterisk bold before single-asterisk italic.
    for open_c, close_c in (("**", "**"), ("*", "*"), ("_", "_")):
        if s.startswith(open_c):
            end = s.find(close_c, len(open_c))
            if end > len(open_c):
                return _cap_title(s[len(open_c):end])
    first_end = min(
        (i for i in (s.find(p) for p in ".!?") if i != -1),
        default=-1,
    )
    if first_end > 0:
        return _cap_title(s[:first_end])
    return _cap_title(s)


def _parse_monthly_bullets(months: list[dict]) -> list[dict]:
    """Flatten monthly files into one entry per bullet, newest-first.

    Each returned dict has:
        year, month, index, title, description_html, pub_date

    `pub_date` is `datetime(year, month, 1)` with a per-bullet offset in
    seconds so RSS readers can keep entries ordered within a month.
    """
    bullets: list[dict] = []
    for m in months:
        # Split raw markdown body on top-level bullet lines. Only `- ` bullets
        # at the start of a line count; indented continuations fold into the
        # preceding bullet.
        current: list[str] = []
        all_bullets: list[str] = []
        for line in m["raw_body"].splitlines():
            if line.startswith("- "):
                if current:
                    all_bullets.append("\n".join(current))
                current = [line[2:]]
            elif current and (line.startswith("  ") or line.strip() == ""):
                current.append(line)
            else:
                if current:
                    all_bullets.append("\n".join(current))
                    current = []
        if current:
            all_bullets.append("\n".join(current))

        for i, body in enumerate(all_bullets):
            if not body.strip():
                continue
            title = _extract_bullet_title(body)
            description_html = markdown.markdown(body, extensions=MD_EXTENSIONS)
            pub_date = datetime(m["year"], m["month"], 1, tzinfo=timezone.utc)
            # Stagger pub_date within a month by bullet index (seconds) so
            # newest bullets sort first in aggregators.
            pub_date = pub_date.replace(
                second=min(59, (len(all_bullets) - i - 1) % 60)
            )
            bullets.append({
                "year": m["year"],
                "month": m["month"],
                "index": i,
                "title": title,
                "description_html": description_html,
                "pub_date": pub_date,
            })
    return bullets


def _build_rss_feed(items: list[dict], section: str, title: str, description: str) -> str:
    """Build an RSS 2.0 XML feed.

    Each item dict must have: title, link, guid, pub_date, description.
    """
    feed_url = f"{SITE_URL}/{section}/feed.xml"
    items_xml = ""
    for item in items[:20]:
        date_rfc822 = item["pub_date"].strftime("%a, %d %b %Y %H:%M:%S +0000")
        items_xml += f"""    <item>
      <title>{escape(item["title"])}</title>
      <link>{item["link"]}</link>
      <guid>{escape(item["guid"])}</guid>
      <pubDate>{date_rfc822}</pubDate>
      <description>{escape(item["description"])}</description>
    </item>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(title)}</title>
    <link>{SITE_URL}/{section}/</link>
    <description>{escape(description)}</description>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>
{items_xml}  </channel>
</rss>
"""


def _render_template(template_str: str, title: str, content: str, last_post_date: str) -> str:
    """Render the base template with the given content."""
    return Template(template_str).safe_substitute(
        title=title,
        content=content,
        last_post_date=last_post_date,
        nav="",
    )


# ---------------------------------------------------------------------------
# Section builders — each returns an HTML snippet for the homepage
# ---------------------------------------------------------------------------

BLOG_SECTIONS = [
    ("posts", "blog", "Blog", "Nathan Douglas's blog"),
]


def _build_blog_sections(
    site_dir: Path, public: Path, template_str: str, last_post_date: str,
) -> str:
    """Build all blog sections (EN + FR): posts, indexes, feeds.

    Returns an HTML snippet of recent posts for the homepage.
    """
    all_posts = []

    for content_subdir, url_prefix, index_title, feed_description in BLOG_SECTIONS:
        posts = []
        posts_dir = site_dir / "content" / content_subdir
        if not posts_dir.exists():
            continue

        seen_slugs: dict[str, Path] = {}
        for md_file in sorted(posts_dir.rglob("*.md")):
            if md_file.name.startswith("_"):
                continue
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
        all_posts.extend((post, url_prefix) for post in posts)

        # Render individual posts
        for post in posts:
            post_dir = public / url_prefix / post["slug"]
            post_dir.mkdir(parents=True, exist_ok=True)
            html = _render_template(
                template_str, strip_title_markdown(post["title"]), post["html"], last_post_date
            )
            (post_dir / "index.html").write_text(html)

        # Render section index
        index_dir = public / url_prefix
        index_dir.mkdir(parents=True, exist_ok=True)
        blog_list_html = f"<h1>{index_title}</h1>\n"
        intro_file = posts_dir / "_intro.md"
        if intro_file.exists():
            intro_parsed = parse_content(intro_file.read_text(), filename=intro_file.name)
            blog_list_html += f'<div class="section-intro">{intro_parsed["html"]}</div>\n'
        blog_list_html += "<ul class=\"post-list\">\n"
        for post in posts:
            date_str = post["date"].strftime("%Y-%m-%d")
            blog_list_html += (
                f'  <li><time datetime="{date_str}">{date_str}</time> '
                f'<a href="/{url_prefix}/{post["slug"]}/">{render_title_html(post["title"])}</a></li>\n'
            )
        blog_list_html += "</ul>"
        html = _render_template(template_str, index_title, blog_list_html, last_post_date)
        (index_dir / "index.html").write_text(html)

        # RSS feed
        feed_items = [
            {
                "title": strip_title_markdown(p["title"]),
                "link": f"{SITE_URL}/{url_prefix}/{p['slug']}/",
                "guid": f"{SITE_URL}/{url_prefix}/{p['slug']}/",
                "pub_date": p["date"].replace(tzinfo=timezone.utc),
                "description": p["html"],
            }
            for p in posts
        ]
        feed_xml = _build_rss_feed(feed_items, url_prefix, index_title, feed_description)
        (index_dir / "feed.xml").write_text(feed_xml)

    # Build recent posts snippet for homepage
    all_posts.sort(key=lambda pair: pair[0]["date"], reverse=True)
    recent = all_posts[:5]
    if not recent:
        return ""

    snippet = '\n<h2>Recent Posts</h2>\n<ul class="post-list">\n'
    for post, url_prefix in recent:
        date_str = post["date"].strftime("%Y-%m-%d")
        snippet += (
            f'  <li><time datetime="{date_str}">{date_str}</time> '
            f'<a href="/{url_prefix}/{post["slug"]}/">{render_title_html(post["title"])}</a></li>\n'
        )
    snippet += "</ul>"
    return snippet


def _build_monthly_section(
    site_dir: Path, public: Path, template_str: str, last_post_date: str,
    section: str, title: str, recent_months: int = 3,
) -> str:
    """Build a monthly-file section: index page, yearly pages, and RSS feed.

    Returns an HTML snippet of recent content for the homepage.
    """
    content_dir = site_dir / "content" / section
    if not content_dir.exists():
        return ""

    months = _parse_monthly_files(content_dir)
    if not months:
        return ""

    # Main index: recent months + archive links
    content_html = f"<h1>{title}</h1>\n"
    for m in months[:recent_months]:
        month_name = calendar.month_name[m["month"]]
        content_html += f"<h2>{month_name} {m['year']}</h2>\n{m['html']}\n"

    years = sorted({m["year"] for m in months}, reverse=True)
    content_html += "<h2>Archive</h2>\n<ul>\n"
    for y in years:
        content_html += f'  <li><a href="/{section}/{y}/">{y}</a></li>\n'
    content_html += "</ul>"

    out_dir = public / section
    out_dir.mkdir(parents=True, exist_ok=True)
    html = _render_template(template_str, title, content_html, last_post_date)
    (out_dir / "index.html").write_text(html)

    # Yearly pages
    for y in years:
        year_months = [m for m in months if m["year"] == y]
        year_html = f"<h1>{title}: {y}</h1>\n"
        for m in year_months:
            month_name = calendar.month_name[m["month"]]
            year_html += f"<h2>{month_name} {y}</h2>\n{m['html']}\n"

        year_dir = out_dir / str(y)
        year_dir.mkdir(parents=True, exist_ok=True)
        page_html = _render_template(
            template_str, f"{title}: {y}", year_html, last_post_date
        )
        (year_dir / "index.html").write_text(page_html)

    # RSS feed — one item per bullet rather than per month, so downstream
    # consumers get a usable per-entry title instead of a month header.
    bullets = _parse_monthly_bullets(months)
    feed_items = [
        {
            "title": b["title"],
            "link": f"{SITE_URL}/{section}/{b['year']}/",
            "guid": f"{section}-{b['year']}-{b['month']:02d}-{b['index']}",
            "pub_date": b["pub_date"],
            "description": b["description_html"],
        }
        for b in bullets
    ]
    feed_xml = _build_rss_feed(
        feed_items, section, f"Nathan Douglas — {title}", title
    )
    (out_dir / "feed.xml").write_text(feed_xml)

    # Return recent snippet for homepage
    snippet = f'\n<h2><a href="/{section}/">Recent {title}</a></h2>\n'
    for m in months[:2]:
        snippet += m["html"] + "\n"
    return snippet


# ---------------------------------------------------------------------------
# Monthly sections — add new ones here
# ---------------------------------------------------------------------------

MONTHLY_SECTIONS = [
    ("reading", "Reading"),
    ("ideas", "Ideas"),
]


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build_site(site_dir: Path) -> None:
    """Build the complete site from site_dir into site_dir/public/."""
    site_dir = Path(site_dir)
    public = site_dir / "public"

    if public.exists():
        shutil.rmtree(public)
    public.mkdir()

    # Load template and populate RSS autodiscovery links
    template_str = (site_dir / "templates" / "base.html").read_text()
    rss_feeds = [
        (title, f"/{prefix}/feed.xml")
        for _, prefix, title, _ in BLOG_SECTIONS
    ]
    for section, label in MONTHLY_SECTIONS:
        if (site_dir / "content" / section).exists():
            rss_feeds.append((f"Nathan Douglas — {label}", f"/{section}/feed.xml"))
    rss_links = "\n  ".join(
        f'<link rel="alternate" type="application/rss+xml" title="{t}" href="{h}">'
        for t, h in rss_feeds
    )
    template_str = Template(template_str).safe_substitute(rss_links=rss_links)

    # Collect all posts to determine last_post_date for vitality
    all_post_dates = []
    for content_subdir, *_ in BLOG_SECTIONS:
        posts_dir = site_dir / "content" / content_subdir
        if posts_dir.exists():
            for md_file in posts_dir.rglob("*.md"):
                if md_file.name.startswith("_"):
                    continue
                relative = md_file.relative_to(posts_dir)
                date, _ = extract_post_date_and_slug(relative)
                all_post_dates.append(date)
    all_post_dates.sort(reverse=True)
    last_post_date = all_post_dates[0].strftime("%Y-%m-%d") if all_post_dates else "1970-01-01"

    # Build sections — each returns a homepage snippet
    homepage_snippets = []
    homepage_snippets.append(
        _build_blog_sections(site_dir, public, template_str, last_post_date)
    )
    for section, title in MONTHLY_SECTIONS:
        homepage_snippets.append(
            _build_monthly_section(site_dir, public, template_str, last_post_date, section, title)
        )

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
                parsed["html"] += "".join(homepage_snippets)
            else:
                out_dir = public / slug
                out_dir.mkdir(parents=True, exist_ok=True)

            html = _render_template(
                template_str, strip_title_markdown(parsed["title"]), parsed["html"], last_post_date
            )
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


if __name__ == "__main__":
    build_site(Path("."))
    print("Site built to public/")
