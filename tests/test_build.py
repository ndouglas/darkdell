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
