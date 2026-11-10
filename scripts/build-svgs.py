#!/usr/bin/env python3
"""生成 GitHub Profile README 使用的 SVG。

视觉与 Blog（D:/MyScienceDemo/Blog）同源：同一套语义色、
藤蔓与叶片的笔触。每个图形输出日间 / 夜间两份，README 用
<picture> 按 prefers-color-scheme 切换。

跑一次：python scripts/build-svgs.py
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# 与 Blog/src/styles/tokens.css 对齐的语义色
# --------------------------------------------------------------------------

THEMES = {
    "light": {
        "fg": "#263b2e",
        "muted": "#48604e",
        "brand": "#3f7050",
        "border": "#878787",
    },
    "dark": {
        "fg": "#eeeeee",
        "muted": "#c8c8c8",
        "brand": "#a9d8b4",
        "border": "#66786c",
    },
}

SANS = (
    'Satoshi, "Avenir Next", "Segoe UI", system-ui, '
    '"PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif'
)
MONO = (
    'ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, '
    '"Microsoft YaHei", monospace'
)

# 站点标志：logo 里的 C 形符号，1024 × 1024 画布。
SYMBOL = (
    "M 1024 512 L 723.933 512 C 723.933 409.823 651.028 322.193 550.557 303.604 "
    "C 450.085 285.015 350.654 340.76 314.096 436.173 C 277.539 531.587 314.264 639.5 "
    "401.435 692.806 C 488.605 746.112 601.398 729.632 669.673 653.614 L 1004.026 653.614 "
    "C 929.662 911.986 668.121 1068.827 405.177 1012.732 C 142.233 956.637 -32.532 706.718 "
    "5.018 440.492 C 42.568 174.266 279.641 -17.565 547.842 1.256 C 816.043 20.077 "
    "1024 243.139 1024 512 Z"
)

# 叶片与叶脉沿用 Blog 中 HeroVine 的笔触（单位约 13）。
LEAF = "M0 0 C1.33 -4.02 6.12 -6.28 13.3 -0.64 C8.78 2.74 3.19 4.02 0 0 Z"
VEIN = "M0.67 0 C4.65 -1.29 8.65 -0.97 12.5 -0.08"
PETIOLE = "M0 0 Q1.5 -1.05 3 0"


def symbol(cx: float, cy: float, size: float, fill: str) -> str:
    s = size / 1024
    return (
        f'<g transform="translate({cx - size / 2:.2f} {cy - size / 2:.2f}) scale({s:.6f})">'
        f'<path d="{SYMBOL}" fill="{fill}"/></g>'
    )


def smooth(points: list[tuple[float, float]]) -> str:
    """Catmull-Rom 转三次贝塞尔，藤蔓才不会有折角。"""
    if not points:
        return ""
    d = f"M {points[0][0]:.2f} {points[0][1]:.2f} "
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += (
            f"C {c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} "
            f"{p2[0]:.2f} {p2[1]:.2f} "
        )
    return d.strip()


def tendril(scale: float = 1.0) -> str:
    pts = []
    for i in range(42):
        t = i / 41
        a = t * 4.4 * math.pi
        r = 0.5 + 2.7 * t
        pts.append((math.cos(a) * r * scale, math.sin(a) * r * scale))
    return smooth(pts)


def leaf(deg: float, scale: float = 1.0, opacity: float = 0.55) -> str:
    return (
        f'<g transform="rotate({deg:.2f}) scale({scale:.3f})">'
        f'<path d="{PETIOLE}" fill="none" stroke="currentColor" stroke-width="0.8" '
        f'stroke-linecap="round" opacity="0.85"/>'
        f'<g transform="translate(3 0)">'
        f'<path d="{LEAF}" fill="currentColor" opacity="{opacity}"/>'
        f'<path d="{VEIN}" fill="none" stroke="currentColor" stroke-width="0.34" '
        f'stroke-linecap="round" opacity="0.55"/>'
        f"</g></g>"
    )


def wrap_svg(width: int, height: int, body: str, title: str = "") -> str:
    if not title:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" aria-hidden="true">{body}</svg>\n'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">'
        f"<title>{title}</title>{body}</svg>\n"
    )


# --------------------------------------------------------------------------
# 1. 首屏横幅
# --------------------------------------------------------------------------


def hero(t: dict) -> str:
    w, h = 1200, 380

    # 藤蔓从标题的句号旁长出来，向右上方伸出去；不画头像框。
    pts = [
        (482, 270), (520, 316), (584, 334), (672, 316),
        (772, 268), (872, 212), (968, 164), (1062, 128), (1150, 110),
    ]

    leaves = ""
    for idx, i in enumerate((1, 3, 4, 6, 7)):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        angle = math.degrees(math.atan2(p2[1] - p0[1], p2[0] - p0[0]))
        tilt = 48 if idx % 2 == 0 else -46
        leaves += (
            f'<g transform="translate({p1[0]} {p1[1]})">'
            f'{leaf(angle + tilt, 1.8, 0.55)}</g>'
        )

    end_angle = math.degrees(
        math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
    )
    tendril_g = (
        f'<g transform="translate({pts[-1][0]} {pts[-1][1]}) rotate({end_angle:.2f})">'
        f'<path d="{tendril(1.1)}" fill="currentColor" opacity="0.5"/></g>'
    )

    grad = (
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["brand"]}"/>'
        f'<stop offset="1" stop-color="{t["fg"]}"/>'
        f"</linearGradient>"
    )

    body = f"""
<defs>{grad}
<style>
  .vine {{ transform-box: fill-box; transform-origin: 0% 100%; animation: sway 13s ease-in-out infinite alternate; }}
  @keyframes sway {{ from {{ transform: rotate(-0.5deg); }} to {{ transform: rotate(0.55deg); }} }}
  @media (prefers-reduced-motion: reduce) {{ .vine {{ animation: none; }} }}
</style>
</defs>

<g transform="translate(80 0)" font-family='{SANS}'>
  <text y="126" font-size="21" fill="{t["fg"]}">你好，我是 <tspan font-size="25" font-weight="700" fill="{t["brand"]}">clerimia</tspan></text>
  <text y="198" font-size="56" font-weight="800" fill="{t["fg"]}" letter-spacing="0.5">\
<tspan fill="url(#accent)">一边</tspan>创作，</text>
  <text y="266" font-size="56" font-weight="800" fill="{t["fg"]}" letter-spacing="0.5">\
<tspan fill="url(#accent)">一边</tspan>成为自己<tspan fill="{t["brand"]}">。</tspan></text>
  <text y="314" font-size="19" fill="{t["muted"]}">合肥工业大学在读，关注 \
<tspan fill="{t["fg"]}" font-weight="600">AI Agent</tspan> 与 \
<tspan fill="{t["fg"]}" font-weight="600">全栈开发</tspan>。</text>
</g>

<g class="vine" color="{t["brand"]}" fill="none">
  <path d="{smooth(pts)}" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" opacity="0.5"/>
  {leaves}
  {tendril_g}
</g>
"""
    return wrap_svg(w, h, body, "clerimia — 一边创作，一边成为自己")


# --------------------------------------------------------------------------
# 2. 分隔线
# --------------------------------------------------------------------------


def divider(t: dict) -> str:
    w, h = 1080, 52
    y = 26
    body = f"""
<g color="{t["brand"]}" fill="none">
  <path d="M 28 {y} H 512" stroke="{t["border"]}" stroke-opacity="0.4" stroke-linecap="round"/>
  <path d="M 568 {y} H 1052" stroke="{t["border"]}" stroke-opacity="0.4" stroke-linecap="round"/>
  <g transform="translate(540 {y})">
    <path d="M 0 6 L 0 -6" stroke="currentColor" stroke-opacity="0.6" stroke-width="1.6" stroke-linecap="round"/>
    <g transform="translate(0 -6)" opacity="0.9">{leaf(-45, 1.8, 0.75)}</g>
    <g transform="translate(0 -6) scale(-1 1)" opacity="0.55">{leaf(-45, 1.45, 0.75)}</g>
    <circle cx="0" cy="8" r="1.6" fill="currentColor" opacity="0.55"/>
  </g>
</g>
"""
    return wrap_svg(w, h, body, "")


# --------------------------------------------------------------------------
# 3. 收尾签名
# --------------------------------------------------------------------------


def outro(t: dict) -> str:
    w, h = 1080, 232
    pts = []
    for i in range(49):
        k = i / 48
        x = 300 + 480 * k
        pts.append((x, 196 + 4.2 * math.sin(k * math.pi * 2.2)))
    leaves = ""
    for k, tilt in ((0.18, -58), (0.5, 62), (0.82, -52)):
        idx = int(k * (len(pts) - 1))
        x, yy = pts[idx]
        leaves += (
            f'<g transform="translate({x:.2f} {yy:.2f})">'
            f'{leaf(tilt, 1.35, 0.6)}</g>'
        )

    body = f"""
<g font-family='{SANS}'>
  {symbol(540, 44, 40, t["brand"])}
  <text x="540" y="118" text-anchor="middle" font-size="29" font-weight="800"
        fill="{t["fg"]}" letter-spacing="0.5">一边创作，一边成为自己<tspan fill="{t["brand"]}">。</tspan></text>
  <text x="540" y="154" text-anchor="middle" font-family='{MONO}' font-size="13"
        fill="{t["brand"]}" letter-spacing="1.2">clerimia.github.io</text>
  <g color="{t["brand"]}" fill="none">
    <path d="{smooth(pts)}" fill="none" stroke="currentColor" stroke-width="1.5"
          stroke-linecap="round" opacity="0.32"/>
    {leaves}
  </g>
</g>
"""
    return wrap_svg(w, h, body, "一边创作，一边成为自己")


# --------------------------------------------------------------------------


def main() -> None:
    builders = {
        "hero": hero,
        "divider": divider,
        "outro": outro,
    }
    for name, build in builders.items():
        for mode, tokens in THEMES.items():
            path = OUT / (f"{name}-{mode}.svg" if mode == "dark" else f"{name}.svg")
            path.write_text(build(tokens), encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
