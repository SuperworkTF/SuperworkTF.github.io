# 핀치 러너 개인정보처리방침
앱 이름 / App Name: 핀치 러너 (Pinch Runner)
시행일 / Effective Date: 2026-08-03
이전 버전 시행일 / Previous Version: 2026-06-21
핀치 러너(이하 "본 앱")는 이용자의 개인정보를 중요하게 생각하며, 「개인정보 보호법」 등 관련 법령을 준수합니다.
제1항 수집하는 개인정보 항목 / Data We Collect
본 앱은 회원가입 절차가 없으며, 이름·전화번호·이메일 등 이용자를 직접 식별할 수 있는 정보를 수집하지 않습니다.
<table header-row="true">
<tr>
<td>수집 항목</td>
<td>수집 방법</td>
<td>필수 여부</td>
</tr>
<tr>
<td>익명 사용자 ID (Firebase Anonymous Auth UID)</td>
<td>앱 최초 실행 시 자동 생성</td>
<td>필수</td>
</tr>
<tr>
<td>게임 기록 (점수, 생존 시간, 연속 성공 횟수)</td>
<td>게임 종료 시 자동 저장</td>
<td>필수</td>
</tr>
<tr>
<td>리더보드 닉네임</td>
<td>이용자 직접 입력</td>
<td>선택</td>
</tr>
<tr>
<td>앱 사용 이벤트 (게임 시작·종료, 세션 시간, 기능 사용 현황)</td>
<td>Firebase Analytics SDK 자동 수집</td>
<td>선택</td>
</tr>
<tr>
<td>오류 및 충돌 로그 (스택 트레이스, 기기 모델, OS 버전)</td>
<td>Firebase Crashlytics SDK 자동 수집</td>
<td>선택</td>
</tr>
<tr>
<td>광고 식별자 (Android 광고 ID)</td>
<td>Google AdMob SDK 자동 수집</td>
<td>선택</td>
</tr>
</table>
수집하지 않는 정보
이름, 생년월일, 전화번호, 이메일 주소, 주소
위치 정보 (위치 권한을 요청하지 않습니다)
연락처, 사진, 파일 등 기기 내 저장 정보
결제 및 구매 기록 — 본 앱에는 인앱 결제 기능이 없습니다.
앱이 요청하는 권한은 인터넷 연결과 진동뿐입니다.
제2항 개인정보 이용 목적 / Purpose of Processing
<table header-row="true">
<tr>
<td>목적</td>
<td>이용 항목</td>
</tr>
<tr>
<td>게임 기능 제공 (리더보드 순위 표시, 기록 저장)</td>
<td>익명 UID, 게임 기록, 닉네임</td>
</tr>
<tr>
<td>앱 오류 진단 및 안정성 개선</td>
<td>충돌 로그, 기기 정보</td>
</tr>
<tr>
<td>이용 패턴 분석을 통한 서비스 개선</td>
<td>앱 사용 이벤트</td>
</tr>
<tr>
<td>광고 게재</td>
<td>광고 식별자</td>
</tr>
</table>
제3항 보유 및 이용 기간 / Retention Periods
<table header-row="true">
<tr>
<td>데이터</td>
<td>보유 기간</td>
</tr>
<tr>
<td>익명 UID</td>
<td>삭제 요청 시까지</td>
</tr>
<tr>
<td>리더보드 닉네임</td>
<td>삭제 요청 시까지</td>
</tr>
<tr>
<td>일별 리더보드 점수</td>
<td>매일 자동 갱신 (당일 기록만 유지)</td>
</tr>
<tr>
<td>충돌 로그</td>
<td>90일 (Firebase 기본 정책)</td>
</tr>
<tr>
<td>분석 이벤트</td>
<td>2개월 (Firebase Analytics 기본 정책)</td>
</tr>
<tr>
<td>기기 내 저장 기록 (최고 점수, 설정값)</td>
<td>앱 삭제 시 함께 삭제</td>
</tr>
</table>
보유 기간이 경과하거나 처리 목적이 달성된 개인정보는 지체 없이 파기합니다.
제4항 개인정보 처리위탁 / Data Processing
본 앱은 서비스 제공을 위해 아래와 같이 개인정보 처리를 위탁하고 있습니다.
<table header-row="true">
<tr>
<td>수탁자</td>
<td>위탁 업무</td>
<td>위탁 항목</td>
</tr>
<tr>
<td>Google LLC (Firebase Authentication)</td>
<td>익명 인증</td>
<td>익명 UID</td>
</tr>
<tr>
<td>Google LLC (Cloud Firestore)</td>
<td>리더보드·기록 저장</td>
<td>익명 UID, 게임 기록, 닉네임</td>
</tr>
<tr>
<td>Google LLC (Firebase Analytics)</td>
<td>이용 통계 분석</td>
<td>앱 사용 이벤트, 기기 정보</td>
</tr>
<tr>
<td>Google LLC (Firebase Crashlytics)</td>
<td>오류 진단</td>
<td>충돌 로그, 기기 정보</td>
</tr>
<tr>
<td>Google LLC (AdMob)</td>
<td>광고 게재</td>
<td>광고 식별자</td>
</tr>
</table>
본 앱은 위탁 외에 개인정보를 제3자에게 제공하거나 판매하지 않습니다.
수탁자의 개인정보처리방침
Google 개인정보처리방침: https://policies.google.com/privacy
Google 광고 정책: https://policies.google.com/technologies/ads
Firebase 데이터 처리 조건: https://firebase.google.com/terms/data-processing-terms
제5항 개인정보의 국외 이전 / International Transfers
본 앱이 이용하는 Google LLC의 서버는 대한민국 외 지역(미국 등)에 위치할 수 있으며, 수집된 정보가 해당 서버에 저장·처리됩니다.
<table header-row="true">
<tr>
<td>이전받는 자</td>
<td>이전 국가</td>
<td>이전 항목</td>
<td>이전 시점 및 방법</td>
</tr>
<tr>
<td>Google LLC</td>
<td>미국 등 Google 데이터센터 소재국</td>
<td>위 4항의 위탁 항목</td>
<td>서비스 이용 시 네트워크를 통해 전송</td>
</tr>
</table>
이전을 원하지 않으시면 앱을 삭제하여 이용을 중단하실 수 있습니다.
제6항 개인정보의 파기 / Data Deletion
파기 절차: 보유 기간이 경과하거나 이용자가 삭제를 요청한 개인정보는 즉시 파기 대상으로 분류하여 지체 없이 파기합니다.
파기 방법: 전자적 파일 형태의 정보는 복구가 불가능한 방법으로 영구 삭제합니다.
앱 삭제 시: 기기에 저장된 최고 점수와 설정값은 앱 삭제와 함께 제거됩니다. 다만 서버(Cloud Firestore)에 저장된 익명 UID 및 리더보드 기록은 자동으로 삭제되지 않으므로, 삭제를 원하시면 아래 9항의 연락처로 요청해 주세요.
제7항 이용자의 권리와 행사 방법 / Your Rights
이용자는 언제든지 다음 권리를 행사할 수 있습니다.
개인정보 열람 요청
개인정보 정정·삭제 요청
개인정보 처리정지 요청
행사 방법: 아래 9항의 이메일로 요청해 주시기 바랍니다.
본 앱은 익명 인증만 사용하므로 본인 확인을 위해 앱 내 리더보드에 표시되는 닉네임을 함께 알려주시면 처리가 빠릅니다.
한국 이용자: 요청일로부터 10일 이내 처리
EU 이용자(GDPR): 요청일로부터 30일 이내 처리. 접근권, 삭제권(잊힐 권리), 데이터 이동권, 처리 반대권, 처리 제한권을 보장합니다. 처리의 법적 근거는 분석·오류 진단의 경우 정당한 이익, 광고 식별자 이용의 경우 동의입니다.
제8항 광고 식별자 및 거부 방법 / Advertising Identifier
본 앱은 광고 게재를 위해 Google AdMob SDK를 사용하며, 이 과정에서 기기의 광고 식별자가 수집됩니다.
거부 방법
Android: 설정 \> Google \> 광고 \> 광고 ID 삭제 또는 맞춤 광고 선택 해제
Google 광고 설정 페이지: https://adssettings.google.com
광고 식별자 수집을 거부하더라도 게임 이용에는 제한이 없으며, 다만 이용자와 관련성이 낮은 광고가 표시될 수 있습니다.
제9항 개인정보 보호책임자 / Contact
<table header-row="true">
<tr>
<td>구분</td>
<td>내용</td>
</tr>
<tr>
<td>직위</td>
<td>개인정보 보호책임자</td>
</tr>
<tr>
<td>이메일</td>
<td>superwork.master+help@gmail.com</td>
</tr>
</table>
개인정보 관련 문의, 열람·정정·삭제·처리정지 요청은 위 이메일로 접수해 주세요.
제10항 개인정보의 안전성 확보 조치 / Security Measures
전송 구간 암호화: 서버와의 모든 통신은 HTTPS/TLS로 암호화합니다.
접근 권한 최소화: Cloud Firestore 보안 규칙을 통해 이용자는 자신의 기록만 수정할 수 있으며, 타인의 기록은 변경할 수 없습니다.
비정상 기록 차단: 서버 측 검증(Cloud Functions)을 통해 조작이 의심되는 점수를 걸러냅니다.
최소 수집 원칙: 서비스 제공에 필요한 최소한의 정보만 수집합니다.
제11항 아동의 개인정보 / Children's Privacy
본 앱은 전 연령이 이용할 수 있는 게임이나, 아동을 주 이용 대상으로 하지 않습니다.
대한민국: 만 14세 미만 아동의 개인정보는 법정대리인의 동의 없이 수집하지 않습니다.
미국(COPPA): 만 13세 미만 아동으로부터 개인정보를 고의로 수집하지 않습니다.
만 14세 미만 아동의 정보가 수집된 사실을 인지한 경우 지체 없이 파기합니다. 자녀의 정보가 수집되었다고 판단되시면 9항의 연락처로 알려주시기 바랍니다.
제12항 권익침해 구제방법 / Remedies
개인정보 침해로 인한 상담 및 피해 구제가 필요하신 경우 아래 기관에 문의하실 수 있습니다.
<table header-row="true">
<tr>
<td>기관</td>
<td>전화</td>
<td>홈페이지</td>
</tr>
<tr>
<td>개인정보침해 신고센터</td>
<td>(국번없이) 118</td>
<td>privacy.kisa.or.kr</td>
</tr>
<tr>
<td>개인정보 분쟁조정위원회</td>
<td>1833-6972</td>
<td>www.kopico.go.kr</td>
</tr>
<tr>
<td>대검찰청 사이버수사과</td>
<td>(국번없이) 1301</td>
<td>www.spo.go.kr</td>
</tr>
<tr>
<td>경찰청 사이버수사국</td>
<td>(국번없이) 182</td>
<td>ecrm.police.go.kr</td>
</tr>
</table>
제13항 정책 변경 안내 / Policy Updates
본 방침의 내용이 추가·삭제·수정되는 경우 시행 7일 전부터 앱 내 공지 또는 본 페이지를 통해 안내합니다. 다만 이용자 권리에 중대한 영향을 미치는 변경은 30일 전에 안내합니다.
개정 이력
<table header-row="true">
<tr>
<td>버전</td>
<td>시행일</td>
<td>주요 변경</td>
</tr>
<tr>
<td>1.1</td>
<td>2026-08-03</td>
<td>인앱 결제 관련 항목 삭제(기능 미구현), 위탁·국외이전·파기·안전성 확보조치·권익침해 구제방법 신설, 광고 식별자 거부 방법 구체화</td>
</tr>
<tr>
<td>1.0</td>
<td>2026-06-21</td>
<td>최초 제정</td>
</tr>
</table>
최종 수정일 / Last updated: 2026-08-03
