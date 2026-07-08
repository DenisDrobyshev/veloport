from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, User


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [AddressInline]
    list_display = ("username", "email", "phone", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "phone", "first_name", "last_name")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Профиль магазина", {"fields": ("phone", "patronymic", "birth_date", "height_cm", "bonus_points")}),
    )
