# superworktf.github.io

앱들의 **개발자 웹사이트**다. 이 도메인의 루트가 목적이고, 그 루트에 `app-ads.txt` 가 선다.

## 이 저장소가 존재하는 이유

`app-ads.txt` 는 **앱별 파일이 아니라 도메인별 파일**이다.
AdMob 크롤러는 스토어 등록정보의 개발자 웹사이트 주소를 읽고 그 **루트 도메인**의
`/app-ads.txt` 만 본다. GitHub Pages 의 프로젝트 사이트는 `…github.io/<저장소>/` 하위 경로라
그 자리가 될 수 없다. 그래서 **조직 사이트 저장소 하나**가 모든 앱의 파일을 대신 맡는다.

게시자 ID 가 하나이므로 줄도 하나다. 앱이 몇 개든 이 파일 하나로 끝난다.
나중에 미디에이션(AppLovin·Unity·Meta 등)을 붙이면 **여기에만** 줄을 추가한다 —
앱마다 복사본을 두면 반드시 갈린다.

## 구조

```
/app-ads.txt          ← 전 앱 공용. 손대는 사람은 위 문단을 먼저 읽을 것
/index.html           ← 앱 목록
/<앱>/index.html      ← 앱별 안내 페이지
```

## 새 앱을 추가할 때

1. `/<앱>/index.html` 을 만든다(짤랑 페이지를 복사해 고치면 된다).
2. `/index.html` 의 목록에 카드 한 장을 더한다.
3. **스토어 등록정보의 `웹사이트` 칸**에 `https://superworktf.github.io/<앱>/` 을 넣는다.
   이 칸이 비면 AdMob 은 app-ads.txt 를 영원히 못 찾는다. (짤랑이 그래서 막혀 있었다)
4. 새 앱이 **다른 AdMob 계정**이면 그 게시자 줄을 `app-ads.txt` 에 한 줄 더한다.

## 확인

```bash
curl -sI https://superworktf.github.io/app-ads.txt   # 200 + text/plain 이어야 한다
curl -s  https://superworktf.github.io/app-ads.txt
```
AdMob → 앱 → 앱 설정 → app-ads.txt 에서 상태를 본다. 크롤링은 보통 하루 안에 돈다.

## 셀렉터(Piclect) 공개 사이트

셀렉터의 소개·문의·정책 문서는 이 공개 저장소의 `piclect/` 에 둔다.
앱 소스는 별도의 비공개 저장소에 유지한다. 앱 코드, 환경 파일, 비공개 문서나
Notion 상위 경로·내부 메타데이터를 이 저장소에 복사하지 않는다.

`word-doodle/` 과 같은 구조·같은 검증 파이프라인을 쓰되, **화면은 공유하지 않는다.**
셀렉터는 앱 저장소 `.agent/DECISIONS.md` D-020·D-025·D-029 의 팔레트
(surface `#0B0B0C`, raised `#17171A`, accent Signal Lime `#D4F24A`, ink `#F2F4F6`,
muted `#B0B8C1`)를 그대로 쓴다. 사진을 판단하기에 가장 좋은 바탕이 근-검정이고,
경쟁 아이콘 150개 측정에서 ΔE00 15 안에 경쟁자가 없던 유일한 색이 라임이었다는
근거가 그 결정에 달려 있다. 이 사이트의 색을 바꾸려면 그 결정부터 읽는다.

### 파일 구조

```text
/piclect/index.html            ← 셀렉터 소개·문의
/piclect/styles.css            ← 셀렉터 페이지 공용 로컬 스타일(근-검정 + Signal Lime)
/piclect/privacy/index.html    ← 개인정보처리방침(생성물)
/piclect/terms/index.html      ← 서비스 이용약관(생성물)
/piclect/policies/privacy.md   ← 공개 정책 본문 원본
/piclect/policies/terms.md     ← 공개 약관 본문 원본
/piclect/policies/sources.json ← 공개 Notion 원문 링크·제목
/piclect/policies/render.py    ← 정책 HTML 갱신 도구(배포 시 실행 불필요)
```

### 배포 주소 — 바꾸지 말 것

- 소개·문의: <https://superworktf.github.io/piclect/>
- 개인정보처리방침: <https://superworktf.github.io/piclect/privacy/>
- 서비스 이용약관: <https://superworktf.github.io/piclect/terms/>

뒤의 두 주소는 **공개된 「서비스 이용약관」 제17조 제2항이 직접 인용**하고 있고
Play Console 등록정보에도 들어간다. 경로를 옮기면 법적 문서가 죽은 주소를 가리킨다.
`render.py` 는 약관 원문에서 이 두 주소가 사라지면 생성을 실패시킨다.

### 문구 규칙 — 이 페이지에서 가장 중요한 부분

앱 저장소는 하루 동안 앱·스토어 등록정보·공개 약관에서 **거짓 문장 일곱 개**를 걷어냈다
(`.agent/FINDINGS.md` F-26..F-34). 그 결과가 이 페이지의 문장이다. 고치기 전에 근거를 읽는다.

- 검토 화면에 없는 것은 **배너**다. 「광고를 넣지 않았다」가 아니다. 삭제를 마치고
  다음 사진으로 넘어갈 때 **전면 광고가 나올 수 있다**(F-30). 한도는 `AdPolicy` 상수
  그대로 — 첫 세션 차단, 90초 간격, 세션당 3회, 하루 6회.
- 복구 가능 여부는 플랫폼마다 다르다. iOS·Android 11 이상은 휴지통으로 가고,
  **Android 10 이하는 즉시 삭제되어 되돌릴 수 없다**(F-27).
- 확보 용량은 **운영체제가 실제로 지웠다고 알려온 것만** 센다.
- 리워드 광고의 보상은 **흐릿함 기준이 넓어지는 것**이지 검사 기간이 아니다(F-28).
- 구독·인앱 결제·계정은 셋 다 없다.

### 정책을 갱신할 때

1. 소개·레이아웃은 `piclect/index.html` 과 `piclect/styles.css` 에서 수정한다.
   외부 스크립트·폰트·분석·추적 도구를 넣지 않는다.
2. 정책은 승인된 공개 Notion 원문에서만 옮긴다. `piclect/policies/` 의 Markdown에는
   **공개 정책 본문만** 보관한다. 법적 내용·날짜·연락처·수치는 임의로 고치지 않는다.
   각 일반 문단은 한 줄로, 목록 항목은 연속된 줄로 저장한다. 중첩 목록은 탭으로 들여쓴다.
   표는 `<table header-row="true">` 형식을 쓰며 셀 안의 Markdown도 렌더링한다.
   셀 안의 줄바꿈은 `<br>` 로 적는다.
3. 원문 링크·제목은 `sources.json` 에서 관리하고, 정책 HTML은 아래 도구로 생성한다.

   ```bash
   uv run --no-project piclect/policies/render.py
   uv run --no-project piclect/policies/render.py --check
   ```

   생성기는 Markdown 원문을 줄·셀 단위로 다시 읽어 **문구 순서와 모든 링크**를 대조하고,
   `--check` 는 파일을 바꾸지 않은 채 체크인된 HTML이 원문에서 밀렸는지 확인한다.
4. 로컬에서 `python3 -m http.server 8000` 으로 확인한다.
   `http://localhost:8000/piclect/` 부터 세 페이지의 메뉴, 원문 링크, 문의 링크,
   키보드 초점, 좁은 화면의 표 가로 스크롤을 점검한다.

```bash
curl -sI https://superworktf.github.io/piclect/
curl -sI https://superworktf.github.io/piclect/privacy/
curl -sI https://superworktf.github.io/piclect/terms/
```

## 그려보카 공개 사이트

그려보카의 소개·문의·정책 문서 정본은 이 저장소에서 배포하는 **GitHub Pages**다.
정책 본문은 `word-doodle/policies/` 의 Markdown에서 관리하고, 공개 문서는
`word-doodle/` 에 둔다. 이후 개정과 이전 방침도 이 사이트에서 관리한다.
앱 소스는 별도의 비공개 저장소에 유지한다. 앱 코드, 환경 파일, 비공개 문서나
내부 템플릿·작성 안내·메타데이터를 이 저장소에 복사하지 않는다.

### 파일 구조

```text
/word-doodle/index.html           ← 그려보카 소개·문의
/word-doodle/styles.css           ← 그려보카 페이지 공용 로컬 스타일
/word-doodle/privacy/index.html   ← 개인정보처리방침
/word-doodle/terms/index.html     ← 서비스 이용약관
/word-doodle/policies/privacy.md  ← 공개 정책 본문 원본
/word-doodle/policies/privacy-2026-09-09.md ← 정비 전 방침 전문(수정 금지)
/word-doodle/privacy/2026-09-09/index.html ← 정비 전 방침 공개 보관
/word-doodle/policies/terms.md    ← 공개 약관 본문 원본
/word-doodle/policies/sources.json ← 공식 공개 주소·문서 제목
/word-doodle/policies/render.py   ← 정책 HTML 갱신 도구(배포 시 실행 불필요)
/word-doodle/policies/test_render.py ← 생성기·보관본·비공개 표식 차단 회귀 검사
```

### 배포 주소

- 소개·문의: <https://superworktf.github.io/word-doodle/>
- 개인정보처리방침: <https://superworktf.github.io/word-doodle/privacy/>
- 서비스 이용약관: <https://superworktf.github.io/word-doodle/terms/>

모두 빌드가 필요 없는 정적 HTML/CSS 파일이다. 기존 GitHub Pages 설정을 사용한다.
별도의 앱 저장소 공개나 Pages 설정 변경은 필요하지 않다. 배포 주소는 게시 후
HTTP 응답과 본문을 확인한다. 스토어 링크는 실제 공개 등록정보가 확인되기 전까지 추가하지 않는다.

### 소개·정책을 갱신할 때

1. 소개·레이아웃은 `word-doodle/index.html` 과 `word-doodle/styles.css` 에서 수정한다.
   외부 스크립트·폰트·분석·추적 도구를 넣지 않는다.
2. 정책을 갱신할 때는 이 저장소의 현재 정본과 승인된 변경 내용을 확인한다.
   `word-doodle/policies/` 의 Markdown에는 **공개 정책 본문만** 보관한다.
   법적 내용·날짜·연락처·수치는 임의로 고치지 않는다. 방침과 앱의 차이는 별도로 검토한다.
   각 일반 문단은 한 줄로, 목록 항목은 연속된 줄로 저장한다. 중첩 목록은 탭으로 들여쓴다.
   표는 기존 `<table header-row="true">` 형식을 사용하며 셀 안의 Markdown도 렌더링한다.
3. 공식 공개 주소·제목은 `sources.json` 에서 관리한다. 정책 HTML은 아래 도구로 생성한다.
   [uv](https://docs.astral.sh/uv/) 가 있으면 고정 버전 Markdown 도구를 별도 환경에서 실행한다.
   이 도구는 개발용이며 정적 사이트 배포에는 Python·uv·의존성이 필요하지 않다.

   ```bash
   uv run --no-project word-doodle/policies/render.py
   uv run --no-project word-doodle/policies/render.py --check
   uv run --no-project word-doodle/policies/test_render.py
   ```

   생성기는 정책의 문구 순서와 링크를 대조하며, `--check` 는 파일을 변경하지 않고
   Markdown과 HTML의 일치를 확인한다. 단순한 게시 위치·표현 수정으로 정책 시행일을 바꾸지 않는다.
   실질적인 개정은 기존 고지 약속을 지키고 승인된 공고일·시행일을 사용한다.
   이전 방침 전문과 적용기간은 날짜별 공개 경로에 보존하고 새 방침에서 연결한다.
   문서 정비만 하는 경우에는 기존 시행일과 실제 문서 정비일을 구분하여 표시한다.
   같은 시행일의 이전 문서에 임의의 적용 종료일을 만들지 않는다.
   `sources.json`의 `archives`에는 보관본의 날짜형 `version`과 공개 안내문 `notice`를 둔다.
   생성기는 해당 `privacy-YYYY-MM-DD.md`를 읽어 보관 경로까지 함께 생성·검증한다.
   이전 전문은 수정하지 않으며, 내부 검토 표식·템플릿 빈칸이 있으면 생성을 중단한다.
4. 로컬에서 `python3 -m http.server 8000` 으로 확인한다.
   `http://localhost:8000/word-doodle/` 부터 세 페이지의 메뉴, 공식 정책 링크, 문의 링크,
   키보드 초점, 좁은 화면의 표 가로 스크롤을 점검한다.
5. 다른 앱의 페이지와 `robots.txt`, `.nojekyll`, `app-ads.txt` 는 유지한다.
   `git diff` 를 검토하고 정적 HTML/CSS와 공개 정책 본문만 게시한다.

```bash
curl -sI https://superworktf.github.io/word-doodle/
curl -sI https://superworktf.github.io/word-doodle/privacy/
curl -sI https://superworktf.github.io/word-doodle/terms/
```
