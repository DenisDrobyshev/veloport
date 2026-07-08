from django.contrib import admin

from .models import ServiceBooking, ServiceType, TradeInRequest


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "price_from", "duration_min", "is_active", "order")
    list_editable = ("price_from", "is_active", "order")


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "phone", "service_type", "store", "preferred_date", "status", "created_at")
    list_filter = ("status", "store", "service_type")
    list_editable = ("status",)
    search_fields = ("number", "name", "phone", "bike_info")
    readonly_fields = ("number", "created_at", "updated_at")


@admin.register(TradeInRequest)
class TradeInRequestAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "phone", "brand", "model", "condition", "estimated_price", "status", "created_at")
    list_filter = ("status", "condition")
    list_editable = ("estimated_price", "status")
    search_fields = ("number", "name", "phone", "brand", "model")
    readonly_fields = ("number", "created_at", "updated_at")
