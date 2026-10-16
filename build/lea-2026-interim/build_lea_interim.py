"""Build the web edition of the Interim Local Economic Assessment 2026.

    economy/lea-2026-interim.html        the report as a page in the house skin
    economy/lea-2026-interim/fig-NN.png  its figures, extracted from the Word file

The Word file is the master. The page is generated from it with mammoth, so
any later correction is made in Word and this script is run again.

    python build/lea-2026-interim/build_lea_interim.py "<path to the .docx>"
"""
import html
import pathlib
import re
import shutil
import sys

import mammoth

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "build" / "transparency"))
from insert_menu import insert  # noqa: E402

CSS_VERSION = "20261016"
SLUG = "lea-2026-interim"
OUT_PAGE = ROOT / "economy" / f"{SLUG}.html"
OUT_DIR = ROOT / "economy" / SLUG

TITLE = "Interim Local Economic Assessment 2026"
DESCRIPTION = ("The interim edition of the Gateshead Local Economic Assessment 2026, "
               "October 2026: business, productivity, population and labour supply, "
               "employment demand, infrastructure, place and policy implications.")

# Word paragraph styles -> HTML. The cover and the Word contents page are
# dropped: the page builds its own header and contents list from the headings.
STYLE_MAP = """
p[style-name='LEA Cover Title'] => !
p[style-name='LEA Cover Sub'] => !
p[style-name='LEA Cover Meta'] => !
p[style-name='toc 1'] => !
p[style-name='toc 2'] => !
p[style-name='Title'] => p.lea-annex:fresh
p[style-name='LEA Box'] => div.tp-box > p:fresh
p[style-name='LEA Standfirst'] => p.tp-lede:fresh
p[style-name='List Bullet'] => ul > li:fresh
p[style-name='LEA Caption'] => p.lea-caption:fresh
p[style-name='LEA Review Block'] => p.lea-block:fresh
p[style-name='LEA Source'] => p.lea-source:fresh
p[style-name='Source Line'] => p.lea-source:fresh
"""

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
<style>
.lea-wrap{{max-width:960px;}}
.lea-wrap h1.lea-ch{{font-size:24px;color:var(--gc-blue-dark);border-bottom:3px solid var(--gc-blue);padding-bottom:6px;margin:44px 0 14px;}}
.lea-wrap h2{{font-size:19px;}}
.lea-wrap img{{max-width:100%;height:auto;display:block;margin:10px auto;}}
.lea-caption,.lea-block.cap{{font-weight:700;color:var(--gc-blue-dark);margin:18px 0 6px !important;}}
.lea-source{{font-size:12.5px;color:#5d6b7a;}}
.lea-annex{{font-size:13px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:#6a7784;margin-top:40px !important;}}
.lea-wrap .tp-scroll table{{width:100%;border-collapse:collapse;font-size:13px;}}
.lea-wrap .tp-scroll td,.lea-wrap .tp-scroll th{{border:1px solid var(--gc-line);padding:6px 8px;vertical-align:top;}}
.lea-wrap .tp-scroll th{{text-align:left;background:var(--gc-panel);color:var(--gc-blue-dark);font-weight:700;}}
.lea-wrap .tp-scroll td p{{margin:0;}}
.lea-toc ol{{list-style:none;margin-left:0;}}
.lea-toc ol ol{{margin:2px 0 4px 18px;font-size:13px;}}
.lea-top{{font-size:12.5px;}}
@media print{{.gc-masthead,.gc-footer,.lea-toc,.lea-top{{display:none;}}}}
</style>
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

<main class="tp-wrap lea-wrap">
<p class="tp-kicker">Economy &middot; Local Economic Assessment</p>
<h1 id="top">{title}</h1>
<p class="tp-byline">Interim edition &middot; October 2026</p>

<nav class="tp-toc lea-toc" aria-label="Contents">
<b>Contents</b>
{toc}
</nav>

{body}
</main>

<footer class="gc-footer">
  <div class="gc-inner">
    Part of the <a href="../index.html">Gateshead Economic Intelligence Catalogue</a> &middot; an independent, unofficial project &middot; <a href="../transparency/index.html">Transparency Statement</a>
  </div>
</footer>

</body>
</html>
"""


def slugify(text, seen):
    s = re.sub(r"[^a-z0-9]+", "-", html.unescape(text).lower()).strip("-")[:60] or "section"
    base, n = s, 2
    while s in seen:
        s, n = f"{base}-{n}", n + 1
    seen.add(s)
    return s


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def main(docx_path):
    docx_path = pathlib.Path(docx_path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    counter = {"n": 0}

    def save_image(image):
        counter["n"] += 1
        # The site is independent of the council, so the cover logo is not published.
        if (image.alt_text or "").startswith("Gateshead Council logo"):
            return {"src": "", "class": "lea-drop"}
        ext ={"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif"}.get(image.content_type, "png")
        name = f"fig-{counter['n']:02d}.{ext}"
        with image.open() as src, open(OUT_DIR / name, "wb") as dst:
            shutil.copyfileobj(src, dst)
        return {"src": f"{SLUG}/{name}", "alt": image.alt_text or ""}

    with open(docx_path, "rb") as f:
        result = mammoth.convert_to_html(
            f, style_map=STYLE_MAP, convert_image=mammoth.images.img_element(save_image))
    body = result.value

    # The site is not a council publication: drop the logo and credit the
    # report's own models and forecasts as "own" rather than to the council.
    body = re.sub(r'<img[^>]*class="lea-drop"[^>]*/>', "", body)
    body = re.sub(r"Gateshead Council (forecasts?|panel model|total GVA forecast|group forecasts)",
                  r"own \1", body)

    # Empty paragraphs and anchors left by Word bookmarks.
    body = re.sub(r'<a id="[^"]*"></a>', "", body)
    body = re.sub(r"<p( class=\"[^\"]*\")?>\s*</p>", "", body)
    # The Word contents page's own heading (its entries are already dropped).
    body = body.replace("<p><strong>Contents</strong></p>", "", 1)

    # Captions: review-block paragraphs that name a table or figure.
    body = re.sub(r'<p class="lea-block">(\s*(?:Table|Figure) \d)', r'<p class="lea-block cap">\1', body)
    # Plain paragraphs that are Table/Figure captions (a few use Normal style).
    body = re.sub(r"<p>((?:Table|Figure) \d+: [^<]{0,160})</p>", r'<p class="lea-caption">\1</p>', body)

    # Tables scroll sideways on a phone rather than widening the page.
    body = body.replace("<table>", '<div class="tp-scroll"><table>').replace("</table>", "</table></div>")

    # Heading ids and a two-level contents list (chapters, then sections).
    seen, toc = set(), []

    def head(m):
        level, inner = m.group(1), m.group(2)
        text = strip_tags(inner)
        hid = slugify(text, seen)
        if level == "1":
            toc.append([text, hid, []])
            return f'<h1 class="lea-ch" id="{hid}">{inner}</h1>'
        if toc:
            toc[-1][2].append((text, hid))
        return f'<h2 id="{hid}">{inner}</h2>'

    body = re.sub(r"<h([12])>(.*?)</h\1>", head, body, flags=re.S)
    body = re.sub(r"(<h1 class=\"lea-ch\")", r'<p class="lea-top"><a href="#top">Back to contents</a></p>\n\1', body)

    items = []
    for text, hid, subs in toc:
        sub = "".join(f'<li><a href="#{s}">{t}</a></li>' for t, s in subs)
        items.append(f'<li><a href="#{hid}">{text}</a>' + (f"<ol>{sub}</ol>" if sub else "") + "</li>")
    toc_html = "<ol>" + "".join(items) + "</ol>"

    # Readable line breaks between block elements.
    body = re.sub(r"(</(?:p|h1|h2|ul|ol|div|table)>)", r"\1\n", body)

    page = SHELL.format(title=TITLE, description=html.escape(DESCRIPTION), css=CSS_VERSION,
                        toc=toc_html, body=body)
    page, _ = insert(page, "../")
    OUT_PAGE.write_text(page, encoding="utf-8")

    print(f"{OUT_PAGE.relative_to(ROOT)}: {len(page):,} bytes, {counter['n']} figures, "
          f"{body.count('<table')} tables, {len(toc)} chapters")
    for m in result.messages:
        if "Unrecognised" not in m.message:
            print("  mammoth:", m.message)


if __name__ == "__main__":
    main(sys.argv[1])
