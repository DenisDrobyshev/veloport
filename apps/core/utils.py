"""Утилиты ядра: транслитерация slug для кириллицы."""

from django.utils.text import slugify

_CYRILLIC = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def ru_slugify(value: str) -> str:
    """Транслитерирует кириллицу в латиницу и делает slug."""
    value = (value or "").lower()
    transliterated = "".join(_CYRILLIC.get(ch, ch) for ch in value)
    return slugify(transliterated)


def unique_slug(instance, value: str, slug_field: str = "slug") -> str:
    """Возвращает уникальный slug для модели instance на основе value."""
    base = ru_slugify(value) or "item"
    model = instance.__class__
    slug = base
    counter = 2
    qs = model._default_manager.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(**{slug_field: slug}).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug
