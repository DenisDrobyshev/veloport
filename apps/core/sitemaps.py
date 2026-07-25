from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.catalog.models import Category, Product
from apps.content.models import Article


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.active()

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticSitemap(Sitemap):
    priority = 0.4
    changefreq = "monthly"

    def items(self):
        return [
            "core:home", "catalog:list", "core:fit_finder", "stores:list",
            "service:index", "service:tradein", "content:blog", "content:guides",
        ]

    def location(self, item):
        return reverse(item)


SITEMAPS = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "articles": ArticleSitemap,
    "static": StaticSitemap,
}
