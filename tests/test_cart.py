from decimal import Decimal

import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory
from django.urls import reverse

from apps.cart.cart import Cart

pytestmark = pytest.mark.django_db


def _req():
    request = RequestFactory().get("/")
    request.session = SessionStore()
    return request


def test_cart_add_and_total(product):
    cart = Cart(_req())
    cart.add(product, qty=2)
    assert len(cart) == 2
    assert cart.total == product.price * 2
    assert cart.shipping == Decimal("0")  # выше порога бесплатной доставки
    assert cart.grand_total == cart.total


def test_cart_shipping_below_threshold(category, brand):
    from apps.catalog.models import Product
    cheap = Product.objects.create(category=category, brand=brand, title="Bottle", sku="Z", price=Decimal("990"), stock_qty=10)
    cart = Cart(_req())
    cart.add(cheap, qty=1)
    assert cart.shipping == Decimal("500")
    assert cart.grand_total == Decimal("1490")


def test_cart_update_and_remove(product):
    cart = Cart(_req())
    cart.add(product, qty=1)
    cart.add(product, qty=5, update=True)
    assert len(cart) == 5
    key = cart._key(product.id)
    cart.remove(key)
    assert cart.is_empty


def test_cart_add_view_htmx(client, product):
    r = client.post(reverse("cart:add", args=[product.id]), {"qty": 2}, HTTP_HX_REQUEST="true")
    assert r.status_code == 200
    assert client.session["cart"]


def test_cart_update_remove_views(client, product):
    client.post(reverse("cart:add", args=[product.id]), {"qty": 1}, HTTP_HX_REQUEST="true")
    key = f"{product.id}:"
    r = client.post(reverse("cart:update", args=[key]), {"qty": 3}, HTTP_HX_REQUEST="true")
    assert r.status_code == 200
    r = client.post(reverse("cart:remove", args=[key]), HTTP_HX_REQUEST="true")
    assert r.status_code == 200
