# 새 앱을 이 사이트에 올리는 법

이 저장소는 `superwork.ai.kr` 다 (저장소 이름은 `SuperworkTF.github.io`, 주소는 커스텀 도메인). 앱마다 **소개 페이지 한 장과 정책 문서**를 낸다.
스토어 심사 양식과 감사 제출에 나가는 주소가 여기이므로, 틀린 채로 나가면 새 심사로만 고친다.

이 문서는 **다른 저장소에서 앱을 만든 사람(또는 에이전트)** 이 읽는다.

---

## 0. 먼저 알아야 하는 것 셋

**① HTML 을 손으로 고치지 않는다.** 정책 페이지는 전부 `tools/render-policies.py` 가 만든다.
손으로 고치면 원본과 갈라지고, 갈라진 뒤에는 **어느 쪽이 사실인지 아무도 모른다.**

**② 원본은 마크다운 한 벌이다.** `<app>/policies/*.md` 가 승인된 낱말이고 HTML 은 그것의
그림자다. 판(version)마다 md 가 하나씩 있어야 한다 — 지난 시행본도 마찬가지다.

**③ 정본은 이 사이트다.** 문서 안에서 「다른 곳이 원문」이라고 말하지 않는다. 아직 노션이
정본인 단계라면 그 사실을 `sources.json` 에 `"notion_source": true` 로 적는다(그러면 렌더러가
원문 링크를 붙이고 `canonical` 을 안 낸다). 정본을 옮기는 것은 **사람이 정하는 일**이다.

---

## 1. 디렉터리를 만든다

    <app>/
      index.html          소개 페이지
      styles.css          이 앱의 색. 뼈대는 다른 앱에서 복사한다
      policies/
        sources.json      브랜드·주소·시행 상태
        privacy.md        개인정보처리방침 원본
        terms.md          서비스 이용약관 원본

디렉터리 이름이 곧 주소다: `superwork.ai.kr/<app>/privacy/`.

## 2. `policies/sources.json`

    {
      "app": {
        "dir": "<app>",              디렉터리 이름과 같아야 한다. 다르면 렌더러가 멈춘다
        "brand": "앱 이름",
        "theme_color": "#RRGGBB"     소개 페이지의 <meta name="theme-color"> 와 같게
      },
      "privacy": {
        "title": "개인정보처리방침",
        "public_url": "https://superwork.ai.kr/<app>/privacy/"
      },
      "terms": {
        "title": "서비스 이용약관",
        "public_url": "https://superwork.ai.kr/<app>/terms/"
      }
    }

### 쓸 수 있는 값들 (전부 선택)

| 키 | 뜻 |
|---|---|
| `sha256` | 승인된 원본의 지문. 있으면 md 가 그 지문과 다를 때 멈춘다. **법정 문장을 바꾸려면 이 값을 일부러 고쳐야 한다** |
| `notion_source` | `true` 면 「원문 보기(Notion)」를 머리말에 적고 `canonical` 을 안 낸다 |
| `status` | `upcoming` · `current` · `dated`. 공고 기간에 **어느 쪽이 오늘 시행 중인지**를 문서가 스스로 말한다 |
| `effective` · `announced` | `status` 와 함께 쓰는 날짜 |
| `current` · `previous` · `previous_label` | `status` 가 가리키는 다른 판의 주소 |
| `archives` | 지난 시행본 목록. `[{"version": "2026-09-05", "notice": "…"}]` |

`archives` 를 적으면 `<kind>-<version>.md` 를 함께 둔다. 예: `privacy-2026-09-05.md`.
**지난 판에도 md 가 있어야 한다** — 없으면 그 HTML 은 다시 만들 수도 검사할 수도 없는 고아가
된다(짤랑이 지금 그 상태다).

## 3. 원본 마크다운 규칙

  · 첫 줄은 `# <브랜드> <문서 제목>` 이고 `sources.json` 의 `brand`·`title` 과 정확히 같아야 한다
  · **한 문단이 한 줄**이다. 빈 줄로 나누지 않는다
  · 목록은 `- ` 또는 `1. `. 이어진 줄이 한 목록이 된다
  · 인용(`> `)은 공고 안내 같은 알림 상자다. 이어진 줄은 **한 덩어리**가 된다
  · 표는 날것의 HTML 로 적는다: `<table header-row="true">` · `<tr>` · `<td>`. 첫 줄이 머리다
  · 셀 안에는 인라인 마크다운을 쓸 수 있다

## 4. 만들고 검사한다

    uv run --no-project tools/render-policies.py <app>           # 쓴다
    uv run --no-project tools/render-policies.py <app> --check   # 쓰지 않고 견준다
    uv run --no-project tools/render-policies.py --all --check   # 전부
    uv run --no-project tools/test_render.py                     # 렌더러 단위 검사

렌더러가 자동으로 무는 것 넷:

  · **충실성** — 렌더된 본문의 글자와 링크를 원본에서 다시 읽어 대조한다. 어긋나면 던진다
  · **정적** — `<script>`·`<iframe>`·`onclick=`·`javascript:` 같은 것이 섞이면 던진다
  · **초안 금지** — 공개용이 아닌 표시가 남아 있으면 던진다
  · **지문** — `sha256` 이 있으면 승인된 원본과 같은지 본다

## 4-1. 공고와 시행 사이 — **시행일은 저절로 온다**

법정 문서를 고치면 공고일과 시행일이 갈린다(보통 7일). 그 사이에는 **문서가 둘**이고, 읽는
사람이 어느 쪽이 오늘 시행 중인지 알아야 한다.

    공고하는 날
      · 개정본을 `privacy.md` 로 올린다 (정본 자리에 선다)
      · 직전 판을 `privacy-<이전시행일>.md` 로 박제하고 `archives` 에 적는다
      · `status: "upcoming"` · `effective` · `announced` · `current: "./<이전시행일>/"`

    시행일 00:00 KST
      · `.github/workflows/policy-switch.yml` 이 날마다 돌며 그날을 잡는다
      · `status` 가 `current` 로 바뀌고 페이지가 다시 쓰인다 — **사람이 할 일이 없다**

손으로 시험할 수 있다:

    uv run --no-project tools/switch-effective.py <app> --at 2026-09-23T00:10+09:00

멱등이다. 전환된 뒤에는 몇 번을 돌려도 no-op 이라 크론이 이듬해에 또 돌아도 안전하다.

**박제를 고치지 않는다.** 지난 시행본은 그날의 글자다. 주소나 오타가 눈에 거슬려도 그대로
둔다 — 고치면 기록을 조작하는 것이 된다.

## 5. 목록에 올린다

루트 `index.html` 의 **서비스 목록**에 카드 한 장을 더한다.

  · 차례는 **가나다순**이다. 만든 순서나 중요도로 두면 앱이 늘 때마다 다시 정해야 한다
  · 설명은 그 앱의 `index.html` 이 자기 `<meta name="description">` 에 적은 문장을 따른다.
    여기서 새로 지으면 설명이 두 벌이 되고, 갈라지는 쪽은 **아무도 안 고치는 이 목록**이다

## 6. 소개 페이지

다른 앱의 `index.html` 을 복사해 뼈대를 쓴다(`word-doodle` 이 기준이다). 바꾸는 것은
**색과 히어로**다 — 히어로는 그 앱이 실제로 내는 그림이어야 한다.

뼈대가 들고 있는 것(지우지 않는다): 건너뛰기 링크 · 브랜드와 메뉴 · `aria-current` ·
문의 자리 · 바닥의 「전체 앱 안내」.

---

## 자주 틀리는 자리

| 증상 | 까닭 |
|---|---|
| `AssertionError` (제목 줄) | md 첫 줄이 `# <brand> <title>` 과 다르다 |
| `Policy text mismatch at N` | 표나 인용을 렌더러가 모르는 모양으로 적었다 |
| `does not match the approved source` | md 를 고쳤는데 `sha256` 을 안 고쳤다. **고친 낱말이 승인된 것인지 먼저 확인한다** |
| `Outdated HTML` | md 를 고치고 렌더러를 안 돌렸거나, HTML 을 손으로 고쳤다 |
| `Active or remote content` | 원본에 `<script>` 류가 들어갔다 |

## 아직 안 끝난 일

  · **짤랑(`jjallang`)은 옛 렌더러를 쓴다.** 충실성 검사가 없고, 지난 판 HTML 넷이 원본
    없는 고아다. 옮기려면 그 판들의 md 를 먼저 세워야 하고, 그것은 「이 HTML 이 그날의
    승인본이 맞다」를 사람이 확인해야 하는 일이다
  · 짤랑의 시행일 전환은 아직 자기 스크립트다(`jjallang/policies/switch_effective.py`).
    그쪽은 문서가 **날짜 폴더에 서고 시행일에 정본 자리로 옮겨 오는** 모양이라 공용
    `tools/switch-effective.py` 와 하는 일이 다르다. 렌더러를 옮길 때 함께 본다
