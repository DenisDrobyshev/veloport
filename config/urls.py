"""Корневые маршруты Veloport."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Veloport — админ-панель"
admin.site.site_title = "Veloport"
admin.site.index_title = "Управление магазином"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("catalog/", include("apps.catalog.urls")),
    path("cart/", include("apps.cart.urls")),
    path("order/", include("apps.orders.urls")),
    path("account/", include("apps.accounts.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("stores/", include("apps.stores.urls")),
    path("service/", include("apps.service.urls")),
    path("blog/", include("apps.content.urls")),
    path("api/", include("apps.catalog.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
