from django.contrib import admin

from .models import Reservation, Stock, Store


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "has_service", "is_active")
    list_editable = ("has_service", "is_active")
    list_filter = ("city", "has_service", "is_active")
    search_fields = ("name", "city", "address")
    inlines = [StockInline]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "store", "qty")
    list_editable = ("qty",)
    list_filter = ("store",)
    search_fields = ("product__title",)
    autocomplete_fields = ("product", "store")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("number", "product", "store", "name", "phone", "qty", "status", "created_at")
    list_filter = ("status", "store")
    list_editable = ("status",)
    search_fields = ("number", "name", "phone")
    readonly_fields = ("number", "created_at", "updated_at")
