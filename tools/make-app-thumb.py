#!/usr/bin/env python3
"""키아트가 없는 앱의 썸네일을 아이콘으로 만든다.

    python3 tools/make-app-thumb.py ururu 우르르 "소속 대항 미니게임, 한 판 20초"

assets/apps/<id>/icon.png 의 주된 색으로 배경을 깔고, 이름·한 줄 소개·아이콘을 얹어
thumb.jpg(1932x828)와 thumb-sm.jpg(800px)를 쓴다. 글자와 아이콘은 16:9 카드로 잘려도
남는 가운데 영역(가로 16%~84%) 안에 둔다. macOS 의 Apple SD Gothic Neo 글꼴을 쓴다.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
W, H = 1932, 828
SAFE_L, SAFE_R = int(W * 0.16), int(W * 0.84)


def font(size, bold=True):
    return ImageFont.truetype(FONT, size, index=6 if bold else 2)


def dominant(img):
    px = [p[:3] for p in img.convert('RGBA').resize((32, 32)).get_flattened_data()
          if p[3] > 200 and min(p[:3]) <= 235 and max(p[:3]) >= 25]
    return tuple(sum(c[i] for c in px) // len(px) for i in range(3)) if px else (60, 70, 90)


def main(app_id, name, tagline):
    d = Path(__file__).resolve().parent.parent / 'assets/apps' / app_id
    icon = Image.open(d / 'icon.png').convert('RGBA') if (d / 'icon.png').exists() else None
    base = dominant(icon) if icon else (60, 70, 90)
    dark = tuple(int(c * .28) for c in base)
    mid = tuple(int(c * .7) for c in base)

    bg = Image.new('RGB', (W, H))
    g = ImageDraw.Draw(bg)
    for x in range(W):
        t = x / W
        g.line([(x, 0), (x, H)], fill=tuple(int(dark[i] * (1 - t) + mid[i] * t) for i in range(3)))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((SAFE_R - 700, -150, SAFE_R + 200, H + 150), fill=base + (150,))
    bg = Image.alpha_composite(bg.convert('RGBA'), glow.filter(ImageFilter.GaussianBlur(120)))

    if icon:
        s = 440
        ic = icon.resize((s, s), Image.LANCZOS)
        mask = Image.new('L', (s, s), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, s, s), radius=100, fill=255)
        x0, y0 = SAFE_R - s - 40, (H - s) // 2
        shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((x0 + 18, y0 + 30, x0 + s + 18, y0 + s + 30), radius=100, fill=(0, 0, 0, 140))
        bg = Image.alpha_composite(bg, shadow.filter(ImageFilter.GaussianBlur(30)))
        bg.paste(ic, (x0, y0), mask)

    dr = ImageDraw.Draw(bg)
    x = SAFE_L + 20
    dr.text((x, 230), 'SUPERWORK', font=font(40), fill=(255, 255, 255, 170))
    dr.text((x - 6, 286), name, font=font(160), fill='white')
    dr.text((x, 500), tagline, font=font(52, bold=False), fill=(255, 255, 255, 215))

    out = bg.convert('RGB')
    out.save(d / 'thumb.jpg', quality=86, optimize=True, progressive=True)
    small = out.copy()
    small.thumbnail((800, 800), Image.LANCZOS)
    small.save(d / 'thumb-sm.jpg', quality=80, optimize=True, progressive=True)
    print(d / 'thumb.jpg')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
