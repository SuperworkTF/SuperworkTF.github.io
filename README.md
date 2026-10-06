# superwork.ai.kr

주식회사 케이티나스미디어가 만드는 앱들의 **개발자 웹사이트**다. 저장소 이름은
`SuperworkTF.github.io`, 주소는 커스텀 도메인 `superwork.ai.kr` 이다.

앱마다 **소개 페이지 한 장과 정책 문서**를 내고, 루트에 전 앱 공용 `app-ads.txt` 를 둔다.
이 README 는 **앱 이름을 늘어놓지 않는다.** 앱이 늘어도 이 파일은 그대로여야 한다 —
앱 하나에만 해당하는 사정은 그 앱 디렉터리의 `README.md` 에 적는다.

## 이 저장소가 존재하는 이유

`app-ads.txt` 는 **앱별 파일이 아니라 도메인별 파일**이다. AdMob 크롤러는 스토어
등록정보의 개발자 웹사이트 주소를 읽고 그 **루트 도메인**의 `/app-ads.txt` 만 본다.
프로젝트 사이트(`…github.io/<저장소>/`)는 그 자리가 될 수 없으므로, 조직 사이트 저장소
하나가 모든 앱의 파일을 맡는다.

게시자 ID 가 같으면 줄도 하나다. 미디에이션을 붙이거나 다른 AdMob 계정의 앱이 오면
**여기에만** 줄을 더한다 — 앱마다 복사본을 두면 반드시 갈린다.

## 구조

```text
/app-ads.txt                 전 앱 공용. 손대기 전에 위 문단을 읽는다
/robots.txt                  검색로봇 수집 규칙. 사이트맵 주소를 적는다
/sitemap.xml                 검색엔진에 내는 주소 목록 (생성물 — tools/render-sitemap.py)
/google*.html · /naver*.html 검색 등록 소유 확인 파일 (지우지 않는다 — 아래 「검색엔진」)
/<32자 16진수>.txt           IndexNow 키 (파일 이름 = 내용. 지우지 않는다)
/favicon.png · /favicon.ico  사이트 아이콘 (SuperWork 마크). 구글은 이 루트의 것 하나만 쓴다
/apple-touch-icon.png        같은 마크 180px
/superwork-512.png           루트 og:image · Organization logo
/<app>/icon-192.png · icon-512.png  그 앱의 아이콘(스토어에 올린 것) — 소개 페이지 아이콘·og:image
/index.html                  서비스 목록 (가나다순) · 조직 소개 링크
/Superwork_KTNasmedia/       회사 소개 — **다른 저장소**(SuperworkTF/Superwork_KTNasmedia)가 같은 도메인에 세운다.
                             사이트맵에 싣는다(tools/other-pages.json). /Superwork-Ideathon/ 도 다른 저장소다(noindex, 싣지 않음)
/<app>/index.html            앱 소개·문의
/<app>/styles.css            그 앱의 화면. 앱끼리 공유하지 않는다
/<app>/<문서>/index.html     정책 문서 (생성물 — 손으로 고치지 않는다)
/<app>/<문서>/<날짜>/        지난 판·공고 중인 개정본의 고정 주소
/<app>/policies/             정책 원본(Markdown)과 sources.json
/<app>/README.md             그 앱에만 해당하는 사정 (있을 때만)
/tools/                      공용 렌더러·시행일 자동 전환·검사
```

`<app>` 디렉터리 이름이 곧 주소다: `https://superwork.ai.kr/<app>/`.
`<문서>` 는 `privacy`(필수) · `terms` · `account-deletion` 중 **그 앱이 실제로 내는 것만** 둔다.
메뉴도 있는 문서만 건다. 어떤 문서를 낼지는 `<app>/policies/sources.json` 이 정한다.

## 원칙

1. **정본은 이 사이트다.** 정책 원본은 `<app>/policies/*.md` 한 벌이고, HTML 은 그 그림자다.
   아직 다른 곳(노션)이 정본인 앱은 `sources.json` 에 그렇게 적는다. 정본을 옮기는 것은
   사람이 정하는 일이다.
2. **HTML 을 손으로 고치지 않는다.** 정책 페이지는 전부 `tools/render-policies.py` 가 만든다.
3. **게시한 주소는 옮기지 않는다.** 스토어 심사 양식·약관 본문·앱이 이 주소를 물고 있다.
4. **박제를 고치지 않는다.** 지난 시행본은 그날의 글자다. 법적 내용·날짜·연락처·수치는
   승인 없이 바꾸지 않는다.
5. **정적 파일만 둔다.** 외부 스크립트·폰트·분석·추적 도구를 넣지 않는다. 빌드도 없다.
   예외는 하나 — 구조화 데이터(`<script type="application/ld+json">`)는 실행되지 않는 **데이터**라 둔다.
   `src` 를 단 것, 다른 `type` 은 안 된다(`tools/check-pages.py` 가 문다).
6. **공개할 것만 둔다.** 앱 소스·환경 파일·내부 검토 메모·템플릿 빈칸·노션 내부 경로를
   복사하지 않는다(렌더러가 일부 표식을 막지만, 전부를 막지는 못한다).

## 소개 페이지 — 앱의 성격이 드러나야 한다

소개 페이지는 템플릿을 채운 안내문이 아니라 **그 앱이 어떤 앱인지 한눈에 보이는 첫 화면**이다.

- **색과 글자는 앱에서 가져온다.** 앱 저장소의 디자인 토큰(테마 파일·디자인 결정 문서)을
  그대로 쓰고, `styles.css` 첫머리 주석에 출처를 적는다. 이 사이트에서 새 색을 짓지 않는다.
- **히어로는 그 앱이 실제로 하는 일을 보여 준다.** 앱의 핵심 장면을 HTML/CSS/SVG 로 그린다
  (예: 명세서 앱이면 명세서 한 장, 사진 정리 앱이면 남길 사진을 고르는 장면).
  이미지 파일보다 코드로 그린 그림을 우선한다. 예시 데이터를 쓰면 **예시라고 밝힌다.**
- **문장은 사실만 쓴다.** 기능·수치·「광고 없음」 같은 말은 앱 코드와 개인정보처리방침에
  비춰 참이어야 한다. 소개 문장이 방침과 어긋나면 방침이 맞다.
- **눈에 띄는 것은 하나만.** 움직임은 한 곳에서 한 번, `prefers-reduced-motion` 을 지킨다.
- **뼈대는 공통이다.** 건너뛰기 링크 · 브랜드와 메뉴(`aria-current`) · 문의 자리 ·
  정책 문서 링크 · 바닥의 「전체 앱 안내」. 정책 페이지가 쓰는 클래스(`legal-shell`,
  `policy-body`, `table-scroll` …)도 같은 `styles.css` 가 맡는다.
- **스토어에 있으면 스토어 단추를 건다.** 히어로의 `.actions` 에 `Google Play 에서 받기` ·
  `App Store 에서 받기`. 주소 모양은 `https://play.google.com/store/apps/details?id=<패키지>` ·
  `https://apps.apple.com/kr/app/id<숫자>` 하나로 쓴다. 아직 스토어에 없으면 걸지 않는다.
- **머리말은 검색엔진과 링크 미리보기가 읽는다.** canonical · og:* · 아이콘 · 구조화 데이터
  (`SoftwareApplication` + `BreadcrumbList`). 모양은 이미 있는 앱 소개를 따른다.
  제목·설명을 고치면 og:title·og:description·구조화 데이터의 description 도 같이 고친다.
  `tools/check-pages.py` 가 어긋남을 잡는다.
- 좁은 화면(360px)에서 가로 스크롤이 없고, 키보드 초점이 보여야 한다.

## 새 앱을 올릴 때

절차 전체는 **[`tools/ADDING-AN-APP.md`](tools/ADDING-AN-APP.md)** 에 있다. 요약:

1. `<app>/policies/` 에 원본과 `sources.json` 을 만들고 렌더러로 페이지를 만든다.
2. `<app>/index.html`·`styles.css` 로 소개 페이지를 만든다(위 절).
3. 루트 `index.html` 서비스 목록에 가나다순으로 카드 한 장을 더한다.
   `tools/render-sitemap.py` 를 돌려 사이트맵에 새 주소를 싣는다.
4. 스토어 등록정보의 **웹사이트** 칸에 `https://superwork.ai.kr/<app>/` 을 넣는다.
   이 칸이 비면 AdMob 은 `app-ads.txt` 를 찾지 못한다.

## 검사

```bash
uv run --no-project tools/render-policies.py <app>           # 만든다
uv run --no-project tools/render-policies.py --all --check   # 커밋된 HTML 이 원본과 같은가
uv run --no-project tools/test_render.py                     # 렌더러 단위 검사
uv run --no-project tools/render-sitemap.py                  # 사이트맵을 다시 쓴다
uv run --no-project tools/check-pages.py                     # 손으로 쓴 페이지의 머리말·구조화 데이터
uv run --no-project tools/indexnow.py --since HEAD^1 --dry-run  # IndexNow 로 보낼 주소
python3 -m http.server 8000                                  # 로컬에서 눈으로 본다
```

CI(`.github/workflows/policies.yml`)가 `--all --check` · `render-sitemap.py --check` · `check-pages.py` 를 돌린다 —
앱을 더해도 CI 를 고칠 필요가 없다. 시행일 자동 전환은 `.github/workflows/policy-switch.yml` 이 날마다 돈다.

게시 후:

```bash
curl -sI https://superwork.ai.kr/app-ads.txt       # 200 + text/plain
curl -sI https://superwork.ai.kr/<app>/            # 200
curl -sI https://superwork.ai.kr/<app>/privacy/    # 200
curl -s  https://superwork.ai.kr/sitemap.xml | grep -c '<url>'   # 사이트맵 주소 수
```

## 검색엔진 (구글 서치콘솔 · 네이버 서치어드바이저)

**검색에 서는 것은 루트 · 앱 소개 · 정책의 정본 자리뿐이다.** 정책의 날짜 주소(지난 판 · 공고
중인 개정본 · 정본과 같은 사본)는 렌더러가 `noindex` 를 달고, 사이트맵에서도 뺀다. 열리는 것은
그대로다(지우지 않는다). 정책 원본(`*/policies/`)·`tools/`·README 는
`robots.txt` 가 수집에서 뺀다.

**소유 확인 토큰은 지우지 않는다.** 구글은 토큰을 주기적으로 다시 확인하고, 사라지면 유예
기간 뒤 소유 권한이 풀린다. 확인된 소유자가 모두 풀리면 그 속성의 **모든 사용자**가 접근을
잃는다. 네이버 토큰도 같은 이유로 지우지 않는다.

  · 구글 서치콘솔 — 도메인 속성 `superwork.ai.kr` 은 가비아 DNS 의 TXT 레코드로 확인한다
    (이 저장소에는 아무것도 없다). URL 접두사 속성을 쓰면 루트의 `google<토큰>.html` 이 토큰이다
  · 네이버 서치어드바이저 — 루트의 `naver<토큰>.html` 이 토큰이다
  · 확인용 계정은 **회사 계정**이다. 개인 계정의 토큰만 남으면 그 사람이 떠날 때 기록과 권한이 같이 간다

**IndexNow.** Pages 빌드가 끝나면 `.github/workflows/indexnow.yml` 이 바뀐 주소(사이트맵에 있는
것만)를 `api.indexnow.org` 로 보낸다. 네이버 · Bing 외 참여 엔진에 함께 전해진다. 구글은 참여하지
않는다 — 구글은 사이트맵과 서치콘솔이 맡는다.

**AI 검색.** 구글은 AI Overviews·AI Mode 에 「따로 필요한 기술 요건이 없다」고 한다 — 색인되고
스니펫 대상이면 된다. 그래서 할 일은 같다: 중요한 내용을 **글자로** 쓰고, 구조화 데이터가 보이는
글과 맞고, 사이트와 스토어의 사실이 같아야 한다. `robots.txt` 는 모든 로봇을 받는다
(`OAI-SearchBot` · `Claude-SearchBot` · `PerplexityBot` · `Yeti` · `Bingbot` 포함). 학습용 로봇
(`GPTBot` · `ClaudeBot` · `Google-Extended`)도 받는다 — 사람이 정했다(2026-10-06). 막아도 검색·AI 검색
노출은 그대로다(각 사업자 문서: 설정이 서로 독립이다). 받는 까닭은 모델이 학습한 지식 안에도 앱이
바르게 남게 하려는 것이다.
`<meta name="robots" content="nosourceinfo">`(네이버 AI 출처설명 끄기)는 쓰지 않는다.
