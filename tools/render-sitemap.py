# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""사이트맵 — 검색엔진에 내는 주소 목록(`/sitemap.xml`)을 만든다.

    uv run --no-project tools/render-sitemap.py           # 쓴다
    uv run --no-project tools/render-sitemap.py --check   # 쓰지 않고 견준다

## 무엇을 싣나

검색에 서야 하는 주소만 싣는다.

  · 루트 `/` (서비스 목록)
  · 맨 윗단의 `<디렉터리>/index.html` 전부 (앱 소개 페이지)
  · 각 앱 `policies/sources.json` 의 판 가운데 **정본 자리**(`privacy` · `terms` · …)
  · 같은 도메인의 다른 저장소 페이지 가운데 사람이 고른 것(`tools/other-pages.json` — 회사 소개)

날짜 주소(`privacy/2026-09-05/`)는 싣지 않는다. 렌더러가 그 자리에 `noindex` 를 다는 것과
**같은 함수**(`render-policies.py` 의 `is_indexed`)로 정한다 — 둘이 갈리면 사이트맵이 「색인하지
말라」고 적힌 주소를 내미는 모순이 된다.

## 손으로 고치지 않는다

`sitemap.xml` 은 이 파일이 만든다. 앱을 더하거나 판을 더한 뒤에는 이것을 다시 돌린다.
CI(`policies.yml`)가 `--check` 로 커밋된 파일과 바이트 단위로 견준다.

`<lastmod>` 는 적지 않는다. CI 의 얕은 체크아웃에서는 파일마다 날짜를 정확히 알 수 없고,
틀린 날짜는 없는 날짜보다 나쁘다(검색엔진이 그 사이트의 `lastmod` 전체를 믿지 않게 된다).

주소의 앞부분(`https://superwork.ai.kr`)은 `CNAME` 에서 읽는다. 도메인을 바꾸면 거기 한 곳이다.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location(
    "render_policies", Path(__file__).with_name("render-policies.py")
)
render = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(render)

SITE = render.SITE
TARGET = SITE / "sitemap.xml"
NOINDEX = '<meta name="robots" content="noindex">'

# 같은 도메인 아래 서지만 **다른 저장소**가 만드는 페이지(`tools/other-pages.json`: 주소 → 저장소).
# GitHub Pages 는 조직 사이트에 커스텀 도메인이 붙으면 조직의 다른 저장소 페이지를 `/<저장소>/` 로
# 세운다. 이 저장소에 파일이 없으므로 존재 검사를 하지 않는다 — 대신 루트가 그리로 잇는지를
# `check-pages.py` 가 본다. 넣는 것은 사람이 정한다: 회사 소개는 싣는다(2026-10-06). 아이디어톤
# (/Superwork-Ideathon/)은 사내 행사이고 그 페이지가 스스로 noindex 라 싣지 않는다.
OTHER_REPOS: dict[str, str] = json.loads((SITE / "tools" / "other-pages.json").read_text(encoding="utf-8"))


def origin() -> str:
    host = (SITE / "CNAME").read_text(encoding="utf-8").strip()
    if not host or "/" in host:
        raise SystemExit(f"CNAME 이 도메인 하나가 아니다: {host!r}")
    return f"https://{host}"


def pages() -> list[str]:
    """싣는 자리들(사이트 루트 기준, `/` 로 끝남). 차례는 정해져 있다 — 돌릴 때마다 같아야 한다."""
    found = ["/"]
    for intro in sorted(SITE.glob("*/index.html")):
        found.append(f"/{intro.parent.name}/")
    for name in render.apps():
        sources = json.loads((SITE / name / "policies" / "sources.json").read_text(encoding="utf-8"))
        sources.pop("app")
        for kind in render.kinds_of(name, sources):
            for edition in render.editions_of(kind, sources[kind]):
                if render.is_indexed(edition):
                    found.append(f"/{name}/{edition['path']}/")
    if len(found) != len(set(found)):
        raise SystemExit("같은 주소가 두 번 실린다")
    for path in found:
        html = SITE / path.strip("/") / "index.html" if path != "/" else SITE / "index.html"
        if not html.exists():
            raise SystemExit(f"없는 페이지를 싣는다: {path}")
        if NOINDEX in html.read_text(encoding="utf-8"):
            raise SystemExit(f"noindex 인 페이지를 싣는다: {path}")
    return found + [path for path in OTHER_REPOS if path not in found]


def assert_robots() -> None:
    """`robots.txt` 가 이 사이트맵을 가리키는가. 도메인을 바꾸고 이 줄을 잊으면 검색로봇이
    옛 주소의 사이트맵을 찾는다."""
    expected = f"Sitemap: {origin()}/sitemap.xml"
    lines = (SITE / "robots.txt").read_text(encoding="utf-8").splitlines()
    if expected not in lines:
        raise SystemExit(f"robots.txt 에 「{expected}」 줄이 없다")


def sitemap() -> str:
    assert_robots()
    base = origin()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += [f"  <url><loc>{escape(base + path)}</loc></url>" for path in pages()]
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="쓰지 않고 커밋된 sitemap.xml 과 견준다")
    args = parser.parse_args()
    content = sitemap()
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != content:
            raise SystemExit("Outdated sitemap.xml — tools/render-sitemap.py 를 돌린다")
        print(f"OK sitemap.xml: {content.count('<url>')} 주소")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print(f"Wrote sitemap.xml: {content.count('<url>')} 주소")


if __name__ == "__main__":
    main()
