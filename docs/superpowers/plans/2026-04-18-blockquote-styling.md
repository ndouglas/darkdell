# Blockquote Styling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add distinctive, theme-appropriate blockquote styling to all three themes (`clean`, `consumed`, `garish`) so `<blockquote>` elements are visually set apart from body prose.

**Architecture:** Pure CSS change — three parallel edits, one per theme stylesheet. Each theme reuses its existing color palette and visual idioms (no new tokens). No Python or template changes.

**Tech Stack:** CSS only. Site is built via `python build.py` (or `make build`); preview via `make serve` at `http://localhost:8000/`.

**Spec:** `docs/superpowers/specs/2026-04-18-blockquote-styling-design.md`

**Testing note:** This is visual CSS work. There is no unit-test framework for rendering. Verification for each task is: build the site, load the Heraclitus post in the browser under the target theme, and confirm the blockquote renders as specified.

**Reference post for verification:** `content/posts/2026/04/18-heraclitus.md` — contains a multi-line poem using `<br>` tags followed by an em-dash attribution paragraph. URL after build: `http://localhost:8000/blog/heraclitus/`.

---

## Task 1: Style blockquotes in the `clean` theme

**Files:**
- Modify: `themes/clean/style.css` (insert new rules after line 64, the `main pre code` rule)

- [ ] **Step 1: Add blockquote rules to `themes/clean/style.css`**

Insert these rules after the `main pre code { background: none; padding: 0; }` line (currently line 64) and before the `.post-list` rule:

```css
main blockquote {
  margin: 1.5rem 0;
  padding: 0.25rem 0 0.25rem 1rem;
  border-left: 3px solid #ccc;
  font-style: italic;
  color: #555;
}
main blockquote p { margin-bottom: 0.75rem; }
main blockquote p:last-child { margin-bottom: 0; }
main blockquote blockquote {
  margin: 0.5rem 0 0.5rem 1rem;
  border: none;
  background: none;
  padding: 0 0 0 1rem;
  transform: none;
}
```

- [ ] **Step 2: Rebuild the site**

Run: `make build`
Expected: "Site built to public/" with no errors.

- [ ] **Step 3: Serve and visually verify**

Run: `make serve` (or if already running, reload). Load `http://localhost:8000/blog/heraclitus/` and switch to the `clean` theme using the theme switcher (bottom-right button). You may need to click it multiple times to cycle to `clean`.

Expected:
- Blockquote has a light gray left border (3px).
- Text is italic and muted gray (`#555`).
- The multi-line poem reads cleanly with `<br>` breaks preserved.
- The em-dash attribution paragraph sits below the poem with normal (not collapsed) spacing.
- No bottom margin after the final paragraph inside the blockquote.

- [ ] **Step 4: Commit**

```bash
git add themes/clean/style.css
git commit -m "Style blockquotes in clean theme"
```

---

## Task 2: Style blockquotes in the `consumed` theme

**Files:**
- Modify: `themes/consumed/style.css` (insert new rules after line 99, the `main pre code` rule)

- [ ] **Step 1: Add blockquote rules to `themes/consumed/style.css`**

Insert these rules after the `main pre code { background: none; padding: 0; }` line (currently line 99) and before the `.post-list` rule:

```css
main blockquote {
  margin: 1.5rem 0;
  padding: 0.75rem 1rem;
  border-left: 2px solid #5a3828;
  background: rgba(212, 184, 168, 0.03);
  font-style: italic;
  color: #baa090;
  text-shadow: 0 0 4px rgba(220, 180, 160, 0.15);
}
main blockquote p { margin-bottom: 0.75rem; }
main blockquote p:last-child { margin-bottom: 0; }
main blockquote blockquote {
  margin: 0.5rem 0 0.5rem 1rem;
  border: none;
  background: none;
  padding: 0 0 0 1rem;
  transform: none;
}
```

- [ ] **Step 2: Rebuild the site**

Run: `make build`
Expected: "Site built to public/" with no errors.

- [ ] **Step 3: Serve and visually verify**

Load `http://localhost:8000/blog/heraclitus/` and switch to the `consumed` theme (this is the default — it should be active on first load with a cleared `localStorage`).

Expected:
- Blockquote has a rust-colored left border (2px, `#5a3828` — the same color as link underlines elsewhere).
- Very faint tan-toned background tint behind the blockquote.
- Text is italic in the lighter rust color (`#baa090`) with a soft glow.
- Poem and attribution both render correctly with proper spacing.
- The glow does not look garish — it's a subtle lift, consistent with the h1 glow.

- [ ] **Step 4: Commit**

```bash
git add themes/consumed/style.css
git commit -m "Style blockquotes in consumed theme"
```

---

## Task 3: Style blockquotes in the `garish` theme

**Files:**
- Modify: `themes/garish/style.css` (insert new rules after line 97, the `main pre code` rule)

- [ ] **Step 1: Add blockquote rules to `themes/garish/style.css`**

Insert these rules after the `main pre code { background: none; color: #00ff00; font-family: monospace; }` line (currently line 97) and before the `.post-list` rule:

```css
main blockquote {
  position: relative;
  margin: 1.5rem 0;
  padding: 1rem 1.25rem 1rem 2.5rem;
  border: 3px dashed #00ffff;
  background: rgba(255, 255, 0, 0.5);
  border-radius: 12px;
  transform: rotate(-0.5deg);
}
main blockquote::before {
  content: '\275D';
  position: absolute;
  top: 0.25rem;
  left: 0.5rem;
  font-size: 2rem;
  color: #ff00ff;
  line-height: 1;
}
main blockquote p { margin-bottom: 0.75rem; }
main blockquote p:last-child { margin-bottom: 0; }
main blockquote blockquote {
  margin: 0.5rem 0 0.5rem 1rem;
  border: none;
  background: none;
  padding: 0 0 0 1rem;
  transform: none;
}
```

Note: `\275D` is the curly opening quote glyph ❝.

- [ ] **Step 2: Rebuild the site**

Run: `make build`
Expected: "Site built to public/" with no errors.

- [ ] **Step 3: Serve and visually verify**

Load `http://localhost:8000/blog/heraclitus/` and switch to the `garish` theme using the theme switcher.

Expected:
- Blockquote has a 3px dashed cyan border with 12px rounded corners.
- Semi-transparent yellow background behind the blockquote.
- Entire blockquote is rotated slightly counter-clockwise (0.5°).
- A large magenta `❝` glyph appears in the top-left inside the blockquote.
- Text does not overlap the `❝` glyph (the `padding-left: 2.5rem` provides clearance).
- Poem and attribution render correctly; no content clipped by the border radius.

- [ ] **Step 4: Commit**

```bash
git add themes/garish/style.css
git commit -m "Style blockquotes in garish theme"
```

---

## Task 4: Cross-theme verification and wrap-up

**Files:** none modified.

- [ ] **Step 1: Cycle through all three themes on the Heraclitus post**

With the dev server running, load `http://localhost:8000/blog/heraclitus/` and click the theme switcher three times, confirming each theme's blockquote renders as described in Tasks 1–3.

Expected: no visual regressions on non-blockquote content (headings, links, paragraphs, nav all look unchanged).

- [ ] **Step 2: Sanity-check a post without a blockquote**

Load any other post (e.g., `http://localhost:8000/blog/` and pick any entry without a blockquote).

Expected: no visual changes compared to before this work. Blockquote rules should not leak into surrounding prose.

- [ ] **Step 3: Remove the implementation plan (optional, per global CLAUDE.md convention)**

Per `~/.claude/CLAUDE.md`: "Remove file when all stages are done." However this project stores plans under `docs/superpowers/plans/` for history — leave the plan in place.

- [ ] **Step 4: Final status check**

Run: `git log --oneline -5`
Expected: Three new commits (one per theme), on top of the spec commit.

Run: `git status`
Expected: clean working tree.
