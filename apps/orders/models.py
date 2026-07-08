from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string

from apps.core.models import TimeStampedModel


class Order(TimeStampedModel):
    """Заказ."""

    STATUS_NEW = "new"
    STATUS_CONFIRMED = "confirmed"
    STATUS_ASSEMBLING = "assembling"
    STATUS_SHIPPED = "shipped"
    STATUS_READY = "ready"
    STATUS_DONE = "done"
    STATUS_CANCELED = "canceled"
    STATUSES = [
        (STATUS_NEW, "Новый"),
        (STATUS_CONFIRMED, "Подтверждён"),
        (STATUS_ASSEMBLING, "Сборка"),
        (STATUS_SHIPPED, "Передан в доставку"),
        (STATUS_READY, "Готов к выдаче"),
        (STATUS_DONE, "Выполнен"),
        (STATUS_CANCELED, "Отменён"),
    ]

    DELIVERY_PICKUP = "pickup"
    DELIVERY_COURIER = "courier"
    DELIVERY_CDEK = "cdek"
    DELIVERY_POST = "post"
    DELIVERY_METHODS = [
        (DELIVERY_PICKUP, "Самовывоз из магазина"),
        (DELIVERY_COURIER, "Курьер по городу"),
        (DELIVERY_CDEK, "СДЭК до пункта выдачи"),
        (DELIVERY_POST, "Почта России"),
    ]

    PAYMENT_CARD = "card_online"
    PAYMENT_SBP = "sbp"
    PAYMENT_CASH = "cash"
    PAYMENT_COURIER = "card_courier"
    PAYMENT_METHODS = [
        (PAYMENT_CARD, "Картой онлайн"),
        (PAYMENT_SBP, "СБП (по QR)"),
        (PAYMENT_CASH, "Наличными при получении"),
        (PAYMENT_COURIER, "Картой при получении"),
    ]

    number = models.CharField("Номер", max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="Пользователь",
    )
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100, blank=True)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)

    delivery_method = models.CharField(
        "Доставка", max_length=12, choices=DELIVERY_METHODS, default=DELIVERY_PICKUP,
    )
    store = models.ForeignKey(
        "stores.Store", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="Магазин (самовывоз)",
    )
    city = models.CharField("Город", max_length=100, blank=True)
    street = models.CharField("Улица", max_length=150, blank=True)
    house = models.CharField("Дом", max_length=20, blank=True)
    apartment = models.CharField("Квартира", max_length=20, blank=True)
    postal_code = models.CharField("Индекс", max_length=10, blank=True)

    payment_method = models.CharField(
        "Оплата", max_length=14, choices=PAYMENT_METHODS, default=PAYMENT_CARD,
    )
    is_paid = models.BooleanField("Оплачен", default=False)
    payment_id = models.CharField("ID платежа (ЮKassa)", max_length=64, blank=True)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=12, choices=STATUSES, default=STATUS_NEW)
    total = models.DecimalField("Сумма", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ {self.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_number() -> str:
        return "VP-" + get_random_string(8, "0123456789")

    def recalc_total(self):
        self.total = sum((i.cost for i in self.items.all()), Decimal("0"))
        Order.objects.filter(pk=self.pk).update(total=self.total)

    @property
    def items_count(self) -> int:
        return sum(i.qty for i in self.items.all())

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_online_payment(self) -> bool:
        return self.payment_method in {self.PAYMENT_CARD, self.PAYMENT_SBP}

    @property
    def needs_payment(self) -> bool:
        return self.is_online_payment and not self.is_paid


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ",
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.SET_NULL, null=True,
        related_name="order_items", verbose_name="Товар",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Вариант",
    )
    title = models.CharField("Название (снимок)", max_length=250)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.title} × {self.qty}"

    @property
    def cost(self) -> Decimal:
        return self.price * self.qty
