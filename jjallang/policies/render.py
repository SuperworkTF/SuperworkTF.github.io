# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown==3.10.3"]
# ///
"""짤랑 정책 문서 배포기 — 원문(Markdown) 한 벌에서 페이지 두 장을 만든다.

원본은 이 저장소가 아니라 **앱 저장소**가 쥔다:
    SuperworkTF/jjallang · ops/legal/짤랑_개인정보처리방침.md · 짤랑_서비스이용약관.md
고칠 일이 생기면 거기를 고치고, 그 파일을 `policies/*.md` 로 복사한 뒤 이 스크립트를 돌린다.
손으로 HTML 을 고치지 마라 — 원문과 페이지가 갈리는 순간 어느 쪽이 사실인지 아무도 모른다.

    uv run --no-project jjallang/policies/render.py           # 새로 쓴다
    uv run --no-project jjallang/policies/render.py --check   # 쓰지 않고 차이만 본다
"""

from __future__ import annotations

import argparse
import json
import re
from html import escape
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
APP = HERE.parent                      # …/jjallang
SOURCES = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))

HEAD = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#f3f1ea">
  <title>{title}</title>
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <a class="skip-link" href="#main">본문 바로가기</a>
  <header class="site-header shell">
    <a class="brand" href="../" aria-label="짤랑 소개"><span class="brand-mark" aria-hidden="true"></span>짤랑</a>
    <nav class="site-nav" aria-label="주요 메뉴">
      <a href="../">앱 소개</a>
      <a href="../privacy/"{privacy_current}>개인정보처리방침</a>
      <a href="../terms/"{terms_current}>이용약관</a>
    </nav>
  </header>
  <main id="main" class="shell legal-shell" tabindex="-1">
    <header class="document-heading">
      <p class="eyebrow">짤랑 · 정책 문서</p>
      <h1>{title}</h1>
      <p class="source-note">시행일 {effective} · <strong>이 페이지가 공식 게시 주소입니다.</strong><br>
        <a href="{notion}">이전에 쓰던 Notion 사본 보기</a>
      </p>
    </header>
"""

FOOT = """    </article>
  </main>
  <footer class="site-footer shell">
    <p>짤랑 · 앱 소개와 정책 안내</p>
    <a href="../../">전체 앱 안내</a>
  </footer>
</body>
</html>
"""

HEADING = re.compile(r"<h2>(.*?)</h2>", re.DOTALL)


def build(key: str) -> tuple[Path, str]:
    meta = SOURCES[key]
    md_text = (HERE / f"{key}.md").read_text(encoding="utf-8")
    lines = md_text.splitlines()
    title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("# ") else meta["title"]
    body_md = "\n".join(lines[1:])

    html = markdown.markdown(body_md, extensions=["tables", "sane_lists", "attr_list"])

    # 절마다 닻을 박고 그것으로 목차를 만든다. 문서가 길어서 목차 없이는 못 읽는다.
    toc: list[str] = []
    counter = 0

    def anchor(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        text = match.group(1)
        plain = re.sub(r"<[^>]+>", "", text)
        toc.append(f'<li><a href="#section-{counter}">{plain}</a></li>')
        return f'<h2 id="section-{counter}">{text}</h2>'

    html = HEADING.sub(anchor, html)

    parts = [HEAD.format(
        title=escape(title), desc=escape(f"{title} — 짤랑 앱의 정책 문서"),
        effective=escape(meta["effective"]), notion=escape(meta["notion_copy"], quote=True),
        privacy_current=' aria-current="page"' if key == "privacy" else "",
        terms_current=' aria-current="page"' if key == "terms" else "",
    )]
    if toc:
        parts.append("    <details class=\"toc\">\n      <summary>목차 보기</summary>\n      <ol>\n")
        parts.append("\n".join(f"        {item}" for item in toc))
        parts.append("\n      </ol>\n    </details>\n")
    if "<table>" in html:
        parts.append('    <p class="table-help">표가 화면보다 넓으면 표 안에서 좌우로 스크롤할 수 있습니다.</p>\n')
    parts.append(f'    <article class="policy-body" aria-label="{escape(title)} 본문">\n')
    parts.append(html)
    parts.append("\n")
    parts.append(FOOT)
    return APP / key / "index.html", "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="쓰지 않고 차이만 확인한다")
    args = parser.parse_args()

    stale = 0
    for key in SOURCES:
        path, html = build(key)
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == html:
            print(f"같음  {path.relative_to(APP.parent)}")
            continue
        stale += 1
        if args.check:
            print(f"다름  {path.relative_to(APP.parent)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
            print(f"씀    {path.relative_to(APP.parent)}")
    return 1 if (args.check and stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
