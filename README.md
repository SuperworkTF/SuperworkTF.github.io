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
