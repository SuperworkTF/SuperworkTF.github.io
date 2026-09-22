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

## 그려보카 공개 사이트

그려보카의 소개·문의·정책 문서는 이 공개 저장소의 `word-doodle/` 에 둔다.
앱 소스는 별도의 비공개 저장소에 유지한다. 앱 코드, 환경 파일, 비공개 문서나
Notion 상위 경로·내부 메타데이터를 이 저장소에 복사하지 않는다.

### 파일 구조

```text
/word-doodle/index.html           ← 그려보카 소개·문의
/word-doodle/styles.css           ← 그려보카 페이지 공용 로컬 스타일
/word-doodle/privacy/index.html   ← 개인정보처리방침
/word-doodle/terms/index.html     ← 서비스 이용약관
/word-doodle/policies/privacy.md  ← 공개 정책 본문 원본
/word-doodle/policies/terms.md    ← 공개 약관 본문 원본
/word-doodle/policies/sources.json ← 공개 Notion 원문 링크·제목
/word-doodle/policies/render.py   ← 정책 HTML 갱신 도구(배포 시 실행 불필요)
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
2. 정책을 갱신할 때는 먼저 승인된 공개 원문을 확인한다.
   `word-doodle/policies/` 의 Markdown에는 **공개 정책 본문만** 보관한다.
   법적 내용·날짜·연락처·수치는 임의로 고치지 않는다. 원문과 앱의 차이는 별도로 검토한다.
   각 일반 문단은 한 줄로, 목록 항목은 연속된 줄로 저장한다. 중첩 목록은 탭으로 들여쓴다.
   표는 기존 `<table header-row="true">` 형식을 사용하며 셀 안의 Markdown도 렌더링한다.
3. 원문 링크·제목은 `sources.json` 에서 관리한다. 정책 HTML은 아래 도구로 생성한다.
   [uv](https://docs.astral.sh/uv/) 가 있으면 고정 버전 Markdown 도구를 별도 환경에서 실행한다.
   이 도구는 개발용이며 정적 사이트 배포에는 Python·uv·의존성이 필요하지 않다.

   ```bash
   uv run --no-project word-doodle/policies/render.py
   uv run --no-project word-doodle/policies/render.py --check
   ```

   생성기는 정책의 문구 순서와 링크를 대조하며, `--check` 는 파일을 변경하지 않고
   Markdown과 HTML의 일치를 확인한다. 정책 시행일은 원문의 날짜를 그대로 유지한다.
4. 로컬에서 `python3 -m http.server 8000` 으로 확인한다.
   `http://localhost:8000/word-doodle/` 부터 세 페이지의 메뉴, 원문 링크, 문의 링크,
   키보드 초점, 좁은 화면의 표 가로 스크롤을 점검한다.
5. 기존 `jjallang/`, `robots.txt`, `.nojekyll` 과 `app-ads.txt` 의 판매자 줄은 유지한다.
   `git diff` 를 검토하고 정적 HTML/CSS와 공개 정책 본문만 게시한다.

```bash
curl -sI https://superworktf.github.io/word-doodle/
curl -sI https://superworktf.github.io/word-doodle/privacy/
curl -sI https://superworktf.github.io/word-doodle/terms/
```
