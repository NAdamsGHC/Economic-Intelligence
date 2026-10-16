"""Insert or refresh the site menu (the Transparency list) in every page banner.

The snippet lives in build/transparency/menu.html. It is self-contained (its own
style and script), so it works on pages that load assets/ei.css and on the
dashboards and bulletins that carry their own inline styles.

Two banner families are handled:
  - the gc-masthead header (landing page, briefs, horizon, transparency pages):
    the menu goes at the right-hand end of the header row
  - the gcbar brand bar (dashboards, policy bulletins): the menu goes after the
    copy-link button

Re-running is safe. Anything between the <!-- gc-menu --> markers is replaced.

    python build/transparency/insert_menu.py          # dry run, lists changes
    python build/transparency/insert_menu.py --write
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNIPPET = (ROOT / "build/transparency/menu.html").read_text(encoding="utf-8").strip()
BLOCK = re.compile(r"\s*<!-- gc-menu -->.*?<!-- /gc-menu -->", re.S)

# Extra files outside the published tree that generate published pages.
TEMPLATES = {ROOT / "build/horizon/template.html": "../"}


def prefix_for(path):
    rel = path.relative_to(ROOT)
    return "" if len(rel.parts) == 1 else "../"


def insert(text, prefix):
    menu = SNIPPET.replace("{{P}}", prefix)
    text = BLOCK.sub("", text)
    m = re.search(r'<header class="gc-masthead">.*?</header>', text, re.S)
    if m:
        head = m.group(0)
        cut = head.rfind("</div>")
        new = head[:cut] + menu + "\n  " + head[cut:]
        return text[:m.start()] + new + text[m.end():], "masthead"
    m = re.search(r'class="gcbar-copy".*?</button>', text, re.S)
    if m:
        return text[:m.end()] + "\n" + menu + text[m.end():], "gcbar"
    return None, "no banner"


def main(write):
    pages = [p for p in ROOT.rglob("*.html")
             if "build" not in p.relative_to(ROOT).parts and ".git" not in p.parts]
    targets = [(p, prefix_for(p)) for p in sorted(pages)] + list(TEMPLATES.items())
    changed, skipped = 0, []
    for path, prefix in targets:
        raw = path.read_bytes()
        nl = "\r\n" if b"\r\n" in raw else "\n"
        text = raw.decode("utf-8").replace("\r\n", "\n")
        new, kind = insert(text, prefix)
        if new is None:
            skipped.append(str(path.relative_to(ROOT)))
            continue
        if new != text:
            changed += 1
            print(f"{kind:9} {path.relative_to(ROOT)}")
            if write:
                path.write_bytes(new.replace("\n", nl).encode("utf-8"))
    print(f"\n{changed} file(s) {'updated' if write else 'would change'}")
    if skipped:
        print("No banner found, left alone:")
        for s in skipped:
            print("  " + s)


if __name__ == "__main__":
    main("--write" in sys.argv)
