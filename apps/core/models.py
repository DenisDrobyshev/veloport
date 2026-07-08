from django.db import models


class TimeStampedModel(models.Model):
    """Абстрактная база с датами создания/обновления."""

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        abstract = True


class Banner(models.Model):
    """Баннер на главной (слайдер/промо)."""

    title = models.CharField("Заголовок", max_length=120)
    subtitle = models.CharField("Подзаголовок", max_length=200, blank=True)
    image = models.ImageField("Изображение", upload_to="banners/", blank=True)
    bg_color = models.CharField("Цвет фона (hex)", max_length=9, default="#0f766e")
    link = models.CharField("Ссылка", max_length=300, blank=True)
    button_text = models.CharField("Текст кнопки", max_length=40, default="В каталог")
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ["order"]

    def __str__(self):
        return self.title


class Subscriber(models.Model):
    """Подписчик на рассылку."""

    email = models.EmailField("Email", unique=True)
    created_at = models.DateTimeField("Подписан", auto_now_add=True)

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
