# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""시행일이 오면 개정본이 정본 자리로 올라간다. **그 전에는 몇 번을 돌려도 아무 일도 안 한다.**

    uv run --no-project tools/switch-effective.py --all
    uv run --no-project tools/switch-effective.py ururu --at 2026-09-23T00:10+09:00

## 무엇을 바꾸는가

`policies/sources.json` 의 `status` 한 글자다. 공고된 문서는 이미 정본 자리(`privacy/`)에
서 있고, 머리말만 「아직 시행 전이며 지금 시행 중인 것은 여기」라고 말하는 중이다
(`status: "upcoming"`). 시행일이 지나면 그 말이 거짓이 되므로 `current` 로 바꾸고 다시 렌더한다.

    upcoming  →  current

## 멱등이다

`current` 가 된 뒤에는 바꿀 것이 없어 no-op 이다. 크론이 이듬해에 또 돌아도 안전하고,
사람이 손으로 여러 번 돌려도 같다.

## 날짜는 KST 자정 기준이다

문서가 「2026-09-23부터 시행」이라고 적으면 그것은 한국 시각이다. 서버가 UTC 라도 그 문장의
뜻은 안 바뀐다.

## 짤랑은 자기 스크립트를 쓴다

`jjallang/policies/switch_effective.py`. 그쪽은 문서가 **날짜 폴더에 서고 시행일에 정본
자리로 옮겨 오는** 모양이라 이 스크립트와 하는 일이 다르다. 짤랑이 공용 렌더러로 옮겨 올 때
함께 본다(`tools/ADDING-AN-APP.md` 의 「아직 안 끝난 일」).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
KST = timezone(timedelta(hours=9))


def apps() -> list[str]:
    return sorted(p.parent.parent.name for p in SITE.glob("*/policies/sources.json"))


def switch_app(name: str, now: datetime) -> bool:
    """`upcoming` 인 문서 가운데 시행일이 지난 것을 `current` 로 돌린다. 바꿨으면 True."""
    path = SITE / name / "policies" / "sources.json"
    sources = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    for kind, meta in sources.items():
        if kind == "app" or not isinstance(meta, dict):
            continue
        if meta.get("status") != "upcoming":
            continue
        effective = meta.get("effective")
        if not effective:
            raise SystemExit(f"{name}/{kind}: status 가 upcoming 인데 effective 가 없다")
        if now.date() < date.fromisoformat(effective):
            continue

        meta["status"] = "current"
        # `current` 머리말은 이전 시행본을 이름으로 든다. 공고 기간에 그 자리를 가리키던
        # `current` 키가 그대로 그 주소다 — 옮겨 적지 않고 이름만 바꾼다.
        previous = meta.pop("current", None)
        if previous and "previous" not in meta:
            meta["previous"] = previous
        if "previous_label" not in meta:
            archives = meta.get("archives") or []
            if archives:
                meta["previous_label"] = f"{archives[-1]['version']} 시행"
        changed = True
        print(f"{name}/{kind}: {effective} 시행 — 정본 자리로 올린다")

    if changed:
        path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        subprocess.run(
            [sys.executable, str(HERE / "render-policies.py"), name],
            check=True, cwd=SITE,
        )
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", nargs="?", help="앱 디렉터리 이름 (--all 이면 생략)")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--at", help="이 시각인 것처럼 돌린다 (손으로 시험할 때)")
    args = parser.parse_args()

    now = datetime.fromisoformat(args.at).astimezone(KST) if args.at else datetime.now(KST)
    names = apps() if args.all else ([args.app] if args.app else [])
    if not names:
        raise SystemExit("앱 이름을 대거나 --all 을 붙인다")

    changed = [name for name in names if switch_app(name, now)]
    if not changed:
        print(f"전환할 것 없음 ({now:%Y-%m-%d %H:%M %Z})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
