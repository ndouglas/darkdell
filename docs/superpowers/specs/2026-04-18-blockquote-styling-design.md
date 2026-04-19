# Blockquote Styling — Design

## Goal

Give `<blockquote>` elements distinctive visual treatment in all three themes (`clean`, `consumed`, `garish`). Currently blockquotes inherit body styling and are visually indistinguishable from surrounding prose.

## Constraints

- Pure CSS — no changes to `build.py`, markdown parsing, or HTML template.
- Each theme's blockquote treatment must use the theme's existing visual vocabulary (colors, borders, motion, typography). No new design tokens.
- Must handle the existing content shape seen in `content/posts/2026/04/18-heraclitus.md`: a multi-line poem using `<br>` within `<p>`, followed by an em-dash attribution `<p>`.

## Per-theme designs

### `themes/clean/style.css` — editorial pull-quote

Classic left-rule treatment.

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
```

### `themes/consumed/style.css` — glowing vellum

Reuses the existing rust/tan palette and soft text-shadow glow language.

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
```

### `themes/garish/style.css` — over-the-top pull-quote box

Pushes the existing dashed-border / rotate / multicolor idioms further.

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
  content: '\275D';  /* ❝ */
  position: absolute;
  top: 0.25rem;
  left: 0.5rem;
  font-size: 2rem;
  color: #ff00ff;
  line-height: 1;
}
main blockquote p { margin-bottom: 0.75rem; }
main blockquote p:last-child { margin-bottom: 0; }
```

## Nested blockquotes

Add this rule to each of the three theme files. Nested blockquotes collapse visual treatment to a deeper left indent only — no re-bordering, no re-rotation. `transform: none` is a no-op in `clean` and `consumed` but cancels the outer rotation in `garish`.

```css
main blockquote blockquote {
  margin: 0.5rem 0 0.5rem 1rem;
  border: none;
  background: none;
  padding: 0 0 0 1rem;
  transform: none;
}
```

## Testing

Render and visually verify:
1. The Heraclitus post (`content/posts/2026/04/18-heraclitus.md`) — multi-line poem with `<br>` and em-dash attribution.
2. Theme switcher cycles through all three themes with blockquote styling applied.
3. Nested blockquote (if/when it appears) — deeper indent only.

No automated tests; verification is visual via `make` / local preview.

## Out of scope

- Special-casing the em-dash attribution paragraph (e.g., right-aligned `cite` styling). Authors handle attribution formatting in the content.
- Styling `<q>` inline quotes.
- Print styles.
