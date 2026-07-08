from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "variant", "title", "price", "qty")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "full_name", "phone", "status", "delivery_method", "total", "is_paid", "created_at")
    list_filter = ("status", "delivery_method", "payment_method", "is_paid")
    list_editable = ("status", "is_paid")
    search_fields = ("number", "first_name", "last_name", "phone", "email")
    readonly_fields = ("number", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
