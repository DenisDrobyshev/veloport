from django.contrib import admin
from django.utils.html import format_html

from .models import Coupon, Order, OrderItem


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "amount", "min_order_sum", "used_count", "usage_limit", "is_active")
    list_editable = ("is_active",)
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)

STATUS_COLORS = {
    Order.STATUS_NEW: "#2563eb",
    Order.STATUS_CONFIRMED: "#0d9488",
    Order.STATUS_ASSEMBLING: "#f59e0b",
    Order.STATUS_SHIPPED: "#7c3aed",
    Order.STATUS_READY: "#0891b2",
    Order.STATUS_DONE: "#16a34a",
    Order.STATUS_CANCELED: "#ef4444",
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "variant", "title", "price", "qty", "cost")
    can_delete = False

    @admin.display(description="Сумма")
    def cost(self, obj):
        return f"{obj.cost} ₽"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "full_name", "phone", "status_badge", "delivery_method", "total_fmt", "paid_badge", "created_at")
    list_filter = ("status", "delivery_method", "payment_method", "is_paid", "created_at")
    search_fields = ("number", "first_name", "last_name", "phone", "email")
    readonly_fields = ("number", "total", "discount", "bonus_used", "bonus_earned",
                       "coupon", "created_at", "updated_at", "payment_id")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    list_per_page = 30
    save_on_top = True
    actions = ["mark_paid", "mark_assembling", "mark_done"]

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#64748b")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;'
            'font-size:11px;font-weight:600;white-space:nowrap">{}</span>',
            color, obj.get_status_display(),
        )

    @admin.display(description="Сумма", ordering="total")
    def total_fmt(self, obj):
        return format_html("<b>{} ₽</b>", int(obj.total))

    @admin.display(description="Оплата")
    def paid_badge(self, obj):
        if obj.is_paid:
            return format_html('<span style="color:#16a34a;font-weight:700">● оплачен</span>')
        return format_html('<span style="color:#94a3b8">○ не оплачен</span>')

    @admin.action(description="Отметить оплаченными")
    def mark_paid(self, request, queryset):
        queryset.update(is_paid=True)

    @admin.action(description="Перевести в «Сборка»")
    def mark_assembling(self, request, queryset):
        queryset.update(status=Order.STATUS_ASSEMBLING)

    @admin.action(description="Отметить выполненными")
    def mark_done(self, request, queryset):
        queryset.update(status=Order.STATUS_DONE)
