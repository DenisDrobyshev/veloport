import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_add_review_updates_rating(client, product):
    client.post(reverse("reviews:add_review", args=[product.id]),
                {"name": "Гость", "rating": "4", "pros": "лёгкий", "text": "ok"})
    product.refresh_from_db()
    assert product.reviews_count == 1
    assert float(product.rating) == 4.0


def test_review_average(client, product):
    for r in ("5", "3"):
        client.post(reverse("reviews:add_review", args=[product.id]), {"name": "N", "rating": r, "text": "t"})
    product.refresh_from_db()
    assert product.reviews_count == 2
    assert float(product.rating) == 4.0


def test_add_question(client, product):
    client.post(reverse("reviews:add_question", args=[product.id]), {"name": "Г", "text": "Есть рассрочка?"})
    assert product.questions.count() == 1
