# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""Optional policy publisher. Deployment serves the checked-in HTML as-is.

Run from the repository root:
    uv run --no-project ururu/policies/render.py
Check without writing:
    uv run --no-project ururu/policies/render.py --check

The canonical policy source uses one prose block per line. A line may begin
with "> " for a callout — the announcement banner on a policy that is published
ahead of its effective date. Consecutive callout lines form one block: a
four-line notice drawn as four boxes reads as four different notices. Consecutive list
items form a list, including tab-indented nested items. Table cells contain
inline Markdown. Keep these conventions when updating the approved sources.
Only public policy content belongs in this directory.
"""

from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
MARKDOWN = MarkdownIt("commonmark", {"html": True, "typographer": False})
TABLE = re.compile(r'<table header-row="true">.*?</table>', re.DOTALL)
LIST_ITEM = re.compile(r"^[ \t]*(?:[-+*]|[0-9]+[.)])\s+")
QUOTE = re.compile(r"^>\s?")


class ExportTable(HTMLParser):
    """Read only the supported policy table format."""

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
    """한 줄이 한 블록이다. 다만 **이어진 줄이 한 덩어리인 것 둘**은 묶는다.

    목록은 원래부터 묶었다. 인용은 공고 안내 때문에 더했다 — 넉 줄짜리 안내가 줄마다 상자를
    하나씩 만들어 한 문단이 네 조각으로 보였다(실기 확인). 읽는 사람에게 그것은 네 개의
    다른 알림이다.
    """
    blocks: list[str] = []
    group: list[str] = []
    kind: str | None = None

    def flush():
        nonlocal kind
        if group:
            blocks.append("\n".join(group))
            group.clear()
        kind = None

    for line in source.splitlines():
        this = "list" if LIST_ITEM.match(line) else "quote" if QUOTE.match(line) else None
        if this is not None:
            if kind != this:
                flush()
            kind = this
            group.append(line)
        else:
            flush()
            if line.strip():
                blocks.append(line)
    flush()
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
            # 인용 표시만 떼고 글자는 그대로 센다 — 떼지 않으면 `>` 가 기대값에만 남는다.
            text = re.sub(r"^>\s*", "", text)
            text = re.sub(r"^(?:[-+*]|[0-9]+[.)])\s+", "", text)
        expected.append(MARKDOWN.renderInline(text))
    expected_text, expected_links = text_and_links("\n".join(expected))
    actual_text, actual_links = text_and_links(body)
    if expected_text != actual_text:
        index = next((i for i, (a, b) in enumerate(zip(expected_text, actual_text)) if a != b), min(len(expected_text), len(actual_text)))
        raise ValueError(f"Policy text mismatch at {index}: expected {expected_text[max(0, index - 30):index + 50]!r}; got {actual_text[max(0, index - 30):index + 50]!r}")
    if expected_links != actual_links:
        raise ValueError("Policy link mismatch")


def page(kind: str, source: str, metadata: dict) -> str:
    # 지난 시행본은 `privacy/2026-09-05/` 처럼 한 칸 더 들어간다. 그 자리도 이 스크립트가
    # 만든다 — 손으로 만든 HTML 이 한 장이라도 남으면 낡는 것은 그 한 장이고, 그 한 장은
    # 7일 고지 기간에 **시행 중인 문서**다.
    up = "../" * (metadata.get("path", kind).count("/") + 1)
    title = f"우르르 {metadata['title']}"
    if source.startswith("# "):
        source_title, source = source.split("\n", 1)
        assert source_title[2:] == title
    body = render_body(source)
    assert_fidelity(source, body)
    headings: list[tuple[str, str]] = []

    def mark_heading(match):
        heading_id = f"section-{len(headings) + 1}"
        headings.append((heading_id, match.group(1)))
        return f'<h2 id="{heading_id}">{match.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", mark_heading, body)
    toc = "\n".join(f'<li><a href="#{heading_id}">{text}</a></li>' for heading_id, text in headings)
    nav = "\n".join(
        f'      <a href="{up}{href}"' + (' aria-current="page"' if name == metadata.get("nav", kind) else '') + f'>{label}</a>'
        for name, href, label in [('intro', '', '앱 소개'), ('privacy', 'privacy/', '개인정보처리방침'), ('terms', 'terms/', '이용약관')]
    )
    canonical_url = escape(metadata['public_url'], quote=True)
    table_help = '<p class="table-help" id="table-help">표가 화면보다 넓으면 표 안에서 좌우로 스크롤할 수 있습니다. 키보드로는 표에 초점을 맞춘 뒤 방향키를 사용하세요.</p>'
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(title, quote=True)} 공식 문서입니다.">
  <link rel="canonical" href="{canonical_url}">
  <meta name="theme-color" content="#f7f4eb">
  <title>{escape(title)}</title>
  <link rel="stylesheet" href="{up}styles.css">
</head>
<body>
  <a class="skip-link" href="#main">본문 바로가기</a>
  <header class="site-header shell">
    <a class="brand" href="{up}" aria-label="우르르 소개"><span class="brand-mark" aria-hidden="true"></span>우르르</a>
    <nav class="site-nav" aria-label="주요 메뉴">
{nav}
    </nav>
  </header>
  <main id="main" class="shell legal-shell" tabindex="-1">
    <header class="document-heading">
      <p class="eyebrow">우르르 · 정책 문서</p>
      <h1>{escape(title)}</h1>
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
    <p><a href="{up}">우르르 소개</a> · <a href="{up}../">전체 앱 안내</a></p>
    <a href="mailto:superwork.master+help@gmail.com">superwork.master+help@gmail.com</a>
  </footer>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed HTML without changing it")
    args = parser.parse_args()
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    for kind, metadata in sources.items():
        source = (HERE / f"{kind}.md").read_text(encoding="utf-8")
        content = page(kind, source, metadata)
        target = SITE / metadata.get("path", kind) / "index.html"
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Outdated HTML: {target.relative_to(SITE)}")
            print(f"OK {target.relative_to(SITE)}: exact source text/links and reproducible HTML")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            print(f"Wrote {target.relative_to(SITE)} (source text and links verified)")


if __name__ == "__main__":
    main()
