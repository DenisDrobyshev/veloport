from django.contrib import admin

from .models import FAQ, Article, Page, SizeChart


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "published_at", "views")
    list_filter = ("category", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title", "excerpt", "body")
    date_hierarchy = "published_at"


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title", "body")


@admin.register(SizeChart)
class SizeChartAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "order", "is_active")
    list_editable = ("category", "order", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("question", "answer")
