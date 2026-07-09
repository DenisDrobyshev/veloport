from django.contrib import admin
from django.utils.html import format_html

from .models import Banner, Subscriber


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("image_thumb", "title", "order", "is_active")
    list_display_links = ("title",)
    list_editable = ("order", "is_active")

    @admin.display(description="Изображение")
    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:36px;width:64px;object-fit:cover;border-radius:6px" />', obj.image.url)
        return "—"


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
    search_fields = ("email",)
