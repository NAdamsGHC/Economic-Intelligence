/* Gateshead Economic Intelligence — landing page engine
   Renders the product catalogue from catalog.json: a Pinned section first,
   then the ONS-topic sections, with live search and copy-deep-link buttons.
   Zero dependencies, zero network beyond catalog.json. */
(function () {
  "use strict";

  var SITE = ""; // filled from catalog.site

  // Recurring publication series. The newest product in each series is pinned
  // automatically; earlier editions collect in an archive section at the foot
  // of the page.
  var SERIES = {
    "whats-new":       { archive: "What's New",            note: "Weekly round-up — earlier editions, newest first" },
    "economic-update": { archive: "Past Economic Updates", note: "Earlier editions, newest first" },
    "policy-update":   { archive: "Past Policy Updates",   note: "Earlier editions, newest first" },
    "lea-update":      { archive: "Past LEA Updates",      note: "Earlier editions, newest first" }
  };
  var SERIES_ORDER = ["whats-new", "economic-update", "policy-update", "lea-update"];

  // ---- SVG icons (chain link + search) ----
  var ICON_LINK =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>' +
    '<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>';
  var ICON_SEARCH =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>';

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function absUrl(p) {
    if (p.external) return p.path;
    var base = SITE.replace(/\/$/, "");
    return base ? base + "/" + p.path : p.path;
  }

  // ---- toast ----
  var toastEl;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "gc-toast"; document.body.appendChild(toastEl); }
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { toastEl.classList.remove("show"); }, 1600);
  }

  function copyLink(url) {
    var done = function () { toast("Link copied — opens this dashboard directly"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, function () { legacyCopy(url); done(); });
    } else { legacyCopy(url); done(); }
  }
  function legacyCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
  }

  // ---- card ----
  function card(p, opts) {
    opts = opts || {};
    var el = document.createElement("article");
    el.className = "gc-card" + (p.pinned ? " pinned" : "");
    el.setAttribute("data-id", p.id);
    var url = absUrl(p);
    var hay = (p.title + " " + p.description + " " + p.sources + " " + (p.keywords || []).join(" ") + " " + p.topic).toLowerCase();
    el.setAttribute("data-search", hay);

    // In the Pinned section the badge names the home topic instead of "Pinned".
    var badge = opts.inPinned
      ? '<div class="gc-pin-badge">' + esc(p.topic) + "</div>"
      : (p.pinned ? '<div class="gc-pin-badge">Pinned</div>' : "");

    el.innerHTML =
      badge +
      '<div class="titlerow"><h3><a href="' + esc(url) + '"' + (p.external ? ' target="_blank" rel="noopener"' : "") + ">" + esc(p.title) + "</a></h3></div>" +
      '<p class="desc">' + esc(p.description) + "</p>" +
      '<div class="meta">' + esc(p.sources) + "</div>" +
      '<div class="actions">' +
        '<span class="grow"></span>' +
        '<a class="gc-open" href="' + esc(url) + '"' + (p.external ? ' target="_blank" rel="noopener"' : "") + ">Open &rsaquo;</a>" +
        '<button class="gc-copy" type="button" aria-label="Copy direct link to this dashboard" title="Copy direct link to this dashboard">' + ICON_LINK + "</button>" +
      "</div>";

    el.querySelector(".gc-copy").addEventListener("click", function () {
      var btn = this;
      copyLink(url);
      btn.classList.add("copied");
      setTimeout(function () { btn.classList.remove("copied"); }, 1400);
    });
    return el;
  }

  // ---- search ----
  function wireSearch() {
    var input = document.getElementById("gc-search");
    var meta = document.getElementById("gc-searchmeta");
    if (!input) return;
    var run = function () {
      var q = input.value.trim().toLowerCase();
      var terms = q ? q.split(/\s+/) : [];
      var shown = 0, shownIds = {}, allIds = {};
      document.querySelectorAll(".gc-topic").forEach(function (topic) {
        var vis = 0;
        if (!topic.querySelectorAll(".gc-card").length) {
          // card-less sections (the publication schedule) hide during search
          topic.style.display = q ? "none" : "";
          return;
        }
        topic.querySelectorAll(".gc-card").forEach(function (c) {
          allIds[c.getAttribute("data-id")] = 1;
          var hay = c.getAttribute("data-search");
          var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; });
          c.style.display = ok ? "" : "none";
          if (ok) { vis++; shown++; shownIds[c.getAttribute("data-id")] = 1; }
        });
        topic.style.display = vis ? "" : "none";
        var cnt = topic.querySelector(".count");
        if (cnt) cnt.textContent = vis + (vis === 1 ? " product" : " products");
      });
      var nr = document.getElementById("gc-noresults");
      if (nr) nr.style.display = shown ? "none" : "";
      if (meta) {
        var nShown = Object.keys(shownIds).length, nAll = Object.keys(allIds).length;
        meta.textContent = q ? (nShown + " of " + nAll + " products match “" + input.value.trim() + "”") : "";
      }
    };
    input.addEventListener("input", run);
    input.addEventListener("keydown", function (e) { if (e.key === "Escape") { input.value = ""; run(); } });
  }

  // ---- render ----
  function topicSection(name, note, id) {
    var sec = document.createElement("section");
    sec.className = "gc-topic";
    sec.id = id;
    sec.innerHTML =
      '<div class="gc-topic-head"><h2>' + esc(name) + "</h2>" +
      '<span class="note">' + esc(note || "") + "</span>" +
      '<span class="count"></span></div>' +
      '<div class="gc-cards"></div>';
    return sec;
  }

  // ---- publication schedule (rendered from catalog.schedule) ----
  function scheduleSection(sch) {
    var sec = document.createElement("section");
    sec.className = "gc-topic gc-sched";
    sec.id = "publication-schedule";
    var head =
      '<div class="gc-topic-head"><h2>Publication schedule</h2>' +
      '<span class="note">What&rsquo;s coming and when &middot; updated ' + esc(sch.updated || "") + "</span></div>";
    var html = '<div class="gc-sched-scroll"><table class="gc-sched-table"><thead><tr><th class="prod">Product</th>';
    sch.months.forEach(function (m) { html += "<th>" + esc(m.label) + "</th>"; });
    html += "</tr></thead><tbody>";
    sch.rows.forEach(function (row) {
      html += '<tr><td class="prod">' + esc(row.name) + '<span class="cad">' + esc(row.cadence || "") + "</span></td>";
      sch.months.forEach(function (m) {
        html += "<td>";
        (row.entries[m.id] || []).forEach(function (e) {
          var cls = "gc-chip " + (e.status || "planned") + (e.kind ? " " + e.kind : "");
          if (e.href) {
            html += '<a class="' + cls + '" href="' + esc(e.href) + '">' + esc(e.label) + "</a>";
          } else {
            html += '<span class="' + cls + '">' + esc(e.label) + "</span>";
          }
        });
        html += "</td>";
      });
      html += "</tr>";
    });
    html += "</tbody></table></div>" +
      '<div class="gc-sched-key"><span><i class="k released"></i>Released &mdash; click to open</span>' +
      "<span><i class=\"k next\"></i>Next up</span><span><i class=\"k planned\"></i>Planned</span></div>";
    sec.innerHTML = head + html;
    return sec;
  }

  function render(cat) {
    SITE = cat.site || "";
    var root = document.getElementById("gc-catalog");
    if (!root) return;
    root.innerHTML = "";

    // Series resolution: newest edition of each series is pinned; the rest
    // are archived out of the topic sections into the foot-of-page sections.
    var bySeries = {};
    cat.products.forEach(function (p) {
      if (p.series && SERIES[p.series]) (bySeries[p.series] = bySeries[p.series] || []).push(p);
    });
    Object.keys(bySeries).forEach(function (s) {
      bySeries[s].sort(function (a, b) { return String(b.date || "").localeCompare(String(a.date || "")); });
      bySeries[s].forEach(function (p, i) { p.pinned = i === 0; p._archived = i > 0; });
    });

    // Pinned section first — flagged products plus each series' latest.
    // Pinned products appear here ONLY (not repeated in their topic section).
    var pinnedProds = cat.products.filter(function (p) { return p.pinned; });
    if (pinnedProds.length) {
      var psec = topicSection("Pinned", "The latest editions and the products the team reaches for most", "topic-pinned");
      psec.classList.add("gc-topic-pinned");
      var pgrid = psec.querySelector(".gc-cards");
      pinnedProds.forEach(function (p) { pgrid.appendChild(card(p, { inPinned: true })); });
      psec.querySelector(".count").textContent = pinnedProds.length + (pinnedProds.length === 1 ? " product" : " products");
      root.appendChild(psec);
    }

    // Publication schedule — the public year view (published products only).
    if (cat.schedule) root.appendChild(scheduleSection(cat.schedule));

    cat.topics.forEach(function (t) {
      var prods = cat.products.filter(function (p) { return p.topic === t.name && !p.pinned && !p._archived; });
      if (!prods.length) return;
      var sec = topicSection(t.name, t.note, "topic-" + t.name.toLowerCase().replace(/[^a-z]+/g, "-"));
      var grid = sec.querySelector(".gc-cards");
      prods.forEach(function (p) { grid.appendChild(card(p)); });
      sec.querySelector(".count").textContent = prods.length + (prods.length === 1 ? " product" : " products");
      root.appendChild(sec);
    });

    // Series archives at the foot of the page.
    SERIES_ORDER.forEach(function (s) {
      var arr = (bySeries[s] || []).filter(function (p) { return p._archived; });
      if (!arr.length) return;
      var sec = topicSection(SERIES[s].archive, SERIES[s].note, "series-" + s);
      var grid = sec.querySelector(".gc-cards");
      arr.forEach(function (p) { grid.appendChild(card(p)); });
      sec.querySelector(".count").textContent = arr.length + (arr.length === 1 ? " edition" : " editions");
      root.appendChild(sec);
    });

    var nr = document.createElement("div");
    nr.id = "gc-noresults"; nr.className = "gc-noresults"; nr.style.display = "none";
    nr.textContent = "No products match your search. Try fewer or different words.";
    root.appendChild(nr);

    wireSearch();
    var sw = document.querySelector(".gc-searchwrap");
    if (sw && !sw.querySelector("svg")) sw.insertAdjacentHTML("afterbegin", ICON_SEARCH);
  }

  function boot() {
    fetch("catalog.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(render)
      .catch(function () {
        var root = document.getElementById("gc-catalog");
        if (root) root.innerHTML = '<div class="gc-noresults">Could not load the product catalogue (catalog.json). If you opened this file directly, view it through the published site or a local server.</div>';
      });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
