/* HowMuchYarn.com — yarn yardage calculator (v2).
   Yardage figures are planning estimates (yards) for an average-size project,
   drawn from standard craft guides (Lion Brand, Craft Yarn Council charts).
   Pure calculation is dependency-free so it also runs in Node for testing. */

var YARN_WEIGHTS = [
  { id: "lace",       name: "Lace (0)",                 skeinYards100g: 700 },
  { id: "fingering",  name: "Super Fine / Fingering (1)", skeinYards100g: 440 },
  { id: "sport",      name: "Fine / Sport (2)",         skeinYards100g: 330 },
  { id: "dk",         name: "Light / DK (3)",           skeinYards100g: 280 },
  { id: "worsted",    name: "Medium / Worsted (4)",     skeinYards100g: 220 },
  { id: "bulky",      name: "Bulky (5)",                skeinYards100g: 120 },
  { id: "superbulky", name: "Super Bulky (6)",          skeinYards100g: 70 }
];

var WEIGHT_ORDER = ["lace", "fingering", "sport", "dk", "worsted", "bulky", "superbulky"];

/* Estimated yardage (yards) per project per yarn weight. Missing entries mean
   that weight is uncommon for the project; the calculator falls back to the
   nearest available weight and says so. */
var PROJECT_YARDAGE = {
  "baby-blanket":  { lace: 1550, fingering: 1400, sport: 1200, dk: 1150, worsted: 1050, bulky: 900, superbulky: 800 },
  "throw-blanket": { fingering: 3200, sport: 3000, dk: 2600, worsted: 2200, bulky: 1750, superbulky: 1400 },
  "twin-blanket":  { dk: 4000, worsted: 3200, bulky: 2400, superbulky: 1800 },
  "queen-blanket": { dk: 6000, worsted: 4600, bulky: 3400, superbulky: 2600 },
  "king-blanket":  { dk: 8500, worsted: 6500, bulky: 4800, superbulky: 3600 },
  "scarf":         { lace: 700, fingering: 500, sport: 425, dk: 400, worsted: 350, bulky: 300, superbulky: 225 },
  "cowl":          { fingering: 450, sport: 400, dk: 350, worsted: 300, bulky: 250, superbulky: 200 },
  "hat":           { fingering: 300, sport: 280, dk: 225, worsted: 200, bulky: 160, superbulky: 130 },
  "socks":         { fingering: 450, sport: 400, dk: 375 },
  "mittens":       { fingering: 250, sport: 230, dk: 210, worsted: 180, bulky: 150 },
  "sweater":       { fingering: 2000, sport: 1900, dk: 1700, worsted: 1400, bulky: 1050, superbulky: 950 },
  "baby-sweater":  { fingering: 800, sport: 750, dk: 700, worsted: 600, bulky: 500 },
  "cardigan":      { fingering: 2200, sport: 2100, dk: 1900, worsted: 1600, bulky: 1250 },
  "shawl":         { lace: 900, fingering: 700, sport: 550, dk: 500, worsted: 450, bulky: 425 },
  "vest":          { sport: 1100, dk: 1000, worsted: 900, bulky: 750 },
  "market-bag":    { sport: 400, dk: 350, worsted: 300, bulky: 250 },
  "amigurumi":     { fingering: 150, sport: 130, dk: 110, worsted: 90 },
  "rug":           { worsted: 1200, bulky: 1000, superbulky: 800 }
};

var PROJECT_LABELS = {
  "baby-blanket": "Baby blanket",
  "throw-blanket": "Throw blanket",
  "twin-blanket": "Twin-size blanket",
  "queen-blanket": "Queen-size blanket",
  "king-blanket": "King-size blanket",
  "scarf": "Scarf",
  "cowl": "Cowl",
  "hat": "Hat / beanie",
  "socks": "Socks (pair)",
  "mittens": "Mittens",
  "sweater": "Adult sweater",
  "baby-sweater": "Baby sweater",
  "cardigan": "Cardigan",
  "shawl": "Shawl",
  "vest": "Vest",
  "market-bag": "Market bag",
  "amigurumi": "Amigurumi toy",
  "rug": "Rug"
};

function weightById(id) {
  for (var i = 0; i < YARN_WEIGHTS.length; i++) {
    if (YARN_WEIGHTS[i].id === id) return YARN_WEIGHTS[i];
  }
  return null;
}

/* Pure calculation: { yards, bufferedYards, meters, skeins, usedWeight, fellBack } */
function calculate(projectKey, weightId, skeinYards, bufferPct) {
  var table = PROJECT_YARDAGE[projectKey];
  if (!table) return null;
  var usedWeight = weightId, fellBack = false;
  if (table[weightId] == null) {
    var target = WEIGHT_ORDER.indexOf(weightId);
    var best = null, bestDist = 99;
    for (var w in table) {
      if (!table.hasOwnProperty(w)) continue;
      var d = Math.abs(WEIGHT_ORDER.indexOf(w) - target);
      if (d < bestDist) { bestDist = d; best = w; }
    }
    usedWeight = best; fellBack = true;
  }
  var yards = table[usedWeight];
  var buffered = Math.round(yards * (1 + bufferPct / 100));
  var skeins = Math.ceil(buffered / skeinYards);
  return {
    yards: yards,
    bufferedYards: buffered,
    meters: Math.round(buffered * 0.9144),
    skeins: skeins,
    usedWeight: usedWeight,
    fellBack: fellBack
  };
}

function fmt(n) { return n.toLocaleString("en-US"); }

/* ---- browser widget wiring (matches the v2 card markup) ---- */
function initCalculator(rootId) {
  var root = document.getElementById(rootId || "yarn-calc");
  if (!root) return;
  var projSel = root.querySelector("[data-field=project]");
  var weightSel = root.querySelector("[data-field=weight]");
  var skeinInput = root.querySelector("[data-field=skein]");
  var bufferInput = root.querySelector("[data-field=buffer]");
  var btn = root.querySelector("[data-action=calculate]");
  var out = root.querySelector("[data-field=result]");
  if (!projSel || !weightSel || !out) return;

  Object.keys(PROJECT_LABELS).forEach(function (k) {
    var o = document.createElement("option");
    o.value = k; o.textContent = PROJECT_LABELS[k];
    projSel.appendChild(o);
  });
  YARN_WEIGHTS.forEach(function (w) {
    var o = document.createElement("option");
    o.value = w.id; o.textContent = w.name;
    weightSel.appendChild(o);
  });

  // Presets: data attributes first, then ?project=&weight= URL params (deep links from project pages)
  var preset = root.getAttribute("data-preset-project");
  var qs = new URLSearchParams(window.location.search || "");
  var qProject = qs.get("project"), qWeight = qs.get("weight");
  if (PROJECT_LABELS[qProject]) projSel.value = qProject;
  else if (preset && PROJECT_LABELS[preset]) projSel.value = preset;
  if (weightById(qWeight)) weightSel.value = qWeight;
  else weightSel.value = "worsted";

  function refreshSkeinDefault() {
    var w = weightById(weightSel.value);
    if (w && !skeinInput.dataset.touched) skeinInput.value = w.skeinYards100g;
  }
  skeinInput.addEventListener("input", function () { skeinInput.dataset.touched = "1"; });
  weightSel.addEventListener("change", function () {
    delete skeinInput.dataset.touched;
    refreshSkeinDefault();
    render();
  });

  function render() {
    var w = weightById(weightSel.value) || weightById("worsted");
    var skeinYards = parseFloat(skeinInput.value);
    if (!(skeinYards > 0)) skeinYards = w.skeinYards100g;
    var buffer = parseFloat(bufferInput.value);
    if (!(buffer >= 0)) buffer = 10;
    var r = calculate(projSel.value, weightSel.value, skeinYards, buffer);
    if (!r) return;
    var fallback = r.fellBack
      ? '<p class="calc-fallback">Estimate shown for ' + weightById(r.usedWeight).name +
        ' — the closest available weight for this project.</p>'
      : "";
    out.innerHTML =
      '<div class="result-row">' +
        '<div class="result-box"><span class="n">' + fmt(r.bufferedYards) + '</span>' +
        '<span class="l">yards needed (' + fmt(r.meters) + ' m)</span></div>' +
        '<div class="result-box"><span class="n">' + r.skeins + '</span>' +
        '<span class="l">skeins of ' + Math.round(skeinYards) + ' yd</span></div>' +
      '</div>' + fallback +
      '<div class="result-note">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3C7 7 5 11 5 14a7 7 0 0 0 14 0c0-3-2-7-7-11z"/></svg>' +
        '<span>Includes a ' + buffer + '% buffer for gauge differences and mistakes. ' +
        'Base estimate before buffer: ' + fmt(r.yards) + ' yards.</span>' +
      '</div>';
  }

  if (btn) btn.addEventListener("click", function (e) { e.preventDefault(); render(); });
  projSel.addEventListener("change", render);
  skeinInput.addEventListener("input", render);
  bufferInput.addEventListener("input", render);
  refreshSkeinDefault();
  render();
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", function () {
    initCalculator("yarn-calc");
    // Mobile hamburger menu
    var mb = document.querySelector(".menu-btn");
    var mn = document.getElementById("site-nav");
    if (mb && mn) {
      mb.addEventListener("click", function () {
        var open = mn.classList.toggle("open");
        mb.setAttribute("aria-expanded", open ? "true" : "false");
        mb.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      });
      mn.addEventListener("click", function (e) {
        if (e.target.closest("a")) {
          mn.classList.remove("open");
          mb.setAttribute("aria-expanded", "false");
          mb.setAttribute("aria-label", "Open menu");
        }
      });
    }
    // Cookie consent (no tracking of its own; remembers choice locally)
    var bar = document.getElementById("cookie-bar");
    try {
      if (bar && !localStorage.getItem("hmy-cookie-ok")) {
        bar.classList.add("show");
        bar.querySelector("button").addEventListener("click", function () {
          localStorage.setItem("hmy-cookie-ok", "1");
          bar.classList.remove("show");
        });
      }
    } catch (e) { /* storage unavailable: leave banner hidden */ }
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    YARN_WEIGHTS: YARN_WEIGHTS,
    PROJECT_YARDAGE: PROJECT_YARDAGE,
    PROJECT_LABELS: PROJECT_LABELS,
    calculate: calculate,
    weightById: weightById
  };
}
