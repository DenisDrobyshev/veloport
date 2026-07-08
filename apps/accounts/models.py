from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь магазина."""

    phone = models.CharField("Телефон", max_length=20, blank=True)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(
        "Рост, см", null=True, blank=True,
        help_text="Поможем подобрать ростовку велосипеда",
    )
    bonus_points = models.PositiveIntegerField("Бонусные баллы", default=0)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.get_full_name() or self.username


class Address(models.Model):
    """Адрес доставки пользователя."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses",
        verbose_name="Пользователь",
    )
    city = models.CharField("Город", max_length=100)
    street = models.CharField("Улица", max_length=150)
    house = models.CharField("Дом", max_length=20)
    apartment = models.CharField("Квартира", max_length=20, blank=True)
    postal_code = models.CharField("Индекс", max_length=10, blank=True)
    is_default = models.BooleanField("По умолчанию", default=False)

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
        ordering = ["-is_default"]

    def __str__(self):
        return f"{self.city}, {self.street} {self.house}"

    @property
    def full(self) -> str:
        parts = [self.postal_code, self.city, f"ул. {self.street}", f"д. {self.house}"]
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        return ", ".join(p for p in parts if p)
