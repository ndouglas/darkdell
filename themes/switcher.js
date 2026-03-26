// themes/switcher.js
// Theme switching: cycle through themes, persist in localStorage.

(function () {
  var THEMES = ['consumed', 'garish', 'clean'];
  var btn = document.getElementById('theme-switcher');
  var link = document.getElementById('theme-css');
  var canvas = document.getElementById('ants-canvas');

  function getTheme() {
    return localStorage.getItem('theme') || 'consumed';
  }

  function setTheme(name) {
    localStorage.setItem('theme', name);
    document.documentElement.setAttribute('data-theme', name);
    link.href = '/themes/' + name + '/style.css';
    btn.textContent = name;

    // Start/stop ant simulation
    if (typeof window.antsSimulation !== 'undefined') {
      if (name === 'consumed') {
        window.antsSimulation.start();
        canvas.style.display = '';
      } else {
        window.antsSimulation.stop();
        canvas.style.display = 'none';
      }
    }
  }

  // Cycle on click
  btn.addEventListener('click', function () {
    var current = getTheme();
    var idx = THEMES.indexOf(current);
    var next = THEMES[(idx + 1) % THEMES.length];
    setTheme(next);
  });

  // Apply saved theme on load
  setTheme(getTheme());
})();
