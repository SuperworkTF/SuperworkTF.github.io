# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown==3.10.3"]
# ///
"""시행일이 오면 개정본을 정본 자리로 올린다. **그 전에는 몇 번을 돌려도 아무 일도 안 한다.**

동작(멱등):
  · sources.json 에서 status == "upcoming" 이고 시행일(KST 자정)이 지났으면
     - 그 항목을 정본 자리(output = privacy/terms)로 돌리고 status → "current"
     - 날짜 폴더(privacy/2026-09-29 등)는 "dated" 항목으로 남긴다 — 공고문이 그 주소를 물고 있다
  · 그리고 render.py 를 돌려 페이지를 다시 쓴다.
  · 전환이 한 번 끝나면 status 가 "current" 라서 영원히 no-op — 크론이 내년에 또 돌아도 안전하다.

수동 테스트:  uv run --no-project jjallang/policies/switch_effective.py --at 2026-09-29T00:10+09:00
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
KST = timezone(timedelta(hours=9))


def main() -> int:
    argv = sys.argv[1:]
    now = datetime.now(KST)
    if len(argv) == 2 and argv[0] == "--at":          # 테스트용 시각 주입
        now = datetime.fromisoformat(argv[1])

    path = HERE / "sources.json"
    src = json.loads(path.read_text(encoding="utf-8"))
    switched = []

    for key in list(src):
        meta = src[key]
        if meta.get("status") != "upcoming":
            continue
        effective = datetime.strptime(meta["effective"], "%Y-%m-%d").replace(tzinfo=KST)
        if now < effective:
            print(f"아직  {key}: 시행일 {meta['effective']} 전 (지금 {now:%Y-%m-%d %H:%M} KST)")
            continue

        dated_output = meta["output"]                  # 예: privacy/2026-09-29
        canonical = meta.get("source", key)            # 예: privacy

        # 날짜 폴더는 고정 주소로 살려 둔다 — 배너를 "시행본 보존" 문장으로 바꾼다.
        src[f"{canonical}_{meta['effective'].replace('-', '_')}"] = {
            **meta, "status": "dated", "output": dated_output, "source": canonical,
        }
        # 개정본이 정본 자리에 선다.
        meta["status"] = "current"
        meta["output"] = canonical
        meta.pop("current", None)
        switched.append(key)

    if not switched:
        return 0

    path.write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("전환:", ", ".join(switched))
    # 같은 인터프리터로 렌더러를 돌린다(의존성 markdown 은 이 스크립트 헤더가 이미 요구한다).
    return subprocess.run([sys.executable, str(HERE / "render.py")]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
