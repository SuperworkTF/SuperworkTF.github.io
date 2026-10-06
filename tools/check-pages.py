# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""손으로 쓰는 페이지(루트 · 앱 소개)의 머리말 검사 — 검색엔진과 링크 미리보기가 읽는 것.

    uv run --no-project tools/check-pages.py

정책 페이지는 렌더러가 만들고 `render-policies.py --check` 가 문다. 이 검사가 무는 것은
사람이 손으로 쓰는 `index.html` 들이다. 손으로 쓰는 곳은 갈라진다 — 제목을 고치고 og:title 을
잊거나, 스토어 단추를 더하고 구조화 데이터의 `sameAs` 를 잊는다. 그러면 검색엔진과 AI 검색이
**서로 다른 두 사실**을 읽는다.

## 무는 것

  · 제목·설명이 한 개씩 있고, og:title·og:description 이 그것과 **같다**
  · canonical 이 그 페이지의 절대 주소이고 og:url 이 그것과 같다
  · og:site_name 이 조직 이름(`SITE_NAME`)이다
  · og:image 가 이 사이트의 파일이고, 네이버 조건(150×150 초과 · 5,000 byte 이상 · 3:1 이하)을 넘는다
  · 아이콘(`rel="icon"`)이 한 개, 절대 주소, 이 사이트의 정사각 PNG 48px 이상이다
    (네이버: 절대 경로 · 같은 rel 한 개 · 32px 이상 권장 / 구글: 48px 초과 권장)
  · `<script>` 는 **구조화 데이터(`application/ld+json`) 뿐**이다. 실행되는 것·바깥을 부르는 것은 없다
  · 구조화 데이터가 읽히고, 보이는 글과 맞는다:
      루트 — WebSite·Organization 의 name 이 조직 이름, url 이 루트
      앱 — SoftwareApplication 의 name 이 `sources.json` 의 brand, url 이 canonical,
           description 이 meta description 안의 글, `sameAs` 가 본문의 스토어 단추와 같은 집합
  · 루트 목록에 모든 앱 소개가 걸려 있다
"""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import sys

SITE = Path(__file__).resolve().parent.parent
SITE_NAME = "SuperWork"
STORE = re.compile(r"^https://(play\.google\.com/store/apps/details\?id=[\w.]+|apps\.apple\.com/kr/app/id\d+)$")
CATEGORIES = {
    "GameApplication", "SocialNetworkingApplication", "TravelApplication", "ShoppingApplication",
    "SportsApplication", "LifestyleApplication", "BusinessApplication", "DesignApplication",
    "DeveloperApplication", "DriverApplication", "EducationalApplication", "HealthApplication",
    "FinanceApplication", "SecurityApplication", "BrowserApplication", "CommunicationApplication",
    "DesktopEnhancementApplication", "EntertainmentApplication", "MultimediaApplication",
    "HomeApplication", "UtilitiesApplication", "ReferenceApplication",
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles: list[str] = []
        self.meta: dict[str, list[str]] = {}
        self.links: dict[str, list[str]] = {}
        self.scripts: list[dict] = []
        self.anchors: list[str] = []
        self._in_title = False
        self._in_head = False
        self._script: dict | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "head":
            self._in_head = True
        # 머리말 밖의 <title>(SVG 그림의 접근성 제목 따위)은 문서 제목이 아니다.
        if tag == "title" and self._in_head:
            self._in_title = True
            self.titles.append("")
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta.setdefault(key, []).append(a.get("content") or "")
        elif tag == "link":
            for rel in (a.get("rel") or "").split():
                self.links.setdefault(rel, []).append(a.get("href") or "")
        elif tag == "script":
            self._script = {"attrs": a, "text": ""}
        elif tag == "a" and a.get("href"):
            self.anchors.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "head":
            self._in_head = False
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._script is not None:
            self.scripts.append(self._script)
            self._script = None

    def handle_data(self, data):
        if self._in_title:
            self.titles[-1] += data
        if self._script is not None:
            self._script["text"] += data


def origin() -> str:
    return "https://" + (SITE / "CNAME").read_text(encoding="utf-8").strip()


def png_size(path: Path) -> tuple[int, int]:
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("PNG 가 아니다")
    return struct.unpack(">II", head[16:24])


def local(url: str, base: str) -> Path:
    if not url.startswith(base + "/"):
        raise ValueError(f"이 사이트의 절대 주소가 아니다: {url}")
    return SITE / url[len(base) + 1:]


def one(errors: list[str], where: str, values: list[str] | None, what: str) -> str:
    values = values or []
    if len(values) != 1:
        errors.append(f"{where}: {what} 가 {len(values)}개다 (하나여야 한다)")
        return values[0] if values else ""
    return values[0]


def nodes_of(data) -> list[dict]:
    if isinstance(data, list):
        return [n for d in data for n in nodes_of(d)]
    if isinstance(data, dict) and "@graph" in data:
        return nodes_of(data["@graph"])
    return [data] if isinstance(data, dict) else []


def check(name: str | None, errors: list[str]) -> None:
    base = origin()
    path = SITE / (f"{name}/index.html" if name else "index.html")
    where = str(path.relative_to(SITE))
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    canonical_expected = f"{base}/{name}/" if name else f"{base}/"

    title = one(errors, where, page.titles, "<title>").strip()
    description = one(errors, where, page.meta.get("description"), "meta description")
    canonical = one(errors, where, page.links.get("canonical"), "canonical")
    if canonical != canonical_expected:
        errors.append(f"{where}: canonical 이 {canonical!r} — {canonical_expected!r} 여야 한다")
    for key, expected in (("og:url", canonical_expected), ("og:title", title),
                          ("og:description", description), ("og:site_name", SITE_NAME)):
        got = one(errors, where, page.meta.get(key), key)
        if got != expected:
            errors.append(f"{where}: {key} 가 {got!r} — {expected!r} 와 같아야 한다")

    image = one(errors, where, page.meta.get("og:image"), "og:image")
    try:
        file = local(image, base)
        w, h = png_size(file)
        if w <= 150 or h <= 150 or file.stat().st_size < 5000 or max(w, h) / min(w, h) > 3:
            errors.append(f"{where}: og:image 가 네이버 조건을 못 넘는다 ({w}x{h}, {file.stat().st_size} bytes)")
    except (ValueError, OSError) as e:
        errors.append(f"{where}: og:image — {e}")

    for rel in ("icon", "apple-touch-icon"):
        hrefs = page.links.get(rel, [])
        if len(hrefs) > 1:
            errors.append(f"{where}: rel={rel} 가 {len(hrefs)}개다 — 네이버는 같은 rel 이 여럿이면 반영하지 않을 수 있다")
    icon = one(errors, where, page.links.get("icon"), 'rel="icon"')
    try:
        w, h = png_size(local(icon, base))
        if w != h or w < 48:
            errors.append(f"{where}: 아이콘이 정사각 48px 이상이 아니다 ({w}x{h})")
    except (ValueError, OSError) as e:
        errors.append(f"{where}: 아이콘 — {e}")

    data = []
    for script in page.scripts:
        if script["attrs"].get("type") != "application/ld+json" or "src" in script["attrs"]:
            errors.append(f"{where}: 구조화 데이터가 아닌 <script> 가 있다 — README 원칙 5")
            continue
        try:
            data.extend(nodes_of(json.loads(script["text"])))
        except json.JSONDecodeError as e:
            errors.append(f"{where}: 구조화 데이터를 읽지 못한다 — {e}")
    types = {n.get("@type"): n for n in data}

    if name is None:
        for kind in ("WebSite", "Organization"):
            node = types.get(kind)
            if not node or node.get("name") != SITE_NAME or node.get("url") != canonical_expected:
                errors.append(f"{where}: {kind} 의 name·url 이 {SITE_NAME!r}·루트가 아니다")
        for app in apps():
            if f"./{app}/" not in page.anchors:
                errors.append(f"{where}: 서비스 목록에 ./{app}/ 이 없다")
        return

    brand = json.loads((SITE / name / "policies" / "sources.json").read_text(encoding="utf-8"))["app"]["brand"]
    node = types.get("SoftwareApplication")
    if not node:
        errors.append(f"{where}: SoftwareApplication 구조화 데이터가 없다")
        return
    if node.get("name") != brand:
        errors.append(f"{where}: SoftwareApplication.name 이 {node.get('name')!r} — brand {brand!r} 여야 한다")
    if node.get("url") != canonical_expected:
        errors.append(f"{where}: SoftwareApplication.url 이 canonical 과 다르다")
    if node.get("applicationCategory") not in CATEGORIES:
        errors.append(f"{where}: applicationCategory {node.get('applicationCategory')!r} 는 구글 지원 값이 아니다")
    if node.get("description", "") not in description:
        errors.append(f"{where}: SoftwareApplication.description 이 meta description 안에 없다 — 보이는 글과 맞춘다")
    if node.get("image") != image:
        errors.append(f"{where}: SoftwareApplication.image 가 og:image 와 다르다")
    stores = {href for href in page.anchors if STORE.match(href)}
    odd = {href for href in page.anchors if re.match(r"https://(play\.google\.com|apps\.apple\.com)/", href)} - stores
    if odd:
        errors.append(f"{where}: 스토어 링크 모양이 다르다 {sorted(odd)} — {STORE.pattern}")
    if set(node.get("sameAs", [])) != stores:
        errors.append(f"{where}: sameAs {sorted(node.get('sameAs', []))} 와 본문 스토어 단추 {sorted(stores)} 가 다르다")
    if stores and node.get("offers", {}).get("price") != "0":
        errors.append(f"{where}: 스토어에 있는 앱인데 offers.price 가 \"0\" 이 아니다")


def apps() -> list[str]:
    return sorted(p.parent.parent.name for p in SITE.glob("*/policies/sources.json"))


def main() -> None:
    errors: list[str] = []
    names: list[str | None] = [None, *apps()]
    for name in names:
        check(name, errors)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK {len(names)} 페이지: 머리말 · 아이콘 · 구조화 데이터가 보이는 글과 맞는다")


if __name__ == "__main__":
    main()
