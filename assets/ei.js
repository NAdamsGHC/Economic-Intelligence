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

  // Cards shown before a section folds behind "Show all".
  var CARD_LIMIT = 3;

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
    el.className = "gc-card" + (p.pinned ? " pinned" : "") + (p.featured ? " featured" : "");
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

  // ---- "Show detail" ----
  // Cards are all the same size, with the title, description and source line
  // clipped to a fixed number of lines. Where text is actually cut, the card
  // gets a button that lifts the clamps on that card alone. Cards whose text
  // already fits never get one, so the button means something when it appears.
  function isClipped(el) {
    return !!el && el.scrollHeight > el.clientHeight + 1;
  }
  function wireDetail(sec) {
    sec.querySelectorAll(".gc-card").forEach(function (c) {
      if (c.classList.contains("gc-detail-open")) return; // measuring an open card tells us nothing
      var cut = isClipped(c.querySelector("h3")) ||
                isClipped(c.querySelector(".desc")) ||
                isClipped(c.querySelector(".meta"));
      var btn = c.querySelector(".gc-detail");
      if (!cut) { if (btn) btn.remove(); return; }
      if (btn) return;
      btn = document.createElement("button");
      btn.type = "button";
      btn.className = "gc-detail";
      btn.textContent = "Show detail";
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Show the full description for " + (c.querySelector("h3") || {}).textContent);
      var actions = c.querySelector(".actions");
      actions.insertBefore(btn, actions.firstChild);
      btn.addEventListener("click", function () {
        var open = c.classList.toggle("gc-detail-open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        btn.textContent = open ? "Hide detail" : "Show detail";
      });
    });
  }
  // Line counts depend on the web font and on the column width, so re-measure
  // once the font has loaded and again after the layout settles on a resize.
  function remeasure() {
    document.querySelectorAll(".gc-topic").forEach(wireDetail);
  }

  // ---- search ----
  function wireSearch() {
    var input = document.getElementById("gc-search");
    var meta = document.getElementById("gc-searchmeta");
    if (!input) return;
    var run = function () {
      var q = input.value.trim().toLowerCase();
      var terms = q ? q.split(/\s+/) : [];
      // While searching, suspend the collapse and show-3 rules so a match can
      // never be hidden behind a fold. The classes stay on the sections; the
      // CSS that acts on them is scoped to body:not(.gc-searching).
      document.body.classList.toggle("gc-searching", !!q);
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
        var noun = topic.getAttribute("data-noun") || "product";
        if (cnt) cnt.textContent = vis + " " + noun + (vis === 1 ? "" : "s");
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
  function topicSection(name, note, id, noun) {
    var sec = document.createElement("section");
    sec.className = "gc-topic";
    sec.id = id;
    sec.setAttribute("data-noun", noun || "product");
    sec.innerHTML =
      '<div class="gc-topic-head"><h2>' + esc(name) + "</h2>" +
      '<span class="note">' + esc(note || "") + "</span>" +
      '<span class="count"></span></div>' +
      '<div class="gc-cards"></div>';
    return sec;
  }

  function setCount(sec, n) {
    var noun = sec.getAttribute("data-noun") || "product";
    sec.querySelector(".count").textContent = n + " " + noun + (n === 1 ? "" : "s");
  }

  // ---- collapse / show-more ----
  // Two folds, both suspended during search (see wireSearch):
  //   collapsible(sec) — whole section folded away behind a Show/Hide button.
  //     Used for the series archives, which start collapsed.
  //   truncate(sec, n) — first n cards shown, the rest behind "Show all".
  //     Used for every other card section.
  // Both remember the reader's choice per browser, so an opened section stays
  // open on the next visit; the default applies only until they choose.
  var STORE = "gc-fold:";
  function saved(key) { try { return localStorage.getItem(STORE + key); } catch (e) { return null; } }
  function save(key, v) { try { localStorage.setItem(STORE + key, v); } catch (e) {} }

  function collapsible(sec, startCollapsed) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "gc-sec-toggle";
    btn.setAttribute("aria-controls", sec.id + "-cards");
    sec.querySelector(".gc-cards").id = sec.id + "-cards";
    btn.innerHTML = '<span class="chev" aria-hidden="true">&#9662;</span><span class="lbl"></span>';
    sec.querySelector(".gc-topic-head").appendChild(btn);

    var apply = function (collapsed) {
      sec.classList.toggle("gc-collapsed", collapsed);
      btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
      btn.querySelector(".lbl").textContent = collapsed ? "Show" : "Hide";
    };
    var s = saved(sec.id);
    apply(s === null ? !!startCollapsed : s === "1");
    btn.addEventListener("click", function () {
      var collapsed = !sec.classList.contains("gc-collapsed");
      apply(collapsed);
      save(sec.id, collapsed ? "1" : "0");
    });
  }

  function truncate(sec, limit) {
    var cards = sec.querySelectorAll(".gc-cards > .gc-card");
    if (cards.length <= limit) return;
    for (var i = limit; i < cards.length; i++) cards[i].classList.add("gc-more");

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "gc-showmore";
    btn.setAttribute("aria-controls", sec.id + "-cards");
    sec.querySelector(".gc-cards").id = sec.id + "-cards";
    sec.appendChild(btn);

    var apply = function (truncated) {
      sec.classList.toggle("gc-truncated", truncated);
      btn.setAttribute("aria-expanded", truncated ? "false" : "true");
      btn.innerHTML = truncated
        ? '<span class="chev" aria-hidden="true">&#9662;</span>Show all ' + cards.length
        : '<span class="chev" aria-hidden="true">&#9662;</span>Show fewer';
    };
    var s = saved(sec.id + ":more");
    apply(s === null ? true : s !== "1");
    btn.addEventListener("click", function () {
      var truncated = !sec.classList.contains("gc-truncated");
      apply(truncated);
      save(sec.id + ":more", truncated ? "0" : "1");
    });
  }

  // ---- publication schedule (rendered from catalog.schedule) ----
  // New key (Oct 2026): the old one only folded the schedule, so earlier
  // choices are not carried over and every reader starts with the row shown.
  var TOPROW_KEY = "gc-toprow-collapsed";
  function scheduleSection(sch) {
    var sec = document.createElement("section");
    sec.className = "gc-topic gc-sched";
    sec.id = "publication-schedule";
    var head =
      '<div class="gc-topic-head"><h2>Publication schedule</h2>' +
      '<span class="note">Last month and the next five &middot; updated ' + esc(sch.updated || "") + "</span>" +
      '<button class="gc-sched-toggle" type="button" aria-expanded="true" aria-controls="gc-sched-body horizon-widget-body">' +
      '<span class="chev" aria-hidden="true">&#9662;</span><span class="lbl">Hide</span></button></div>';
    // Six months: the month just gone, the viewer's current month and the four
    // after it. Falls back to the last six held if the schedule runs out.
    var now = new Date(), cur = now.getFullYear() + "-" + ("0" + (now.getMonth() + 1)).slice(-2);
    var from = 0;
    while (from < sch.months.length && sch.months[from].id < cur) from++;
    from = Math.max(0, from - 1);
    if (from > sch.months.length - 6) from = Math.max(0, sch.months.length - 6);
    var months = sch.months.slice(from, from + 6);
    var html = '<div class="gc-sched-body" id="gc-sched-body">' +
      '<div class="gc-sched-scroll"><table class="gc-sched-table"><thead><tr><th class="prod">Product</th>';
    months.forEach(function (m) { html += "<th>" + esc(m.label) + "</th>"; });
    html += "</tr></thead><tbody>";
    sch.rows.forEach(function (row) {
      html += '<tr><td class="prod">' + esc(row.name) + '<span class="cad">' + esc(row.cadence || "") + "</span></td>";
      months.forEach(function (m) {
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
      "<span><i class=\"k next\"></i>Next up</span><span><i class=\"k planned\"></i>Planned</span></div></div>";
    sec.innerHTML = head + html;

    // The Hide button folds the whole top row (schedule and Horizon Calendar
    // together); wired in render() once both halves exist. Shown by default.
    return sec;
  }

  // ---- Horizon Calendar widget (a small wall calendar, rendered from horizon/horizon.json) ----
  // Each day with items is filled with its highest priority. Hover or focus a
  // day to see what lands on it. Clicking the card opens the full calendar at
  // the month on show.
  var MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  var RAGW = { r: "Red", a: "Amber", g: "Green" }, RANK = { r: 3, a: 2, g: 1 };
  function ymd(d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); }

  function horizonSection(p) {
    var sec = document.createElement("section");
    sec.className = "gc-topic gc-topic-horizon";
    sec.id = "horizon-widget";
    sec.setAttribute("data-noun", "calendar");
    sec.innerHTML =
      '<div class="gc-topic-head"><h2>Horizon Calendar</h2><span class="note">Dates that matter</span></div>' +
      '<div class="gc-cards gc-cards-one" id="horizon-widget-body"></div>';
    var url = absUrl(p);
    var el = document.createElement("article");
    el.className = "gc-card gc-hzw";
    el.setAttribute("data-id", p.id);
    el.setAttribute("data-search", (p.title + " " + p.description + " " + p.sources + " " + (p.keywords || []).join(" ") + " " + p.topic).toLowerCase());
    el.innerHTML = '<div class="hz-hang" aria-hidden="true"><i></i><i></i></div>' +
      '<div class="hz-top"><button type="button" class="hz-nav" data-step="-1" aria-label="Previous month">&lsaquo;</button>' +
      '<b></b><button type="button" class="hz-nav" data-step="1" aria-label="Next month">&rsaquo;</button></div>' +
      '<div class="hz-body"><div class="hz-grid"><table aria-label="Horizon Calendar, month view"><thead><tr>' +
      ["M", "T", "W", "T", "F", "S", "S"].map(function (d) { return "<th>" + d + "</th>"; }).join("") +
      "</tr></thead><tbody></tbody></table></div>" +
      '<div class="hz-key"><span><i style="background:#c62828"></i>Red, act on the day</span>' +
      '<span><i style="background:#e0a030"></i>Amber, prepare</span><span><i style="background:#3f8a40"></i>Green, noted</span></div>' +
      '<div class="hz-foot"><span class="hz-count">Loading dates</span><a class="gc-open" href="' + esc(url) + '">Open &rsaquo;</a></div></div>';
    sec.querySelector(".gc-cards").appendChild(el);

    var tip = document.createElement("div");
    tip.className = "gc-hztip";
    tip.setAttribute("role", "tooltip");
    document.body.appendChild(tip);

    var today = new Date(), view = new Date(today.getFullYear(), today.getMonth(), 1);
    var byDay = {}, undated = {}, minM = ymd(view).slice(0, 7), maxM = minM;

    function monthUrl() { return url + "?view=month&month=" + ymd(view).slice(0, 7); }

    function draw() {
      var y = view.getFullYear(), m = view.getMonth(), key = ymd(view).slice(0, 7);
      el.querySelector(".hz-top b").innerHTML = esc(MONTHS[m]) + "<small>" + y + "</small>";
      el.querySelector('[data-step="-1"]').disabled = key <= minM;
      el.querySelector('[data-step="1"]').disabled = key >= maxM;
      var first = new Date(y, m, 1);
      var start = new Date(y, m, 1 - ((first.getDay() + 6) % 7));
      var rows = "", n = 0, t = ymd(today);
      for (var w = 0; w < 6; w++) {
        rows += "<tr>";
        for (var i = 0; i < 7; i++) {
          var d = new Date(start.getFullYear(), start.getMonth(), start.getDate() + w * 7 + i), k = ymd(d);
          if (d.getMonth() !== m) { rows += '<td class="out">' + d.getDate() + "</td>"; continue; }
          var its = byDay[k] || [], top = "";
          its.forEach(function (x) { if (!top || RANK[x.rag] > RANK[top]) top = x.rag; });
          n += its.length;
          var cls = (k === t ? "today " : "") + (its.length ? "has " + top : "");
          var label = its.length
            ? d.getDate() + " " + MONTHS[m] + ". " + its.map(function (x) { return RAGW[x.rag] + ", " + x.title; }).join(". ")
            : "";
          rows += '<td class="' + cls + '"' +
            (its.length ? ' data-day="' + k + '" tabindex="0" aria-label="' + esc(label) + '"' : "") + ">" + d.getDate() + "</td>";
        }
        rows += "</tr>";
      }
      el.querySelector("tbody").innerHTML = rows;
      var u = (undated[key] || []).length;
      el.querySelector(".hz-count").textContent = n + " dated item" + (n === 1 ? "" : "s") + " this month" +
        (u ? ", plus " + u + " with no fixed day" : "");
    }

    function showTip(td) {
      var its = byDay[td.getAttribute("data-day")] || [];
      if (!its.length) return;
      var d = new Date(td.getAttribute("data-day") + "T12:00:00");
      tip.innerHTML = "<b>" + d.getDate() + " " + MONTHS[d.getMonth()] + "</b>" + its.map(function (x) {
        return '<div><span class="w ' + x.rag + '">' + RAGW[x.rag] + "</span>" + (x.time ? esc(x.time) + " " : "") + esc(x.title) + "</div>";
      }).join("");
      tip.style.display = "block";
      var r = td.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
      var left = Math.min(Math.max(8, r.left + r.width / 2 - tw / 2), window.innerWidth - tw - 8);
      var top = r.top - th - 8 < 8 ? r.bottom + 8 : r.top - th - 8;
      tip.style.left = left + "px";
      tip.style.top = top + "px";
    }
    function hideTip() { tip.style.display = "none"; }

    el.addEventListener("mouseover", function (e) {
      var td = e.target.closest("td[data-day]");
      if (td) showTip(td); else hideTip();
    });
    el.addEventListener("mouseleave", hideTip);
    el.addEventListener("focusin", function (e) { var td = e.target.closest("td[data-day]"); if (td) showTip(td); });
    el.addEventListener("focusout", hideTip);
    window.addEventListener("scroll", hideTip, { passive: true });
    el.addEventListener("click", function (e) {
      var nav = e.target.closest(".hz-nav");
      if (nav) {
        view = new Date(view.getFullYear(), view.getMonth() + (+nav.getAttribute("data-step")), 1);
        hideTip();
        draw();
        return;
      }
      if (e.target.closest("a")) return;
      window.location.href = monthUrl();
    });
    el.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.closest("td[data-day]")) window.location.href = monthUrl();
    });

    draw();
    fetch(p.path.replace(/index\.html$/, "") + "horizon.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (h) {
        h.items.forEach(function (x) {
          if (x.routine) return;
          var mk = x.date.slice(0, 7);
          if (x.date_label) { (undated[mk] = undated[mk] || []).push(x); return; }
          (byDay[x.date] = byDay[x.date] || []).push(x);
          if (mk > maxM) maxM = mk;
        });
        draw();
      })
      .catch(function () { el.querySelector(".hz-count").textContent = "Dates could not be loaded"; });
    return sec;
  }

  // The widget takes the height of a standard product card, measured live, so it
  // stays the same size as the squares around it whatever the font or width.
  function syncWidgetHeight() {
    var w = document.querySelector(".gc-hzw");
    if (!w) return;
    var ref = null;
    document.querySelectorAll(".gc-card:not(.gc-hzw):not(.gc-detail-open)").forEach(function (c) {
      if (!ref && c.offsetHeight) ref = c;
    });
    w.style.height = ref && window.innerWidth > 700 ? ref.offsetHeight + "px" : "";
  }

  // One Hide/Show button folds the schedule and the Horizon Calendar together,
  // leaving both headings in place. State remembered per browser.
  function wireTopRow(row) {
    var btn = row.querySelector(".gc-sched-toggle");
    if (!btn) return;
    var setState = function (collapsed) {
      row.classList.toggle("gc-row-collapsed", collapsed);
      btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
      btn.querySelector(".lbl").textContent = collapsed ? "Show" : "Hide";
    };
    var saved = null;
    try { saved = localStorage.getItem(TOPROW_KEY); } catch (e) {}
    setState(saved === "1");
    btn.addEventListener("click", function () {
      var collapsed = !row.classList.contains("gc-row-collapsed");
      setState(collapsed);
      try { localStorage.setItem(TOPROW_KEY, collapsed ? "1" : "0"); } catch (e) {}
      if (!collapsed) syncWidgetHeight();
    });
  }

  // "Last updated" line in the hero, from catalog.updated_at (ISO date-time).
  function lastUpdated(cat) {
    var el = document.getElementById("gc-updated");
    if (!el) return;
    var d = cat.updated_at ? new Date(cat.updated_at) : null;
    if (d && !isNaN(d)) {
      // Always UK time, whatever the reader's own time zone.
      var f = function (o) { return d.toLocaleString("en-GB", Object.assign({ timeZone: "Europe/London" }, o)); };
      el.textContent = "Last updated " + f({ day: "numeric", month: "long", year: "numeric" }) +
        " at " + f({ hour: "2-digit", minute: "2-digit", hour12: false });
      el.setAttribute("datetime", cat.updated_at);
    } else if (cat.updated) {
      el.textContent = "Last updated " + cat.updated;
    }
  }

  function render(cat) {
    lastUpdated(cat);
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

    // Top row: the publication schedule (next six months) beside the Horizon
    // Calendar widget, which is its permanent home on the landing page.
    var widgets = cat.products.filter(function (p) { return p.widget === "horizon"; });
    cat.products = cat.products.filter(function (p) { return !p.widget; });
    if (cat.schedule || widgets.length) {
      var row = document.createElement("div");
      row.className = "gc-toprow";
      if (cat.schedule) row.appendChild(scheduleSection(cat.schedule));
      if (widgets.length) row.appendChild(horizonSection(widgets[0]));
      root.appendChild(row);
      wireTopRow(row);
    }

    // Pinned section — the latest edition of each recurring update series.
    // Pinned products appear here ONLY (not repeated in their topic section).
    var pinnedProds = cat.products.filter(function (p) { return p.pinned; });
    if (pinnedProds.length) {
      var psec = topicSection("Pinned", "The latest updates — new editions land here first", "topic-pinned");
      psec.classList.add("gc-topic-pinned");
      var pgrid = psec.querySelector(".gc-cards");
      pinnedProds.forEach(function (p) { pgrid.appendChild(card(p, { inPinned: true })); });
      setCount(psec, pinnedProds.length);
      root.appendChild(psec);
      wireDetail(psec);
      truncate(psec, CARD_LIMIT);
    }

    // Featured section — recently published ad hoc analysis (featured flag).
    var featuredProds = cat.products.filter(function (p) { return p.featured && !p.pinned && !p._archived; });
    if (featuredProds.length) {
      var fsec = topicSection("Featured", "Recently published ad hoc analysis", "topic-featured");
      fsec.classList.add("gc-topic-featured");
      var fgrid = fsec.querySelector(".gc-cards");
      featuredProds.forEach(function (p) { fgrid.appendChild(card(p, { inPinned: true })); });
      setCount(fsec, featuredProds.length);
      root.appendChild(fsec);
      wireDetail(fsec);
      truncate(fsec, CARD_LIMIT);
    }

    cat.topics.forEach(function (t) {
      var prods = cat.products.filter(function (p) { return p.topic === t.name && !p.pinned && !p.featured && !p._archived; });
      if (!prods.length) return;
      var sec = topicSection(t.name, t.note, "topic-" + t.name.toLowerCase().replace(/[^a-z]+/g, "-"));
      var grid = sec.querySelector(".gc-cards");
      prods.forEach(function (p) { grid.appendChild(card(p)); });
      setCount(sec, prods.length);
      root.appendChild(sec);
      wireDetail(sec);
      truncate(sec, CARD_LIMIT);
    });

    // Series archives at the foot of the page — collapsed by default, because
    // they are a back catalogue rather than something to browse on arrival.
    SERIES_ORDER.forEach(function (s) {
      var arr = (bySeries[s] || []).filter(function (p) { return p._archived; });
      if (!arr.length) return;
      var sec = topicSection(SERIES[s].archive, SERIES[s].note, "series-" + s, "edition");
      sec.classList.add("gc-topic-archive");
      var grid = sec.querySelector(".gc-cards");
      arr.forEach(function (p) { grid.appendChild(card(p)); });
      setCount(sec, arr.length);
      root.appendChild(sec);
      wireDetail(sec);
      collapsible(sec, true);
    });

    var nr = document.createElement("div");
    nr.id = "gc-noresults"; nr.className = "gc-noresults"; nr.style.display = "none";
    nr.textContent = "No products match your search. Try fewer or different words.";
    root.appendChild(nr);

    wireSearch();
    var sw = document.querySelector(".gc-searchwrap");
    if (sw && !sw.querySelector("svg")) sw.insertAdjacentHTML("afterbegin", ICON_SEARCH);

    syncWidgetHeight();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { remeasure(); syncWidgetHeight(); });
    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(function () { remeasure(); syncWidgetHeight(); }, 180);
    });
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
