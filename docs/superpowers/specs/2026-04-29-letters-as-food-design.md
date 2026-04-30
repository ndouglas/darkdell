# Letters as Food — Design Spec

## Summary

When a reader navigates from one page to another on the "consumed" theme, the visible above-the-fold text on the current page becomes food for the existing ant colony simulation. The page content briefly dissolves in place over ~400ms, with food piles deposited into the canvas at grid cells matching the text's on-screen position. The next page loads with those food piles still present, and ants forage them through the existing pheromone-based simulation.

The feature is a single-file extension of `themes/consumed/ants.js`. No new files, no new dependencies, no build-system changes.

## Decisions

| Question | Decision |
| --- | --- |
| Trigger | On internal link click (page leave) |
| Spatial mapping | Positional, only above-the-fold text |
| Transition | ~400ms dissolve animation, then hard nav |
| Granularity | Per-character, coalesced by canvas grid cell |
| Food economy | Random food keeps spawning + letter drops accumulate, with food decay and FIFO cap |
| Drop animation | Dissolve in place (CSS opacity + blur on the article container) |
| Persistence | sessionStorage; consumed-theme-only; fresh start on direct entry, refresh, back/forward, or external links in |

## Architecture

Single file: `themes/consumed/ants.js`. Lifecycle:

1. **On simulation start** (consumed theme active): before initializing food sources, read `sessionStorage.darkdell.pendingDrop`. If present, parse it into a list of `{x, y, amount, source: 'letter', depositedAt}` food entries, append them to the `foods` array, and delete the storage key.
2. **While the page is live**: install a delegated `click` handler on `document` that filters for qualifying same-origin link clicks (see Filtering below). Also install matching pointer-event guards.
3. **On qualifying click**:
   1. `event.preventDefault()`.
   2. Set `inFlight = true` to ignore subsequent clicks during the dissolve.
   3. Walk visible text via `Range.getClientRects()`, build `cellCounts: Map<"x,y", count>` clipped to `[0, viewportH]`.
   4. Convert each non-empty cell to a food source `{x, y, amount: count * FOOD_PER_LETTER, source: 'letter', depositedAt: now}`.
   5. Append to in-memory `foods` array (so the current page's ants react during the dissolve), evicting oldest entries if total exceeds `MAX_FOOD_SOURCES`.
   6. Serialize the new entries to `sessionStorage.darkdell.pendingDrop` (JSON).
   7. Add CSS class `darkdell-dissolving` to `<body>`. CSS rule transitions article opacity to 0 and applies a 2px blur over 400ms.
   8. `setTimeout(() => { location.href = href; }, 400)`.
4. **On theme switch away from consumed** (`setTheme('garish'|'clean')`): existing teardown stops the simulation. Extend it to remove the click handler.
5. **On theme switch to consumed**: existing setup starts the simulation. Extend it to install the click handler.

## Capture: visible text → grid cells

```
GRID_W = 128, GRID_H = 64 (existing constants)
cellW = window.innerWidth  / GRID_W
cellH = window.innerHeight / GRID_H

walker = TreeWalker over document.body, NodeFilter.SHOW_TEXT
  reject: nodes inside <script>, <style>, the canvas itself, or
          the theme switcher button

cellCounts = empty Map

for each text node:
  range = new Range(); range.selectNode(node)
  for each rect in range.getClientRects():
    if rect.bottom <= 0 || rect.top >= window.innerHeight: continue
    visibleTop    = max(0, rect.top)
    visibleBottom = min(window.innerHeight, rect.bottom)
    visibleRatio  = (visibleBottom - visibleTop) / rect.height
    chars         = node.length * (rect.width / total node width across rects) * visibleRatio
    distribute chars uniformly across rect.width into grid cells:
      for x in [rect.left, rect.right) stepping by cellW:
        cellX = floor(x / cellW)
        cellY = floor((visibleTop + visibleBottom) / 2 / cellH)
        cellCounts.add(cellX, cellY, chars * (cellW / rect.width))
```

The "total node width across rects" denominator handles multi-line wrapping; we want the chars distributed across all rects of one node proportionally to width. Implementation can iterate rects twice (sum widths first, then distribute).

`FOOD_PER_LETTER = 4`. A typical dense cell with ~20 chars yields `amount = 80`, matching the existing `FOOD_PER_SOURCE = 80` baseline. This is the starting calibration; tune in manual testing.

## Drop animation

CSS (added to `themes/consumed/style.css` or inlined as a `<style>` block from JS):

```css
body.darkdell-dissolving article,
body.darkdell-dissolving main,
body.darkdell-dissolving .post {
  transition: opacity 400ms ease-in, filter 400ms ease-in;
  opacity: 0;
  filter: blur(2px);
  pointer-events: none;
}
```

(Selector matches whichever container the consumed theme actually wraps post content in — to be confirmed when implementing by inspecting the rendered HTML.)

The dissolve runs concurrently with the food being deposited into the in-memory `foods` array, so the user sees the existing ants on the current page begin reacting (heads turn, pheromone trails light up) while the article fades. After 400ms `setTimeout`, hard nav fires.

The next page's `ants.js` reads sessionStorage on init and recreates the food list. Pheromone state and ant positions are fresh; ants spawn at the hive and have to discover the food. The cognitive trick: the previous page showed food being deposited; the next page shows the consequences.

## Food economy

Three changes to the existing food model:

**(a) Decay.** New constant `FOOD_DECAY_PER_TICK = 0.0001`. In `tick()`, after pheromone decay, walk `foods`:

```js
for (var k = 0; k < foods.length; k++) {
  foods[k].amount = Math.max(0, foods[k].amount - FOOD_DECAY_PER_TICK);
}
```

At 180 ticks/sec (60fps × 3 ticks/frame), an `amount=4` letter pile lasts ~3.7 minutes untouched; an `amount=80` random pile lasts ~74 minutes. The existing filter `foods = foods.filter(f => f.amount > 0)` already removes depleted entries — no change needed there.

**(b) Random food spawning unchanged.** The existing 8-source baseline metabolism continues. Letter drops layer on top.

**(c) FIFO cap.** New constant `MAX_FOOD_SOURCES = 300`. In the deposit code, after appending letter drops, if `foods.length > MAX_FOOD_SOURCES`, sort by `depositedAt` ascending and slice off the oldest. Both `spawnFoods` and the letter-drop deposit tag entries with `depositedAt: Date.now()`. The cap will rarely be hit in normal use; it exists as a safety bound on the inner foraging loop.

**Vitality unchanged.** Stays tied to last post date. Reading activity does not factor in. The vitality signal represents the writer's recency, not the reader's engagement; conflating them would make the canvas more "alive" when the writer has gone quiet.

**Pheromone behavior unchanged.** Letter food sources are regular `{x, y, amount}` foods. The existing pheromone learning loop will naturally cluster ants on dense letter drops because larger amounts mean more successful trips, more pheromone reinforcement.

## Link interception filter

The handler runs `preventDefault()` only when ALL of these are true:

- `event.button === 0` (primary click only)
- `!event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey`
- `!event.defaultPrevented`
- The closest `<a>` ancestor exists, has an `href` attribute
- `<a>` has no `target` attribute, or `target === '_self'`
- `<a>` has no `download` attribute
- The `href`, resolved via `new URL(a.href, location.href)`, has the same `origin` as `location.origin`
- The resolved URL is not just an in-page anchor — i.e., not (same `pathname` AND same `search` AND `hash` differs only)
- Protocol is `http:` or `https:`
- `inFlight` flag is `false`

If any check fails, the handler returns and the browser proceeds normally. This means cmd-click, middle-click, external links, downloads, mailto, in-page anchors, target="_blank" all work unchanged.

**Re-entry guard:** when intercepting, set `inFlight = true`. Failsafe `setTimeout(() => { inFlight = false; }, 1000)` resets it in case nav was canceled (e.g., user pressed Escape, network error before any new page navigation, etc.).

**Reduced motion:** the existing simulation start short-circuits on `prefers-reduced-motion: reduce`. Extend that — when reduced motion is set, also skip click handler installation. These users get the canvas off and normal nav.

**Theme other than consumed:** click handler is not installed. Normal nav. No food drop. No sessionStorage write. The next page (whatever theme it is) will have no `pendingDrop` to read.

## Edge cases

| Case | Behavior |
| --- | --- |
| Direct entry from URL bar | No `pendingDrop` in storage. Canvas starts with random food only. |
| Refresh | sessionStorage survives refresh, but the previous page's nav already cleared the key on load. Refresh on a page reads no `pendingDrop`. Canvas starts with random food only. |
| Back / forward button | Browser-driven nav, no click event, no interception, no drop. Lands on a page with no `pendingDrop`. |
| Cmd-click, middle-click, target="_blank" | Filter rejects, no interception. New tab opens; in that tab, no sessionStorage was written from the originating tab's click, so the new tab loads with no `pendingDrop`. |
| External link | Filter rejects (different origin). No drop. |
| In-page anchor (`#footnote-1`) | Filter rejects. No nav, no drop. |
| `mailto:`, `tel:` | Filter rejects (protocol). |
| Modifier-key click | Filter rejects. |
| User clicks twice during the 400ms dissolve | First click sets `inFlight`. Second click is ignored. |
| Theme switch mid-session away from consumed | Click handler removed. Existing canvas hidden. |
| Theme switch back to consumed | Canvas re-initialized, click handler re-installed. The previous canvas state is lost (existing behavior); first nav after switching back behaves like a fresh entry. |
| `prefers-reduced-motion: reduce` | No canvas, no click handler, normal nav. |
| Reader has JS disabled | Normal browser nav, no canvas, no drop. Hugo-rendered links work. |

## Testing approach

This is a static blog with no JS test framework. Standing up Vitest/Jest is out of scope.

**Pragmatic plan:**

1. **Extend `?debug` overlay** in `ants.js`. Tag food sources with `source: 'letter' | 'random'`. In debug mode, color letter food cyan and random food green. Update the HUD title-text to show `Letter food: N | Random food: M`.

2. **Pure-function helpers** for testability:
   - `coalesceTextRectsToCells(textNodes, viewportW, viewportH, gridW, gridH)` — returns `Map<"x,y", count>`. Pure, callable from console.
   - `shouldInterceptClick(event)` — returns `boolean`. Pure given the event and `location` snapshot.

   Both are exported via `window.antsSimulation.debug.{coalesce, shouldIntercept}` for ad-hoc verification.

3. **Manual smoke checklist** (run via `make serve`):
   - [ ] Click an internal link → article fades over 400ms → next page loads with letter food at viewport-relative positions
   - [ ] Cmd-click → opens new tab, no dissolve, no drop
   - [ ] Middle-click → opens new tab, no dissolve
   - [ ] In-page anchor (e.g., `#fn1`) → no dissolve, normal anchor jump
   - [ ] External link → no dissolve
   - [ ] `mailto:` link → no dissolve
   - [ ] Switch to garish theme → click links → no dissolve, normal nav
   - [ ] Switch back to consumed → dissolve resumes on next click
   - [ ] Hard reload page → fresh state, no carry-over food
   - [ ] Use back button → no carry-over food
   - [ ] Reading-heavy session (10+ navs) → food count plateaus near `MAX_FOOD_SOURCES`
   - [ ] `prefers-reduced-motion: reduce` (system or DevTools emulation) → canvas hidden, nav unchanged
   - [ ] Debug overlay (`?debug` or `antsSimulation.debug()`) shows letter food vs random food in different colors

## Out of scope

- Persistent state across tab/session (localStorage). Decision: sessionStorage only.
- Reading activity feeding into vitality. Decision: vitality stays tied to last post date.
- Per-glyph particle dispersion animation. Decision: simple opacity+blur dissolve.
- "Pulled toward the hive" magnet animation. Decision: dissolve in place.
- Capturing on themes other than consumed for "delayed delivery." Decision: consumed-only.
- Adding a JS test framework. Decision: pragmatic helpers + manual checklist.
- Continuous nibbling on the live page (letters degrading as ants pass over them). Decision: drops only at nav.

## Open implementation questions (for the plan stage)

- Which DOM container is the "article" for purposes of the dissolve CSS selector? To be confirmed by inspecting the consumed theme's rendered HTML during implementation.
- Should the dissolve also apply to the header/nav, or only the post body? Lean: only post body, so the theme switcher and site frame stay stable through the transition. To be confirmed.
- Exact value of `FOOD_PER_LETTER`. Starting at 4 with calibration during manual testing.
- Does the build's link rendering emit any markers (e.g., `rel="external"`, `data-no-intercept`) that should be respected? To be confirmed by sampling `public/` output during implementation. (Note: README says Hugo but `Makefile` runs `python build.py` — the project's actual generator is the custom Python script.)
