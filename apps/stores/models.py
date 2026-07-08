from django.db import models
from django.utils.crypto import get_random_string

from apps.core.models import TimeStampedModel
from apps.core.utils import unique_slug


class Store(TimeStampedModel):
    """Физический магазин сети."""

    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("URL", max_length=140, unique=True, blank=True)
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=200)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    work_hours = models.CharField("Часы работы", max_length=120, default="Пн-Вс 10:00–21:00")
    latitude = models.FloatField("Широта", null=True, blank=True)
    longitude = models.FloatField("Долгота", null=True, blank=True)
    has_service = models.BooleanField("Есть веломастерская", default=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.name} ({self.city})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, f"{self.name}-{self.city}")
        super().save(*args, **kwargs)


class Stock(models.Model):
    """Остаток товара в конкретном магазине."""

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="stocks", verbose_name="Магазин",
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="stocks",
        verbose_name="Товар",
    )
    qty = models.PositiveIntegerField("Остаток", default=0)

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки по магазинам"
        unique_together = ("store", "product")

    def __str__(self):
        return f"{self.product} @ {self.store}: {self.qty}"

    @property
    def status(self) -> str:
        if self.qty == 0:
            return "Нет в наличии"
        if self.qty <= 2:
            return "Мало"
        return "В наличии"


class Reservation(TimeStampedModel):
    """Онлайн-резерв товара в магазине."""

    STATUS_NEW = "new"
    STATUS_READY = "ready"
    STATUS_DONE = "done"
    STATUS_CANCELED = "canceled"
    STATUSES = [
        (STATUS_NEW, "Новый"),
        (STATUS_READY, "Готов к выдаче"),
        (STATUS_DONE, "Выдан"),
        (STATUS_CANCELED, "Отменён"),
    ]

    number = models.CharField("Номер", max_length=20, unique=True, editable=False)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="reservations", verbose_name="Магазин",
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="reservations",
        verbose_name="Товар",
    )
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    qty = models.PositiveIntegerField("Количество", default=1)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=10, choices=STATUSES, default=STATUS_NEW)

    class Meta:
        verbose_name = "Резерв"
        verbose_name_plural = "Резервы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Резерв {self.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = "RS-" + get_random_string(7, "0123456789")
        super().save(*args, **kwargs)
