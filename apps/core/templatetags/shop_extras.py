from django import template

register = template.Library()

NBSP = " "


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
