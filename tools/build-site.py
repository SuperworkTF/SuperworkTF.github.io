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
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = 'https://superwork.ai.kr/'
DATA = json.loads((ROOT / 'assets/apps.json').read_text(encoding='utf-8'))
SITE = json.loads((ROOT / 'assets/site.json').read_text(encoding='utf-8'))
CATS = {c['id']: c for c in DATA['categories']}
OS = {'앱인토스': 'Web (Toss)', 'Google Play': 'Android', '원스토어': 'Android', 'App Store': 'iOS'}


def header(base, current):
    def nav(href, label, key, cls=''):
        cur = ' aria-current="page"' if key == current else ''
        return f'<a href="{base}{href}"{cls}{cur}>{label}</a>'
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="brand grad" href="{base}">Superwork</a>
    <nav class="site-nav">
      {nav('#workflow', '개발 체계', '', ' class="hide-sm"')}
      {nav('#tools', '도구', '')}
      {nav('#apps', '앱', 'apps')}
      {nav('#channels', '채널', '')}
      {nav('#directory', '정책', '')}
    </nav>
  </div>
</header>'''


def footer(base):
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div><a class="brand grad" href="{base}">Superwork</a></div>
      <div><h4>사이트</h4><ul><li><a href="{base}#workflow">개발 체계</a></li><li><a href="{base}#tools">도구</a></li><li><a href="{base}#apps">앱</a></li><li><a href="{base}#channels">채널</a></li></ul></div>
      <div><h4>정책</h4><ul><li><a href="{base}#directory">정책 및 약관</a></li><li><a href="{base}app-ads.txt">app-ads.txt</a></li></ul></div>
      <div><h4>문의</h4><ul><li><a href="mailto:superwork.master@gmail.com">superwork.master@gmail.com</a></li></ul></div>
    </div>
    <p class="copyright">© 2026 Superwork. All rights reserved.</p>
  </div>
</footer>'''


def page(title, desc, base, current, body, style='', head_extra=''):
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}"/>
<meta name="theme-color" content="#0a0c10"/>
<meta property="og:title" content="{e(title)}"/>
<meta property="og:description" content="{e(desc)}"/>
<meta property="og:type" content="website"/>
{head_extra}<link rel="stylesheet" href="{base}assets/site.css"/>
<style>{style}</style>
</head>
<body>
{header(base, current)}
<main>
{body}
</main>
{footer(base)}
</body>
</html>
'''


DETAIL_STYLE = '''
.app-hero{position:relative;min-height:540px;display:flex;align-items:flex-end;overflow:hidden}
.app-hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;animation:kb 18s ease-in-out infinite alternate}
.app-hero::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,16,.15) 0%,rgba(10,12,16,.55) 55%,var(--bg) 100%)}
.app-hero.soft>img{filter:blur(28px) brightness(.7) saturate(1.2);transform:scale(1.2);animation:none}
@keyframes kb{to{transform:scale(1.12) translate(-2%,-2%)}}
.app-hero .wrap{position:relative;z-index:1;padding-bottom:52px}
.crumbs{display:flex;gap:8px;flex-wrap:wrap;color:rgba(255,255,255,.7);font-weight:700;font-size:14px;margin-bottom:26px}
.crumbs a:hover{color:#fff}
.app-id{display:flex;align-items:center;gap:22px;margin-bottom:20px}
.app-id img{width:96px;height:96px;border-radius:24px;box-shadow:0 14px 34px rgba(0,0,0,.5)}
.app-id .genre{color:var(--accent);font-weight:800}
.app-id h1{font-size:clamp(38px,6vw,72px);line-height:1.05;font-weight:900;letter-spacing:-.03em}
.app-lead{font-size:clamp(17px,2vw,21px);max-width:720px;color:rgba(255,255,255,.9);margin-bottom:30px}
.app-cta{display:flex;gap:12px;flex-wrap:wrap;align-items:center}

.block{padding:72px 0 0}
.block>h2{font-size:clamp(26px,3.4vw,38px);font-weight:900;letter-spacing:-.02em;margin-bottom:24px}
.block>h2 small{display:block;color:var(--accent);font-size:13px;letter-spacing:.12em;margin-bottom:10px}
.media-grid{display:grid;grid-template-columns:2fr 1fr;gap:24px}
.art{border-radius:var(--radius);overflow:hidden;border:1px solid var(--line)}
.art img{width:100%;aspect-ratio:2.34;object-fit:cover}
.art video{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#000}
.side{display:grid;gap:16px;align-content:start}
.side h3{font-size:15px;color:var(--dim);margin-bottom:12px}
.facts-table{display:grid;grid-template-columns:auto 1fr;gap:10px 18px;font-size:15px}
.facts-table dt{color:var(--dim)}
.qr{display:flex;gap:18px;align-items:center}
.qr img{width:112px;height:112px;border-radius:12px;background:#fff;padding:6px}
.qr p{color:var(--dim);font-size:14px}

.svc-head{font-size:clamp(24px,3vw,34px);font-weight:900;letter-spacing:-.02em;margin-bottom:12px}
.svc-lead{color:#c9ced6;font-size:18px;max-width:820px;margin-bottom:18px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.chips span{font-size:14px;font-weight:700;padding:7px 14px;border-radius:999px;background:rgba(255,255,255,.07);border:1px solid var(--line)}
.svc-section{margin-top:40px}
.svc-section h3{font-size:22px;font-weight:800;margin-bottom:8px}
.svc-section>p{color:var(--dim);margin-bottom:18px;max-width:820px}
.items{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
.item b{display:block;font-size:18px;margin-bottom:6px}
.item p{color:var(--dim);font-size:15px}
.item .no{color:var(--accent);font-weight:900;font-size:14px;margin-bottom:8px;display:block}
.privacy{margin-top:40px;background:linear-gradient(135deg,rgba(61,90,128,.25),rgba(0,217,163,.06));border-color:rgba(120,160,220,.35)}
.privacy h3{font-size:20px;margin-bottom:8px}
.privacy p{color:#c9ced6}

.docs{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.doc{display:flex;flex-direction:column;gap:6px}
.doc b{font-size:18px}
.doc span{color:var(--dim);font-size:13px;overflow-wrap:anywhere}
.note{color:var(--dim);font-size:14px;margin-top:14px}
@media(max-width:860px){.media-grid{grid-template-columns:1fr}.app-hero{min-height:460px}.app-id img{width:72px;height:72px}}
'''


def media(app, base):
    if app.get('video'):
        poster = f' poster="{base}{e(app["videoPoster"])}"' if app.get('videoPoster') else ''
        return (f'<figure class="art reveal"><video src="{base}{e(app["video"])}"{poster} '
                f'autoplay muted loop playsinline preload="metadata" aria-label="{e(app["name"])} 소개 영상"></video></figure>')
    return f'<figure class="art reveal"><img src="{base}{e(app["thumb"])}" alt="{e(app["name"])} 대표 이미지"></figure>'


def card(o, base):
    icon = f'<img src="{base}{e(o["icon"])}" alt="">' if o.get('icon') else ''
    return (f'<a class="acard reveal" href="{base}{e(o["path"])}">'
            f'<div class="acard-media"><img src="{base}{e(o["thumbSm"])}" alt="" loading="lazy" style="object-position:{e(o["thumbPos"])}"><span class="acard-more">자세히 보기 →</span></div>'
            f'<div class="acard-body">{icon}<div><div class="acard-genre">{e(o["genre"])}</div><b>{e(o["name"])}</b></div></div>'
            f'<p class="acard-desc">{e(o["desc"])}</p></a>')


def service(app):
    d = app['details']
    out = []
    if d.get('headline'):
        out.append(f'<p class="svc-head reveal">{e(d["headline"])}</p>')
    out.append(f'<p class="svc-lead reveal">{e(d["lead"])}</p>')
    if d.get('facts'):
        out.append('<div class="chips reveal">' + ''.join(f'<span>{e(f)}</span>' for f in d['facts']) + '</div>')
    for sec in d.get('sections', []):
        numbered = all(i.get('desc') for i in sec['items']) and len(sec['items']) <= 3
        items = ''
        for n, i in enumerate(sec['items'], 1):
            no = f'<span class="no">{n:02d}</span>' if numbered else ''
            desc = f'<p>{e(i["desc"])}</p>' if i.get('desc') else ''
            items += f'<div class="panel item reveal">{no}<b>{e(i["title"])}</b>{desc}</div>'
        intro = f'<p>{e(sec["intro"])}</p>' if sec.get('intro') else ''
        out.append(f'<div class="svc-section"><h3 class="reveal">{e(sec["title"])}</h3>{intro}<div class="items">{items}</div></div>')
    if d.get('privacy'):
        p = d['privacy']
        out.append(f'<div class="panel privacy reveal"><h3>{e(p["title"])}</h3><p>{e(p["body"])}</p></div>')
    return ''.join(out)


def jsonld(app):
    oses = sorted({OS[c] for c in app.get('channels', []) if c in OS})
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
    if app.get('link'):
        data['installUrl'] = app['link']
    body = json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')
    return f'<script type="application/ld+json">\n{body}\n</script>\n'


def detail(app, others):
    base = '../../'
    cat = CATS[app['category']]
    icon = f'<img src="{base}{e(app["icon"])}" alt="">' if app.get('icon') else ''
    cta = (f'<a class="btn btn-primary" href="{e(app["link"])}" target="_blank" rel="noopener">{e(app["store"])} ↗</a>'
           if app.get('link') else '<span class="btn btn-ghost" aria-disabled="true">스토어 링크 준비 중</span>')

    facts = [('분류', f'{cat["label"]} · {app["genre"]}')]
    if app.get('channels'):
        facts.append(('출시 채널', ' · '.join(app['channels'])))
    facts.append(('문의', 'superwork.master@gmail.com'))
    side = [f'<div class="panel reveal"><h3>이용 정보</h3><dl class="facts-table">'
            + ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in facts) + '</dl></div>']
    if app.get('qr'):
        side.append(f'<div class="panel qr reveal"><img src="{base}{e(app["qr"])}" alt="{e(app["name"])} QR"><p>휴대폰 카메라로 스캔하면<br>바로 열립니다.</p></div>')

    policy_block = '''<section class="block"><h2><small>POLICY</small>정책 문서</h2>
  <p class="note">이 앱의 개인정보처리방침과 이용약관은 앱이 출시된 스토어와 앱 안에서 확인할 수 있습니다.</p></section>'''

    body = f'''
<section class="app-hero{' soft' if app.get('heroSoft') else ''}">
  <img src="{base}{e(app["thumb"])}" alt="" style="object-position:{e(app["thumbPos"])}">
  <div class="wrap">
    <nav class="crumbs" aria-label="위치"><a href="{base}#apps">앱</a><span>/</span><a href="{base}#apps-{e(cat["id"])}">{e(cat["label"])}</a><span>/</span><span>{e(app["name"])}</span></nav>
    <div class="app-id">{icon}<div><div class="genre">{e(app["genre"])}</div><h1>{e(app["name"])}</h1></div></div>
    <p class="app-lead">{e(app["desc"])}</p>
    <div class="app-cta">{cta}</div>
  </div>
</section>
<div class="wrap">
  <section class="block"><h2><small>{'VIDEO' if app.get('video') else 'OVERVIEW'}</small>{'소개 영상' if app.get('video') else '한눈에 보기'}</h2>
    <div class="media-grid">{media(app, base)}<aside class="side">{''.join(side)}</aside></div></section>
  <section class="block"><h2><small>SERVICE</small>서비스 설명</h2>{service(app)}</section>
  {policy_block}
  <section class="block"><h2><small>MORE</small>다른 앱도 둘러보세요</h2>
    <div class="track">{''.join(card(o, base) for o in others)}</div></section>
</div>
<div style="height:80px"></div>'''
    return page(f'{app["name"]} — Superwork', app['desc'], base, 'apps', body, DETAIL_STYLE,
                f'<link rel="canonical" href="{SITE_URL}{e(app["path"])}"/>\n{jsonld(app)}')


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
        same = [o for o in apps if o['category'] == app['category'] and o['id'] != app['id']]
        rest = [o for o in apps if o['category'] != app['category']]
        out = ROOT / app['path'] / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(detail(app, (same + rest)[:8]), encoding='utf-8')
    build_home()
    print(f'index.html 생성 구역 7곳, apps/ 쇼케이스 {len(showcase)}개')


if __name__ == '__main__':
    main()
