#!/usr/bin/env python3
"""Static site generator for darkdell.net."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from string import Template

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
