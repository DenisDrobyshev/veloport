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
)


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "is_active", "show_in_menu", "order")
    list_filter = ("is_active", "show_in_menu")
    search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "is_active", "is_featured")
    list_editable = ("is_active", "is_featured")
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


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
        "title", "brand", "category", "product_type",
        "price", "old_price", "stock_qty", "rating", "is_active", "is_featured",
    )
    list_editable = ("price", "stock_qty", "is_active", "is_featured")
    list_filter = ("product_type", "is_active", "is_featured", "is_new", "is_bestseller", "brand", "category")
    search_fields = ("title", "sku", "short_description")
    readonly_fields = ("rating", "reviews_count", "views", "created_at", "updated_at")
    inlines = [ProductImageInline, BikeInline, SpecificationInline, ProductVariantInline]
    list_select_related = ("brand", "category")
    fieldsets = (
        (None, {"fields": ("title", "slug", "sku", "product_type", "category", "brand")}),
        ("Описание", {"fields": ("short_description", "description")}),
        ("Цена и склад", {"fields": ("price", "old_price", "stock_qty", "warranty_months")}),
        ("Флаги", {"fields": ("is_active", "is_featured", "is_new", "is_bestseller")}),
        ("Служебное", {"fields": ("rating", "reviews_count", "views", "created_at", "updated_at")}),
    )
