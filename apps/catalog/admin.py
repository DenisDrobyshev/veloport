from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin

from .models import (
    Bike,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
    Specification,
    StockNotification,
)


@admin.register(StockNotification)
class StockNotificationAdmin(admin.ModelAdmin):
    list_display = ("email", "product", "is_notified", "created_at")
    list_filter = ("is_notified",)
    search_fields = ("email", "product__title")
    autocomplete_fields = ("product",)


def _thumb(url, h=44):
    return format_html(
        '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;'
        'border-radius:6px;border:1px solid #e5e7eb;background:#fff" />',
        url, h, int(h * 1.3),
    )


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "is_active", "show_in_menu", "order")
    list_filter = ("is_active", "show_in_menu")
    search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("logo_thumb", "name", "country", "is_active", "is_featured")
    list_display_links = ("name",)
    list_editable = ("is_active", "is_featured")
    search_fields = ("name",)

    @admin.display(description="Лого")
    def logo_thumb(self, obj):
        if obj.logo:
            return _thumb(obj.logo.url, 30)
        return "—"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("preview",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.image:
            return _thumb(obj.image.url, 70)
        return "—"


class BikeInline(admin.StackedInline):
    model = Bike
    extra = 0
    max_num = 1
    can_delete = True


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "thumb", "title", "brand", "category", "product_type",
        "price", "old_price", "stock_badge", "rating", "is_active", "is_featured",
    )
    list_display_links = ("title",)
    list_editable = ("price", "is_active", "is_featured")
    list_filter = ("product_type", "is_active", "is_featured", "is_new", "is_bestseller", "brand", "category")
    search_fields = ("title", "sku", "short_description")
    readonly_fields = ("rating", "reviews_count", "views", "created_at", "updated_at", "big_preview")
    inlines = [ProductImageInline, BikeInline, SpecificationInline, ProductVariantInline]
    list_select_related = ("brand", "category")
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (None, {"fields": ("big_preview", "title", "slug", "sku", "product_type", "category", "brand")}),
        ("Описание", {"fields": ("short_description", "description")}),
        ("Цена и склад", {"fields": ("price", "old_price", "stock_qty", "warranty_months")}),
        ("Флаги", {"fields": ("is_active", "is_featured", "is_new", "is_bestseller")}),
        ("Служебное", {"fields": ("rating", "reviews_count", "views", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Фото")
    def thumb(self, obj):
        if obj.main_image:
            return _thumb(obj.main_image.url, 40)
        return "—"

    @admin.display(description="Превью")
    def big_preview(self, obj):
        if obj.main_image:
            return _thumb(obj.main_image.url, 150)
        return "Фото появится после сохранения"

    @admin.display(description="Склад")
    def stock_badge(self, obj):
        if obj.stock_qty == 0:
            color, text = "#ef4444", "нет"
        elif obj.stock_qty <= 2:
            color, text = "#f59e0b", f"{obj.stock_qty} шт"
        else:
            color, text = "#16a34a", f"{obj.stock_qty} шт"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;'
            'font-size:11px;font-weight:600">{}</span>', color, text,
        )
