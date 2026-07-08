from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.core.utils import unique_slug


class Article(TimeStampedModel):
    """Статья блога / гайд / обзор."""

    CATEGORY_GUIDE = "guide"
    CATEGORY_REVIEW = "review"
    CATEGORY_NEWS = "news"
    CATEGORY_HOWTO = "howto"
    CATEGORIES = [
        (CATEGORY_GUIDE, "Гайд по выбору"),
        (CATEGORY_REVIEW, "Обзор"),
        (CATEGORY_NEWS, "Новости"),
        (CATEGORY_HOWTO, "Инструкция"),
    ]

    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", max_length=220, unique=True, blank=True)
    category = models.CharField("Раздел", max_length=10, choices=CATEGORIES, default=CATEGORY_GUIDE)
    excerpt = models.CharField("Анонс", max_length=300, blank=True)
    body = models.TextField("Текст")
    cover = models.ImageField("Обложка", upload_to="articles/", blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="articles", verbose_name="Автор",
    )
    is_published = models.BooleanField("Опубликована", default=True)
    published_at = models.DateTimeField("Дата публикации", default=timezone.now)
    views = models.PositiveIntegerField("Просмотры", default=0)
    reading_time = models.PositiveSmallIntegerField("Время чтения, мин", default=5)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Блог и гайды"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("content:article", args=[self.slug])


class Page(TimeStampedModel):
    """Статическая страница (доставка, гарантия, о компании)."""

    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", max_length=220, unique=True, blank=True)
    body = models.TextField("Содержимое")
    is_published = models.BooleanField("Опубликована", default=True)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("content:page", args=[self.slug])


class SizeChart(models.Model):
    """Размерная сетка (ростовка велосипеда по росту и т.п.)."""

    title = models.CharField("Название", max_length=150)
    slug = models.SlugField("URL", max_length=170, unique=True, blank=True)
    intro = models.CharField("Пояснение", max_length=300, blank=True)
    body = models.TextField("HTML-таблица")
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Размерная сетка"
        verbose_name_plural = "Размерные сетки"
        ordering = ["order"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)


class FAQ(models.Model):
    """Частый вопрос."""

    question = models.CharField("Вопрос", max_length=250)
    answer = models.TextField("Ответ")
    category = models.CharField("Раздел", max_length=80, default="Общие", blank=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Вопрос-ответ (FAQ)"
        verbose_name_plural = "FAQ"
        ordering = ["order"]

    def __str__(self):
        return self.question
