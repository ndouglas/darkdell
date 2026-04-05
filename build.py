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
    # Priority: frontmatter > filename date prefix (YYYY-MM-DD-*) > mtime > now
    date = None
    if "date" in frontmatter:
        d = frontmatter["date"]
        if isinstance(d, datetime):
            date = d
        else:
            date = datetime.fromisoformat(str(d))
    else:
        date_prefix = re.match(r"^(\d{4}-\d{2}-\d{2})-", filename)
        if date_prefix:
            date = datetime.fromisoformat(date_prefix.group(1))
        elif mtime is not None:
            date = datetime.fromtimestamp(mtime)
        else:
            date = datetime.now()

    # Render markdown to HTML
    html = markdown.markdown(body, extensions=["fenced_code", "codehilite", "tables"])

    return {"title": title, "date": date, "html": html, "frontmatter": frontmatter}


def _humanize_filename(filename: str) -> str:
    """Convert '2026-03-25-b-trees-are-neat.md' to 'B Trees Are Neat'."""
    stem = Path(filename).stem
    # Strip date prefix if present
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
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
            for md_file in sorted(posts_dir.glob("*.md")):
                raw = md_file.read_text()
                mtime = md_file.stat().st_mtime
                parsed = parse_content(raw, filename=md_file.name, mtime=mtime)
                slug = md_file.stem
                slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
                parsed["slug"] = slug
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
