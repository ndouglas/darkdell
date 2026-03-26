// themes/consumed/ants.js
// Ant Colony Optimization background simulation for the Consumed theme.
// Renders pheromone trails as subtle color gradients on a background canvas.

(function () {
  'use strict';

  // --- Configuration ---
  var GRID_W = 128;
  var GRID_H = 64;
  var CELL_PX = 6;
  var NUM_FOOD_SOURCES = 8;
  var FOOD_PER_SOURCE = 80;
  var DECAY_RATE = 0.4;
  var MARK_STRENGTH = 25;
  var MAX_PHEROMONE = 255;
  var FOOD_RESPAWN_TICKS = 600;
  var MAX_DAYS = 60;

  // Inbound channels (carrying food home) — warm tones
  var INBOUND_CHANNELS = [
    { r: 197, g: 64, b: 48 },   // vermilion
    { r: 200, g: 120, b: 20 },  // amber
    { r: 170, g: 30, b: 40 },   // crimson
  ];

  // Outbound channels (foraging) — muted cool tones
  var OUTBOUND_CHANNELS = [
    { r: 35, g: 20, b: 90 },    // dark indigo
    { r: 20, g: 30, b: 70 },    // deep navy
    { r: 25, g: 50, b: 65 },    // muted teal
  ];

  var NUM_CHANNELS = INBOUND_CHANNELS.length + OUTBOUND_CHANNELS.length;
  var CHANNELS = INBOUND_CHANNELS.concat(OUTBOUND_CHANNELS);

  var canvas, ctx;
  var grid;
  var ants;
  var hive;
  var foods;
  var vitality;
  var antCount;
  var running = false;
  var rafId = null;
  var tickCounter = 0;

  function rand(max) { return Math.floor(Math.random() * max); }
  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }
  function wrap(v, max) { return ((v % max) + max) % max; }

  function init() {
    canvas = document.getElementById('ants-canvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    vitality = calcVitality();
    antCount = Math.round(5 + 95 * vitality);

    // Canvas at grid resolution — CSS stretches to fill viewport
    canvas.width = GRID_W;
    canvas.height = GRID_H;

    grid = new Float32Array(GRID_W * GRID_H * NUM_CHANNELS);

    hive = {
      x: 10 + rand(GRID_W - 20),
      y: 5 + rand(GRID_H - 10)
    };

    foods = [];
    spawnFoods(NUM_FOOD_SOURCES);

    ants = [];
    for (var i = 0; i < antCount; i++) {
      ants.push(createAnt());
    }

    tickCounter = 0;
  }

  function createAnt() {
    return {
      x: hive.x + rand(3) - 1,
      y: hive.y + rand(3) - 1,
      dx: rand(3) - 1 || 1,
      dy: rand(3) - 1,
      carrying: false,
      channel: rand(INBOUND_CHANNELS.length)
    };
  }

  function spawnFoods(count) {
    for (var i = 0; i < count; i++) {
      var food = {
        x: rand(GRID_W),
        y: rand(GRID_H),
        amount: FOOD_PER_SOURCE
      };
      if (Math.abs(food.x - hive.x) < 5 && Math.abs(food.y - hive.y) < 5) {
        food.x = wrap(food.x + 20, GRID_W);
      }
      foods.push(food);
    }
  }

  function calcVitality() {
    if (typeof lastPostDate === 'undefined' || !lastPostDate || lastPostDate === '1970-01-01') {
      return 0;
    }
    var posted = new Date(lastPostDate);
    var now = new Date();
    var days = (now - posted) / (1000 * 60 * 60 * 24);
    return Math.max(0, 1 - days / MAX_DAYS);
  }

  function tick() {
    for (var i = 0; i < ants.length; i++) {
      stepAnt(ants[i]);
    }

    var decay = DECAY_RATE * (0.3 + 0.7 * vitality);
    for (var j = 0; j < grid.length; j++) {
      grid[j] = Math.max(0, grid[j] - decay);
    }

    tickCounter++;
    var respawnRate = Math.max(2000, FOOD_RESPAWN_TICKS / Math.max(vitality, 0.1));
    if (tickCounter % Math.round(respawnRate) === 0) {
      foods = foods.filter(function (f) { return f.amount > 0; });
      if (foods.length < NUM_FOOD_SOURCES) {
        spawnFoods(1);
      }
    }
  }

  function stepAnt(ant) {
    if (ant.carrying) {
      var hdx = hive.x - ant.x;
      var hdy = hive.y - ant.y;
      ant.dx = hdx === 0 ? (rand(3) - 1) : (hdx > 0 ? 1 : -1);
      ant.dy = hdy === 0 ? (rand(3) - 1) : (hdy > 0 ? 1 : -1);

      if (Math.random() < 0.2) {
        ant.dx = rand(3) - 1;
        ant.dy = rand(3) - 1;
      }

      // Carrying ants mark inbound (warm) pheromone
      var inIdx = (ant.y * GRID_W + ant.x) * NUM_CHANNELS + ant.channel;
      grid[inIdx] = Math.min(MAX_PHEROMONE, grid[inIdx] + MARK_STRENGTH * (0.3 + 0.7 * vitality));

      if (Math.abs(ant.x - hive.x) <= 1 && Math.abs(ant.y - hive.y) <= 1) {
        ant.carrying = false;
        ant.channel = INBOUND_CHANNELS.length + rand(OUTBOUND_CHANNELS.length);
        ant.dx = rand(3) - 1 || 1;
        ant.dy = rand(3) - 1;
      }
    } else {
      // Foraging ants mark outbound (cool) pheromone
      var outIdx = (ant.y * GRID_W + ant.x) * NUM_CHANNELS + ant.channel;
      grid[outIdx] = Math.min(MAX_PHEROMONE, grid[outIdx] + MARK_STRENGTH * 0.3 * (0.3 + 0.7 * vitality));

      // Follow inbound (warm) pheromone trails to find food
      var bestPheromone = 0;
      var bestDx = ant.dx;
      var bestDy = ant.dy;

      for (var ddx = -1; ddx <= 1; ddx++) {
        for (var ddy = -1; ddy <= 1; ddy++) {
          if (ddx === 0 && ddy === 0) continue;
          var nx = wrap(ant.x + ddx, GRID_W);
          var ny = wrap(ant.y + ddy, GRID_H);
          // Foraging ants sniff inbound channels (0..2) — those trails lead to food
          var total = 0;
          for (var ci = 0; ci < INBOUND_CHANNELS.length; ci++) {
            total += grid[(ny * GRID_W + nx) * NUM_CHANNELS + ci];
          }
          if (total > bestPheromone) {
            bestPheromone = total;
            bestDx = ddx;
            bestDy = ddy;
          }
        }
      }

      if (bestPheromone > 5 && Math.random() < 0.6) {
        ant.dx = bestDx;
        ant.dy = bestDy;
      } else if (Math.random() < 0.3) {
        ant.dx = rand(3) - 1;
        ant.dy = rand(3) - 1;
      }

      for (var f = 0; f < foods.length; f++) {
        var food = foods[f];
        if (food.amount > 0 && Math.abs(ant.x - food.x) <= 2 && Math.abs(ant.y - food.y) <= 2) {
          ant.carrying = true;
          food.amount--;
          ant.channel = rand(INBOUND_CHANNELS.length);
          break;
        }
      }
    }

    if (ant.dx === 0 && ant.dy === 0) ant.dx = 1;
    ant.x = wrap(ant.x + ant.dx, GRID_W);
    ant.y = wrap(ant.y + ant.dy, GRID_H);
  }

  // --- Debug mode ---
  // Toggle from browser console: antsSimulation.debug()
  // Or add ?debug to the URL
  var debugMode = window.location.search.indexOf('debug') !== -1;

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    var imageData = ctx.createImageData(GRID_W, GRID_H);
    var data = imageData.data;
    var saturation = debugMode ? 1.0 : (0.3 + 0.7 * vitality);
    var alphaBoost = debugMode ? 255 : 180;

    for (var y = 0; y < GRID_H; y++) {
      for (var x = 0; x < GRID_W; x++) {
        var pIdx = (y * GRID_W + x) * NUM_CHANNELS;
        var pixIdx = (y * GRID_W + x) * 4;

        var r = 0, g = 0, b = 0, a = 0;
        for (var c = 0; c < NUM_CHANNELS; c++) {
          var intensity = grid[pIdx + c] / MAX_PHEROMONE;
          r += CHANNELS[c].r * intensity * saturation;
          g += CHANNELS[c].g * intensity * saturation;
          b += CHANNELS[c].b * intensity * saturation;
          a = Math.max(a, intensity);
        }

        data[pixIdx] = clamp(Math.round(r), 0, 255);
        data[pixIdx + 1] = clamp(Math.round(g), 0, 255);
        data[pixIdx + 2] = clamp(Math.round(b), 0, 255);
        data[pixIdx + 3] = clamp(Math.round(a * alphaBoost * saturation), 0, 255);
      }
    }

    ctx.putImageData(imageData, 0, 0);

    // Debug overlay: show ants, hive, food sources
    if (debugMode) {
      // Hive — white square
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.fillRect(hive.x - 1, hive.y - 1, 3, 3);

      // Food sources — green dots, size proportional to remaining amount
      for (var f = 0; f < foods.length; f++) {
        var food = foods[f];
        if (food.amount > 0) {
          var sz = Math.max(1, Math.round(food.amount / FOOD_PER_SOURCE * 3));
          ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
          ctx.fillRect(food.x, food.y, sz, sz);
        } else {
          ctx.fillStyle = 'rgba(255, 0, 0, 0.4)';
          ctx.fillRect(food.x, food.y, 1, 1);
        }
      }

      // Ants — bright dots, color by state
      for (var i = 0; i < ants.length; i++) {
        var ant = ants[i];
        if (ant.carrying) {
          ctx.fillStyle = 'rgba(255, 255, 0, 0.9)'; // yellow = carrying
        } else {
          ctx.fillStyle = 'rgba(255, 255, 255, 0.6)'; // white = foraging
        }
        data[(ant.y * GRID_W + ant.x) * 4 + 0] = 255;
        data[(ant.y * GRID_W + ant.x) * 4 + 3] = 255;
        ctx.fillRect(ant.x, ant.y, 1, 1);
      }

      // HUD
      var carrying = ants.filter(function(a) { return a.carrying; }).length;
      var totalFood = foods.reduce(function(s, f) { return s + f.amount; }, 0);
      canvas.title = 'Ants: ' + ants.length +
        ' | Carrying: ' + carrying +
        ' | Food remaining: ' + totalFood +
        ' | Vitality: ' + vitality.toFixed(2) +
        ' | Tick: ' + tickCounter;
    }
  }

  var TICKS_PER_FRAME = 3;

  function loop() {
    for (var i = 0; i < TICKS_PER_FRAME; i++) {
      tick();
    }
    render();
    rafId = requestAnimationFrame(loop);
  }

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
      // Toggle CSS blur so you can see the pixels clearly
      if (canvas) canvas.style.filter = debugMode ? 'none' : 'blur(10px)';
      console.log('Ant debug mode: ' + (debugMode ? 'ON' : 'OFF'));
      console.log('Ants: ' + ants.length + ' | Vitality: ' + vitality.toFixed(2));
    }
  };

  var theme = localStorage.getItem('theme') || 'consumed';
  if (theme === 'consumed') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        window.antsSimulation.start();
      });
    } else {
      window.antsSimulation.start();
    }
  }
})();
