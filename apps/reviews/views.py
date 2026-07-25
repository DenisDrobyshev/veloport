from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .models import Question, Review


def _display_name(request, fallback="Гость"):
    if request.user.is_authenticated:
        return request.user.get_full_name() or request.user.username
    return request.POST.get("name", "").strip() or fallback


@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        rating = int(request.POST.get("rating", 5))
    except (TypeError, ValueError):
        rating = 5
    Review.objects.create(
        product=product,
        author=request.user if request.user.is_authenticated else None,
        name=_display_name(request),
        rating=max(1, min(5, rating)),
        pros=request.POST.get("pros", "").strip(),
        cons=request.POST.get("cons", "").strip(),
        text=request.POST.get("text", "").strip(),
    )
    messages.success(request, "Спасибо за отзыв!")
    return redirect(product.get_absolute_url() + "#reviews")


@require_POST
def add_question(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    text = request.POST.get("text", "").strip()
    if text:
        Question.objects.create(
            product=product,
            author=request.user if request.user.is_authenticated else None,
            name=_display_name(request),
            text=text,
        )
        messages.success(request, "Вопрос отправлен, ответим в ближайшее время")
    return redirect(product.get_absolute_url() + "#questions")


@require_POST
def like_review(request, review_id):
    """Голос «полезно» за отзыв (один раз на сессию)."""
    review = get_object_or_404(Review, id=review_id)
    liked = request.session.get("liked_reviews", [])
    if review_id not in liked:
        Review.objects.filter(pk=review.pk).update(likes=F("likes") + 1)
        liked.append(review_id)
        request.session["liked_reviews"] = liked
        request.session.modified = True
        review.refresh_from_db()
    return render(request, "reviews/_review_likes.html", {"review": review, "liked_reviews": liked})
