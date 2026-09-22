# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""시행일이 오면 개정본이 정본 자리에 선다. **그 전에는 몇 번을 돌려도 아무 일도 안 한다.**

    uv run --no-project tools/switch-effective.py --all
    uv run --no-project tools/switch-effective.py jjallang --at 2026-09-29T00:10+09:00

## 공고 기간의 두 모양

앱마다 공고를 다르게 낸다. 어느 쪽이든 「시행 전인 판」에 `status: "upcoming"` 이 붙어 있고,
이 스크립트는 그 판의 시행일이 왔는지만 본다.

    (가) 개정본이 정본 자리에 먼저 선다 — 우르르
         `privacy`(upcoming, 개정본) · `privacy/2026-09-05`(지난 판)
         시행일에 **상태만 뒤집는다.** 글이 움직이지 않는다.

    (나) 개정본이 날짜 주소에 서고 정본 자리는 현행이 지킨다 — 짤랑
         `privacy`(current, 현행) · `privacy/2026-09-04`(같은 글) · `privacy/2026-09-29`(upcoming)
         시행일에 **개정본이 정본 자리로 올라온다.** 현행은 자기 날짜 주소에 남는다.

(나)에서 현행이 자기 날짜 주소를 안 가지고 있으면 올라오는 순간 **그 글이 사이트에서
사라진다.** 그래서 올리기 전에 그 자리가 있는지 확인하고, 없으면 멈춘다.

## 멱등이다

`upcoming` 이 없으면 no-op 이다. 크론이 날마다 돌아도, 이듬해에 또 돌아도 같다.

## 날짜는 KST 자정 기준이다

문서가 「2026-09-29부터 시행」이라고 적으면 그것은 한국 시각이다. 서버가 UTC 라도 뜻은 안 바뀐다.
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

# 정본 자리가 개정본을 물려받을 때 함께 옮기는 칸들. 여기 없는 칸은 정본 자리가 자기 것을
# 지킨다(`path` 는 자리 그 자체이므로 절대 안 옮긴다).
ADOPTED = ("source", "title", "effective", "announced", "sha256")


def apps() -> list[str]:
    return sorted(p.parent.parent.name for p in SITE.glob("*/policies/sources.json"))


def promote(kind: str, editions: list[dict], ready: dict) -> None:
    """(나) 날짜 주소의 개정본이 정본 자리로 올라온다."""
    canonical = editions[0]
    if canonical["path"] != kind:
        raise SystemExit(f"{kind}: 첫 항목이 정본 자리가 아니다")
    outgoing = canonical.get("effective")
    if outgoing:
        parked = any(e["path"] == f"{kind}/{outgoing}" for e in editions)
        if not parked:
            raise SystemExit(
                f"{kind}: 지금 정본({outgoing})이 자기 날짜 주소를 안 가지고 있다. "
                f"올리면 그 글이 사이트에서 사라진다 — {kind}/{outgoing} 판을 먼저 세운다")
    for key in ADOPTED:
        if key in ready:
            canonical[key] = ready[key]
        else:
            canonical.pop(key, None)
    canonical["status"] = "current"
    for key in ("upcoming", "upcoming_effective", "upcoming_announced"):
        canonical.pop(key, None)
    if outgoing:
        canonical["previous"] = f"./{outgoing}/"
        canonical["previous_label"] = f"{outgoing} 시행"
    # 날짜 주소는 고정 주소로 살려 둔다 — 공고문이 이 주소를 물고 있다.
    ready["status"] = "dated"
    ready.pop("current", None)


def switch_app(name: str, now: datetime) -> bool:
    path = SITE / name / "policies" / "sources.json"
    sources = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    for kind in ("privacy", "terms"):
        editions = sources[kind]["editions"]
        for edition in list(editions):
            if edition.get("status") != "upcoming":
                continue
            effective = edition.get("effective")
            if not effective:
                raise SystemExit(f"{name}/{kind}: upcoming 인데 effective 가 없다")
            if now.date() < date.fromisoformat(effective):
                continue

            if edition["path"] == kind:
                # (가) 자리에서 상태만 뒤집는다.
                edition["status"] = "current"
                previous = edition.pop("current", None)
                if previous:
                    edition.setdefault("previous", previous)
                if "previous_label" not in edition:
                    others = [e["path"].partition("/")[2] for e in editions if e["path"] != kind]
                    if others:
                        edition["previous_label"] = f"{max(others)} 시행"
            else:
                promote(kind, editions, edition)
            changed = True
            print(f"{name}/{kind}: {effective} 시행 — {edition['path']} 가 정본이 된다")

    if changed:
        path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(HERE / "render-policies.py"), name], check=True, cwd=SITE)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", nargs="?", help="앱 디렉터리 이름 (--all 이면 생략)")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--at", help="이 시각인 것처럼 돌린다 (리허설)")
    args = parser.parse_args()

    now = datetime.fromisoformat(args.at).astimezone(KST) if args.at else datetime.now(KST)
    names = apps() if args.all else ([args.app] if args.app else [])
    if not names:
        raise SystemExit("앱 이름을 대거나 --all 을 붙인다")

    if not [n for n in names if switch_app(n, now)]:
        print(f"전환할 것 없음 ({now:%Y-%m-%d %H:%M %Z})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
