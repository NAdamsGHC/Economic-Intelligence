"""Build the three transparency pages.

    transparency/index.html            from statement.body.html
    transparency/runbook.html          from runbook.body.html
    transparency/performance-log.html  generated from transparency/performance-log.json

Each page gets the same masthead, menu and footer. Run after any change to a
body file or to the log, then run check_voice.py over the three outputs.

    python build/transparency/build.py
"""
import datetime as dt
import html
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "transparency"
sys.path.insert(0, str(HERE))
from insert_menu import insert  # noqa: E402

CSS_VERSION = "20261016"

SHELL = """<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &middot; Gateshead Economic Intelligence</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/ei.css?v={css}">
</head>
<body>

<header class="gc-masthead">
  <div class="gc-inner">
    <a class="gc-logo" href="../index.html">
      <span class="mark">G</span>
      <span class="word">Gateshead<small>Economic Intelligence</small></span>
    </a>
    <span class="spacer"></span>
    <a class="gc-home" href="../index.html">&lsaquo; All products</a>
  </div>
</header>

<main class="tp-wrap">
{body}
</main>

<footer class="gc-footer">
  <div class="gc-inner">
    Part of the <a href="../index.html">Gateshead Economic Intelligence Catalogue</a> &middot; an independent, unofficial project &middot; <a href="index.html">Transparency Statement</a> &middot; <a href="runbook.html">Regular Reports Runbook</a> &middot; <a href="performance-log.html">Performance Log</a>
  </div>
</footer>

</body>
</html>
"""


def esc(s):
    return html.escape(s, quote=False)


def nice_date(s):
    if len(s) == 7:
        return dt.datetime.strptime(s, "%Y-%m").strftime("%B %Y")
    d = dt.date.fromisoformat(s)
    return f"{d.day} {d.strftime('%B %Y')}"


def page(name, title, description, body):
    text = SHELL.format(title=esc(title), description=html.escape(description),
                        css=CSS_VERSION, body=body.strip())
    text, _ = insert(text, "../")
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print("wrote transparency/" + name)


STAGE_CLASS = {"Published": "pub", "Draft": "draft", "Caught by checks": "caught"}


def performance_log():
    log = json.loads((OUT / "performance-log.json").read_text(encoding="utf-8"))
    entries = sorted(log["entries"], key=lambda e: (e["found"], e["id"]), reverse=True)
    for e in entries:
        assert e["stage"] in log["stages"], e["id"]
        assert e["type"] in log["types"], e["id"]
        assert e["function"] in log["functions"], e["id"]
        assert e["status"] in ("Open", "Closed"), e["id"]

    count = lambda **kw: sum(all(e[k] == v for k, v in kw.items()) for e in entries)
    out = []
    out.append(f"""<p class="tp-kicker">Transparency</p>
<h1>Performance Log</h1>
<p class="tp-byline">Nathaniel Adams, Economic Intelligence Analyst &middot; last updated {nice_date(log['updated'])}</p>
<p class="tp-lede">Every material error found in our work, how it was found and what changed as a result. Errors caught before publication sit alongside those that reached a published product, because our checks are only worth something if we can show what they catch.</p>
""")
    out.append("""<h2>How the Log Works</h2>
<ul>
<li>An error is logged if it would change a figure, a finding or what a reader takes from a product. Typing and style fixes are not logged</li>
<li>Each entry records where the error got to, what kind of error it was, which part of our process produced it, how it was found and what we changed</li>
<li>An error that reached a published product is also corrected in that product or in the next edition, and the correction says so on its face</li>
<li>Entries are never rewritten after the event. The only later change is closing an open entry once its fix is made and checked</li>
<li>Two errors of the same kind from the same part of the process within 90 days put that part on probation. Nathaniel then reviews every output from it line by line until it has produced three products in a row with nothing logged</li>
</ul>
""")
    rows = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in log["stages"].items())
    out.append(f"""<div class="tp-scroll"><table class="tp-table"><thead><tr><th>Stage</th><th>Meaning</th></tr></thead><tbody>{rows}</tbody></table></div>
""")

    out.append("<h2>Probation</h2>")
    if not log["probation"]:
        out.append("<p>No part of the process is on probation.</p>")
    else:
        prow = "".join(
            f"<tr><td>{esc(p['function'])}</td><td>{nice_date(p['since'])}</td><td>{esc(p['reason'])}</td><td>{esc(p['status'])}</td></tr>"
            for p in log["probation"])
        out.append(f'<div class="tp-scroll"><table class="tp-table"><thead><tr><th>Function</th><th>Since</th><th>Reason</th><th>Status</th></tr></thead><tbody>{prow}</tbody></table></div>')

    out.append(f"""<h2>Summary</h2>
<div class="tp-tiles">
<div><b>{len(entries)}</b><span>errors logged</span></div>
<div><b>{count(stage='Published')}</b><span>reached a published product</span></div>
<div><b>{count(stage='Draft')}</b><span>reached Nathaniel and stopped there</span></div>
<div><b>{count(stage='Caught by checks')}</b><span>caught by our own checks first</span></div>
<div><b>{count(status='Open')}</b><span>still open</span></div>
</div>
""")
    funcs = [f for f in log["functions"] if any(e["function"] == f for e in entries)]
    frows = "".join(
        f"<tr><td>{esc(f)}</td><td>{esc(log['functions'][f])}</td>"
        + "".join(f"<td>{count(function=f, stage=s)}</td>" for s in log["stages"])
        + "</tr>" for f in funcs)
    out.append(f"""<h3>Errors by Function</h3>
<div class="tp-scroll"><table class="tp-table"><thead><tr><th>Function</th><th>What it does</th><th>Published</th><th>Draft</th><th>Caught by checks</th></tr></thead><tbody>{frows}</tbody></table></div>
""")

    out.append("<h2>Entries</h2>")
    out.append(f"<p>Newest first. Entries found before {nice_date(log['rules_from'])} were reconstructed from our working records when the log started, so they are as complete as those records allow. Probation counts errors from {nice_date(log['rules_from'])} onward.</p>")
    for e in entries:
        cls = STAGE_CLASS[e["stage"]]
        rule = f'<dt>Rule</dt><dd>{esc(e["rule"])} in our standing rules</dd>' if e.get("rule") else ""
        out.append(f"""<article class="tp-entry {cls}" id="{e['id']}">
<div class="meta"><b>{e['id']}</b><span>Found {nice_date(e['found'])}</span><span class="tp-tag {cls}">{esc(e['stage'])}</span><span class="tp-tag {e['status'].lower()}">{e['status']}</span></div>
<h3>{esc(e['product'])}</h3>
<dl>
<dt>What</dt><dd>{esc(e['what'])}</dd>
<dt>Kind</dt><dd>{esc(e['type'])}</dd>
<dt>Function</dt><dd>{esc(e['function'])}</dd>
<dt>Found by</dt><dd>{esc(e['found_by'])}</dd>
<dt>What changed</dt><dd>{esc(e['fix'])}</dd>
{rule}</dl>
</article>""")
    page("performance-log.html", "Performance Log",
         "Every material error found in the Gateshead Economic Intelligence work, how it was found and what changed as a result.",
         "\n".join(out))


def main():
    page("index.html", "Transparency Statement",
         "How the Gateshead Economic Intelligence site is produced, who is accountable, the AI team behind it, the principles it works to and the guidance it follows.",
         (HERE / "statement.body.html").read_text(encoding="utf-8"))
    page("runbook.html", "Regular Reports Runbook",
         "Step-by-step instructions a person can follow to produce the four regular reports on the Gateshead Economic Intelligence site without AI tools.",
         (HERE / "runbook.body.html").read_text(encoding="utf-8"))
    performance_log()


if __name__ == "__main__":
    main()
