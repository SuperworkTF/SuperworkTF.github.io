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
/index.html                  서비스 목록 (가나다순)
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
- 좁은 화면(360px)에서 가로 스크롤이 없고, 키보드 초점이 보여야 한다.

## 새 앱을 올릴 때

절차 전체는 **[`tools/ADDING-AN-APP.md`](tools/ADDING-AN-APP.md)** 에 있다. 요약:

1. `<app>/policies/` 에 원본과 `sources.json` 을 만들고 렌더러로 페이지를 만든다.
2. `<app>/index.html`·`styles.css` 로 소개 페이지를 만든다(위 절).
3. 루트 `index.html` 서비스 목록에 가나다순으로 카드 한 장을 더한다.
4. 스토어 등록정보의 **웹사이트** 칸에 `https://superwork.ai.kr/<app>/` 을 넣는다.
   이 칸이 비면 AdMob 은 `app-ads.txt` 를 찾지 못한다.

## 검사

```bash
uv run --no-project tools/render-policies.py <app>           # 만든다
uv run --no-project tools/render-policies.py --all --check   # 커밋된 HTML 이 원본과 같은가
uv run --no-project tools/test_render.py                     # 렌더러 단위 검사
python3 -m http.server 8000                                  # 로컬에서 눈으로 본다
```

CI(`.github/workflows/policies.yml`)가 `--all --check` 를 돌린다 — 앱을 더해도 CI 를 고칠
필요가 없다. 시행일 자동 전환은 `.github/workflows/policy-switch.yml` 이 날마다 돈다.

게시 후:

```bash
curl -sI https://superwork.ai.kr/app-ads.txt       # 200 + text/plain
curl -sI https://superwork.ai.kr/<app>/            # 200
curl -sI https://superwork.ai.kr/<app>/privacy/    # 200
```
