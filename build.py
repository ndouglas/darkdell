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
            "html": html,
            "sort_key": (-year, -month),
        })
    months.sort(key=lambda m: m["sort_key"])
    return months


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

    # Render monthly sections
    recent_reading = _build_monthly_section(
        site_dir, public, template_str, last_post_date, "reading", "Reading"
    )
    recent_ideas = _build_monthly_section(
        site_dir, public, template_str, last_post_date, "ideas", "Ideas"
    )

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
                parsed["html"] += recent_reading
                parsed["html"] += recent_ideas
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

    # RSS feed
    feed_url = f"{SITE_URL}/{section}/feed.xml"
    items = ""
    for m in months[:20]:
        month_name = calendar.month_name[m["month"]]
        link = f"{SITE_URL}/{section}/{m['year']}/"
        date_rfc822 = datetime(m["year"], m["month"], 1, tzinfo=timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )
        items += f"""    <item>
      <title>{escape(month_name)} {m["year"]}</title>
      <link>{link}</link>
      <guid isPermaLink="false">{section}-{m["year"]}-{m["month"]:02d}</guid>
      <pubDate>{date_rfc822}</pubDate>
      <description>{escape(m["html"])}</description>
    </item>
"""
    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Nathan Douglas — {escape(title)}</title>
    <link>{SITE_URL}/{section}/</link>
    <description>{escape(title)}</description>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>
{items}  </channel>
</rss>
"""
    (out_dir / "feed.xml").write_text(feed_xml)

    # Return recent snippet for homepage
    recent = months[0]
    month_name = calendar.month_name[recent["month"]]
    return (
        f'\n<h2>Recent {title} '
        f'<a href="/{section}/">({month_name} {recent["year"]})</a></h2>\n'
        f'{recent["html"]}\n'
    )


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
