# HappyPug(happy-pug) — 이 앱만의 사정

공통 규칙은 저장소 루트 `README.md` 와 `tools/ADDING-AN-APP.md` 를 따른다.
여기에는 **HappyPug 에만 해당하는 것**만 적는다.

앱 소스는 별도 저장소(`happypug`)에 있다. 앱 코드, 환경 파일, 내부 검토 문서를 이 저장소에 복사하지 않는다.

### 주소 — `/apps/happy-pug/` 에서 `/happy-pug/` 로 (2026-10-12)

- 소개 페이지가 생겨 사이트 규칙대로 `/happy-pug/` 로 바로 간다.
- 옛 주소 `/apps/happy-pug/` 는 QR·스토어 등에 이미 나갔을 수 있어 지우지 않는다.
  `assets/apps.json` 의 `formerPath` 로 `tools/build-site.py` 가 이동 페이지(meta refresh · noindex · canonical)를 만든다.
- 앱 1.0.6 부터 앱 안의 정책 링크가 이 사이트를 가리킨다. 그 전 판은 Notion 과
  `happy-pug.web.app/privacy-policy` 등을 연다. 후자는 Firebase Hosting 에서 이 사이트로 301 이동시킨다(앱 저장소 `firebase/firebase.json`).

### 정책 원본을 고른 근거

공개돼 있던 사본이 여러 벌(Notion · 앱 저장소 md · Firebase Hosting HTML)이고 서로 조금씩 달랐다.
앱 저장소의 md 를 원본으로 삼았다 — 가장 완전하고, 이력이 커밋으로 남아 있다.

| 원본 | 앱 저장소 커밋 |
|---|---|
| `privacy-2026-05-27.md` | a76c65f |
| `privacy-2026-10-15.md`, `location-terms-2026-10-15.md` | 68710aa |
| `location-terms-2026-05-27.md` | 8a49e5e |
| `privacy-2026-11-12.md` | 1.0.6 보안 조치에 맞춘 개정(2026-10-12 작성) |
| `terms.md` | 앱 저장소 md — 시행일 2026-05-15 (Hosting HTML 은 04-29 로 달랐다. md 를 따른다) |
| `account-deletion.md` | 새로 씀. 서버 1.0.6 의 삭제 범위(사진·후기 포함) 기준 |

바뀐 것은 첫 줄 제목 `# HappyPug <문서 제목>` 과 사이트 표 형식뿐이다. 그 밖의 글자는 그대로다.

### 개정판이 연달아 있다

- 처리방침: 05-27(현행) → 10-15(공고 09-18) → 11-12(공고 10-13)
- 위치기반서비스 약관: 05-27(현행) → 10-15(공고 09-18)

공고일 09-18 은 게시돼 있던 문서의 「최종 개정」 날짜다. 11-12 판 공고일 10-13 은 **실제 게시일과 맞춰야 한다**(시행 30일 전).
전환은 `policy-switch` 워크플로가 시행일에 한다. 10-15 전환 뒤에도 정본 페이지는 11-12 판 공고를 계속 보여 준다
(`tools/switch-effective.py` 의 `promote()`).

### 계정 삭제 안내는 서버 배포와 함께 병합한다

`account-deletion` 은 1.0.6 서버 함수(deleteAccount)가 지우는 범위를 적었다. 함수 배포 전에 게시하면 실제와 어긋난다.
