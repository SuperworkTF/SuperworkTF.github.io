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
        sources.json      브랜드·주소·시행 상태, 어떤 문서를 내는가
        privacy.md        개인정보처리방침 원본 (필수)
        terms.md          서비스 이용약관 원본 (약관이 있을 때)
        account-deletion.md  계정 삭제 안내 원본 (계정이 있을 때 — 스토어가 웹 삭제 요청 주소를 요구한다)

**내는 문서는 앱마다 다르다.** `sources.json` 에 칸이 있는 문서만 만들고 메뉴에 건다.
쓸 수 있는 문서 칸은 `privacy` · `terms` · `account-deletion` 이다(`tools/render-policies.py`
의 `DOCUMENTS`). 새 종류가 필요하면 거기에 한 줄 더한다.

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
        "public_url": "https://superwork.ai.kr/<app>/privacy/",
        "editions": [
          { "path": "privacy", "source": "privacy" }
        ]
      },
      "terms": {
        "title": "서비스 이용약관",
        "public_url": "https://superwork.ai.kr/<app>/terms/",
        "editions": [
          { "path": "terms", "source": "terms" }
        ]
      }
    }

### 쓸 수 있는 값들 (전부 선택)

### 판 목록 — **출력 한 장 = 항목 하나**

`editions` 가 낼 페이지를 하나씩 적는다. 항목이 드는 것은 셋이다 — **어느 원본을 읽어
(`source`), 어느 자리에 서고(`path`), 어떤 상태인가(`status`)**.

첫 항목은 반드시 정본 자리(`path` = `privacy` 또는 `terms`)다. 나머지는 그 아래 날짜다.

| 항목의 키 | 뜻 |
|---|---|
| `path` | 낼 자리. `privacy` 또는 `privacy/2026-09-05` |
| `source` | 읽을 md 이름(확장자 없이). `privacy-2026-09-05` |
| `title` | 그 판의 제목. **박제된 판이 당시에 든 이름과 다르면 안 된다** |
| `status` | `upcoming` · `current` · `dated`. **상태는 자리에 붙는다** — 문서 칸에서 물려받지 않는다 |
| `effective` · `announced` | 그 판의 시행일·공고일 |
| `current` | `upcoming` 일 때 지금 시행 중인 문서의 주소 |
| `previous` · `previous_label` | `current` 일 때 이전 시행본의 주소·이름 |
| `upcoming` · `upcoming_effective` · `upcoming_announced` | `current` 인데 개정이 공고돼 있을 때 |
| `notice` | 지난 판 안내 한 문장. 있으면 제목에 「— 정비 전 문서」가 붙는다 |
| `sha256` | 승인된 원본의 지문. 있으면 md 가 그 지문과 다를 때 멈춘다. **법정 문장을 바꾸려면 이 값을 일부러 고쳐야 한다** |

문서 칸(`privacy`/`terms`)에 두는 것은 판마다 안 바뀌는 것뿐이다: `title`(기본값) ·
`public_url` · `notion_source` · `source_of_truth`.

| 문서 칸의 키 | 뜻 |
|---|---|
| `notion_source` | `true` 면 「원문 보기(Notion)」를 머리말에 적고 `canonical` 을 안 낸다 |
| `source_of_truth` | 원본을 쥔 곳이 다른 저장소일 때 적는다(짤랑) |

**판마다 md 가 하나씩 있어야 한다.** 없으면 그 HTML 은 다시 만들 수도 검사할 수도 없는
고아가 된다. 한 원본이 두 자리에 설 수는 있다 — 그때는 두 항목이 같은 `source` 를 든다.

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
      **(가) 개정본을 정본 자리에 먼저 세우는 길** — 우르르
        · 개정본을 `privacy-<새시행일>.md` 로 올리고 정본 자리 항목이 그것을 읽는다
        · 그 항목에 `status: "upcoming"` · `effective` · `announced` · `current: "./<이전시행일>/"`
        · 직전 판은 자기 날짜 주소 항목에 남는다

      **(나) 정본 자리는 현행이 지키고 개정본을 날짜 주소에 세우는 길** — 짤랑
        · 개정본 항목을 `privacy/<새시행일>` 자리에 `status: "upcoming"` 으로 더한다
        · 정본 자리 항목은 `status: "current"` 에 `upcoming`·`upcoming_effective`·
          `upcoming_announced` 를 더해 **개정 공고를 함께 말한다**
        · 현행이 **자기 날짜 주소 항목을 가지고 있어야 한다** — 없으면 전환 때 멈춘다

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

뼈대는 다른 앱의 `index.html` 에서 가져오되, **화면은 그 앱의 것**이어야 한다.
색·글자는 앱 저장소의 디자인 토큰에서, 히어로는 앱이 실제로 하는 일을 그린 장면으로.
규칙은 루트 `README.md` 「소개 페이지 — 앱의 성격이 드러나야 한다」에 있다.

뼈대가 들고 있는 것(지우지 않는다): 건너뛰기 링크 · 브랜드와 메뉴 · `aria-current` ·
문의 자리 · 바닥의 「전체 앱 안내」. 메뉴에는 그 앱이 **실제로 내는 문서만** 건다.

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
  · 모든 앱이 공용 렌더러를 쓴다(2026-09-22). 앱별 `policies/render.py` 는 없다
