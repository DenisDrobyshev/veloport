"""Генерация «студийных» SVG-изображений товаров.

Пока нет реальных фото — рисуем аккуратный технический контур велосипеда
(тёмный штрих, красные ободья, мягкая тень на светлом фоне) и минималистичные
line-иконки для аксессуаров. Выглядит как продуманный продуктовый рендер, а не
как случайная нейрокартинка. Реальные фото загружаются в админке поверх.
"""

import math

from django.core.files.base import ContentFile

INK = "#0b0f14"
RED = "#e4002b"
BG = "#f4f5f7"
GREY = "#94a3b8"


def _wheel(cx, cy, r):
    spokes = ""
    for i in range(12):
        a = math.pi * 2 * i / 12
        x = cx + (r - 16) * math.cos(a)
        y = cy + (r - 16) * math.sin(a)
        spokes += (
            f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" '
            f'stroke="{INK}" stroke-width="2" opacity="0.3"/>'
        )
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="11"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r - 13}" fill="none" stroke="{RED}" stroke-width="4"/>'
        f"{spokes}"
        f'<circle cx="{cx}" cy="{cy}" r="8" fill="{INK}"/>'
    )


def _bike():
    return f"""
  {_wheel(255, 350, 100)}
  {_wheel(600, 350, 100)}
  <g fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round">
    <path d="M420 350 L255 350 M420 350 L380 195 M420 350 L560 205 M380 195 L560 205 M380 195 L255 350 M560 205 L600 350"/>
    <path d="M560 205 L548 166" stroke-width="10"/>
    <path d="M512 158 L582 180" stroke-width="11"/>
    <path d="M352 190 Q382 180 412 192" stroke-width="11"/>
    <path d="M420 350 L452 374 M420 350 L388 326" stroke-width="8"/>
  </g>
  <circle cx="420" cy="350" r="15" fill="{INK}"/>
"""


GEAR = {
    "shlemy": f"""
  <g fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">
    <path d="M270 350 a150 135 0 0 1 300 -6 a18 18 0 0 1 -18 20 H288 a18 18 0 0 1 -18 -14 z"/>
    <path d="M300 364 H548"/>
    <path d="M360 240 l34 70 M430 226 l24 82 M498 244 l30 66" stroke="{RED}" stroke-width="9"/>
  </g>""",
    "zamki": f"""
  <g fill="none" stroke="{INK}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round">
    <rect x="320" y="300" width="160" height="140" rx="18"/>
    <path d="M352 300 v-34 a48 48 0 0 1 96 0 v34"/>
    <circle cx="400" cy="358" r="15" fill="{RED}" stroke="none"/>
    <path d="M400 358 v34"/>
  </g>""",
    "nasosy": f"""
  <g fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">
    <rect x="372" y="240" width="56" height="200" rx="10"/>
    <path d="M400 240 v-44 M362 196 h76"/>
    <path d="M428 410 h54 a16 16 0 0 1 16 16 v18" stroke="{RED}"/>
  </g>""",
    "fary": f"""
  <g fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">
    <rect x="322" y="286" width="118" height="88" rx="18"/>
    <path d="M322 306 h-28 M322 354 h-28"/>
    <path d="M452 300 l64 -22 M452 330 l68 2 M452 360 l64 22" stroke="{RED}" stroke-width="9"/>
  </g>""",
    "flyagi": f"""
  <g fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">
    <path d="M362 262 h76 v22 l10 22 v128 a22 22 0 0 1 -22 22 h-52 a22 22 0 0 1 -22 -22 V306 l10 -22 z"/>
    <path d="M377 262 v-22 h46 v22"/>
    <path d="M352 352 h96" stroke="{RED}"/>
  </g>""",
    "ekipirovka": f"""
  <g fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">
    <path d="M344 254 l-46 34 l34 44 l30 -22 v138 h176 v-138 l30 22 l34 -44 l-46 -34 l-58 -12 a46 34 0 0 1 -96 0 z"/>
    <path d="M400 246 v52" stroke="{RED}"/>
  </g>""",
}


def _gear(cat_slug):
    return GEAR.get(
        cat_slug,
        f'<g fill="none" stroke="{INK}" stroke-width="13" stroke-linejoin="round">'
        f'<path d="M400 250 L560 330 L400 410 L240 330 Z"/>'
        f'<path d="M240 330 V430 L400 510 L560 430 V330" /></g>',
    )


def generate_svg(product) -> str:
    cat_slug = product.category.slug
    is_bike = product.product_type in ("bike", "ebike")
    figure = _bike() if is_bike else _gear(cat_slug)

    brand = (product.brand.name if product.brand else "VELOPORT").upper()
    title = product.title if len(product.title) <= 30 else product.title[:28] + "…"
    ebike = (
        f'<g transform="translate(700,64)"><rect x="-96" y="-24" width="96" height="34" rx="6" fill="{RED}"/>'
        f'<text x="-48" y="-1" fill="#fff" font-size="18" font-weight="800" text-anchor="middle" letter-spacing="1">E-BIKE</text></g>'
        if product.product_type == "ebike"
        else ""
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600" font-family="Inter, Arial, sans-serif">
  <defs>
    <radialGradient id="glow" cx="50%" cy="42%" r="55%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="{BG}"/>
    </radialGradient>
  </defs>
  <rect width="800" height="600" fill="url(#glow)"/>
  <ellipse cx="427" cy="474" rx="290" ry="24" fill="{INK}" opacity="0.08"/>
  {figure}
  {ebike}
  <text x="48" y="548" fill="{GREY}" font-size="20" font-weight="700" letter-spacing="2">{brand}</text>
  <text x="48" y="580" fill="{INK}" font-size="30" font-weight="800">{title}</text>
</svg>"""


def attach_image(product, force: bool = False):
    """Создаёт ProductImage со сгенерированным SVG, если фото ещё нет."""
    from .models import ProductImage

    if product.images.exists():
        if not force:
            return None
        product.images.all().delete()

    svg = generate_svg(product).encode("utf-8")
    image = ProductImage(product=product, is_main=True, alt=product.title)
    image.image.save(f"{product.slug}.svg", ContentFile(svg), save=True)
    return image
