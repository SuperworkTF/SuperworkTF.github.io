# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""정책 문서 배포기 — 원문(Markdown) 한 벌에서 페이지를 만든다. **네 앱이 함께 쓴다.**

    uv run --no-project tools/render-policies.py ururu
    uv run --no-project tools/render-policies.py ururu --check
    uv run --no-project tools/render-policies.py --all --check

## 왜 한 벌인가

앱마다 이 파일을 복사해 왔고, 넷이 서로 126~367줄 갈라졌다. 복사 비용은 앱 수에 비례하고,
새 앱마다 「어느 것을 복사하지」를 시간에 쫓기며 고르게 된다 — 짤랑이 그렇게 골라
**충실성 검사가 빠진 채로** 돌고 있었다(원문과 HTML 이 어긋나도 아무도 몰랐다).

## 앱의 차이는 **데이터로만** 적는다

`if app == "..."` 를 두지 않는다. 브랜드·테마색·시행 상태·검증 켜기가 전부 각 앱의
`policies/sources.json` 에 있다. 설정으로 못 적는 차이가 생기면 그것은 **제품이 갈린
것**이므로, 그때 이 파일을 쪼갤지 사람이 정한다.

## 안전 장치

`--all --check` 는 커밋된 HTML 과 **바이트 단위로** 견준다. 이 파일을 고쳤는데 어느 앱의
문서든 한 글자라도 달라지면 거기서 멈춘다. 그래서 「고치면 넷이 깨질까 봐 무섭다」가
「바뀌면 안 넘어간다」가 된다.

The canonical policy source uses one prose block per line. Consecutive list
items form a list, including tab-indented nested items. Table cells contain
inline Markdown. Keep these conventions when updating the approved sources.
Only public policy content belongs in this directory.
"""

from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re

from markdown_it import MarkdownIt

SITE = Path(__file__).resolve().parent.parent
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


# 셀렉터가 세운 장치 둘(piclect/policies/render.py). 공용으로 옮기면서 **지문은 있을 때만**
# 검사한다 — 승인 지문을 아직 안 쥔 앱이 있다.

ACTIVE_HTML = re.compile(
    r"<\s*(?:script|iframe|object|embed|link|style|form|meta)\b"
    r"|\son[a-z]+\s*=|javascript:|\ssrc\s*=|@import",
    re.IGNORECASE,
)


def assert_source_digest(kind: str, source_bytes: bytes, metadata: dict) -> None:
    """**승인된 낱말**을 못 박는다. 마크다운↔HTML 일치만으로는 모자라다.

    이것이 없으면 정책 문장을 고치고 다시 돌리는 것만으로 `--check` 가 다시 통과한다:
    HTML 은 고쳐진 마크다운과 맞고, 충실성 검사가 읽는 것은 그 마크다운뿐이다. 지문은
    **사람이 이 낱말을 승인했다**는 기록이므로, 법정 문장을 바꾸려면 `sources.json` 을
    일부러 고쳐야 한다.

    `sha256` 이 없는 앱은 건너뛴다. 없는 것을 있다고 우기지 않는다.
    """
    approved = metadata.get("sha256")
    if approved is None:
        return
    digest = hashlib.sha256(source_bytes).hexdigest()
    if approved != digest:
        raise SystemExit(
            f"{kind}.md 가 승인된 원문과 다르다.\n"
            f"  승인 sha256: {approved}\n"
            f"  디스크    : {digest}\n"
            f"새 낱말이 승인된 것이라면 sources.json[{kind!r}]['sha256'] 을 일부러 고친다."
        )


def assert_static_html(kind: str, body: str) -> None:
    """**실행되거나 바깥을 부르는 것**은 게시 페이지에 닿을 수 없다.

    원문이 날것의 `<table>`·`<br>` 을 쓰므로 `html: True` 로 렌더한다. 그 스위치는 다른
    날것의 태그도 함께 통과시키므로, 믿지 않고 렌더된 본문을 검사한다.
    """
    found = ACTIVE_HTML.search(body)
    if found:
        raise ValueError(f"Active or remote content in {kind}: {found.group(0)!r}")


def assert_public_source(source: str):
    private_markers = (
        "내부 검토용", "[내부 확인", "작성 안내 — 공개본에서는 삭제",
        "작성 시 확인할 사항", "## 복사용 본문", "approved-template-internal",
        "<ancestor-path>", "<mention-page", "{{", r"\{\{",
    )
    if any(marker in source for marker in private_markers):
        raise ValueError("Policy source contains private drafting material or placeholders")


# ──────────────────────────────────────────────────────────────────────
# 시행 상태 — 공고 기간에 무엇이 정본인지 **문서 스스로 말한다**
# ──────────────────────────────────────────────────────────────────────
#
# 짤랑이 먼저 세운 장치다(a3f4a72). 공고와 시행 사이에는 문서가 둘이고, 그때 **어느 쪽이
# 오늘 시행 중인지**를 읽는 사람이 알아야 한다. 어느 경우에도 「다른 곳이 정본」이라고
# 말하지 않는다 — 이 사이트가 정본이다.
#
#   upcoming  공고됐고 아직 시행 전. 날짜 주소에 서고, 정본 자리는 아직 옛 판이다
#   current   오늘 시행 중. 이 페이지가 정본이다
#   dated     시행이 지난 날짜 주소. 공고문이 이 주소를 물고 있으므로 죽이지 않는다
STATUS_NOTES = {
    "upcoming": ('<strong>이 판은 {effective}부터 시행됩니다.</strong> 공고일 {announced}.'
                 ' 지금 시행 중인 문서는 <a href="{current}">여기</a>에서 봅니다.'),
    "current": ('시행일 {effective} · 공고일 {announced} · <strong>이 페이지가 정본입니다.</strong>'
                ' <a href="{previous}">이전 시행본({previous_label}) 보기</a>'),
    "dated": ('<strong>{effective} 시행본</strong>의 고정 주소입니다. 공고일 {announced}.'
              ' 정본 자리는 <a href="../">여기</a>입니다.'),
}


def status_note(metadata: dict) -> str:
    """머리말 한 문단. `status` 가 없으면 빈 문자열 — 상태를 안 적는 앱도 있다."""
    status = metadata.get("status")
    if status is None:
        return ""
    if status not in STATUS_NOTES:
        raise SystemExit(f"Unknown status: {status}")
    filled = STATUS_NOTES[status].format(**{k: escape(str(v)) for k, v in metadata.items()})
    return f'      <p class="source-note">{filled}</p>\n'


def page(kind: str, source: str, metadata: dict, app: dict, *, archive: dict | None = None) -> str:
    assert_public_source(source)
    brand = app["brand"]
    title = f"{brand} {metadata['title']}"
    if source.startswith("# "):
        source_title, source = source.split("\n", 1)
        assert source_title[2:] == title
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
    site_prefix = "../../" if archive else "../"
    nav = "\n".join(
        f'      <a href="{href}"' + (' aria-current="page"' if name == kind else '') + f'>{label}</a>'
        for name, href, label in [('intro', site_prefix, '앱 소개'), ('privacy', site_prefix + 'privacy/', '개인정보처리방침'), ('terms', site_prefix + 'terms/', '이용약관')]
    )
    public_url = metadata['public_url']
    archive_note = ""
    document_title = title
    if archive:
        version = archive['version']
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", version):
            raise ValueError("Invalid archive version")
        public_url = f"{public_url.rstrip('/')}/{version}/"
        document_title += " — 정비 전 문서"
        archive_note = (
            f'      <p class="archive-note">{escape(archive["notice"])} '
            f'<a href="{site_prefix}{kind}/">현재 방침 보기</a></p>\n'
        )
    status_line = status_note(metadata)

    """
    ## 정본이 이 사이트인가, 아직 노션인가 — **앱마다 다르고, 그것은 제품의 상태다**

    그려보카·우르르는 이 사이트가 정본이라 `rel="canonical"` 이 자기를 가리킨다. 셀렉터는
    아직 노션이 정본이라 그 사실을 머리말에 적고 canonical 을 안 낸다.

    렌더러가 한쪽으로 몰지 않는다. **정본을 옮기는 것은 사람이 정하는 일**이고, 그날
    `sources.json` 에서 `notion_source` 를 떼면 된다.
    """
    notion_source = metadata.get("notion_source", False)
    if notion_source:
        description = f"{title} — 기존 공개 정책의 내용과 원문 링크를 확인하세요."
        canonical_line = ""
        status_line = (
            f'      <p class="source-note">기존 공개 Notion 문서의 내용을 옮긴 페이지입니다.<br>\n'
            f'        <a href="{escape(public_url, quote=True)}">'
            f'{escape(metadata["title"])} 원문 보기 (Notion)</a>\n      </p>\n'
        ) + status_line
    else:
        description = f"{title} 공식 문서입니다."
        canonical_line = f'\n  <link rel="canonical" href="{escape(public_url, quote=True)}">'
    canonical_url = escape(public_url, quote=True)
    root_prefix = "../../../" if archive else "../../"
    table_help = '<p class="table-help" id="table-help">표가 화면보다 넓으면 표 안에서 좌우로 스크롤할 수 있습니다. 키보드로는 표에 초점을 맞춘 뒤 방향키를 사용하세요.</p>'
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">{canonical_line}
  <meta name="theme-color" content="{escape(app["theme_color"], quote=True)}">
  <title>{escape(document_title)}</title>
  <link rel="stylesheet" href="{site_prefix}styles.css">
</head>
<body>
  <a class="skip-link" href="#main">본문 바로가기</a>
  <header class="site-header shell">
    <a class="brand" href="{site_prefix}" aria-label="{escape(brand + ' 소개', quote=True)}"><span class="brand-mark" aria-hidden="true"></span>{escape(brand)}</a>
    <nav class="site-nav" aria-label="주요 메뉴">
{nav}
    </nav>
  </header>
  <main id="main" class="shell legal-shell" tabindex="-1">
    <header class="document-heading">
      <p class="eyebrow">{escape(brand)} · 정책 문서</p>
      <h1>{escape(title)}</h1>
{archive_note}{status_line}    </header>
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
    <p><a href="{site_prefix}">{escape(brand)} 소개</a> · <a href="{root_prefix}">전체 앱 안내</a></p>
    <a href="mailto:superwork.master+help@gmail.com">superwork.master+help@gmail.com</a>
  </footer>
</body>
</html>
'''


def render_app(name: str, check: bool) -> None:
    here = SITE / name / "policies"
    sources = json.loads((here / "sources.json").read_text(encoding="utf-8"))
    app = sources.pop("app")
    if app["dir"] != name:
        raise SystemExit(f"{name}/policies/sources.json names a different directory")
    for kind in ("privacy", "terms"):
        editions = [(here / f"{kind}.md", SITE / name / kind / "index.html", None)]
        for archive in sources[kind].get("archives", []):
            version = archive["version"]
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", version):
                raise ValueError("Invalid archive version")
            editions.append((here / f"{kind}-{version}.md", SITE / name / kind / version / "index.html", archive))
        for source_path, target, archive in editions:
            source_bytes = source_path.read_bytes()
            source = source_bytes.decode("utf-8")
            if archive is None:
                assert_source_digest(kind, source_bytes, sources[kind])
            content = page(kind, source, sources[kind], app, archive=archive)
            relative_target = target.relative_to(SITE)
            if check:
                if not target.exists() or target.read_text(encoding="utf-8") != content:
                    raise SystemExit(f"Outdated HTML: {relative_target}")
                print(f"OK {relative_target}: exact source text/links and reproducible HTML")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                print(f"Wrote {relative_target} (source text and links verified)")


def apps() -> list[str]:
    """앱 디렉터리 이름들. `<app>/policies/sources.json` 이 있는 곳이 앱이다."""
    return sorted(p.parent.parent.name for p in SITE.glob("*/policies/sources.json"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", nargs="?", help="앱 디렉터리 이름 (--all 이면 생략)")
    parser.add_argument("--all", action="store_true", help="policies/sources.json 이 있는 앱 전부")
    parser.add_argument("--check", action="store_true", help="쓰지 않고 커밋된 HTML 과 견준다")
    args = parser.parse_args()
    names = apps() if args.all else ([args.app] if args.app else [])
    if not names:
        raise SystemExit("앱 이름을 대거나 --all 을 붙인다")
    for name in names:
        render_app(name, args.check)


if __name__ == "__main__":
    main()
