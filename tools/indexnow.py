# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""IndexNow — 바뀐 주소를 검색엔진에 바로 알린다.

    uv run --no-project tools/indexnow.py --since HEAD^1 --dry-run   # 무엇을 보낼지만 본다
    uv run --no-project tools/indexnow.py --since HEAD^1             # 보낸다
    uv run --no-project tools/indexnow.py --all                       # 사이트맵 전부

## 왜

네이버 서치어드바이저와 Bing 이 IndexNow 를 받는다. 한 곳(api.indexnow.org)에 보내면 참여
엔진(Bing · Naver · Yandex · Seznam · Yep · Amazonbot · Internet Archive)에 함께 전해진다.
Bing 색인은 Copilot 같은 AI 검색에도 쓰인다. **구글은 참여하지 않는다** — 구글은 사이트맵과
서치콘솔로 다룬다. IndexNow 는 사이트맵을 대신하지 않는다(사이트맵은 그대로 둔다).

## 무엇을 보내나

`--since <rev>` 와 지금(HEAD) 사이에 바뀐 파일을 주소로 바꾸고, **사이트맵에 있는 주소만**
보낸다. 날짜 주소(noindex)나 원본 md 는 사이트맵에 없으므로 보내지 않는다. 바뀐 그림
(`<app>/icon-512.png` 등)은 그 디렉터리의 소개 페이지로 친다.

## 키

루트의 `<key>.txt` 한 개가 키다. 파일 이름과 내용이 같다(IndexNow 규칙). 키는 공개 값이다 —
비밀이 아니다. 키 파일을 지우면 엔진이 요청을 거절한다(403).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request

SITE = Path(__file__).resolve().parent.parent
ENDPOINT = "https://api.indexnow.org/indexnow"


def key() -> str:
    found = [p for p in SITE.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)
             and p.read_text(encoding="utf-8").strip() == p.stem]
    if len(found) != 1:
        raise SystemExit(f"IndexNow 키 파일이 하나여야 한다 — {[p.name for p in found]}")
    return found[0].stem


def host() -> str:
    return (SITE / "CNAME").read_text(encoding="utf-8").strip()


def sitemap_urls() -> list[str]:
    text = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", text)


def changed_urls(since: str) -> list[str]:
    files = subprocess.run(["git", "diff", "--name-only", since, "HEAD"], cwd=SITE,
                           check=True, capture_output=True, text=True).stdout.split()
    base = f"https://{host()}/"
    candidates = set()
    for f in files:
        parts = f.split("/")
        if parts[-1] == "README.md" or parts[0] in {"tools", ".github"}:
            continue                                 # 사람이 읽는 문서 · 도구는 페이지가 아니다
        if len(parts) == 1:
            candidates.add(base)                     # 루트의 파일(index.html · favicon …)
        elif parts[-1] == "index.html":
            candidates.add(base + "/".join(parts[:-1]) + "/")
        elif parts[1] != "policies":
            candidates.add(base + parts[0] + "/")    # 그 앱의 그림·스타일 → 소개 페이지
    listed = sitemap_urls()
    return [u for u in listed if u in candidates]


def submit(urls: list[str], dry_run: bool) -> None:
    if not urls:
        print("보낼 주소가 없다")
        return
    payload = {"host": host(), "key": key(), "keyLocation": f"https://{host()}/{key()}.txt", "urlList": urls}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if dry_run:
        return
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow {response.status} — {len(urls)} 주소")
    except urllib.error.HTTPError as e:
        # 202 는 성공 쪽(키 확인 중)이다. 400·403·422·429 는 실패다.
        print(f"IndexNow {e.code} — {e.read().decode('utf-8', 'replace')[:300]}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--since", help="이 커밋 이후 바뀐 파일만 (예: HEAD^1)")
    group.add_argument("--all", action="store_true", help="사이트맵의 주소 전부")
    parser.add_argument("--dry-run", action="store_true", help="보내지 않고 보낼 내용만 찍는다")
    args = parser.parse_args()
    key()  # 키 파일이 없으면 여기서 멈춘다
    urls = sitemap_urls() if args.all else changed_urls(args.since)
    submit(urls, args.dry_run)


if __name__ == "__main__":
    main()
