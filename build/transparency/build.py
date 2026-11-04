"""Build the transparency and best-practice pages.

    transparency/index.html                   from statement.body.html
    transparency/runbook.html                 from runbook.body.html
    transparency/performance-log.html         generated from transparency/performance-log.json
    transparency/library-evals.html           generated from transparency/library-evals.json
    transparency/best-practice.html           from best-practice.body.html
    transparency/best-practice-councils.html  from best-practice-councils.body.html

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
    Part of the <a href="../index.html">Gateshead Economic Intelligence Catalogue</a> &middot; an independent, unofficial project &middot; <a href="index.html">Transparency Statement</a> &middot; <a href="runbook.html">Regular Reports Runbook</a> &middot; <a href="performance-log.html">Performance Log</a> &middot; <a href="library-evals.html">Document Library Evaluation</a> &middot; <a href="best-practice.html">General Best Practice</a> &middot; <a href="best-practice-councils.html">Best Practice in Local Authorities</a>
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
<p class="tp-byline">Last updated {nice_date(log['updated'])}</p>
<p class="tp-lede">Every material error found in our work, how it was found and what changed as a result. Errors caught before publication sit alongside those that reached a published product, because our checks are only worth something if we can show what they catch.</p>
""")
    out.append("""<h2>How the Log Works</h2>
<ul>
<li>An error is logged if it would change a figure, a finding or what a reader takes from a product. Typing and style fixes are not logged</li>
<li>Each entry records where the error got to, what kind of error it was, which part of our process produced it, how it was found and what we changed</li>
<li>An error that reached a published product is also corrected in that product or in the next edition, and the correction says so on its face</li>
<li>Entries are never rewritten after the event. The only later change is closing an open entry once its fix is made and checked</li>
<li>Two errors of the same kind from the same part of the process within 90 days put that part on probation. The site owner then reviews every output from it line by line until it has produced three products in a row with nothing logged</li>
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
<div><b>{count(stage='Draft')}</b><span>reached the site owner and stopped there</span></div>
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


def library_evals():
    d = json.loads((OUT / "library-evals.json").read_text(encoding="utf-8"))
    c, t, lib = d["current"], d["test"], d["library"]
    frac = lambda p: f"{p[0]} of {p[1]}"  # noqa: E731
    out = [f"""<p class="tp-kicker">Transparency</p>
<h1>Document Library Evaluation</h1>
<p class="tp-byline">Last updated {nice_date(d['updated'])}</p>
<p class="tp-lede">The AI team keeps a searchable library of published documents, such as government guidance, strategies and evidence reviews, so it can find the right passage instead of relying on memory. This page reports how well that search works, measured by a fixed test that is re-run after every change.</p>
""",
           f"""<h2>What the Library Does</h2>
<ul>
<li>Whole documents are split into passages and indexed two ways, by the words they contain and by what they mean. A second model then reads the question alongside each candidate passage and puts the best answers first</li>
<li>Every passage keeps its document, page, edition and date, so anything the team takes from it can be cited and checked</li>
<li>When a newer edition of a document arrives, the older one is marked superseded and drops out of normal searches</li>
<li>Figures found in a document are treated as leads only. They are always re-pulled from the official source before they are quoted</li>
<li>It holds published documents only, not our own products, and everything runs locally at no cost</li>
</ul>
<p>The library holds {lib['documents']} documents ({lib['current']} current and {lib['superseded']} superseded), split into {lib['passages']:,} passages.</p>
""",
           f"""<h2>How the Test Works</h2>
<p>The test is a set of {t['answerable'] + t['supersession'] + t['no_answer']} questions, each worded differently from the document so that it tests meaning and not just matching words. Questions are added whenever documents are, and the settings are re-tested each time.</p>
<ul>
<li><b>{t['answerable']} answerable questions</b> – each has an answer key naming the document and page that answers it. Where the answer is a value, the passage must contain the value itself, so a passage from the right page that has lost the number does not count</li>
<li><b>{t['supersession']} edition questions</b> – the current edition must be found, and the older edition must be recorded as superseded by it</li>
<li><b>{t['no_answer']} questions the library cannot answer</b> – the right result is a flag saying the library probably does not hold the answer</li>
</ul>
<p>The answer keys were found by searching the original PDFs directly, not through the library, and were then checked page by page in a separate verification pass. That pass found six wrong or incomplete keys, which were corrected (E-2026-47).</p>
""",
           f"""<h2>Current Scores</h2>
<div class="tp-tiles">
<div><b>{frac(c['top8'])}</b><span>answerable questions with a correct passage in the top eight, the results the team reads</span></div>
<div><b>{frac(c['top5'])}</b><span>with a correct passage in the top five</span></div>
<div><b>{frac(c['top1'])}</b><span>with a correct passage first</span></div>
<div><b>{frac(c['supersession'])}</b><span>edition questions passed</span></div>
<div><b>{frac(c['no_answer'])}</b><span>unanswerable questions flagged</span></div>
<div><b>{frac(c['false_missing'])}</b><span>real answers wrongly flagged as missing</span></div>
</div>
<p>Mean reciprocal rank, which averages how near the top the first correct passage sits (1 means always first), is {c['mrr']}. Wrongly telling the team an answer is missing is the more harmful mistake, because it stops the search, so the flag is set to fire only when two separate measures agree.</p>
"""]
    rows = "".join(
        f"<tr><td>{r['n']}</td><td>{esc(r['change'])}</td><td>{r['top5']} of {r.get('of', t['answerable'])}</td>"
        f"<td>{r['top1']} of {r.get('of', t['answerable'])}</td><td>{r['mrr']}</td><td>{esc(r['decision'])}</td></tr>"
        for r in d["runs"])
    first = [r["n"] for r in d["runs"] if r["key"] == "first"]
    grown = [r["n"] for r in d["runs"] if r.get("of", t["answerable"]) != d["runs"][0].get("of", t["answerable"])]
    grown_note = (f" From run {grown[0]} the library and the test are larger, so those scores are out of a larger total and"
                  " are not directly comparable with earlier runs either. Adding documents is not a setting, so a fall"
                  " it causes is recorded, not reverted.") if grown else ""
    out.append(f"""<h2>Score History</h2>
<p>Each change to a setting is tested against the previous score, and one that lowers it is reverted. Runs {first[0]} to {first[-1]} used the first answer key, before verification corrected it, so their scores are not directly comparable with the later runs.{grown_note}</p>
<div class="tp-scroll"><table class="tp-table plain"><thead><tr><th>Run</th><th>Change tested</th><th>Correct in top five</th><th>Correct first</th><th>Mean reciprocal rank</th><th>Decision</th></tr></thead><tbody>{rows}</tbody></table></div>
""")
    links = ", ".join(f'<a href="performance-log.html#{e}">{e}</a>' for e in d["log_entries"])
    out.append(f"""<h2>What the Test Does Not Show</h2>
<ul>
<li>It tests whether the right passage is found, not whether a written answer built from it is correct. Answers are checked separately by the verification step before any product ships</li>
<li>The settings were chosen using this same set of questions, so the scores are likely to flatter the library a little until new questions confirm them</li>
<li>The not-in-library flag rests on seven questions, which is too few to rely on. The team is told to read the passages every time, whatever the flag says</li>
<li>Tables are the weakest point. The second model reads flattened tables badly, so passages it marks down but the first-stage search ranked highly are returned as extra results</li>
</ul>
<h2>Errors Found While Building It</h2>
<p>Five errors were found and fixed during the build, and all are recorded in the Performance Log ({links}).</p>
<h2>Next Steps</h2>
<ul>
<li>Add test questions written by the site owner, which reflect real use better than questions drafted from the documents</li>
<li>Re-run the test at every quarterly library review and after every large batch of new documents, and add each run to this page</li>
</ul>
""")
    page("library-evals.html", "Document Library Evaluation",
         "How well the Gateshead Economic Intelligence team's document library finds the right passage, measured by a fixed test re-run after every change.",
         "\n".join(out))


def main():
    page("index.html", "Transparency Statement",
         "How the Gateshead Economic Intelligence site is produced, who is accountable, the AI team behind it, the principles it works to and the guidance it follows.",
         (HERE / "statement.body.html").read_text(encoding="utf-8"))
    page("runbook.html", "Regular Reports Runbook",
         "Step-by-step instructions a person can follow to produce the four regular reports on the Gateshead Economic Intelligence site without AI tools.",
         (HERE / "runbook.body.html").read_text(encoding="utf-8"))
    performance_log()
    library_evals()
    page("best-practice.html", "General Best Practice",
         "A short guide to running analytical work with AI agents, covering accountability, written rules, memory, guardrails, checks and tracking.",
         (HERE / "best-practice.body.html").read_text(encoding="utf-8"))
    page("best-practice-councils.html", "Best Practice in Local Authorities",
         "What changes when a council uses AI agents for analysis, covering governance, data protection, public sector standards, openness and continuity.",
         (HERE / "best-practice-councils.body.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
