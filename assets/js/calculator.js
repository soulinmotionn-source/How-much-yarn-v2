/* HowMuchYarn.com — yarn yardage calculator (v3).
   Modes: project preset | custom dimensions.
   Factors: craft (knit 1.0 / crochet 1.27), stitch pattern, safety buffer.
   Optional cost estimate from price per skein.
   Yardage figures are planning estimates (yards) for average-size projects,
   drawn from standard craft guides (Lion Brand, Craft Yarn Council charts).
   Pure calculation is dependency-free so it also runs in Node for testing. */

var YARN_WEIGHTS = [
  { id: "lace",       name: "Lace (0)",                 skeinYards100g: 700 },
  { id: "fingering",  name: "Super Fine / Fingering (1)", skeinYards100g: 440 },
  { id: "sport",      name: "Fine / Sport (2)",         skeinYards100g: 330 },
  { id: "dk",         name: "Light / DK (3)",           skeinYards100g: 280 },
  { id: "worsted",    name: "Medium / Worsted (4)",     skeinYards100g: 220 },
  { id: "bulky",      name: "Bulky (5)",               skeinYards100g: 120 },
  { id: "superbulky", name: "Super Bulky (6)",          skeinYards100g: 70 }
];

var WEIGHT_ORDER = ["lace", "fingering", "sport", "dk", "worsted", "bulky", "superbulky"];

var CRAFTS = [
  { id: "knit",    name: "Knitting", factor: 1.0 },
  { id: "crochet", name: "Crochet",  factor: 1.27 }
];

var STITCHES = [
  { id: "smooth",   name: "Smooth / stockinette",      factor: 1.0 },
  { id: "garter",   name: "Garter / textured",         factor: 1.1 },
  { id: "cables",   name: "Cables / heavy texture",    factor: 1.18 },
  { id: "lace",     name: "Lace / openwork",           factor: 0.85 }
];

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

/* Yards per square inch for custom-size mode (knit, smooth stitch).
   Calibrated from our own project table: worsted baseline 0.92, other
   weights scaled by their average yardage ratio vs worsted. */
var WEIGHT_AREA_YDS = (function () {
  var base = 0.92, ratios = {}, counts = {};
  Object.keys(PROJECT_YARDAGE).forEach(function (pk) {
    var t = PROJECT_YARDAGE[pk];
    if (t.worsted == null) return;
    Object.keys(t).forEach(function (w) {
      if (w === "worsted") return;
      ratios[w] = (ratios[w] || 0) + t[w] / t.worsted;
      counts[w] = (counts[w] || 0) + 1;
    });
  });
  var out = { worsted: base };
  Object.keys(ratios).forEach(function (w) { out[w] = base * ratios[w] / counts[w]; });
  return out;
})();

function weightById(id) {
  for (var i = 0; i < YARN_WEIGHTS.length; i++) {
    if (YARN_WEIGHTS[i].id === id) return YARN_WEIGHTS[i];
  }
  return null;
}
function craftById(id) {
  for (var i = 0; i < CRAFTS.length; i++) {
    if (CRAFTS[i].id === id) return CRAFTS[i];
  }
  return CRAFTS[0];
}
function stitchById(id) {
  for (var i = 0; i < STITCHES.length; i++) {
    if (STITCHES[i].id === id) return STITCHES[i];
  }
  return STITCHES[0];
}
function nearestWeight(table, weightId) {
  if (table[weightId] != null) return { id: weightId, fellBack: false };
  var target = WEIGHT_ORDER.indexOf(weightId), best = null, bestDist = 99;
  for (var w in table) {
    if (!table.hasOwnProperty(w)) continue;
    var d = Math.abs(WEIGHT_ORDER.indexOf(w) - target);
    if (d < bestDist) { bestDist = d; best = w; }
  }
  return { id: best, fellBack: true };
}

/* Pure calculation.
   opts: { mode: "project"|"custom",
           projectKey, width, length, unit: "in"|"cm",
           weightId, craftId, stitchId, skeinYards, bufferPct, pricePerSkein }
   returns { yards, bufferedYards, meters, skeins, cost, usedWeight, fellBack, note } */
function calculate(opts) {
  var craft = craftById(opts.craftId);
  var stitch = stitchById(opts.stitchId);
  var nw = nearestWeight(PROJECT_YARDAGE[opts.projectKey] || PROJECT_YARDAGE["scarf"], opts.weightId);
  var usedWeight = nw.id, fellBack = nw.fellBack;
  var yards;
  if (opts.mode === "custom") {
    var wIn = parseFloat(opts.width), lIn = parseFloat(opts.length);
    if (!(wIn > 0) || !(lIn > 0)) return null;
    if (opts.unit === "cm") { wIn = wIn / 2.54; lIn = lIn / 2.54; }
    var perIn2 = WEIGHT_AREA_YDS[usedWeight] || WEIGHT_AREA_YDS.worsted;
    yards = Math.round(wIn * lIn * perIn2);
  } else {
    var table = PROJECT_YARDAGE[opts.projectKey];
    if (!table) return null;
    yards = table[usedWeight];
  }
  yards = Math.round(yards * craft.factor * stitch.factor);
  var buffered = Math.round(yards * (1 + opts.bufferPct / 100));
  var skeinYards = parseFloat(opts.skeinYards);
  var w = weightById(usedWeight);
  if (!(skeinYards > 0)) skeinYards = w ? w.skeinYards100g : 220;
  var skeins = Math.ceil(buffered / skeinYards);
  var price = parseFloat(opts.pricePerSkein);
  var cost = (price > 0) ? Math.round(skeins * price * 100) / 100 : null;
  return {
    yards: yards,
    bufferedYards: buffered,
    meters: Math.round(buffered * 0.9144),
    skeins: skeins,
    cost: cost,
    usedWeight: usedWeight,
    fellBack: fellBack,
    craftName: craft.name,
    stitchName: stitch.name
  };
}

function fmt(n) { return n.toLocaleString("en-US"); }
function money(n) { return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

/* ---- browser widget wiring ---- */
function initCalculator(rootId) {
  var root = document.getElementById(rootId || "yarn-calc");
  if (!root) return;
  function q(sel) { return root.querySelector(sel); }
  var projSel = q("[data-field=project]");
  var weightSel = q("[data-field=weight]");
  var skeinInput = q("[data-field=skein]");
  var bufferInput = q("[data-field=buffer]");
  var bufferVal = q("[data-field=buffer-val]");
  var craftRadios = root.querySelectorAll("[data-field=craft]");
  var stitchSel = q("[data-field=stitch]");
  var widthInput = q("[data-field=width]");
  var lengthInput = q("[data-field=length]");
  var unitSel = q("[data-field=unit]");
  var priceInput = q("[data-field=price]");
  var btn = q("[data-action=calculate]");
  var out = q("[data-field=result]");
  var modeTabs = root.querySelectorAll("[data-mode-tab]");
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
  STITCHES.forEach(function (s) {
    var o = document.createElement("option");
    o.value = s.id; o.textContent = s.name;
    stitchSel.appendChild(o);
  });

  var mode = "project";
  function setMode(m) {
    mode = m;
    for (var i = 0; i < modeTabs.length; i++) {
      var t = modeTabs[i];
      var active = t.getAttribute("data-mode-tab") === m;
      t.classList.toggle("active", active);
      t.setAttribute("aria-selected", active ? "true" : "false");
    }
    var pf = root.querySelectorAll('[data-show="project"]');
    var cf = root.querySelectorAll('[data-show="custom"]');
    for (var j = 0; j < pf.length; j++) pf[j].hidden = (m !== "project");
    for (var k = 0; k < cf.length; k++) cf[k].hidden = (m !== "custom");
    render();
  }
  for (var ti = 0; ti < modeTabs.length; ti++) {
    (function (t) {
      t.addEventListener("click", function (e) {
        e.preventDefault();
        setMode(t.getAttribute("data-mode-tab"));
      });
    })(modeTabs[ti]);
  }

  // Presets: data attributes first, then ?project=&weight= URL params (deep links)
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

  function currentCraft() {
    for (var i = 0; i < craftRadios.length; i++) {
      if (craftRadios[i].checked) return craftRadios[i].value;
    }
    return "knit";
  }
  function syncBufferLabel() {
    var v = parseFloat(bufferInput.value) || 0;
    if (bufferVal) bufferVal.textContent = v + "%";
    var pct = Math.max(0, Math.min(50, v)) / 50 * 100;
    bufferInput.style.background =
      "linear-gradient(to right,var(--forest) 0%,var(--forest) " + pct +
      "%,var(--line) " + pct + "%,var(--line) 100%)";
  }

  function render() {
    var w = weightById(weightSel.value) || weightById("worsted");
    var skeinYards = parseFloat(skeinInput.value);
    if (!(skeinYards > 0)) skeinYards = w.skeinYards100g;
    var buffer = parseFloat(bufferInput.value);
    if (!(buffer >= 0)) buffer = 10;
    syncBufferLabel();
    var r = calculate({
      mode: mode,
      projectKey: projSel.value,
      width: widthInput ? widthInput.value : 0,
      length: lengthInput ? lengthInput.value : 0,
      unit: unitSel ? unitSel.value : "in",
      weightId: weightSel.value,
      craftId: currentCraft(),
      stitchId: stitchSel ? stitchSel.value : "smooth",
      skeinYards: skeinYards,
      bufferPct: buffer,
      pricePerSkein: priceInput ? priceInput.value : 0
    });
    if (!r) return;
    var fallback = r.fellBack
      ? '<p class="calc-fallback">Estimate shown for ' + weightById(r.usedWeight).name +
        " — the closest available weight for this project.</p>"
      : "";
    var costBox = (r.cost != null)
      ? '<div class="result-box"><span class="n">' + money(r.cost) + "</span>" +
        '<span class="l">estimated cost (' + r.skeins + " skeins)</span></div>"
      : "";
    var label = mode === "custom"
      ? "yards for your custom size"
      : "yards for " + (PROJECT_LABELS[projSel.value] || "your project").toLowerCase();
    out.innerHTML =
      '<div class="result-row">' +
        '<div class="result-box"><span class="n">' + fmt(r.bufferedYards) + "</span>" +
        '<span class="l">' + label + " (" + fmt(r.meters) + " m)</span></div>" +
        '<div class="result-box"><span class="n">' + r.skeins + "</span>" +
        '<span class="l">skeins of ' + Math.round(skeinYards) + " yd</span></div>" +
        costBox +
      "</div>" + fallback +
      '<div class="result-note">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3C7 7 5 11 5 14a7 7 0 0 0 14 0c0-3-2-7-7-11z"/></svg>' +
        "<span>" + r.craftName + " · " + r.stitchName.toLowerCase() + " · includes a " + buffer +
        "% buffer. Base estimate before buffer: " + fmt(r.yards) + " yards.</span>" +
      "</div>";
  }

  if (btn) btn.addEventListener("click", function (e) { e.preventDefault(); render(); });
  [projSel, weightSel, stitchSel, unitSel].forEach(function (el) {
    if (el) el.addEventListener("change", render);
  });
  [skeinInput, bufferInput, widthInput, lengthInput, priceInput].forEach(function (el) {
    if (el) el.addEventListener("input", render);
  });
  for (var ci = 0; ci < craftRadios.length; ci++) {
    craftRadios[ci].addEventListener("change", render);
  }
  refreshSkeinDefault();
  syncBufferLabel();
  setMode("project");
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
          mb.setAttribute("aria-label", open ? "Close menu" : "Open menu");
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
    // Embed code copy button
    document.querySelectorAll("[data-action=copy-embed]").forEach(function (b) {
      b.addEventListener("click", function () {
        var ta = document.getElementById("embed-code");
        var done = function () {
          b.textContent = "Copied!";
          setTimeout(function () { b.textContent = "Copy code"; }, 2000);
        };
        if (ta) {
          var txt = ta.textContent;
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(txt).then(done, done);
          } else {
            var tmp = document.createElement("textarea");
            tmp.value = txt;
            document.body.appendChild(tmp);
            tmp.select();
            try { document.execCommand("copy"); } catch (e) {}
            document.body.removeChild(tmp);
            done();
          }
        }
      });
    });
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    YARN_WEIGHTS: YARN_WEIGHTS,
    PROJECT_YARDAGE: PROJECT_YARDAGE,
    PROJECT_LABELS: PROJECT_LABELS,
    CRAFTS: CRAFTS,
    STITCHES: STITCHES,
    WEIGHT_AREA_YDS: WEIGHT_AREA_YDS,
    calculate: calculate,
    weightById: weightById,
    craftById: craftById,
    stitchById: stitchById
  };
}
