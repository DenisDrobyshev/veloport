import json

import pytest
from django.urls import reverse

from apps.orders.models import Order

pytestmark = pytest.mark.django_db


def _add(client, product, qty=1):
    client.post(reverse("cart:add", args=[product.id]), {"qty": qty}, HTTP_HX_REQUEST="true")


def test_checkout_empty_redirects(client):
    r = client.get(reverse("orders:checkout"))
    assert r.status_code == 302
    assert reverse("cart:detail") in r.url


def test_checkout_creates_order(client, product, store):
    _add(client, product, qty=2)
    r = client.post(reverse("orders:checkout"), {
        "first_name": "Денис", "phone": "+79990001122", "email": "d@t.ru",
        "delivery_method": "pickup", "store": store.id, "payment_method": "cash",
    })
    order = Order.objects.latest("id")
    assert r.status_code == 302
    assert reverse("orders:success", args=[order.number]) in r.url
    assert order.items.count() == 1
    assert order.total == product.price * 2
    assert order.number.startswith("VP-")


def test_online_payment_flow(client, product, store):
    _add(client, product)
    r = client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "1", "delivery_method": "pickup",
        "store": store.id, "payment_method": "card_online",
    })
    order = Order.objects.latest("id")
    assert reverse("orders:pay", args=[order.number]) in r.url
    assert order.needs_payment is True

    assert client.get(reverse("orders:pay", args=[order.number])).status_code == 200
    client.post(reverse("orders:mock_confirm", args=[order.number]))
    order.refresh_from_db()
    assert order.is_paid and order.status == Order.STATUS_CONFIRMED


def test_webhook_marks_paid(client, product, store):
    _add(client, product)
    client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "1", "delivery_method": "pickup",
        "store": store.id, "payment_method": "sbp",
    })
    order = Order.objects.latest("id")
    payload = json.dumps({"event": "payment.succeeded", "object": {"metadata": {"order_number": order.number}}})
    r = client.post(reverse("orders:yookassa_webhook"), data=payload, content_type="application/json")
    order.refresh_from_db()
    assert r.status_code == 200 and order.is_paid


def test_pickup_requires_store(client, product):
    _add(client, product)
    r = client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "1", "delivery_method": "pickup", "payment_method": "cash",
    })
    assert r.status_code == 200  # форма невалидна, остаёмся на странице
    assert Order.objects.count() == 0
