from django.conf import settings

from apps.catalog.models import Category


def catalog_menu(request):
    """Категории для главного меню (корневые + дети)."""
    categories = (
        Category.objects.filter(is_active=True, show_in_menu=True, level=0)
        .prefetch_related("children")
    )
    return {"menu_categories": categories}


def compare_count(request):
    ids = request.session.get(settings.COMPARE_SESSION_ID, [])
    return {"compare_count": len(ids)}
