from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Review(TimeStampedModel):
    """Отзыв на товар с рейтингом, плюсами и минусами."""

    RATING_CHOICES = [(i, f"{i} ★") for i in range(1, 6)]

    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="reviews",
        verbose_name="Товар",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviews", verbose_name="Автор",
    )
    name = models.CharField("Имя", max_length=100)
    rating = models.PositiveSmallIntegerField("Оценка", choices=RATING_CHOICES, default=5)
    pros = models.CharField("Достоинства", max_length=500, blank=True)
    cons = models.CharField("Недостатки", max_length=500, blank=True)
    text = models.TextField("Комментарий", blank=True)
    is_published = models.BooleanField("Опубликован", default=True)
    likes = models.PositiveIntegerField("Полезно", default=0)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.product} ({self.rating}★)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_rating()


class Question(TimeStampedModel):
    """Вопрос о товаре (Q&A)."""

    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="questions",
        verbose_name="Товар",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="questions", verbose_name="Автор",
    )
    name = models.CharField("Имя", max_length=100)
    text = models.TextField("Вопрос")
    is_published = models.BooleanField("Опубликован", default=True)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Вопрос от {self.name}"


class Answer(TimeStampedModel):
    """Ответ на вопрос."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers", verbose_name="Вопрос",
    )
    name = models.CharField("Имя", max_length=100, default="Veloport")
    text = models.TextField("Ответ")
    is_staff_answer = models.BooleanField("Ответ магазина", default=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ["created_at"]

    def __str__(self):
        return f"Ответ на #{self.question_id}"
