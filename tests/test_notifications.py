import pytest
from django.core import mail
from django.urls import reverse

from apps.catalog.models import StockNotification
from apps.orders.models import Order
from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


def _add(client, product, qty=1):
    client.post(reverse("cart:add", args=[product.id]), {"qty": qty}, HTTP_HX_REQUEST="true")


def test_order_confirmation_email(client, product, store):
    _add(client, product)
    client.post(reverse("orders:checkout"), {
        "first_name": "Денис", "phone": "1", "email": "buyer@test.ru",
        "delivery_method": "pickup", "store": store.id, "payment_method": "cash",
    })
    order = Order.objects.latest("id")
    assert any(order.number in m.subject for m in mail.outbox)
    assert any("buyer@test.ru" in m.to for m in mail.outbox)


def test_restock_signal_notifies(product):
    product.stock_qty = 0
    product.save()
    StockNotification.objects.create(product=product, email="wait@test.ru")
    mail.outbox.clear()

    product.stock_qty = 5
    product.save()

    assert len(mail.outbox) == 1
    assert "снова в наличии" in mail.outbox[0].subject
    note = StockNotification.objects.get(product=product, email="wait@test.ru")
    assert note.is_notified is True


def test_restock_not_sent_twice(product):
    product.stock_qty = 0
    product.save()
    StockNotification.objects.create(product=product, email="w@test.ru")
    product.stock_qty = 3
    product.save()
    mail.outbox.clear()
    product.stock_qty = 7
    product.save()
    assert len(mail.outbox) == 0  # уже уведомлён


def test_service_booking_email(client, service_type, store):
    client.post(reverse("service:index"), {
        "service_type": service_type.id, "name": "Гость", "phone": "1",
        "email": "c@test.ru", "bike_info": "Trek",
    })
    assert any("веломастерскую" in m.subject for m in mail.outbox)


def test_review_like_once_per_session(client, product):
    rev = Review.objects.create(product=product, name="N", rating=5, text="ok")
    client.post(reverse("reviews:like", args=[rev.id]), HTTP_HX_REQUEST="true")
    rev.refresh_from_db()
    assert rev.likes == 1
    client.post(reverse("reviews:like", args=[rev.id]), HTTP_HX_REQUEST="true")
    rev.refresh_from_db()
    assert rev.likes == 1
