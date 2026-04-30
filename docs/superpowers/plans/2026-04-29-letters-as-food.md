# Letters as Food Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a reader navigates from one page to another on the consumed theme, the visible above-the-fold text becomes food piles in the ant-colony canvas at viewport-relative grid positions; the leaving page dissolves in place over ~400ms before navigation fires.

**Architecture:** Single-file extension of `themes/consumed/ants.js` plus a CSS rule in `themes/consumed/style.css`. Pure helpers (cell coalescing, link filtering) are extracted as testable functions and exposed via `window.antsSimulation.helpers.*`. State carries across hard navigation via `sessionStorage`. No new build dependencies.

**Tech Stack:** Vanilla JavaScript (ES5-compatible to match existing `ants.js` style), Range API, `getClientRects()`, sessionStorage, CSS transitions. No test framework — verification is a bare-bones browser test page in `tests/ants/test-ants.html` that runs `console.assert` against the pure helpers.

**Spec reference:** `docs/superpowers/specs/2026-04-29-letters-as-food-design.md`

---

## File Structure

| File | Action | Responsibility |
| --- | --- | --- |
| `themes/consumed/ants.js` | Modify | Existing simulation; add food provenance, decay, cap, helpers, click handler, sessionStorage I/O |
| `themes/consumed/style.css` | Modify | Add `body.darkdell-dissolving main` opacity+blur rule |
| `themes/switcher.js` | Modify (small) | Notify ants module on theme switch so it can install/remove the click handler |
| `tests/ants/test-ants.html` | Create | Self-contained in-browser test page; runs `console.assert` calls against the pure helpers |
| `.gitignore` | No change | (already excludes `public/`) |

`tests/ants/test-ants.html` is opened directly via `file://` to verify the pure helpers. It is not part of the build output (build.py only copies `static/` and `themes/`, not `tests/`).

---

## Notes for the implementer

- Match the existing `ants.js` style: ES5 syntax, single IIFE wrapping the module, `var` declarations, no arrow functions, no `let`/`const`. The file already declares `'use strict'`.
- All numeric constants live near the top of the IIFE alongside the existing `GRID_W`, `DECAY_RATE`, etc.
- Each task ends with a `git commit`. Don't batch commits across tasks.
- Tests for pure helpers are run by opening `tests/ants/test-ants.html` directly in a browser (double-click the file or `open tests/ants/test-ants.html` from the project root). The page runs assertions on load and prints PASS / FAIL to the page and `console`.
- The simulation auto-starts on `DOMContentLoaded` when the saved theme is `consumed`. The test page works around this by setting `localStorage.setItem('theme', 'clean')` before loading the script (the script then doesn't auto-start). Helpers are still exposed.

---

### Task 1: Add provenance, decay, and FIFO cap to the food model

**Goal:** Each food entry now carries `source` and `depositedAt`. Food amounts decay slowly each tick. The total array is capped at 300 entries with FIFO eviction.

**Files:**
- Modify: `themes/consumed/ants.js`

- [ ] **Step 1: Add three constants near the top of the IIFE (after `MAX_DAYS`)**

In `themes/consumed/ants.js`, find the configuration block (around line 18). Add after the line `var MAX_DAYS = 60;`:

```js
  var FOOD_DECAY_PER_TICK = 0.0001;
  var MAX_FOOD_SOURCES = 300;
  var FOOD_PER_LETTER = 4;
```

- [ ] **Step 2: Tag random food sources with `source` and `depositedAt`**

Find `function spawnFoods(count)` (around line 93). Replace its body with:

```js
  function spawnFoods(count) {
    for (var i = 0; i < count; i++) {
      var food = {
        x: rand(GRID_W),
        y: rand(GRID_H),
        amount: FOOD_PER_SOURCE,
        source: 'random',
        depositedAt: Date.now()
      };
      if (Math.abs(food.x - hive.x) < 5 && Math.abs(food.y - hive.y) < 5) {
        food.x = wrap(food.x + 20, GRID_W);
      }
      foods.push(food);
    }
    enforceCap();
  }
```

- [ ] **Step 3: Add the `enforceCap` helper above `spawnFoods`**

Just above `function spawnFoods(count) {`, add:

```js
  function enforceCap() {
    if (foods.length <= MAX_FOOD_SOURCES) return;
    foods.sort(function (a, b) { return a.depositedAt - b.depositedAt; });
    foods = foods.slice(foods.length - MAX_FOOD_SOURCES);
  }
```

- [ ] **Step 4: Add per-tick food decay inside `tick()`**

Find `function tick()` (around line 117). After the existing pheromone-decay loop ends and before `tickCounter++`, add:

```js
    for (var k = 0; k < foods.length; k++) {
      foods[k].amount = Math.max(0, foods[k].amount - FOOD_DECAY_PER_TICK);
    }
```

- [ ] **Step 5: Manual smoke check**

Run `make serve` from the project root, open `http://localhost:8000/`, switch to the consumed theme if not already there, leave the page open for ~30 seconds. The canvas should still show ants and pheromone trails. There is no observable visual change yet — this task is structural.

In the browser console, run `window.antsSimulation` (the existing object). Confirm no errors appeared during simulation startup.

- [ ] **Step 6: Commit**

```bash
git add themes/consumed/ants.js
git commit -m "feat(ants): tag food entries, add decay and FIFO cap

Prep for letter-drop feature: every food entry now carries source
('random'|'letter') and depositedAt timestamp. Food amounts decay
0.0001/tick. The foods array is capped at 300 entries with oldest-first
eviction."
```

---

### Task 2: Create the in-browser test harness

**Goal:** A self-contained HTML page that loads `ants.js`, runs `console.assert` against pure helpers, and renders pass/fail to the DOM. We can open it via `file://` for fast iteration.

**Files:**
- Create: `tests/ants/test-ants.html`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p tests/ants
```

- [ ] **Step 2: Write the test harness scaffold**

Create `tests/ants/test-ants.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>ants.js helper tests</title>
  <script>
    // Disable auto-start so the simulation does not run during tests.
    localStorage.setItem('theme', 'clean');
  </script>
  <style>
    body { font-family: ui-monospace, monospace; padding: 1rem; }
    .pass { color: green; }
    .fail { color: red; font-weight: bold; }
    h1 { font-size: 1rem; }
    pre { margin: 0.25rem 0; }
  </style>
</head>
<body>
  <h1>ants.js helper tests</h1>
  <div id="results"></div>
  <script src="../../themes/consumed/ants.js"></script>
  <script>
    var passed = 0;
    var failed = 0;
    var results = document.getElementById('results');

    function check(name, condition, detail) {
      var line = document.createElement('pre');
      if (condition) {
        line.className = 'pass';
        line.textContent = 'PASS  ' + name;
        passed++;
      } else {
        line.className = 'fail';
        line.textContent = 'FAIL  ' + name + (detail ? ('  -- ' + detail) : '');
        failed++;
        console.error('FAIL', name, detail);
      }
      results.appendChild(line);
    }

    function eq(actual, expected) {
      return JSON.stringify(actual) === JSON.stringify(expected);
    }

    // Helpers expose hook — populated as we add tests.
    var H = (window.antsSimulation && window.antsSimulation.helpers) || {};

    // Test cases will be appended here in subsequent tasks.

    var summary = document.createElement('h1');
    summary.textContent = passed + ' passed, ' + failed + ' failed';
    summary.className = failed === 0 ? 'pass' : 'fail';
    document.body.appendChild(summary);
  </script>
</body>
</html>
```

- [ ] **Step 3: Open the test page**

Run `open tests/ants/test-ants.html` (macOS) or open it manually in a browser. You should see:

```
ants.js helper tests
0 passed, 0 failed
```

No errors in the console. (It's empty because we have no test cases yet, but the harness loads.)

- [ ] **Step 4: Commit**

```bash
git add tests/ants/test-ants.html
git commit -m "test(ants): add in-browser test harness for pure helpers

Loads ants.js with auto-start disabled and runs console.assert-style
checks against window.antsSimulation.helpers. Open via file:// for
fast iteration."
```

---

### Task 3: TDD `coalesceLineRectsToCells`

**Goal:** Pure function: given a list of `{rects, totalChars}` line groups + viewport + grid dimensions, return a `Map<"x,y", count>` of grid cells with weighted character counts. Above-the-fold clipping, multi-rect distribution by width, no DOM access.

**Function signature:**

```js
// rectGroups: Array<{ rects: Array<{left, top, right, bottom}>, totalChars: number }>
// viewportW, viewportH: numbers
// gridW, gridH: numbers
// returns: Map<string, number>  where keys are "cellX,cellY"
function coalesceLineRectsToCells(rectGroups, viewportW, viewportH, gridW, gridH)
```

**Files:**
- Modify: `themes/consumed/ants.js`
- Modify: `tests/ants/test-ants.html`

- [ ] **Step 1: Write the failing tests**

In `tests/ants/test-ants.html`, find the comment `// Test cases will be appended here in subsequent tasks.` and replace it with:

```js
// --- coalesceLineRectsToCells ---

(function () {
  var coalesce = H.coalesceLineRectsToCells;
  if (!coalesce) {
    check('coalesceLineRectsToCells exists', false, 'helper not exposed');
    return;
  }

  // Single rect, single cell
  var r1 = coalesce(
    [{ rects: [{ left: 0, top: 0, right: 5, bottom: 10 }], totalChars: 8 }],
    640, 320, 128, 64
  );
  // viewport 640x320, grid 128x64 => cellW=5, cellH=5
  // rect from x=0..5 -> cell 0; y center = 5 -> cell 1
  check('single rect lands in single cell',
    r1.size === 1 && Math.abs(r1.get('0,1') - 8) < 0.001,
    'got ' + JSON.stringify(Array.from(r1.entries())));

  // Single rect spanning two cells horizontally
  var r2 = coalesce(
    [{ rects: [{ left: 0, top: 0, right: 10, bottom: 10 }], totalChars: 10 }],
    640, 320, 128, 64
  );
  // 10px wide spans cells 0 and 1 horizontally; chars distribute evenly
  check('single rect spanning two cells distributes chars',
    r2.size === 2 &&
      Math.abs(r2.get('0,1') - 5) < 0.001 &&
      Math.abs(r2.get('1,1') - 5) < 0.001,
    'got ' + JSON.stringify(Array.from(r2.entries())));

  // Multiple rects from one line group share totalChars proportionally to width
  var r3 = coalesce(
    [{
      rects: [
        { left: 0, top: 0, right: 10, bottom: 10 },   // width 10
        { left: 0, top: 10, right: 20, bottom: 20 }   // width 20
      ],
      totalChars: 30
    }],
    640, 320, 128, 64
  );
  // First rect gets 10/30 of chars = 10; second gets 20/30 = 20
  // Cells touched: rect1 -> (0..1, 1); rect2 -> (0..3, 3)
  var sum1 = (r3.get('0,1') || 0) + (r3.get('1,1') || 0);
  var sum2 = (r3.get('0,3') || 0) + (r3.get('1,3') || 0)
           + (r3.get('2,3') || 0) + (r3.get('3,3') || 0);
  check('multi-rect group distributes proportionally to width',
    Math.abs(sum1 - 10) < 0.001 && Math.abs(sum2 - 20) < 0.001,
    'sum1=' + sum1 + ' sum2=' + sum2);

  // Above-the-fold clipping
  var r4 = coalesce(
    [{ rects: [{ left: 0, top: 300, right: 5, bottom: 340 }], totalChars: 8 }],
    640, 320, 128, 64
  );
  // rect spans y=300..340; viewport ends at 320; visibleRatio = 20/40 = 0.5
  // Surviving chars = 8 * 0.5 = 4
  var sumR4 = 0;
  r4.forEach(function (v) { sumR4 += v; });
  check('above-the-fold clipping reduces by visible ratio',
    Math.abs(sumR4 - 4) < 0.001,
    'sum=' + sumR4);

  // Below-the-fold rect contributes nothing
  var r5 = coalesce(
    [{ rects: [{ left: 0, top: 400, right: 5, bottom: 410 }], totalChars: 8 }],
    640, 320, 128, 64
  );
  check('below-the-fold rect contributes nothing', r5.size === 0);

  // Empty input
  var r6 = coalesce([], 640, 320, 128, 64);
  check('empty input returns empty map', r6.size === 0);
})();
```

- [ ] **Step 2: Open the test page; confirm failures**

Run `open tests/ants/test-ants.html`. Expected output:

```
FAIL  coalesceLineRectsToCells exists  -- helper not exposed
0 passed, 1 failed
```

(Or 6 fails if the early return check is removed — either way, all should fail.)

- [ ] **Step 3: Implement the helper inside `ants.js`**

In `themes/consumed/ants.js`, just below the IIFE's `'use strict'` line, add:

```js
  function coalesceLineRectsToCells(rectGroups, viewportW, viewportH, gridW, gridH) {
    var cellW = viewportW / gridW;
    var cellH = viewportH / gridH;
    var cells = new Map();

    function add(key, amount) {
      cells.set(key, (cells.get(key) || 0) + amount);
    }

    for (var g = 0; g < rectGroups.length; g++) {
      var group = rectGroups[g];
      var totalWidth = 0;
      for (var ri = 0; ri < group.rects.length; ri++) {
        totalWidth += Math.max(0, group.rects[ri].right - group.rects[ri].left);
      }
      if (totalWidth <= 0) continue;

      for (var rj = 0; rj < group.rects.length; rj++) {
        var rect = group.rects[rj];
        var rectWidth = Math.max(0, rect.right - rect.left);
        if (rectWidth <= 0) continue;

        var visibleTop = Math.max(0, rect.top);
        var visibleBottom = Math.min(viewportH, rect.bottom);
        if (visibleBottom <= visibleTop) continue;
        var rectHeight = Math.max(0.001, rect.bottom - rect.top);
        var visibleRatio = (visibleBottom - visibleTop) / rectHeight;

        var rectChars = group.totalChars * (rectWidth / totalWidth) * visibleRatio;
        var midY = (visibleTop + visibleBottom) / 2;
        var cellY = Math.floor(midY / cellH);

        var startCellX = Math.floor(rect.left / cellW);
        var endCellX = Math.floor((rect.right - 0.0001) / cellW);
        for (var cx = startCellX; cx <= endCellX; cx++) {
          var cellLeft = cx * cellW;
          var cellRight = (cx + 1) * cellW;
          var overlap = Math.min(rect.right, cellRight) - Math.max(rect.left, cellLeft);
          if (overlap <= 0) continue;
          var charsInCell = rectChars * (overlap / rectWidth);
          add(cx + ',' + cellY, charsInCell);
        }
      }
    }
    return cells;
  }
```

- [ ] **Step 4: Expose it on `window.antsSimulation.helpers`**

Find the existing `window.antsSimulation = { ... };` block (around line 300). Replace it with:

```js
  window.antsSimulation = {
    start: function () {
      if (running) return;
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      running = true;
      init();
      loop();
    },
    stop: function () {
      running = false;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = null;
    },
    debug: function () {
      debugMode = !debugMode;
      if (canvas) canvas.style.filter = debugMode ? 'none' : 'blur(10px)';
      console.log('Ant debug mode: ' + (debugMode ? 'ON' : 'OFF'));
      console.log('Ants: ' + ants.length + ' | Vitality: ' + vitality.toFixed(2));
    },
    helpers: {
      coalesceLineRectsToCells: coalesceLineRectsToCells
    }
  };
```

- [ ] **Step 5: Reload the test page; confirm passes**

Reload `tests/ants/test-ants.html` in the browser. Expected output:

```
PASS  single rect lands in single cell
PASS  single rect spanning two cells distributes chars
PASS  multi-rect group distributes proportionally to width
PASS  above-the-fold clipping reduces by visible ratio
PASS  below-the-fold rect contributes nothing
PASS  empty input returns empty map
6 passed, 0 failed
```

- [ ] **Step 6: Commit**

```bash
git add themes/consumed/ants.js tests/ants/test-ants.html
git commit -m "feat(ants): add coalesceLineRectsToCells helper

Pure function: given a list of line-rect groups (each carrying its
total character count), produce a Map of grid-cell -> weighted char
count. Handles above-the-fold clipping and multi-rect lines."
```

---

### Task 4: TDD `shouldInterceptUrl`

**Goal:** Pure function that decides whether a URL qualifies for interception, given the URL string and a snapshot of `location` (origin, pathname, search).

**Function signature:**

```js
// href: string (the resolved absolute URL)
// loc: { origin, pathname, search }
// returns: boolean
function shouldInterceptUrl(href, loc)
```

**Files:**
- Modify: `themes/consumed/ants.js`
- Modify: `tests/ants/test-ants.html`

- [ ] **Step 1: Append the test cases to `test-ants.html`**

Append (after the existing IIFE):

```js
// --- shouldInterceptUrl ---

(function () {
  var fn = H.shouldInterceptUrl;
  if (!fn) {
    check('shouldInterceptUrl exists', false, 'helper not exposed');
    return;
  }

  var loc = { origin: 'https://darkdell.net', pathname: '/blog/', search: '' };

  check('same-origin same-protocol => true',
    fn('https://darkdell.net/posts/2026/04/29-foo/', loc) === true);

  check('different origin => false',
    fn('https://example.com/foo', loc) === false);

  check('http scheme on same origin => true',
    fn('http://darkdell.net/foo', { origin: 'http://darkdell.net', pathname: '/', search: '' }) === true);

  check('mailto => false',
    fn('mailto:foo@bar.com', loc) === false);

  check('tel => false',
    fn('tel:+1234', loc) === false);

  check('javascript: => false',
    fn('javascript:void(0)', loc) === false);

  check('in-page anchor (same path same search, different hash) => false',
    fn('https://darkdell.net/blog/#footnote-1', loc) === false);

  check('different path on same origin => true',
    fn('https://darkdell.net/projects/', loc) === true);

  check('same path with different search => true',
    fn('https://darkdell.net/blog/?page=2', loc) === true);
})();
```

- [ ] **Step 2: Reload the test page; confirm failures**

Expected: `FAIL  shouldInterceptUrl exists` (helper not exposed).

- [ ] **Step 3: Implement the helper in `ants.js`**

Add below `coalesceLineRectsToCells`:

```js
  function shouldInterceptUrl(href, loc) {
    var url;
    try {
      url = new URL(href);
    } catch (e) {
      return false;
    }
    if (url.protocol !== 'http:' && url.protocol !== 'https:') return false;
    if (url.origin !== loc.origin) return false;
    if (url.pathname === loc.pathname && url.search === loc.search) {
      // In-page anchor or no-op nav; let the browser handle.
      return false;
    }
    return true;
  }
```

- [ ] **Step 4: Expose it on `window.antsSimulation.helpers`**

Update the helpers object:

```js
    helpers: {
      coalesceLineRectsToCells: coalesceLineRectsToCells,
      shouldInterceptUrl: shouldInterceptUrl
    }
```

- [ ] **Step 5: Reload and confirm all pass**

Expected: 9 new passes for this section, all green.

- [ ] **Step 6: Commit**

```bash
git add themes/consumed/ants.js tests/ants/test-ants.html
git commit -m "feat(ants): add shouldInterceptUrl link filter

Pure URL-level check: same-origin http(s) only, rejects mailto/tel/
javascript and in-page anchors."
```

---

### Task 5: TDD `eventQualifiesForIntercept`

**Goal:** Pure function over a `MouseEvent` that returns `true` only when the event is a non-modifier left-click on a same-tab link with no `target`/`download` attribute. Combined with `shouldInterceptUrl`, this is the full filter.

**Function signature:**

```js
// event: MouseEvent
// returns: { ok: boolean, href?: string }
function eventQualifiesForIntercept(event)
```

Returns the resolved `href` so the caller doesn't reparse.

**Files:**
- Modify: `themes/consumed/ants.js`
- Modify: `tests/ants/test-ants.html`

- [ ] **Step 1: Append test cases to `test-ants.html`**

```js
// --- eventQualifiesForIntercept ---

(function () {
  var fn = H.eventQualifiesForIntercept;
  if (!fn) {
    check('eventQualifiesForIntercept exists', false, 'helper not exposed');
    return;
  }

  function makeAnchor(attrs) {
    var a = document.createElement('a');
    Object.keys(attrs).forEach(function (k) { a.setAttribute(k, attrs[k]); });
    document.body.appendChild(a);
    return a;
  }

  function makeEvent(target, opts) {
    opts = opts || {};
    var e = new MouseEvent('click', {
      button: opts.button !== undefined ? opts.button : 0,
      ctrlKey: !!opts.ctrlKey,
      shiftKey: !!opts.shiftKey,
      altKey: !!opts.altKey,
      metaKey: !!opts.metaKey,
      bubbles: true,
      cancelable: true
    });
    Object.defineProperty(e, 'target', { value: target });
    return e;
  }

  var a1 = makeAnchor({ href: '/blog/' });
  check('plain primary click on internal link => ok',
    fn(makeEvent(a1)).ok === true);

  var a2 = makeAnchor({ href: '/blog/', target: '_blank' });
  check('target=_blank => not ok',
    fn(makeEvent(a2)).ok === false);

  var a3 = makeAnchor({ href: '/blog/', target: '_self' });
  check('target=_self => ok',
    fn(makeEvent(a3)).ok === true);

  var a4 = makeAnchor({ href: '/file.pdf', download: '' });
  check('download attribute => not ok',
    fn(makeEvent(a4)).ok === false);

  var a5 = makeAnchor({ href: '/blog/' });
  check('cmd-click => not ok',
    fn(makeEvent(a5, { metaKey: true })).ok === false);

  var a6 = makeAnchor({ href: '/blog/' });
  check('ctrl-click => not ok',
    fn(makeEvent(a6, { ctrlKey: true })).ok === false);

  var a7 = makeAnchor({ href: '/blog/' });
  check('middle-click => not ok',
    fn(makeEvent(a7, { button: 1 })).ok === false);

  var a8 = makeAnchor({ href: '/blog/' });
  var ev8 = makeEvent(a8);
  ev8.preventDefault();
  check('defaultPrevented => not ok', fn(ev8).ok === false);

  // Click target inside an <a> bubbles up
  var a9 = makeAnchor({ href: '/blog/' });
  var span = document.createElement('span');
  a9.appendChild(span);
  check('click inside anchor finds it via closest()',
    fn(makeEvent(span)).ok === true);

  var stray = document.createElement('span');
  document.body.appendChild(stray);
  check('click outside any anchor => not ok',
    fn(makeEvent(stray)).ok === false);

  var a10 = makeAnchor({});
  check('anchor without href => not ok',
    fn(makeEvent(a10)).ok === false);
})();
```

- [ ] **Step 2: Reload, confirm failures**

Expected: `FAIL  eventQualifiesForIntercept exists`.

- [ ] **Step 3: Implement in `ants.js`**

Add below `shouldInterceptUrl`:

```js
  function eventQualifiesForIntercept(event) {
    if (event.defaultPrevented) return { ok: false };
    if (event.button !== 0) return { ok: false };
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return { ok: false };

    var target = event.target;
    if (!target || typeof target.closest !== 'function') return { ok: false };
    var a = target.closest('a');
    if (!a) return { ok: false };
    if (!a.hasAttribute('href')) return { ok: false };
    if (a.hasAttribute('download')) return { ok: false };

    var tgt = a.getAttribute('target');
    if (tgt && tgt !== '_self') return { ok: false };

    return { ok: true, href: a.href };
  }
```

- [ ] **Step 4: Expose on helpers**

```js
    helpers: {
      coalesceLineRectsToCells: coalesceLineRectsToCells,
      shouldInterceptUrl: shouldInterceptUrl,
      eventQualifiesForIntercept: eventQualifiesForIntercept
    }
```

- [ ] **Step 5: Reload, confirm all pass**

Expected: 11 new passes.

- [ ] **Step 6: Commit**

```bash
git add themes/consumed/ants.js tests/ants/test-ants.html
git commit -m "feat(ants): add eventQualifiesForIntercept event filter

Pure check over a MouseEvent: rejects modifier clicks, middle-click,
target=_blank, downloads, and clicks outside any <a>. Returns the
resolved href when ok."
```

---

### Task 6: Add `extractVisibleLineRects` (DOM-walker)

**Goal:** Walks all visible text nodes under `document.body` and returns a list of `{rects, totalChars}` line groups suitable for `coalesceLineRectsToCells`. Skips `<script>`, `<style>`, the canvas, and the theme switcher button.

**Files:**
- Modify: `themes/consumed/ants.js`

- [ ] **Step 1: Implement the walker**

Add below `eventQualifiesForIntercept` in `themes/consumed/ants.js`:

```js
  function extractVisibleLineRects(root) {
    var groups = [];
    var SKIP = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, CANVAS: 1 };
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var p = node.parentNode;
        while (p && p !== root) {
          if (SKIP[p.nodeName]) return NodeFilter.FILTER_REJECT;
          if (p.id === 'theme-switcher') return NodeFilter.FILTER_REJECT;
          p = p.parentNode;
        }
        if (!node.nodeValue || !/\S/.test(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });

    var node;
    while ((node = walker.nextNode())) {
      var range = document.createRange();
      range.selectNodeContents(node);
      var clientRects = range.getClientRects();
      if (clientRects.length === 0) continue;
      var rects = [];
      for (var i = 0; i < clientRects.length; i++) {
        var r = clientRects[i];
        rects.push({ left: r.left, top: r.top, right: r.right, bottom: r.bottom });
      }
      groups.push({ rects: rects, totalChars: node.nodeValue.length });
    }
    return groups;
  }
```

- [ ] **Step 2: Expose on helpers**

```js
    helpers: {
      coalesceLineRectsToCells: coalesceLineRectsToCells,
      shouldInterceptUrl: shouldInterceptUrl,
      eventQualifiesForIntercept: eventQualifiesForIntercept,
      extractVisibleLineRects: extractVisibleLineRects
    }
```

- [ ] **Step 3: Manual verification in browser**

Run `make serve`, open `http://localhost:8000/`, ensure consumed theme is active. Open the JS console and run:

```js
var groups = window.antsSimulation.helpers.extractVisibleLineRects(document.body);
console.log('Line groups:', groups.length);
console.log('Sample:', groups.slice(0, 3));
```

Expected: a couple dozen line groups (depends on page content), each with at least one rect and a non-zero `totalChars`. Sample rects should have plausible viewport coordinates.

- [ ] **Step 4: Sanity check the full pipeline**

In the same console:

```js
var groups = window.antsSimulation.helpers.extractVisibleLineRects(document.body);
var cells = window.antsSimulation.helpers.coalesceLineRectsToCells(groups, window.innerWidth, window.innerHeight, 128, 64);
console.log('Cells:', cells.size);
var total = 0;
cells.forEach(function (v) { total += v; });
console.log('Total chars:', total);
```

Expected: `cells.size` is dozens, `total` is in the hundreds. If `total` is 0 or `cells.size` is 0, something is wrong with the walker.

- [ ] **Step 5: Commit**

```bash
git add themes/consumed/ants.js
git commit -m "feat(ants): add extractVisibleLineRects DOM walker

Walks text nodes under a root, skipping script/style/canvas/theme-
switcher. Uses Range.getClientRects() to get one rect per visual
line and returns line groups suitable for coalesceLineRectsToCells."
```

---

### Task 7: Add CSS for the dissolve animation

**Goal:** When `<body>` has the class `darkdell-dissolving`, the `<main>` element fades to opacity 0 with a 2px blur over 400ms.

**Files:**
- Modify: `themes/consumed/style.css`

- [ ] **Step 1: Append the rule**

Append to `themes/consumed/style.css`:

```css
body.darkdell-dissolving main {
  transition: opacity 400ms ease-in, filter 400ms ease-in;
  opacity: 0;
  filter: blur(2px);
  pointer-events: none;
}
```

- [ ] **Step 2: Quick visual verify**

Run `make serve`, open `http://localhost:8000/`, ensure consumed theme. In the console:

```js
document.body.classList.add('darkdell-dissolving');
```

Expected: the main content fades out with blur over ~400ms. Then:

```js
document.body.classList.remove('darkdell-dissolving');
```

Content fades back in (the same transition runs in reverse).

- [ ] **Step 3: Commit**

```bash
git add themes/consumed/style.css
git commit -m "feat(ants): add dissolve transition for nav handoff

When body has the .darkdell-dissolving class, <main> fades to 0
opacity with a 2px blur over 400ms. Used by the click handler to
animate page handoff before navigation."
```

---

### Task 8: Click handler — capture, deposit, persist, dissolve, navigate

**Goal:** On qualifying internal link clicks, capture the visible-text-to-food map, append to the in-memory `foods` array (so the current page reacts), serialize to sessionStorage, kick off the CSS dissolve, and navigate after 400ms.

**Files:**
- Modify: `themes/consumed/ants.js`

- [ ] **Step 1: Add module-level state**

Near other module-level vars (where `running`, `rafId`, etc. live, around line 44), add:

```js
  var clickHandler = null;
  var inFlight = false;
  var DISSOLVE_MS = 400;
  var STORAGE_KEY = 'darkdell.pendingDrop';
```

- [ ] **Step 2: Add the deposit + nav function**

Add inside the IIFE (above `window.antsSimulation = ...`):

```js
  function depositLetterFood(now) {
    var groups = extractVisibleLineRects(document.body);
    var cells = coalesceLineRectsToCells(
      groups, window.innerWidth, window.innerHeight, GRID_W, GRID_H
    );
    var drops = [];
    cells.forEach(function (count, key) {
      var parts = key.split(',');
      var amount = count * FOOD_PER_LETTER;
      if (amount <= 0) return;
      drops.push({
        x: parseInt(parts[0], 10),
        y: parseInt(parts[1], 10),
        amount: amount,
        source: 'letter',
        depositedAt: now
      });
    });

    for (var i = 0; i < drops.length; i++) {
      foods.push(drops[i]);
    }
    enforceCap();

    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(drops));
    } catch (e) {
      // Storage may be full or disabled; non-fatal — the nav still happens,
      // the next page just won't see the drop.
    }

    return drops;
  }

  function handleQualifyingClick(event, href) {
    event.preventDefault();
    inFlight = true;
    setTimeout(function () { inFlight = false; }, 1000); // failsafe

    depositLetterFood(Date.now());
    document.body.classList.add('darkdell-dissolving');
    setTimeout(function () { window.location.href = href; }, DISSOLVE_MS);
  }

  function onDocumentClick(event) {
    if (inFlight) { event.preventDefault(); return; }
    var q = eventQualifiesForIntercept(event);
    if (!q.ok) return;
    if (!shouldInterceptUrl(q.href, {
      origin: window.location.origin,
      pathname: window.location.pathname,
      search: window.location.search
    })) return;
    handleQualifyingClick(event, q.href);
  }

  function installClickHandler() {
    if (clickHandler) return;
    clickHandler = onDocumentClick;
    document.addEventListener('click', clickHandler, true);
  }

  function removeClickHandler() {
    if (!clickHandler) return;
    document.removeEventListener('click', clickHandler, true);
    clickHandler = null;
  }
```

- [ ] **Step 3: Hook install into `start()` and remove into `stop()`**

Update the existing `start` and `stop` methods on `window.antsSimulation`:

```js
    start: function () {
      if (running) return;
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      running = true;
      init();
      installClickHandler();
      loop();
    },
    stop: function () {
      running = false;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = null;
      removeClickHandler();
      document.body.classList.remove('darkdell-dissolving');
    },
```

- [ ] **Step 4: Manual smoke test**

Run `make serve`, open `http://localhost:8000/`. Click an internal link (e.g., `/blog/`). Expected:
- The current page's main content fades and blurs over ~400ms.
- Then navigation fires; the next page loads as a hard refresh.
- (Food restoration on the next page comes in Task 9 — for now, the new page's canvas appears as before.)

In the console on the *current* page (before clicking), you can verify the deposit by clicking and quickly switching tabs / pausing, then in DevTools running:

```js
JSON.parse(sessionStorage.getItem('darkdell.pendingDrop'))
```

Expected: an array of `{x, y, amount, source: 'letter', depositedAt}` entries with sane values.

Also test:
- Cmd-click an internal link → opens new tab, no dissolve on current page.
- Click an in-page anchor (if any) → no dissolve, normal jump.
- Click an external link (e.g., a link to another site) → no dissolve.

- [ ] **Step 5: Commit**

```bash
git add themes/consumed/ants.js
git commit -m "feat(ants): intercept link clicks, deposit letter food, dissolve

On qualifying same-origin clicks: capture above-the-fold text into
food piles, append to in-memory foods array, write to
sessionStorage.darkdell.pendingDrop, add the .darkdell-dissolving
class to <body>, and navigate after 400ms. The next page does not
yet read the storage — that comes in the next task."
```

---

### Task 9: On-init — restore pending letter drops from sessionStorage

**Goal:** When the simulation initializes, before scattering random food, read `sessionStorage.darkdell.pendingDrop`, append those entries to `foods`, and clear the key. The next page now loads with the previous page's text food in place.

**Files:**
- Modify: `themes/consumed/ants.js`

- [ ] **Step 1: Add the restore step inside `init()`**

Find `function init()` (around line 52). Replace the section starting at `foods = [];` and ending after `spawnFoods(NUM_FOOD_SOURCES);` with:

```js
    foods = [];
    restorePendingDrops();
    spawnFoods(NUM_FOOD_SOURCES);
```

- [ ] **Step 2: Add the `restorePendingDrops` helper**

Add above `function init()`:

```js
  function restorePendingDrops() {
    var raw;
    try {
      raw = sessionStorage.getItem(STORAGE_KEY);
      sessionStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      return;
    }
    if (!raw) return;
    var parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (e) {
      return;
    }
    if (!Array.isArray(parsed)) return;
    for (var i = 0; i < parsed.length; i++) {
      var drop = parsed[i];
      if (typeof drop !== 'object' || drop === null) continue;
      if (typeof drop.x !== 'number' || typeof drop.y !== 'number') continue;
      if (typeof drop.amount !== 'number' || drop.amount <= 0) continue;
      foods.push({
        x: drop.x,
        y: drop.y,
        amount: drop.amount,
        source: 'letter',
        depositedAt: typeof drop.depositedAt === 'number' ? drop.depositedAt : Date.now()
      });
    }
  }
```

- [ ] **Step 3: Manual end-to-end smoke test**

Run `make serve`, open `http://localhost:8000/`. Click an internal link.

Expected: the dissolve fires, navigation happens, and on the new page the ants should converge on cells matching where the previous page's text was. To verify, open the JS console immediately on the new page:

```js
// Should be cleared (we removed it on init)
sessionStorage.getItem('darkdell.pendingDrop')  // null
```

To inspect food sources, enable debug mode:

```js
window.antsSimulation.debug();
```

The canvas un-blurs and you should see green dots (letter food piles) in viewport-relative positions, plus 8 random food spots from `spawnFoods`. Ants should be scrambling toward them.

- [ ] **Step 4: Verify back-button behavior**

Click forward into a post, then click the browser back button. The previous page loads, no dissolve happens (back-nav is browser-driven, not click-driven). Storage was cleared on the forward-nav's init, so no carry-over food appears. Canvas starts with random food only. This is the expected behavior per spec.

- [ ] **Step 5: Verify refresh behavior**

Hard reload the page (Cmd-R). No carry-over food. Canvas starts with random food only. Expected.

- [ ] **Step 6: Commit**

```bash
git add themes/consumed/ants.js
git commit -m "feat(ants): restore pending letter drops on simulation init

On init, before spawning random food, read and clear
sessionStorage.darkdell.pendingDrop. Validates each entry
defensively (drop x/y/amount must be numbers, amount > 0).
This closes the loop: text on the previous page appears as
food on the next."
```

---

### Task 10: Notify ants module on theme switch

**Goal:** When the user toggles to/away from the consumed theme via the switcher button, the ants module's `start()`/`stop()` already fire (existing code). The click handler install/remove is already inside `start()`/`stop()` from Task 8. But there's a subtle issue: when the user is on a non-consumed theme initially (so `start()` was never called), and then switches to consumed, the handler installs correctly. When they switch away, it's removed. This task confirms that flow works and adds defensive cleanup.

**Files:**
- Modify: `themes/consumed/ants.js`
- Modify (small): `themes/switcher.js`

- [ ] **Step 1: Verify switcher.js already calls start/stop**

Read `themes/switcher.js`. Lines 21-29 already call `window.antsSimulation.start()` and `.stop()` on theme transitions. No changes needed in switcher.js for the click handler — it's wired through start/stop.

- [ ] **Step 2: Defensive cleanup in `stop()`**

Already done in Task 8 (Step 3). Confirm `stop()` calls `removeClickHandler()` and removes the dissolving class. If somehow `stop()` is called mid-dissolve, navigation can still complete because `setTimeout` schedules the redirect independently.

- [ ] **Step 3: Manual switch flow verification**

Run `make serve`, open `http://localhost:8000/`. Switch through themes:
- Start on consumed → click an internal link → dissolve + nav fires. ✓
- Switch to garish → click an internal link → no dissolve, normal browser nav. ✓
- Switch back to consumed → click an internal link → dissolve + nav fires. ✓
- Switch to clean → click an internal link → no dissolve. ✓

In the JS console, after switching to garish, run:

```js
typeof document.querySelector('a').onclick
```

(The handler is on document, not on individual anchors, so the test above isn't conclusive.) Better:

```js
// After switching to garish
window.antsSimulation;  // start/stop should still exist
// click events on links should NOT call preventDefault from our handler
```

Confirm by clicking a link on garish — if the page navigates instantly (no 400ms delay, no fade), the handler is correctly removed.

- [ ] **Step 4: Commit (only if there are actual changes from defensive cleanup)**

If no code changed in this task, no commit. The verification is sufficient. If you spotted a missing teardown step and added it, commit:

```bash
git add themes/consumed/ants.js
git commit -m "fix(ants): tighten teardown on theme switch away from consumed"
```

Otherwise note in the executing-plans tracker that this task is verification-only and skip the commit.

---

### Task 11: Tag letter vs random food in the debug overlay

**Goal:** Existing `?debug` mode shows all food in green. Differentiate letter-drop food (cyan) from random food (green) and surface counts in the HUD.

**Files:**
- Modify: `themes/consumed/ants.js`

- [ ] **Step 1: Update the debug-mode food rendering**

Find the debug overlay block in `render()` (around line 254). Replace the food-source loop with:

```js
      // Food sources — color by source, size proportional to remaining amount
      var letterCount = 0;
      var randomCount = 0;
      for (var f = 0; f < foods.length; f++) {
        var food = foods[f];
        if (food.source === 'letter') letterCount++;
        else randomCount++;
        if (food.amount > 0) {
          var sz = Math.max(1, Math.round(food.amount / FOOD_PER_SOURCE * 3));
          ctx.fillStyle = food.source === 'letter'
            ? 'rgba(0, 220, 255, 0.85)'
            : 'rgba(0, 255, 0, 0.8)';
          ctx.fillRect(food.x, food.y, sz, sz);
        } else {
          ctx.fillStyle = 'rgba(255, 0, 0, 0.4)';
          ctx.fillRect(food.x, food.y, 1, 1);
        }
      }
```

- [ ] **Step 2: Update the HUD title text**

In the same `render()` function, find the `canvas.title = ...` block (around line 281). Replace with:

```js
      canvas.title = 'Ants: ' + ants.length +
        ' | Carrying: ' + carrying +
        ' | Food: ' + foods.length + ' (letter ' + letterCount + ', random ' + randomCount + ')' +
        ' | Total food: ' + totalFood +
        ' | Vitality: ' + vitality.toFixed(2) +
        ' | Tick: ' + tickCounter;
```

- [ ] **Step 3: Manual verification**

Run `make serve`, open `http://localhost:8000/?debug` (or call `window.antsSimulation.debug()` from the console). Click an internal link. On the next page (still in debug mode if the URL has `?debug`):

- Cyan dots: letter food at viewport-relative positions matching where the previous page's text was.
- Green dots: 8 random food sources at random positions.
- Hover over the canvas — the tooltip should read e.g. `Ants: 50 | Carrying: 3 | Food: 47 (letter 39, random 8) | Total food: ...`.

- [ ] **Step 4: Commit**

```bash
git add themes/consumed/ants.js
git commit -m "feat(ants): color-code letter vs random food in debug mode

Cyan = letter drops, green = random spawns. HUD shows letter/random
counts so it's easy to verify the deposit pipeline in browser."
```

---

### Task 12: Final smoke test pass

**Goal:** Walk the spec's manual checklist end-to-end. Catch anything skipped during piecemeal verification.

**Files:** none modified.

- [ ] **Step 1: Run the full checklist**

Run `make serve`. Open `http://localhost:8000/` in two browsers if possible (one with `prefers-reduced-motion`).

For each item, mark pass / fail and note any issues. Re-open a task above for any failure.

- [ ] Click an internal link → article fades over 400ms → next page loads with letter food at viewport-relative positions
- [ ] Cmd-click → opens new tab, no dissolve, no drop
- [ ] Middle-click → opens new tab, no dissolve
- [ ] In-page anchor (e.g., `#fn1`) → no dissolve, normal anchor jump (find or add a footnote-bearing post for this)
- [ ] External link → no dissolve, normal nav
- [ ] `mailto:` link → no dissolve (test by adding one to a post and clicking)
- [ ] Switch to garish theme → click links → no dissolve, normal nav
- [ ] Switch back to consumed → dissolve resumes on next click
- [ ] Hard reload page → fresh state, no carry-over food
- [ ] Use back button → no carry-over food
- [ ] Reading-heavy session (10+ navs) → food count plateaus near `MAX_FOOD_SOURCES` (300). Use debug HUD to check.
- [ ] `prefers-reduced-motion: reduce` (system or DevTools emulation) → canvas hidden, nav unchanged, no dissolve
- [ ] Debug overlay (`?debug` or `antsSimulation.debug()`) shows letter food (cyan) vs random food (green)

- [ ] **Step 2: If everything passes, no commit needed for this task**

This task is verification-only.

- [ ] **Step 3: If issues are found, fix them and re-run the failing checklist items**

Open the relevant task in this plan, add a corrective step, and commit the fix with a message like `fix(ants): <what was broken>`.

---

## Self-Review

Spec coverage check:

- ✅ Trigger on internal link click → Tasks 5, 8
- ✅ Above-the-fold positional mapping → Tasks 3 (clipping), 6 (extraction)
- ✅ ~400ms dissolve → Tasks 7 (CSS), 8 (timing)
- ✅ Per-character coalesced by cell → Task 3
- ✅ Hybrid economy with random + accumulating letter food → Tasks 1 (tagging), 9 (restore)
- ✅ Food decay → Task 1
- ✅ FIFO cap at 300 → Task 1
- ✅ Dissolve in place via opacity + blur → Task 7
- ✅ sessionStorage persistence → Tasks 8 (write), 9 (read+clear)
- ✅ Consumed-theme-only scope → Tasks 8/10 (handler tied to start/stop)
- ✅ Reduced-motion bypass → existing simulation start short-circuit, also gates handler install (Task 8 Step 3 in `start()`)
- ✅ Link filter (modifiers, target, download, mailto, in-page anchor) → Tasks 4, 5
- ✅ In-flight re-entry guard → Task 8
- ✅ Vitality unchanged → no task touches it (intentional)
- ✅ Pheromone behavior unchanged → no task touches the pheromone code path
- ✅ Debug overlay distinguishes letter vs random food → Task 11
- ✅ Open question: dissolve target container (`<main>`) → resolved via `templates/base.html` inspection, used in Task 7
- ⚠️ Open question: build-emitted link markers (`rel="external"` etc.) — not addressed in any task. The link filter rejects external origins regardless, so this is moot for safety. Worth a console-grep during Task 12 just in case any in-origin link has a marker we should respect; if found, return to Task 5 and extend the filter.

Type/name consistency check:
- `STORAGE_KEY = 'darkdell.pendingDrop'` — used identically in Tasks 8 and 9.
- `coalesceLineRectsToCells`, `shouldInterceptUrl`, `eventQualifiesForIntercept`, `extractVisibleLineRects` — names match between definition (Tasks 3-6) and usage (Task 8).
- `FOOD_PER_LETTER`, `MAX_FOOD_SOURCES`, `FOOD_DECAY_PER_TICK`, `DISSOLVE_MS` — defined once, used consistently.
- `enforceCap()` — defined in Task 1 Step 3, called from `spawnFoods` (Task 1 Step 2) and `depositLetterFood` (Task 8 Step 2). Consistent.

No placeholders, no "TBD"s. Plan is ready to execute.
