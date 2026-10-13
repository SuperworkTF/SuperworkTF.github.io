#!/usr/bin/env python3
"""assets/apps.json · assets/site.json 에서 홈의 생성 구역과 앱 페이지를 만든다.

    python3 tools/build-site.py

    index.html 의 <!-- 생성: … --> 구역     흘러가는 썸네일 · 일곱 단계 · 도구 · 앱 카드 · 워커 · 채널 · 앱 소개 링크
    apps/<앱>/index.html                   이 저장소에 소개 페이지가 없는 앱(토스·원스토어)의 쇼케이스

이 저장소에 소개 페이지(<앱>/)가 있는 앱은 홈 카드가 그 페이지로 바로 간다 — 앱마다 주소는 하나다.
주소에 분류를 넣지 않는다. 분류는 홈 화면에서 묶어 보이는 데만 쓴다(분류를 옮겨도 주소는 그대로).

글을 고칠 때는 두 JSON 만 고치고 이 스크립트를 다시 돌린다. 생성 구역 밖의 index.html 은 손으로 쓴다.
README 원칙 5 에 따라 결과물에 실행되는 <script> 를 넣지 않는다 — 움직임은 CSS 로만 한다.
정책 문서의 정본은 <앱>/<문서>/ 이고 render-policies.py 가 만든다. 여기서는 본문을 복사하지 않는다.
"""
import json
import re
import shutil
import sys
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = 'https://superwork.ai.kr/'
DATA = json.loads((ROOT / 'assets/apps.json').read_text(encoding='utf-8'))
SITE = json.loads((ROOT / 'assets/site.json').read_text(encoding='utf-8'))
CATS = {c['id']: c for c in DATA['categories']}
# apps.json 의 stores 키 → (단추·출시 채널 이름, 운영체제). 단추는 이 순서로 놓는다.
STORES = {'appstore': ('App Store', 'iOS'), 'play': ('Google Play', 'Android'), 'toss': ('앱인토스', 'Web (Toss)')}


def stores(app):
    """스토어 주소를 STORES 순서로 돌려준다. 모르는 키는 오타로 보고 멈춘다."""
    got = app.get('stores') or {}
    unknown = set(got) - set(STORES)
    if unknown:
        sys.exit(f'{app["id"]}: 모르는 stores 키 {sorted(unknown)} — {sorted(STORES)} 중에서 쓴다')
    return {k: got[k] for k in STORES if got.get(k)}


def jsonld(app):
    oses = sorted({STORES[k][1] for k in stores(app)})
    data = {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': app['name'],
        'description': app['details']['lead'],
        'applicationCategory': 'GameApplication' if app['category'] == 'game' else 'UtilitiesApplication',
        'genre': app['genre'],
        'url': SITE_URL + app['path'],
        'image': SITE_URL + app['thumb'],
        'publisher': {'@type': 'Organization', 'name': 'Superwork', 'url': SITE_URL},
    }
    if oses:
        data['operatingSystem'] = ', '.join(oses)
    if stores(app):
        data['installUrl'] = list(stores(app).values())
    body = json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')
    return f'<script type="application/ld+json">\n{body}\n</script>\n'


CONTACT = 'superwork.master+help@gmail.com'
# 단추 글 — 그려보카 소개 페이지의 「Google Play 에서 받기」 꼴을 따른다
STORE_CTA = {'appstore': 'App Store 에서 받기', 'play': 'Google Play 에서 받기', 'toss': '토스 앱에서 열기'}


def detail(app):
    """apps/<앱>/index.html — 그려보카(word-doodle/) 소개 페이지와 같은 짜임·스타일(assets/app-intro.css)."""
    base = '../../'
    cat = CATS[app['category']]
    name, desc = e(app['name']), e(app['desc'])
    got = stores(app)
    icon = f'<img src="{base}{e(app["icon"])}" alt="" width="30" height="30">' if app.get('icon') else ''
    buttons = ''.join(f'<a class="button" href="{e(url)}">{STORE_CTA[k]}</a>' for k, url in got.items())
    if not buttons:
        buttons = '<span class="button" aria-disabled="true">스토어 링크 준비 중</span>'
    channels = ' · '.join(STORES[k][0] for k in got) or '준비 중'
    pg = app['details'].get('page') or {}
    br = lambda s: e(s).replace('\n', '<br>')
    how = pg.get('how')
    if how:
        how_items = [(i['title'], i.get('desc')) for i in how['items']]
    else:  # 소개 글이 아직 없는 앱은 특징 이름만 보인다
        how = {'eyebrow': '주요 특징', 'title': f'{app["name"]}, 이런 앱이에요.',
               'intro': app['details']['lead'] if app['details']['lead'] != app['desc'] else ''}
        how_items = [(i['title'], None) for sec in app['details'].get('sections', []) for i in sec['items']]
    steps = ''.join(f'''
        <li class="step">
          <span class="step-number" aria-hidden="true">{n:02d}</span>
          <h3>{e(t)}</h3>{f"""
          <p>{e(d)}</p>""" if d else ''}
        </li>''' for n, (t, d) in enumerate(how_items, 1))
    intro = f'\n      <p class="section-intro">{e(how["intro"])}</p>' if how.get('intro') else ''
    how_block = f'''
    <section class="section" id="how-it-works" aria-labelledby="how-heading">
      <p class="eyebrow">{e(how["eyebrow"])}</p>
      <h2 id="how-heading">{e(how["title"])}</h2>{intro}
      <ol class="steps">{steps}
      </ol>
    </section>''' if how_items else ''
    more = f'\n          <a href="#how-it-works">{name} 알아보기 <span aria-hidden="true">↓</span></a>' if how_items else ''
    n2 = pg.get('note2') or {'eyebrow': '이용 정보', 'title': '어디서 받고,\n무엇을 확인하나요', 'body': []}
    n2_body = ''.join(f'\n        <p>{e(p)}</p>' for p in n2['body'])
    faq = pg.get('faq') or []
    faq_items = ''.join(f'''
        <div class="faq-item">
          <h3>{e(f["q"])}</h3>
          <p>{e(f["a"])}</p>
        </div>''' for f in faq)
    faq_block = f'''
    <section class="section" id="faq" aria-labelledby="faq-heading">
      <p class="eyebrow">궁금할 때 먼저 보기</p>
      <h2 id="faq-heading">자주 묻는 질문</h2>
      <div class="faq-list">{faq_items}
      </div>
    </section>''' if faq else ''
    body = f'''  <a class="skip-link" href="#main">본문 바로가기</a>
  <header class="site-header shell">
    <a class="brand" href="./" aria-label="{name} 소개">{icon}{name}</a>
    <nav class="site-nav" aria-label="주요 메뉴">
      <a href="./" aria-current="page">앱 소개</a>
      <a href="{base}#apps-{e(cat["id"])}">{e(cat["label"])} 앱</a>
      <a href="{base}">전체 앱 안내</a>
    </nav>
  </header>
  <main id="main" class="shell" tabindex="-1">
    <section class="hero" aria-labelledby="intro-heading">
      <div>
        <p class="eyebrow">{e(pg.get("eyebrow") or app["genre"])}</p>
        <h1 id="intro-heading">{br(pg["headline"]) if pg.get("headline") else name}</h1>
        <p class="hero-copy">{e(pg.get("heroCopy") or app["desc"])}</p>
        <div class="actions">
          {buttons}{more}
        </div>
        <p class="age-note">{e(pg.get("note") or f'{cat["label"]} · {channels}')}</p>
      </div>
      <figure class="shot-card">
        <img src="{base}{e(app["thumb"])}" alt="{name} 대표 이미지" style="object-position:{e(app["thumbPos"])}">
        <figcaption><strong>{name}</strong><span>{e(app["genre"])}</span></figcaption>
      </figure>
    </section>{how_block}
    <section class="local-note" aria-labelledby="info-heading">
      <div>
        <p class="eyebrow">{e(n2["eyebrow"])}</p>
        <h2 id="info-heading">{br(n2["title"])}</h2>
      </div>
      <div>{n2_body}
        <dl class="facts">
          <dt>분류</dt><dd>{e(cat["label"])} · {e(app["genre"])}</dd>
          <dt>출시 채널</dt><dd>{e(channels)}</dd>
        </dl>
        <p>개인정보처리방침과 이용약관은 앱이 출시된 스토어의 앱 정보와 앱 안에서 확인할 수 있습니다.</p>
      </div>
    </section>{faq_block}
    <section class="section contact" id="contact" aria-labelledby="contact-heading">
      <div>
        <p class="eyebrow">도움이 필요할 때</p>
        <h2 id="contact-heading">문의 안내</h2>
      </div>
      <div>
        <p>앱 이용에 관한 궁금한 점이나 도움이 필요한 내용을 이메일로 보내 주세요.</p>
        <p><a class="contact-address" href="mailto:{CONTACT}">{CONTACT}</a></p>
        <div class="document-links">
          <a href="{base}#apps-{e(cat["id"])}">{e(cat["label"])} 앱 더 보기 <span aria-hidden="true">↗</span></a>
          <a href="{base}">SuperWork 전체 앱 안내 <span aria-hidden="true">↗</span></a>
        </div>
      </div>
    </section>
  </main>
  <footer class="site-footer shell">
    <p>{name} · 앱 소개</p>
    <a href="{base}">전체 앱 안내</a>
  </footer>'''
    title = f'{app["name"]} — {app["genre"]}'
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#f7f4eb">
  <title>{e(title)}</title>
  <link rel="canonical" href="{SITE_URL}{e(app["path"])}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="SuperWork">
  <meta property="og:locale" content="ko_KR">
  <meta property="og:url" content="{SITE_URL}{e(app["path"])}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{SITE_URL}{e(app["thumb"])}">
  <meta name="twitter:card" content="summary_large_image">
  {jsonld(app)}  <link rel="stylesheet" href="{base}assets/app-intro.css">
  <style>:root {{ --accent: {e(app.get("accent", "#8d442a"))}; }}</style>
</head>
<body>
{body}
</body>
</html>
'''


ICONS = {
    'search': '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    'branch': '<circle cx="12" cy="19.5" r="1.8"/><path d="M12 17.7V12M12 12L6 6.5M12 12l6-5.5M12 12V5"/><circle cx="6" cy="5.2" r="1.6"/><circle cx="18" cy="5.2" r="1.6"/><circle cx="12" cy="3.6" r="1.6"/>',
    'doc': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M12 11v6M9 14h6"/>',
    'rocket': '<path d="M5 15c-1.5 1.5-2 5-2 5s3.5-.5 5-2"/><path d="M9 15l-3-3a12 12 0 0 1 12-9 12 12 0 0 1-9 12z"/><circle cx="14.5" cy="9.5" r="1.6"/>',
    'eye': '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'chart': '<path d="M3 21h18M6 21v-7M11 21V9M16 21v-4M21 21V5"/>',
    'orbit': '<circle cx="12" cy="12" r="3"/><ellipse cx="12" cy="12" rx="10" ry="4.5" transform="rotate(-30 12 12)"/><circle cx="19.6" cy="7.4" r="1.4" fill="currentColor"/>',
    'factory': '<path d="M3 21V10l6 4V10l6 4V6l6 3v12z"/><path d="M7 17h2M12 17h2M17 17h2"/>',
    'plug': '<path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0zM12 18v4"/>',
    'puzzle': '<path d="M10 3h4v3a2 2 0 1 0 4 0V3h3v7h-3a2 2 0 1 0 0 4h3v7h-7v-3a2 2 0 1 0-4 0v3H3v-7h3a2 2 0 1 0 0-4H3V3z"/>',
    'megaphone': '<path d="M3 11v2a1 1 0 0 0 1 1h3l6 5V5L7 10H4a1 1 0 0 0-1 1z"/><path d="M17 8a5 5 0 0 1 0 8M20 5a9 9 0 0 1 0 14"/>',
    'gamepad': '<path d="M6 8h12a4 4 0 0 1 4 4v1a4 4 0 0 1-7 2.6L14 15h-4l-1 .6A4 4 0 0 1 2 13v-1a4 4 0 0 1 4-4z"/><path d="M7 11v3M5.5 12.5h3"/><circle cx="16" cy="11.5" r=".9" fill="currentColor"/><circle cx="18" cy="13.5" r=".9" fill="currentColor"/>',
}
CHANNEL_ICONS = {
    'youtube': '<svg viewBox="0 0 24 24" fill="#ff0033" aria-hidden="true"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/></svg>',
    'tiktok': '<svg viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M19.6 6.7a4.8 4.8 0 0 1-3.8-4.2V2h-3.4v13.4a2.9 2.9 0 1 1-2-2.7V9.2a6.3 6.3 0 1 0 5.4 6.2V8.6a8.2 8.2 0 0 0 4.8 1.5V6.7h-1z"/></svg>',
    'instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="#e1306c" stroke-width="2" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4.5"/><circle cx="17.6" cy="6.4" r="1" fill="#e1306c"/></svg>',
}


def svg(key):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[key]}</svg>'


def home_marquee():
    apps = DATA['apps']
    half = (len(apps) + 1) // 2
    def row(items, rev):
        cells = ''.join(f'<a href="./{e(a["path"])}" tabindex="-1"><img src="./{e(a["thumbSm"])}" alt="" loading="lazy"></a>'
                        for a in items + items)
        return f'<div class="marquee-row{" rev" if rev else ""}">{cells}</div>'
    return row(apps[:half], False) + '\n' + row(apps[half:], True)


def home_flow():
    steps = SITE['steps']
    nodes = []
    for i, st in enumerate(steps):
        pins = ''.join(f'<span>{e(h)}</span>' for h in st.get('human', []))
        pins = f'<div class="pins">{pins}</div>' if pins else ''
        start = 30 + i * 5
        nodes.append(
            f'<li class="node{" orbit" if st.get("orbit") else ""}" style="animation-range:entry {start}% cover {start + 14}%">'
            f'<div class="node-ring">{svg(st["icon"])}<span class="node-no">{i + 1}</span></div>'
            f'<div class="node-text"><code>{e(st["cmd"])}</code><h3>{e(st["title"])}</h3><p>{e(st["desc"])}</p>{pins}</div></li>')
    return ('<div class="flow-bands"><div class="band">hatchery <span>아이디어 → 수요 판정</span></div>'
            '<div class="band orbit">orbit <span>배포</span></div></div>\n'
            '<div class="flow-track"><div class="flow-line" aria-hidden="true"></div>\n<ol class="flow-steps">\n'
            + '\n'.join(nodes) + '\n</ol></div>\n'
            '<div class="flow-legend"><span><i style="background:var(--accent)"></i>에이전트가 하는 일</span>'
            '<span><i style="background:#ffd166"></i>사람이 정하는 지점</span>'
            '<span><i style="background:#7aa8ff"></i>orbit 배포 구간</span></div>')


TOOL_STATUS = {'public': '공개', 'soon': 'GitHub 공개 예정', 'draft': '소개 준비 중'}


def home_tools():
    """도구는 분류(toolGroups)별로 묶는다. 도구가 없는 분류는 내지 않는다 — 늘어나면 site.json 에 한 줄 더한다."""
    groups = {g['id']: g for g in SITE['toolGroups']}
    for tool in SITE['tools']:
        if tool['group'] not in groups:
            raise SystemExit(f"도구 {tool['name']!r} 의 group {tool['group']!r} 이 toolGroups 에 없다")
        if tool['status'] not in TOOL_STATUS or (tool['status'] == 'public') != bool(tool.get('url')):
            raise SystemExit(f"도구 {tool['name']!r}: status 가 public 이면 url 이 있어야 하고, 아니면 없어야 한다")
    out = []
    for g in SITE['toolGroups']:
        items = [x for x in SITE['tools'] if x['group'] == g['id']]
        if not items:
            continue
        cards = []
        for x in items:
            if x['status'] == 'public':
                foot = f'<a class="tool-link" href="{e(x["url"])}" target="_blank" rel="noopener">GitHub ↗</a>'
            else:
                foot = f'<span class="tool-badge {e(x["status"])}">{e(TOOL_STATUS[x["status"]])}</span>'
            body = ''
            if x.get('tag'):
                body += f'<p class="tool-tag">{e(x["tag"])}</p>'
            if x.get('flow'):
                body += '<div class="tool-flow">' + '<i>→</i>'.join(f'<code>{e(f)}</code>' for f in x['flow']) + '</div>'
            if x.get('chips'):
                body += '<div class="tool-chips">' + ''.join(f'<span>{e(c)}</span>' for c in x['chips']) + '</div>'
            stat = f'<span class="tool-stat">{e(x["stat"])}</span>' if x.get('stat') else '<span></span>'
            cards.append(
                f'<article class="tool reveal{" empty" if not body else ""}">'
                f'<div class="tool-top"><span class="tool-icon">{svg(x["icon"])}</span><h4>{e(x["name"])}</h4></div>'
                f'{body}<div class="tool-foot">{stat}{foot}</div></article>')
        out.append(
            f'<div class="tool-group reveal" id="tools-{e(g["id"])}">'
            f'<div class="tool-group-head"><span class="tool-group-icon">{svg(g["icon"])}</span>'
            f'<div><h3>{e(g["label"])}<i>{len(items)}</i></h3><p>{e(g["desc"])}</p></div></div>'
            f'<div class="tool-grid">{"".join(cards)}</div></div>')
    return '\n'.join(out)


def home_card(a):
    icon = f'<img src="./{e(a["icon"])}" alt="" loading="lazy">' if a.get('icon') else ''
    video = (f'<video src="./{e(a["video"])}" muted loop playsinline autoplay preload="metadata" aria-hidden="true"></video>'
             if a.get('video') else '')
    return (f'<a class="acard" href="./{e(a["path"])}">'
            f'<div class="acard-media"><img src="./{e(a["thumbSm"])}" alt="{e(a["name"])}" loading="lazy" style="object-position:{e(a["thumbPos"])}">'
            f'{video}<span class="acard-more">자세히 보기 →</span></div>'
            f'<div class="acard-body">{icon}<div><div class="acard-genre">{e(a["genre"])}</div><b>{e(a["name"])}</b></div></div>'
            f'<p class="acard-desc">{e(a["desc"])}</p></a>')


def home_apps():
    out = []
    for c in DATA['categories']:
        items = [a for a in DATA['apps'] if a['category'] == c['id']]
        out.append(
            f'<div class="group" id="apps-{e(c["id"])}"><div class="group-head reveal">'
            f'<div><h3>{e(c["label"])}<i>{len(items)}</i></h3><p>{e(c["desc"])}</p></div></div>'
            f'<div class="track">{"".join(home_card(a) for a in items)}</div></div>')
    return '\n'.join(out)


def home_workers():
    return '\n'.join(
        f'<figure class="worker-card reveal"><img src="./assets/workers/{e(w["id"])}.jpg" alt="{e(w["id"])}" loading="lazy">'
        f'<b>{e(w["id"])}</b>'
        f'<span class="worker-role">{e(w["role"])}</span><p>“{e(w["quote"])}”</p></figure>'
        for w in SITE['workers'])


def home_channels():
    return '\n'.join(
        f'<article class="panel channel reveal" style="--glow:{e(c["color"])}">{CHANNEL_ICONS[c["icon"]]}'
        f'<h3>{e(c["name"])}</h3><p>{e(c["desc"])}</p>'
        f'<a class="btn btn-ghost" href="{e(c["url"])}" target="_blank" rel="noopener">채널 보기 ↗</a></article>'
        for c in SITE['channels'])


def home_intro_links():
    """푸터의 「앱 소개 · 정책」 — 루트가 모든 앱 소개(<앱>/)를 잇는다(check-pages.py). 가나다순.
    tools/render-llms.py 는 이 a.card 의 차례와 주소만 읽고, 제목·설명은 각 소개 페이지에서 가져온다."""
    intros = sorted((a for a in DATA['apps'] if a.get('intro')), key=lambda a: a['name'])
    return '\n'.join(f'<a class="card" href="./{e(a["intro"])}"><div class="t">{e(a["name"])}</div></a>' for a in intros)


def build_home():
    path = ROOT / 'index.html'
    html = path.read_text(encoding='utf-8')
    blocks = {'marquee': home_marquee(), 'flow': home_flow(), 'tools': home_tools(), 'apps': home_apps(),
              'workers': home_workers(), 'channels': home_channels(), 'intro-links': home_intro_links()}
    for key, body in blocks.items():
        pattern = re.compile(rf'(<!-- 생성: {re.escape(key)} [^>]*-->\n).*?(<!-- /생성: {re.escape(key)} -->)', re.S)
        html, n = pattern.subn(lambda m: m.group(1) + body + '\n' + m.group(2), html)
        if n != 1:
            raise SystemExit(f'index.html 에 생성 구역 「{key}」 이 {n}개 있다 — 하나여야 한다')
    path.write_text(html, encoding='utf-8')


def moved_page(app):
    """옛 쇼케이스 주소에 남기는 안내 한 장 — 새 소개 페이지로 바로 넘긴다."""
    target = SITE_URL + app['intro']
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{e(app["name"])} — 새 주소로 옮겼습니다</title>
<meta name="robots" content="noindex"/>
<link rel="canonical" href="{e(target)}"/>
<meta http-equiv="refresh" content="0; url={e(target)}"/>
</head>
<body>
<p>{e(app["name"])} 소개와 정책 문서는 <a href="{e(target)}">{e(target)}</a> 로 옮겼습니다.</p>
</body>
</html>
'''


def main():
    apps = DATA['apps']
    out_root = ROOT / 'apps'
    if out_root.exists():
        shutil.rmtree(out_root)
    showcase = [a for a in apps if not a.get('intro')]
    for app in showcase:
        # 정본 소개 페이지(<앱>/index.html)를 덮어쓰지 않도록 apps/ 밖에는 쓰지 않는다
        if not app['path'].startswith('apps/') or app['path'].count('/') != 2:
            raise SystemExit(f"{app['id']}: 쇼케이스 주소는 apps/<앱>/ 이어야 한다 — {app['path']!r}")
        out = ROOT / app['path'] / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(detail(app), encoding='utf-8')
    # 소개 페이지로 옮겨 간 앱의 옛 쇼케이스 주소는 지우지 않고 새 주소로 넘긴다.
    # 그 주소가 QR·공유 링크·스토어 등록정보에 이미 나가 있을 수 있다(해피퍼그 apps/happy-pug/).
    # 정적 HTML 의 meta refresh 만 쓴다 — 스크립트는 넣지 않는다(README 원칙 5).
    moved = [a for a in apps if a.get('intro') and a.get('formerPath')]
    for app in moved:
        former = app['formerPath']
        if not former.startswith('apps/') or former.count('/') != 2:
            raise SystemExit(f"{app['id']}: 옛 주소는 apps/<앱>/ 이어야 한다 — {former!r}")
        out = ROOT / former / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(moved_page(app), encoding='utf-8')
    build_home()
    print(f'index.html 생성 구역 7곳, apps/ 쇼케이스 {len(showcase)}개, 옮겨 간 주소 {len(moved)}개')


if __name__ == '__main__':
    main()
