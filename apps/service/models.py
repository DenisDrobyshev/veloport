from django.db import models
from django.utils.crypto import get_random_string

from apps.core.models import TimeStampedModel
from apps.core.utils import unique_slug


class ServiceType(models.Model):
    """Услуга веломастерской (ТО, сборка, обслуживание вилки и т.д.)."""

    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("URL", max_length=140, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    price_from = models.DecimalField("Цена от, ₽", max_digits=8, decimal_places=2, default=0)
    duration_min = models.PositiveSmallIntegerField("Длительность, мин", default=60)
    icon = models.CharField("Иконка (emoji)", max_length=8, blank=True)
    is_active = models.BooleanField("Активна", default=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Услуга мастерской"
        verbose_name_plural = "Услуги мастерской"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)


class ServiceBooking(TimeStampedModel):
    """Запись в веломастерскую."""

    STATUS_NEW = "new"
    STATUS_CONFIRMED = "confirmed"
    STATUS_IN_WORK = "in_work"
    STATUS_DONE = "done"
    STATUS_CANCELED = "canceled"
    STATUSES = [
        (STATUS_NEW, "Новая"),
        (STATUS_CONFIRMED, "Подтверждена"),
        (STATUS_IN_WORK, "В работе"),
        (STATUS_DONE, "Готово"),
        (STATUS_CANCELED, "Отменена"),
    ]

    number = models.CharField("Номер", max_length=20, unique=True, editable=False)
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="bookings", verbose_name="Услуга",
    )
    store = models.ForeignKey(
        "stores.Store", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="service_bookings", verbose_name="Магазин",
    )
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    bike_info = models.CharField("Велосипед (марка/модель)", max_length=200, blank=True)
    preferred_date = models.DateField("Желаемая дата", null=True, blank=True)
    preferred_time = models.CharField("Желаемое время", max_length=40, blank=True)
    comment = models.TextField("Что беспокоит", blank=True)
    status = models.CharField("Статус", max_length=12, choices=STATUSES, default=STATUS_NEW)

    class Meta:
        verbose_name = "Запись в мастерскую"
        verbose_name_plural = "Записи в мастерскую"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Запись {self.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = "SB-" + get_random_string(7, "0123456789")
        super().save(*args, **kwargs)


class TradeInRequest(TimeStampedModel):
    """Заявка на trade-in (сдать б/у велосипед в зачёт нового)."""

    CONDITION_CHOICES = [
        ("excellent", "Отличное"),
        ("good", "Хорошее"),
        ("normal", "Среднее"),
        ("poor", "Требует ремонта"),
    ]
    STATUS_NEW = "new"
    STATUS_ESTIMATED = "estimated"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"
    STATUSES = [
        (STATUS_NEW, "Новая"),
        (STATUS_ESTIMATED, "Оценена"),
        (STATUS_ACCEPTED, "Принята"),
        (STATUS_DECLINED, "Отклонена"),
    ]

    number = models.CharField("Номер", max_length=20, unique=True, editable=False)
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    brand = models.CharField("Марка", max_length=80)
    model = models.CharField("Модель", max_length=120, blank=True)
    year = models.PositiveSmallIntegerField("Год", null=True, blank=True)
    condition = models.CharField("Состояние", max_length=12, choices=CONDITION_CHOICES, default="good")
    description = models.TextField("Описание", blank=True)
    photo = models.ImageField("Фото", upload_to="tradein/", blank=True)
    desired_product = models.ForeignKey(
        "catalog.Product", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tradein_requests", verbose_name="Хочу взамен",
    )
    estimated_price = models.DecimalField(
        "Оценка, ₽", max_digits=10, decimal_places=2, null=True, blank=True,
    )
    status = models.CharField("Статус", max_length=10, choices=STATUSES, default=STATUS_NEW)

    class Meta:
        verbose_name = "Заявка trade-in"
        verbose_name_plural = "Заявки trade-in"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Trade-in {self.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = "TI-" + get_random_string(7, "0123456789")
        super().save(*args, **kwargs)
