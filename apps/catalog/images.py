"""Генерация SVG-изображений товаров (пока нет реальных фото).

Рисуем аккуратный велосипед для байков и иконку для аксессуаров на
фирменном градиенте. Изображения сохраняются в media и показываются
как обычные <img>. Реальные фото можно загрузить в админке — они
заменят сгенерированные.
"""

from django.core.files.base import ContentFile

PALETTE = {
    "gornye": ("#0f766e", "#14b8a6"),
    "shosseynye": ("#1d4ed8", "#3b82f6"),
    "gorodskie": ("#b45309", "#f59e0b"),
    "gravel": ("#9a3412", "#ea580c"),
    "detskie": ("#be185d", "#ec4899"),
    "electro": ("#6d28d9", "#8b5cf6"),
}
DEFAULT_COLORS = ("#334155", "#64748b")

GEAR_EMOJI = {
    "shlemy": "🪖",
    "zamki": "🔒",
    "nasosy": "💨",
    "fary": "🔦",
    "flyagi": "🍶",
    "ekipirovka": "👕",
}

_BIKE = """
  <g fill="none" stroke="#ffffff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" opacity="0.95">
    <circle cx="230" cy="340" r="92"/>
    <circle cx="620" cy="340" r="92"/>
    <circle cx="230" cy="340" r="6" fill="#fff"/>
    <circle cx="620" cy="340" r="6" fill="#fff"/>
    <path d="M400 340 L230 340 M400 340 L360 190 M400 340 L520 200 M360 190 L520 200 M360 190 L230 340 M520 200 L620 340"/>
    <path d="M520 200 L505 165 M470 158 L525 176"/>
    <path d="M336 186 L392 186"/>
    <circle cx="400" cy="340" r="15" fill="#fff"/>
  </g>
"""


def _gradient_bg(c1, c2):
    return f"""
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="url(#g)"/>
  <circle cx="680" cy="90" r="220" fill="#ffffff" opacity="0.06"/>
  <circle cx="120" cy="520" r="180" fill="#ffffff" opacity="0.06"/>
"""


def generate_svg(product) -> str:
    cat_slug = product.category.slug
    is_bike = product.product_type in ("bike", "ebike")
    colors = PALETTE.get(cat_slug, DEFAULT_COLORS if not is_bike else PALETTE.get("gornye"))
    if is_bike and cat_slug in PALETTE:
        colors = PALETTE[cat_slug]
    c1, c2 = colors

    brand = product.brand.name if product.brand else "Veloport"
    title = product.title if len(product.title) <= 26 else product.title[:24] + "…"

    if is_bike:
        figure = _BIKE
        badge = "⚡ E-BIKE" if product.product_type == "ebike" else ""
    else:
        emoji = GEAR_EMOJI.get(cat_slug, "🧰")
        figure = f'<text x="400" y="330" font-size="200" text-anchor="middle" dominant-baseline="central">{emoji}</text>'
        badge = ""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600" font-family="Inter, sans-serif">
{_gradient_bg(c1, c2)}
  <text x="48" y="70" fill="#ffffff" opacity="0.85" font-size="30" font-weight="700">{brand}</text>
  {f'<text x="752" y="70" fill="#ffffff" opacity="0.9" font-size="24" font-weight="700" text-anchor="end">{badge}</text>' if badge else ''}
  {figure}
  <text x="48" y="545" fill="#ffffff" font-size="38" font-weight="800">{title}</text>
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
