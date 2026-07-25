from decimal import Decimal

from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from apps.core.models import TimeStampedModel
from apps.core.utils import unique_slug


class Category(MPTTModel):
    """Категория каталога (дерево через MPTT)."""

    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("URL", max_length=140, unique=True, blank=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", verbose_name="Родитель",
    )
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Картинка", upload_to="categories/", blank=True)
    icon = models.CharField("Иконка (emoji)", max_length=8, blank=True)
    is_active = models.BooleanField("Активна", default=True)
    show_in_menu = models.BooleanField("Показывать в меню", default=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class MPTTMeta:
        order_insertion_by = ["order", "name"]

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category", args=[self.slug])


class Brand(models.Model):
    """Бренд/производитель."""

    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL", max_length=120, unique=True, blank=True)
    logo = models.ImageField("Логотип", upload_to="brands/", blank=True)
    country = models.CharField("Страна", max_length=60, blank=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активен", default=True)
    is_featured = models.BooleanField("Рекомендуемый", default=False)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:brand", args=[self.slug])


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def in_stock(self):
        return self.filter(stock_qty__gt=0)

    def with_discount(self):
        return self.filter(old_price__isnull=False, old_price__gt=models.F("price"))


class Product(TimeStampedModel):
    """Товар: велосипед, компонент, аксессуар, экипировка."""

    TYPE_BIKE = "bike"
    TYPE_EBIKE = "ebike"
    TYPE_COMPONENT = "component"
    TYPE_ACCESSORY = "accessory"
    TYPE_APPAREL = "apparel"
    TYPE_PROTECTION = "protection"
    PRODUCT_TYPES = [
        (TYPE_BIKE, "Велосипед"),
        (TYPE_EBIKE, "Электровелосипед"),
        (TYPE_COMPONENT, "Компонент"),
        (TYPE_ACCESSORY, "Аксессуар"),
        (TYPE_APPAREL, "Экипировка"),
        (TYPE_PROTECTION, "Защита"),
    ]

    category = TreeForeignKey(
        Category, on_delete=models.PROTECT, related_name="products",
        verbose_name="Категория",
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="products", verbose_name="Бренд",
    )
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("URL", max_length=220, unique=True, blank=True)
    sku = models.CharField("Артикул", max_length=40, unique=True)
    product_type = models.CharField(
        "Тип товара", max_length=20, choices=PRODUCT_TYPES, default=TYPE_BIKE,
    )
    short_description = models.CharField("Краткое описание", max_length=300, blank=True)
    description = models.TextField("Описание", blank=True)

    price = models.DecimalField("Цена, ₽", max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        "Старая цена, ₽", max_digits=10, decimal_places=2, null=True, blank=True,
    )
    stock_qty = models.PositiveIntegerField("Остаток на складе", default=0)

    is_active = models.BooleanField("Активен", default=True)
    is_featured = models.BooleanField("Рекомендуемый", default=False)
    is_new = models.BooleanField("Новинка", default=False)
    is_bestseller = models.BooleanField("Хит продаж", default=False)

    warranty_months = models.PositiveSmallIntegerField("Гарантия, мес.", default=12)

    rating = models.DecimalField("Рейтинг", max_digits=2, decimal_places=1, default=0)
    reviews_count = models.PositiveIntegerField("Кол-во отзывов", default=0)
    views = models.PositiveIntegerField("Просмотры", default=0)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "product_type"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product", args=[self.slug])

    @property
    def in_stock(self) -> bool:
        return self.stock_qty > 0

    @property
    def has_discount(self) -> bool:
        return bool(self.old_price and self.old_price > self.price)

    @property
    def discount_percent(self) -> int:
        if not self.has_discount:
            return 0
        return round((self.old_price - self.price) / self.old_price * 100)

    @property
    def savings(self) -> Decimal:
        return (self.old_price - self.price) if self.has_discount else Decimal("0")

    @property
    def main_image(self):
        img = self.images.filter(is_main=True).first() or self.images.first()
        return img.image if img else None

    def update_rating(self):
        """Пересчитывает кэш рейтинга и кол-ва отзывов."""
        agg = self.reviews.filter(is_published=True).aggregate(
            avg=Avg("rating"), cnt=Count("id"),
        )
        self.rating = round(agg["avg"] or 0, 1)
        self.reviews_count = agg["cnt"] or 0
        Product.objects.filter(pk=self.pk).update(
            rating=self.rating, reviews_count=self.reviews_count,
        )


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар",
    )
    image = models.ImageField("Изображение", upload_to="products/")
    alt = models.CharField("Alt-текст", max_length=200, blank=True)
    is_main = models.BooleanField("Главное фото", default=False)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"
        ordering = ["-is_main", "order"]

    def __str__(self):
        return f"Фото {self.product.title}"


class ProductVariant(models.Model):
    """Вариант товара (ростовка рамы / цвет / размер одежды)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants", verbose_name="Товар",
    )
    group = models.CharField("Параметр", max_length=60, default="Ростовка")
    value = models.CharField("Значение", max_length=60)
    sku = models.CharField("Артикул", max_length=50, blank=True)
    price_delta = models.DecimalField(
        "Доплата, ₽", max_digits=10, decimal_places=2, default=0,
    )
    stock_qty = models.PositiveIntegerField("Остаток", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товара"
        ordering = ["group", "value"]

    def __str__(self):
        return f"{self.group}: {self.value}"

    @property
    def price(self):
        return self.product.price + self.price_delta


class Bike(models.Model):
    """Велоспецификация — используется для умного фасетного фильтра и подбора."""

    WHEEL_SIZES = [
        ("12", '12"'), ("16", '16"'), ("20", '20"'), ("24", '24"'),
        ("26", '26"'), ("27.5", '27.5"'), ("29", '29"'), ("700c", "700C"),
    ]
    FRAME_MATERIALS = [
        ("alu", "Алюминий"), ("steel", "Сталь"), ("carbon", "Карбон"),
        ("titanium", "Титан"), ("chromoly", "Хроммолибден"),
    ]
    FRAME_SIZES = [
        ("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL"), ("XXL", "XXL"),
    ]
    BRAKE_TYPES = [
        ("disc_hydraulic", "Дисковые гидравлические"),
        ("disc_mech", "Дисковые механические"),
        ("v_brake", "Ободные V-brake"),
        ("rim", "Ободные"),
    ]
    SUSPENSIONS = [
        ("rigid", "Ригид (без амортизации)"),
        ("hardtail", "Хардтейл"),
        ("full", "Двухподвес"),
    ]
    GENDERS = [
        ("male", "Мужской"), ("female", "Женский"),
        ("unisex", "Унисекс"), ("kids", "Детский"),
    ]

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="bike", verbose_name="Товар",
    )
    model_year = models.PositiveSmallIntegerField("Год модели", default=2025)
    gender = models.CharField("Пол", max_length=10, choices=GENDERS, default="unisex")
    wheel_size = models.CharField("Размер колёс", max_length=6, choices=WHEEL_SIZES, blank=True)
    frame_material = models.CharField("Материал рамы", max_length=12, choices=FRAME_MATERIALS, blank=True)
    frame_size = models.CharField("Ростовка рамы", max_length=4, choices=FRAME_SIZES, blank=True)
    brake_type = models.CharField("Тормоза", max_length=16, choices=BRAKE_TYPES, blank=True)
    suspension = models.CharField("Амортизация", max_length=10, choices=SUSPENSIONS, blank=True)
    speeds = models.PositiveSmallIntegerField("Кол-во скоростей", default=1)
    fork_travel = models.PositiveSmallIntegerField("Ход вилки, мм", null=True, blank=True)
    is_electric = models.BooleanField("Электро", default=False)
    weight_kg = models.DecimalField("Вес, кг", max_digits=4, decimal_places=1, null=True, blank=True)
    max_rider_weight = models.PositiveSmallIntegerField("Макс. вес райдера, кг", null=True, blank=True)
    rider_height_min = models.PositiveSmallIntegerField("Рост райдера от, см", null=True, blank=True)
    rider_height_max = models.PositiveSmallIntegerField("Рост райдера до, см", null=True, blank=True)

    class Meta:
        verbose_name = "Велоспецификация"
        verbose_name_plural = "Велоспецификации"

    def __str__(self):
        return f"Спец: {self.product.title}"


class Specification(models.Model):
    """Произвольная характеристика для таблицы на карточке товара."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specs", verbose_name="Товар",
    )
    group = models.CharField("Группа", max_length=60, default="Основные")
    name = models.CharField("Характеристика", max_length=80)
    value = models.CharField("Значение", max_length=200)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name}: {self.value}"


class StockNotification(models.Model):
    """Подписка «сообщить о поступлении» товара."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_notifications",
        verbose_name="Товар",
    )
    email = models.EmailField("Email")
    is_notified = models.BooleanField("Уведомлён", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Подписка на поступление"
        verbose_name_plural = "Подписки на поступление"
        unique_together = ("product", "email")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} → {self.product}"
