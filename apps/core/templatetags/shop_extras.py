from django import template
from django.utils.safestring import mark_safe

register = template.Library()

NBSP = " "


@register.filter
def rub(value):
    """Форматирует число как рубли: 45 000 ₽ (неразрывные пробелы)."""
    try:
        value = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    grouped = f"{value:,}".replace(",", NBSP)
    return f"{grouped}{NBSP}₽"


@register.filter
def num(value):
    """Число с разделителями тысяч без валюты."""
    try:
        value = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    return f"{value:,}".replace(",", NBSP)


@register.filter
def stars(value):
    """Возвращает строку из звёзд по рейтингу (0..5)."""
    try:
        full = int(round(float(value)))
    except (TypeError, ValueError):
        full = 0
    full = max(0, min(5, full))
    return "★" * full + "☆" * (5 - full)


@register.simple_tag
def query_replace(request, **kwargs):
    """Обновляет query-параметры текущего URL."""
    params = request.GET.copy()
    for key, val in kwargs.items():
        params[key] = val
    return params.urlencode()


# --- SVG-иконки (feather-style, currentColor) вместо эмодзи ---
ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/>',
    "cart": '<circle cx="9" cy="20" r="1.6"/><circle cx="18" cy="20" r="1.6"/><path d="M2 3h3l2.4 12.2a1.6 1.6 0 0 0 1.6 1.3h8.3a1.6 1.6 0 0 0 1.6-1.2L22 7H6"/>',
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "compare": '<path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/><path d="M8 3 4 5l4 2"/><path d="m16 10 4 2-4 2"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "chevron": '<path d="M6 9l6 6 6-6"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.5-1.1a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2z"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.3L3 18l3 3 6.4-6.3a4 4 0 0 0 5.3-5.4l-2.6 2.6-2.3-.4-.4-2.3z"/>',
    "recycle": '<path d="M7 19H4a2 2 0 0 1-1.7-3l2.3-4"/><path d="m10 11-3.2 2 2.7 4.6"/><path d="M12 5.5 14 2l3.4 6"/><path d="M20.5 14 22 17a2 2 0 0 1-1.7 3H14"/>',
    "truck": '<rect x="1" y="4" width="14" height="12" rx="1"/><path d="M15 8h4l4 4v4h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "star": '<path d="M12 2l3 6.5 7 .9-5 4.9 1.2 7-6.2-3.4L5.8 21 7 14.3 2 9.4l7-.9z"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "minus": '<path d="M5 12h14"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
    "bolt": '<path d="M13 2 4 14h6l-1 8 9-12h-6z"/>',
    "box": '<path d="M21 8 12 3 3 8l9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/>',
    "ruler": '<path d="M3 8l13-5 5 13-13 5z"/><path d="M7 9l1 2M11 8l1 2M15 11l1 2M9 13l1 2"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 1 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "return": '<path d="M3 7v6h6"/><path d="M3 13a9 9 0 1 0 3-7.7L3 7"/>',
}


@register.simple_tag
def icon(name, css="w-5 h-5"):
    body = ICONS.get(name, "")
    return mark_safe(
        f'<svg class="{css}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )
