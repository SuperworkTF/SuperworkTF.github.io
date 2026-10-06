# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""llms.txt — AI 에이전트가 읽는 사이트 요약(`/llms.txt`)을 만든다.

    uv run --no-project tools/render-llms.py           # 쓴다
    uv run --no-project tools/render-llms.py --check   # 쓰지 않고 견준다

## 이 파일의 자리

llms.txt 는 공식 표준이 아니라 제안(https://llmstxt.org/)이다. 구글은 「구글 검색에는 필요 없고
노출·순위에 좋게도 나쁘게도 영향이 없다. 다른 서비스를 위해 두는 것은 괜찮다」고 적었다
(검색 센터 변경 로그, 2026-06-15). 비용이 낮아서 둔다 — 사람이 정했다(2026-10-06).

## 새로 짓지 않는다

모든 글은 **이미 페이지에 있는 것**에서 온다. 그래야 llms.txt 가 페이지와 갈라지지 않는다.

  · 제목 줄 · 요약 — 루트의 og:site_name · meta description
  · 조직 — 루트 구조화 데이터(Organization)와 「조직 소개」 카드
  · 앱 — 루트 서비스 목록의 차례(가나다순), 각 소개 페이지의 <title> 과
    구조화 데이터(SoftwareApplication: description · operatingSystem · offers · sameAs)
  · 정책 — 각 앱 `policies/sources.json` 의 정본 자리(사이트맵과 같은 규칙)

손으로 고치지 않는다. 페이지를 고친 뒤 이것을 다시 돌린다. CI 가 `--check` 로 문다.
"""

from __future__ import annotations

import argparse
import importlib.util
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("check_pages", Path(__file__).with_name("check-pages.py"))
pages = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(pages)

SITE = pages.SITE
TARGET = SITE / "llms.txt"
DOCUMENT_LABELS = {"privacy": "개인정보처리방침", "terms": "서비스 이용약관", "account-deletion": "계정 삭제 안내"}


class Cards(HTMLParser):
    """루트의 `<a class="card" href=…><div class="t">…</div><div class="d">…</div></a>` 를 차례대로."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards: list[dict] = []
        self._card: dict | None = None
        self._field: str | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "card" in (a.get("class") or "").split():
            self._card = {"href": a.get("href", ""), "t": "", "d": ""}
        elif tag == "div" and self._card is not None and a.get("class") in ("t", "d"):
            self._field = a["class"]

    def handle_endtag(self, tag):
        if tag == "div":
            self._field = None
        elif tag == "a" and self._card is not None:
            self.cards.append({k: v.strip() for k, v in self._card.items()})
            self._card = None

    def handle_data(self, data):
        if self._card is not None and self._field:
            self._card[self._field] += data


def read(path: Path):
    page = pages.Page()
    page.feed(path.read_text(encoding="utf-8"))
    nodes = []
    for script in page.scripts:
        if script["attrs"].get("type") == "application/ld+json":
            nodes.extend(pages.nodes_of(json.loads(script["text"])))
    return page, {n.get("@type"): n for n in nodes}


def store_label(url: str) -> str:
    return "Google Play" if "play.google.com" in url else "App Store"


def llms() -> str:
    base = pages.origin()
    root, root_nodes = read(SITE / "index.html")
    cards = Cards()
    cards.feed((SITE / "index.html").read_text(encoding="utf-8"))
    org = root_nodes["Organization"]
    parent = org.get("parentOrganization", {})

    lines = [f"# {root.meta['og:site_name'][0]}", "", f"> {root.meta['description'][0]}", ""]
    others_names = ", ".join(parent.get("alternateName", []))
    lines.append(f"{org['name']}는 {parent['name']}의 사내 조직입니다. "
                 f"스토어의 개발자 이름은 {others_names}입니다. 문의: {org['email']}")
    lines += ["", "## 앱", ""]
    apps = set(pages.apps())
    for card in cards.cards:
        name = card["href"].strip("./")
        if name not in apps:
            continue
        page, nodes = read(SITE / name / "index.html")
        app = nodes["SoftwareApplication"]
        facts = [app["description"]]
        os_ = app.get("operatingSystem")
        if os_:
            facts.append("·".join(os_) if isinstance(os_, list) else os_)
        if app.get("offers", {}).get("price") == "0":
            facts.append("무료")
        stores = " · ".join(f"[{store_label(u)}]({u})" for u in app.get("sameAs", []))
        tail = f" {stores}" if stores else " 아직 스토어에 공개되지 않았습니다."
        lines.append(f"- [{page.titles[0].strip()}]({app['url']}): {' '.join(facts[:1])} "
                     f"{', '.join(facts[1:])}{'.' if len(facts) > 1 else ''}{tail}".replace("  ", " "))
    lines += ["", "## 정책 문서", ""]
    for card in cards.cards:
        name = card["href"].strip("./")
        if name not in apps:
            continue
        sources = json.loads((SITE / name / "policies" / "sources.json").read_text(encoding="utf-8"))
        brand = sources.pop("app")["brand"]
        for kind, label in DOCUMENT_LABELS.items():
            if kind in sources:
                lines.append(f"- [{brand} {label}]({base}/{name}/{kind}/)")
    others = [c for c in cards.cards if c["href"].strip("./") not in apps]
    if others:
        lines += ["", "## 조직 소개", ""]
        lines += [f"- [{c['t']}]({base}/{c['href'].lstrip('./')}): {c['d']}" for c in others]
    lines += ["", "## Optional", "", f"- [사이트맵]({base}/sitemap.xml)", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="쓰지 않고 커밋된 llms.txt 와 견준다")
    args = parser.parse_args()
    content = llms()
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != content:
            raise SystemExit("Outdated llms.txt — tools/render-llms.py 를 돌린다")
        print("OK llms.txt")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print("Wrote llms.txt")


if __name__ == "__main__":
    main()
