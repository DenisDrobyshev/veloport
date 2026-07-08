from django.contrib import admin

from .models import Answer, Question, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "rating", "is_published", "created_at")
    list_filter = ("rating", "is_published", "created_at")
    list_editable = ("is_published",)
    search_fields = ("name", "text", "product__title")
    autocomplete_fields = ("product", "author")


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("name", "text", "product__title")
    autocomplete_fields = ("product", "author")
    inlines = [AnswerInline]
