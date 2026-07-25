"""Корневые маршруты Veloport."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core import views as core_views
from apps.core.sitemaps import SITEMAPS

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
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", core_views.robots_txt, name="robots"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
