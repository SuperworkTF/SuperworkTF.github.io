#!/usr/bin/env python3
"""장면 HTML 을 프레임 단위로 캡처해 반복 재생용 mp4 로 만든다.

    python3 tools/app-video/render.py tools/app-video/subscribers.html \
        assets/apps/subscribers/preview.mp4 --duration 14

CSS 애니메이션을 실시간으로 녹화하지 않고, 프레임마다 모든 애니메이션의 시간을
직접 맞춘 뒤 캡처한다. 그래서 컴퓨터가 느려도 프레임이 빠지지 않는다.
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

SEEK = """t => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; }
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html', type=Path)
    ap.add_argument('out', type=Path)
    ap.add_argument('--duration', type=float, required=True)
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--size', default='1920x1080')
    ap.add_argument('--crf', type=int, default=24, help='클수록 작고 흐리다. 배경용 영상은 28 정도')
    ap.add_argument('--poster-at', type=float, default=None, help='포스터 이미지로 쓸 시점(초)')
    args = ap.parse_args()

    w, h = map(int, args.size.split('x'))
    frames = round(args.duration * args.fps)
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome')
        page = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
        page.goto(args.html.resolve().as_uri())
        page.evaluate('document.fonts.ready')
        page.wait_for_load_state('networkidle')
        for i in range(frames):
            page.evaluate(SEEK, i * 1000 / args.fps)
            page.screenshot(path=f'{tmp}/{i:05d}.png')
        if args.poster_at is not None:
            page.evaluate(SEEK, args.poster_at * 1000)
            page.screenshot(path=str(args.out.with_suffix('.jpg')), type='jpeg', quality=85)
        browser.close()

        args.out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            'ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(args.fps), '-i', f'{tmp}/%05d.png',
            '-c:v', 'libx264', '-preset', 'slow', '-crf', str(args.crf), '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart', '-an', str(args.out),
        ], check=True)
    print(f'{args.out} ({frames} frames, {args.out.stat().st_size / 1024:.0f} KB)')


if __name__ == '__main__':
    main()
