#!/usr/bin/env python3
"""Static site generator for the essays collection (Python stdlib only)."""

from __future__ import annotations

import html
import math
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ESSAYS_DIR = ROOT / "essays"
README_PATH = ROOT / "README.md"
STYLE_PATH = Path(__file__).resolve().parent / "style.css"
OUT_DIR = ROOT / "_site"
REPO_URL = "https://github.com/grove/essays"

SAKURA_PETAL = "M0-2.5 C-3.8-6.5 -4.2-11.5 -1.4-14 L0-12.1 L1.4-14 C4.2-11.5 3.8-6.5 0-2.5Z"

SAKURA_SVG = (
    '<svg class="sakura-mark" width="22" height="22" viewBox="0 0 32 32" '
    'fill="currentColor" aria-hidden="true">'
    '<g transform="translate(16 16)">'
    + "".join(
        f'<path d="{SAKURA_PETAL}"' + (f' transform="rotate({deg})"' if deg else "") + "/>"
        for deg in (0, 72, 144, 216, 288)
    )
    + '<circle r="2.2" fill="var(--accent)"/>'
    "</g></svg>"
)

FAVICON_DATA = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Cg transform='translate(16 16)' fill='%23e7b2bf'%3E"
    + "".join(
        "%3Cpath d='M0-2.5C-3.8-6.5-4.2-11.5-1.4-14L0-12.1L1.4-14C4.2-11.5 3.8-6.5 0-2.5Z'"
        + (f" transform='rotate({deg})'" if deg else "")
        + "/%3E"
        for deg in (0, 72, 144, 216, 288)
    )
    + "%3Ccircle r='2.2' fill='%23a94f67'/%3E%3C/g%3E%3C/svg%3E"
)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def strip_markdown(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_]+", "", text)
    return " ".join(text.split())


def reading_minutes(text: str) -> int:
    words = len(re.findall(r"\b\w+(?:['’]\w+)*\b", strip_markdown(text)))
    return max(1, math.ceil(words / 230))


# ponytail: stdlib Markdown subset (headings, lists, blockquotes, fences, inline
# code/bold/italic/links with balanced parens); swap in python-markdown or pandoc
# if future essays need tables, footnotes, or nested lists.
def render_inline(text: str, resolve_link) -> str:
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "`":
            end = text.find("`", i + 1)
            if end != -1:
                out.append(f"<code>{html.escape(text[i + 1 : end])}</code>")
                i = end + 1
                continue
        elif ch == "[":
            close_bracket = text.find("]", i + 1)
            if close_bracket != -1 and close_bracket + 1 < n and text[close_bracket + 1] == "(":
                depth = 1
                j = close_bracket + 2
                while j < n and depth > 0:
                    if text[j] == "(":
                        depth += 1
                    elif text[j] == ")":
                        depth -= 1
                    j += 1
                if depth == 0:
                    label = render_inline(text[i + 1 : close_bracket], resolve_link)
                    href = resolve_link(text[close_bracket + 2 : j - 1].strip())
                    out.append(f'<a href="{html.escape(href, quote=True)}">{label}</a>')
                    i = j
                    continue
        elif text.startswith("**", i):
            end = text.find("**", i + 2)
            if end != -1 and end > i + 2:
                out.append(f"<strong>{render_inline(text[i + 2 : end], resolve_link)}</strong>")
                i = end + 2
                continue
        elif ch == "*":
            end = text.find("*", i + 1)
            if end != -1 and end > i + 1 and not text[i + 1].isspace():
                out.append(f"<em>{render_inline(text[i + 1 : end], resolve_link)}</em>")
                i = end + 1
                continue
        out.append(html.escape(ch))
        i += 1
    return "".join(out)


def render_markdown(md: str, resolve_link) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    blocks: list[str] = []
    seen_ids: dict[str, int] = {}
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            code_lines: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1
            blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            raw = heading.group(2).strip()
            base_id = slugify(strip_markdown(raw))
            count = seen_ids.get(base_id, 0)
            seen_ids[base_id] = count + 1
            hid = base_id if count == 0 else f"{base_id}-{count + 1}"
            blocks.append(f'<h{level} id="{hid}">{render_inline(raw, resolve_link)}</h{level}>')
            i += 1
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            blocks.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < n and lines[i].strip().startswith(">"):
                q = lines[i].lstrip()[1:]
                quote_lines.append(q[1:] if q.startswith(" ") else q)
                i += 1
            inner = render_markdown("\n".join(quote_lines), resolve_link)
            blocks.append(f"<blockquote>\n{inner}\n</blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip(), count=1))
                i += 1
            rendered = "\n".join(f"<li>{render_inline(it, resolve_link)}</li>" for it in items)
            blocks.append(f"<ul>\n{rendered}\n</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip(), count=1))
                i += 1
            rendered = "\n".join(f"<li>{render_inline(it, resolve_link)}</li>" for it in items)
            blocks.append(f"<ol>\n{rendered}\n</ol>")
            continue

        para_lines: list[str] = []
        while i < n:
            cur = lines[i].strip()
            if (
                not cur
                or cur.startswith("```")
                or cur.startswith(">")
                or re.match(r"^(#{1,6})\s+", cur)
                or re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", cur)
                or re.match(r"^([-*]|\d+\.)\s+", cur)
            ):
                break
            para_lines.append(cur)
            i += 1
        blocks.append(f"<p>{render_inline(' '.join(para_lines), resolve_link)}</p>")

    return "\n".join(blocks)


def split_header(md: str) -> tuple[str, str | None, str]:
    """Extract leading '# Title', optional '*Subtitle*', and remaining body."""
    lines = md.replace("\r\n", "\n").split("\n")
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    title = ""
    if idx < len(lines) and lines[idx].startswith("# "):
        title = lines[idx][2:].strip()
        idx += 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    subtitle = None
    if idx < len(lines):
        cand = lines[idx].strip()
        if cand.startswith("*") and cand.endswith("*") and not cand.startswith("**") and cand.count("*") == 2:
            subtitle = cand[1:-1].strip()
            idx += 1
    body = "\n".join(lines[idx:]).strip()
    return title, subtitle, body


def first_paragraph_text(md: str) -> str:
    for block in re.split(r"\n\s*\n", md.strip()):
        s = block.strip()
        if s and not s.startswith(("#", ">", "-", "*", "```")):
            return strip_markdown(s)[:180]
    return ""


def parse_readme(md: str) -> tuple[str, str | None, str, str, list[dict[str, str]]]:
    title, subtitle, body = split_header(md)
    parts = re.split(r"^##\s+Reading order\s*$", body, maxsplit=1, flags=re.MULTILINE)
    intro_md = parts[0].strip()
    rest = parts[1] if len(parts) > 1 else ""
    rest = re.split(r"^##\s+", rest, maxsplit=1, flags=re.MULTILINE)[0].strip()

    note_lines: list[str] = []
    entries: list[dict[str, str]] = []
    item_re = re.compile(
        r"^\d+\.\s+\*\*\[([^\]]+)\]\(\./essays/([^)]+)\.md\)\*\*\s*(?:[—–-]\s*(.+))?$"
    )
    for line in rest.splitlines():
        s = line.strip()
        if not s:
            continue
        m = item_re.match(s)
        if m:
            entries.append(
                {
                    "slug": m.group(2),
                    "title": m.group(1).strip(),
                    "summary": (m.group(3) or "").strip(),
                }
            )
        elif not entries:
            note_lines.append(s)

    return title, subtitle, intro_md, " ".join(note_lines), entries


def html_shell(*, title: str, description: str, css_href: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <link rel="icon" href="{FAVICON_DATA}">
  <link rel="stylesheet" href="{css_href}">
</head>
<body>
  <div class="page">
{body}
    <footer class="site-footer">
      <span>{SAKURA_SVG}</span>
      <div class="footer-links">
        <a href="{REPO_URL}/blob/main/LICENSE">Apache License 2.0</a>
        <a href="{REPO_URL}">GitHub</a>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def build(out_dir: Path = OUT_DIR) -> list[Path]:
    readme_md = README_PATH.read_text(encoding="utf-8")
    site_title, site_subtitle, intro_md, reading_note, listed = parse_readme(readme_md)

    # Ensure every essay in essays/ is included even if not yet added to README.md.
    by_slug = {e["slug"]: e for e in listed}
    ordered = list(listed)
    for path in sorted(ESSAYS_DIR.glob("*.md")):
        if path.stem not in by_slug:
            t, sub, b = split_header(path.read_text(encoding="utf-8"))
            ordered.append({"slug": path.stem, "title": t or path.stem, "summary": sub or first_paragraph_text(b)})

    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "essays").mkdir(parents=True, exist_ok=True)
    shutil.copy2(STYLE_PATH, out_dir / "style.css")
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")

    internal_links: list[tuple[Path, str]] = []
    written: list[Path] = []

    def make_resolver(page_path: Path, in_essays: bool):
        def resolve(href: str) -> str:
            if href == "./LICENSE":
                return f"{REPO_URL}/blob/main/LICENSE"
            if href.startswith(("http://", "https://", "mailto:", "#")):
                return href
            if in_essays and href.startswith("./") and href.endswith(".md"):
                target = href[2:-3] + ".html"
                internal_links.append((page_path, target))
                return target
            if not in_essays and href.startswith("./essays/") and href.endswith(".md"):
                target = "essays/" + href[9:-3] + ".html"
                internal_links.append((page_path, target))
                return target
            return href

        return resolve

    total = len(ordered)
    for idx, entry in enumerate(ordered):
        md_path = ESSAYS_DIR / f"{entry['slug']}.md"
        raw_md = md_path.read_text(encoding="utf-8")
        title, subtitle, body_md = split_header(raw_md)
        entry["title"] = title or entry["title"]
        entry["minutes"] = str(reading_minutes(raw_md))

        out_path = out_dir / "essays" / f"{entry['slug']}.html"
        resolve = make_resolver(out_path, in_essays=True)
        body_html = render_markdown(body_md, resolve)

        prev_link = ""
        if idx > 0:
            p = ordered[idx - 1]
            prev_link = (
                f'<a class="pager-link prev" href="{p["slug"]}.html">'
                f'<span class="pager-label">&larr; Previous</span>'
                f'<span class="pager-title">{html.escape(p["title"])}</span></a>'
            )
        next_link = ""
        if idx + 1 < total:
            nx = ordered[idx + 1]
            next_link = (
                f'<a class="pager-link next" href="{nx["slug"]}.html">'
                f'<span class="pager-label">Next &rarr;</span>'
                f'<span class="pager-title">{html.escape(nx["title"])}</span></a>'
            )

        subtitle_html = f'\n      <p class="subtitle">{html.escape(subtitle)}</p>' if subtitle else ""
        page_body = f"""    <nav class="top-nav" aria-label="Breadcrumb">
      <a class="back-link" href="../">&larr; All essays</a>
      <span class="top-meta">{idx + 1:02d} / {total:02d} &middot; {entry["minutes"]} min read</span>
    </nav>
    <main>
      <article>
        <header>
          <h1>{html.escape(entry["title"])}</h1>{subtitle_html}
        </header>
        {body_html}
      </article>
      <nav class="pager" aria-label="Essay navigation">
        {prev_link}
        {next_link}
      </nav>
    </main>"""

        desc = subtitle or entry["summary"] or first_paragraph_text(body_md)
        out_path.write_text(
            html_shell(
                title=f"{entry['title']} — {site_title}",
                description=desc,
                css_href="../style.css",
                body=page_body,
            ),
            encoding="utf-8",
        )
        written.append(out_path)

    # Index page
    index_path = out_dir / "index.html"
    intro_html = render_markdown(intro_md, make_resolver(index_path, in_essays=False))
    list_items: list[str] = []
    for idx, entry in enumerate(ordered, start=1):
        summary_html = (
            f'<p class="essay-summary">{render_inline(entry["summary"], make_resolver(index_path, False))}</p>'
            if entry["summary"]
            else ""
        )
        list_items.append(
            f"""        <li class="essay-item">
          <a class="essay-link" href="essays/{entry['slug']}.html">
            <span class="essay-num">{idx:02d}</span>
            <div class="essay-head">
              <span class="essay-title">{html.escape(entry['title'])}</span>
              <span class="essay-meta">{entry['minutes']} min</span>
            </div>
            {summary_html}
          </a>
        </li>"""
        )

    subtitle_html = f'\n      <p class="subtitle">{html.escape(site_subtitle)}</p>' if site_subtitle else ""
    note_html = f'\n      <p class="reading-note">{html.escape(reading_note)}</p>' if reading_note else ""
    index_body = f"""    <header class="site-header">
      {SAKURA_SVG}
      <h1>{html.escape(site_title)}</h1>{subtitle_html}
    </header>
    <main>
      <section class="intro">
        {intro_html}
      </section>
      <section aria-labelledby="reading-order">
        <h2 id="reading-order" class="section-heading">Reading order</h2>{note_html}
        <ol class="essay-list">
{chr(10).join(list_items)}
        </ol>
      </section>
    </main>"""

    index_path.write_text(
        html_shell(
            title=site_title,
            description=site_subtitle or first_paragraph_text(intro_md),
            css_href="style.css",
            body=index_body,
        ),
        encoding="utf-8",
    )
    written.append(index_path)

    # Verify every rewritten internal link resolves to a generated file.
    for source, target in internal_links:
        resolved = (source.parent / target).resolve()
        if not resolved.exists():
            raise RuntimeError(f"Broken internal link in {source.name}: {target}")

    return written


def self_check() -> None:
    id_res = lambda u: u
    # Balanced parentheses in URLs (e.g., DOI link in implementation-and-understanding.md)
    doi = render_inline("[Paper](https://doi.org/10.1016/0165-6074(85)90032-8)", id_res)
    assert 'href="https://doi.org/10.1016/0165-6074(85)90032-8"' in doi, doi
    # Inline code escapes HTML and preserves asterisks
    code = render_inline("call `fsync(*a < b)` now", id_res)
    assert "<code>fsync(*a &lt; b)</code>" in code, code
    # Multi-paragraph blockquote
    bq = render_markdown("> First\n>\n> Second", id_res)
    assert bq == "<blockquote>\n<p>First</p>\n<p>Second</p>\n</blockquote>", bq
    # Build and verify all essays rendered
    pages = build()
    expected = len(list(ESSAYS_DIR.glob("*.md"))) + 1
    assert len(pages) == expected, f"Expected {expected} pages, built {len(pages)}"


if __name__ == "__main__":
    if "--check" in sys.argv:
        self_check()
        print("OK: self-check and build passed.")
    else:
        built = build()
        print(f"Built {len(built)} pages into {OUT_DIR.relative_to(ROOT)}/")
