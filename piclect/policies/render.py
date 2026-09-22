# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""Optional policy publisher. Deployment serves the checked-in HTML as-is.

Run from the repository root:
    uv run --no-project piclect/policies/render.py
Check without writing:
    uv run --no-project piclect/policies/render.py --check

privacy.md and terms.md are sanitized exports of the approved public Notion
documents named in sources.json. The export uses one prose block per line.
Consecutive list items form a list, including tab-indented nested items. Table
cells contain inline Markdown and use <br> for a hard line break inside a cell.
Keep these conventions when updating the approved sources. Only public policy
content belongs in this directory.

The published URLs /piclect/privacy/ and /piclect/terms/ are cited by the
Terms themselves (제17조 제2항) and by the Play Console listing. Do not move
them; render_check_urls() fails the build if the citation disappears.
"""

from __future__ import annotations

import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
MARKDOWN = MarkdownIt("commonmark", {"html": True, "typographer": False})
TABLE = re.compile(r'<table header-row="true">.*?</table>', re.DOTALL)
LIST_ITEM = re.compile(r"^[ \t]*(?:[-+*]|[0-9]+[.)])\s+")
BRAND = "셀렉터"
CONTACT = "superwork.master+help@gmail.com"
THEME_COLOR = "#0B0B0C"
PUBLISHED_URLS = (
    "https://superworktf.github.io/piclect/privacy/",
    "https://superworktf.github.io/piclect/terms/",
)
NOTION_API = "https://cautious-oxygen-897.notion.site/api/v3/loadPageChunk"
# Raw HTML is enabled for the <table header-row="true"> and <br> conventions
# only. Nothing that executes, loads or tracks may reach a published page.
ACTIVE_HTML = re.compile(
    r"<\s*(?:script|iframe|object|embed|link|style|form|meta)\b"
    r"|\son[a-z]+\s*=|javascript:|\ssrc\s*=|@import",
    re.IGNORECASE,
)


class ExportTable(HTMLParser):
    """Read only the small, known Notion table export format."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.rows.append([])
        elif tag == "td":
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append("<br>")
        elif tag != "table":
            raise ValueError(f"Unexpected source table tag: {tag}")

    def handle_endtag(self, tag):
        if tag == "td":
            assert self.cell is not None
            self.rows[-1].append("".join(self.cell))
            self.cell = None
        elif tag not in {"table", "tr", "br"}:
            raise ValueError(f"Unexpected source table closing tag: {tag}")

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        elif data.strip():
            raise ValueError("Unexpected text outside a source table cell")


def render_table(raw: str, number: int, heading: str) -> str:
    parsed = ExportTable()
    parsed.feed(raw)
    rows = parsed.rows
    assert len(rows) > 1
    columns = len(rows[0])
    assert all(len(row) == columns for row in rows)
    label = escape(f"{heading} — 표 {number}", quote=True)
    result = [f'<div class="table-scroll" role="region" tabindex="0" aria-label="{label}" aria-describedby="table-help">',
              f'<table data-columns="{columns}">', '<thead><tr>']
    for cell in rows[0]:
        result.append(f'<th scope="col">{MARKDOWN.renderInline(cell)}</th>')
    result.append('</tr></thead><tbody>')
    for row in rows[1:]:
        result.append('<tr>')
        for cell in row:
            result.append(f'<td>{MARKDOWN.renderInline(cell)}</td>')
        result.append('</tr>')
    result.append('</tbody></table></div>')
    return "\n".join(result) + "\n"


def render_blocks(source: str) -> str:
    blocks: list[str] = []
    list_lines: list[str] = []

    def flush_list():
        if list_lines:
            blocks.append("\n".join(list_lines))
            list_lines.clear()

    for line in source.splitlines():
        if LIST_ITEM.match(line):
            list_lines.append(line)
        else:
            flush_list()
            if line.strip():
                blocks.append(line)
    flush_list()
    return MARKDOWN.render("\n\n".join(blocks))


def render_body(source: str) -> str:
    parts: list[str] = []
    end = 0
    for number, match in enumerate(TABLE.finditer(source), 1):
        prefix = source[end:match.start()]
        parts.append(render_blocks(prefix))
        headings = re.findall(r"^#{2,3} (.+)$", source[:match.start()], re.MULTILINE)
        parts.append(render_table(match.group(), number, headings[-1] if headings else "사업자 정보"))
        end = match.end()
    parts.append(render_blocks(source[end:]))
    return "".join(parts)


class VisibleText(HTMLParser):
    """Collect text tokens without folding inline boundaries into new words."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.links: list[str] = []

    def handle_data(self, data):
        self.text.append(data)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.links.append(attrs["href"])
        if tag == "br":
            self.text.append(" ")


def text_and_links(fragment: str):
    parser = VisibleText()
    parser.feed(fragment)
    return re.sub(r"\s+", " ", "".join(parser.text)).strip(), parser.links


def assert_fidelity(source: str, body: str):
    # Independent per-line/per-cell reading of the sanitized source. Check the
    # ordered text and all actual Markdown links, including links in tables.
    lines = re.sub(r"</?(?:table|tr|td)\b[^>]*>", "\n", source).splitlines()
    expected: list[str] = []
    for line in lines:
        text = line.strip()
        if not text or text == "---":
            continue
        if text.startswith("#"):
            text = re.sub(r"^#{1,6} ", "", text)
        else:
            text = re.sub(r"^(?:[-+*]|[0-9]+[.)])\s+", "", text)
        expected.append(MARKDOWN.renderInline(text))
    expected_text, expected_links = text_and_links("\n".join(expected))
    actual_text, actual_links = text_and_links(body)
    if expected_text != actual_text:
        index = next((i for i, (a, b) in enumerate(zip(expected_text, actual_text)) if a != b), min(len(expected_text), len(actual_text)))
        raise ValueError(f"Policy text mismatch at {index}: expected {expected_text[max(0, index - 30):index + 50]!r}; got {actual_text[max(0, index - 30):index + 50]!r}")
    if expected_links != actual_links:
        raise ValueError("Policy link mismatch")


def assert_static_html(kind: str, body: str):
    """Nothing that executes, loads or tracks may reach a published page.

    Markdown is rendered with ``html: True`` because the sanitized export uses
    raw <table> and <br>. That switch also lets any other raw tag through, so
    the rendered body is checked instead of trusted.
    """
    found = ACTIVE_HTML.search(body)
    if found:
        raise ValueError(f"Active or remote content in {kind}: {found.group(0)!r}")


def assert_source_digest(kind: str, source_bytes: bytes, metadata: dict):
    """Pin the approved wording, not merely markdown-to-HTML agreement.

    Without this, editing a policy sentence and re-running the generator makes
    ``--check`` pass again: the HTML matches the edited markdown, and the
    markdown is the only thing the fidelity check reads. The digest is the
    record that a human approved *these* words, so any change to a legal
    sentence has to be an explicit, reviewable edit of sources.json.
    """
    digest = hashlib.sha256(source_bytes).hexdigest()
    approved = metadata.get("sha256")
    if approved != digest:
        raise SystemExit(
            f"{kind}.md does not match the approved source.\n"
            f"  approved sha256: {approved}\n"
            f"  on disk sha256:  {digest}\n"
            f"Re-read {metadata['public_url']} and, if the new wording is the approved\n"
            f"wording, update sources.json[{kind!r}]['sha256'] deliberately."
        )


def notion_blocks(page_id: str):
    """Read a public Notion page through the same endpoint the site uses.

    Paging matters: the terms document needs three chunks, and a single
    request silently returns a prefix of the page.
    """
    dashed = "-".join([page_id[0:8], page_id[8:12], page_id[12:16], page_id[16:20], page_id[20:32]])
    blocks: dict = {}
    cursor: dict = {"stack": []}
    for chunk in range(24):
        payload = json.dumps({
            "pageId": dashed, "limit": 200, "cursor": cursor,
            "chunkNumber": chunk, "verticalColumns": False,
        }).encode("utf-8")
        request = urllib.request.Request(
            NOTION_API, payload,
            {"content-type": "application/json", "user-agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        for block_id, record in (data.get("recordMap") or {}).get("block", {}).items():
            value = record.get("value")
            if isinstance(value, dict) and "value" in value:
                value = value["value"]
            blocks[block_id] = value
        cursor = data.get("cursor") or {"stack": []}
        if not cursor.get("stack"):
            break
    else:
        raise ValueError("Notion page did not finish paging")
    return blocks, dashed


def notion_text_and_links(blocks: dict, root_id: str, title: str):
    """Ordered visible text and link targets of the published document.

    The page title is the document's heading. One source repeats it as a
    first heading block; that repeat is dropped here and in the markdown, so
    both sides carry the title exactly once.
    """
    text: list[str] = [title]
    links: list[str] = []

    def read(props):
        # Segments inside one block are adjacent runs of the same sentence and
        # must not gain a space; separate blocks and cells are separate
        # elements, so they get one.
        run: list[str] = []
        for segment in props or []:
            run.append(segment[0])
            for mark in (segment[1] if len(segment) > 1 and segment[1] else []):
                if mark[0] == "a":
                    links.append(mark[1])
        text.append("".join(run))

    for position, block_id in enumerate(blocks[root_id].get("content") or []):
        block = blocks.get(block_id)
        if not block:
            continue
        if position == 0 and block.get("type", "").endswith("header"):
            repeated = "".join(s[0] for s in (block.get("properties") or {}).get("title", []))
            if repeated == title:
                continue
        if block.get("type") == "table":
            columns = block["format"]["table_block_column_order"]
            for row_id in block.get("content") or []:
                row = blocks[row_id].get("properties") or {}
                for column in columns:
                    read(row.get(column))
        else:
            read((block.get("properties") or {}).get("title"))
    return re.sub(r"\s+", " ", " ".join(text)).strip(), links


def verify_source(kind: str, source: str, metadata: dict):
    """Diff the checked-in markdown against the live public Notion original.

    Network-dependent, so it is opt-in: deployment never runs it. It answers
    the one question --check cannot, namely whether the approved document
    still says what this repository publishes.
    """
    page_id = metadata["public_url"].rstrip("/").rsplit("/", 1)[-1]
    blocks, dashed = notion_blocks(page_id)
    title = "".join(s[0] for s in (blocks[dashed].get("properties") or {}).get("title", []))
    if not source.startswith("# "):
        raise SystemExit(f"{kind}.md must open with the document title as an H1")
    heading, source = source.split("\n", 1)
    if heading[2:] != title:
        raise SystemExit(f"{kind}: title is {heading[2:]!r}; Notion says {title!r}")
    expected_text, expected_links = notion_text_and_links(blocks, dashed, title)
    body_text, actual_links = text_and_links(render_body(source))
    actual_text = f"{title} {body_text}".strip()
    if expected_text != actual_text:
        index = next((i for i, (a, b) in enumerate(zip(expected_text, actual_text)) if a != b),
                     min(len(expected_text), len(actual_text)))
        raise SystemExit(
            f"{kind}: drifted from Notion at {index}\n"
            f"  Notion: {expected_text[max(0, index - 40):index + 60]!r}\n"
            f"  local:  {actual_text[max(0, index - 40):index + 60]!r}"
        )
    if expected_links != actual_links:
        raise SystemExit(f"{kind}: link targets differ from Notion")
    print(f"OK {kind}: matches {metadata['public_url']} ({len(expected_links)} links)")


def render_check_urls(kind: str, source: str):
    """The Terms cite their own published address in 제17조 제2항.

    Those URLs are also filed with the store listing, so a path rename must
    fail loudly here instead of silently publishing a dead citation.
    """
    if kind != "terms":
        return
    for url in PUBLISHED_URLS:
        if url not in source:
            raise ValueError(f"Terms no longer cite the published URL {url}")


def page(kind: str, source: str, metadata: dict) -> str:
    title = f"{BRAND} {metadata['title']}"
    if source.startswith("# "):
        source_title, source = source.split("\n", 1)
        assert source_title[2:] == title
    render_check_urls(kind, source)
    body = render_body(source)
    assert_fidelity(source, body)
    assert_static_html(kind, body)
    headings: list[tuple[str, str]] = []

    def mark_heading(match):
        heading_id = f"section-{len(headings) + 1}"
        headings.append((heading_id, match.group(1)))
        return f'<h2 id="{heading_id}">{match.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", mark_heading, body)
    toc = "\n".join(f'<li><a href="#{heading_id}">{text}</a></li>' for heading_id, text in headings)
    nav = "\n".join(
        f'      <a href="{href}"' + (' aria-current="page"' if name == kind else '') + f'>{label}</a>'
        for name, href, label in [('intro', '../', '앱 소개'), ('privacy', '../privacy/', '개인정보처리방침'), ('terms', '../terms/', '이용약관')]
    )
    source_url = escape(metadata['public_url'], quote=True)
    table_help = '<p class="table-help" id="table-help">표가 화면보다 넓으면 표 안에서 좌우로 스크롤할 수 있습니다. 키보드로는 표에 초점을 맞춘 뒤 방향키를 사용하세요.</p>'
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(title, quote=True)} — 기존 공개 정책의 내용과 원문 링크를 확인하세요.">
  <meta name="theme-color" content="{THEME_COLOR}">
  <title>{escape(title)}</title>
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <a class="skip-link" href="#main">본문 바로가기</a>
  <header class="site-header shell">
    <a class="brand" href="../" aria-label="{BRAND} 소개"><span class="brand-mark" aria-hidden="true"></span>{BRAND}</a>
    <nav class="site-nav" aria-label="주요 메뉴">
{nav}
    </nav>
  </header>
  <main id="main" class="shell legal-shell" tabindex="-1">
    <header class="document-heading">
      <p class="eyebrow">{BRAND} · 정책 문서</p>
      <h1>{escape(title)}</h1>
      <p class="source-note">기존 공개 Notion 문서의 내용을 옮긴 페이지입니다.<br>
        <a href="{source_url}">{escape(metadata['title'])} 원문 보기 (Notion)</a>
      </p>
    </header>
    <details class="toc">
      <summary>목차 보기</summary>
      <ol>
{toc}
      </ol>
    </details>
    {table_help}
    <article class="policy-body" id="policy-body" aria-label="{escape(metadata['title'], quote=True)} 본문">
{body}    </article>
  </main>
  <footer class="site-footer shell">
    <p><a href="../">{BRAND} 소개</a> · <a href="../../">전체 앱 안내</a></p>
    <a href="mailto:{CONTACT}">{CONTACT}</a>
  </footer>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed HTML without changing it")
    parser.add_argument("--verify-source", action="store_true",
                        help="also diff the markdown against the live public Notion document (needs network)")
    args = parser.parse_args()
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    for kind in ("privacy", "terms"):
        raw = (HERE / f"{kind}.md").read_bytes()
        assert_source_digest(kind, raw, sources[kind])
        source = raw.decode("utf-8")
        if args.verify_source:
            verify_source(kind, source, sources[kind])
        content = page(kind, source, sources[kind])
        target = SITE / kind / "index.html"
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Outdated HTML: piclect/{kind}/index.html")
            print(f"OK {kind}: exact source text/links and reproducible HTML")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            print(f"Wrote piclect/{kind}/index.html (source text and links verified)")


if __name__ == "__main__":
    main()
