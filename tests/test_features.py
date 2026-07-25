from decimal import Decimal

import pytest
from django.urls import reverse

from apps.catalog.models import Bike, Product, StockNotification
from apps.orders.models import Coupon, Order

pytestmark = pytest.mark.django_db


def _add(client, product, qty=1):
    client.post(reverse("cart:add", args=[product.id]), {"qty": qty}, HTTP_HX_REQUEST="true")


# --- Избранное ---

def test_wishlist_toggle_and_page(client, product):
    client.post(reverse("core:wishlist_toggle", args=[product.id]), HTTP_HX_REQUEST="true")
    assert client.session["wishlist"] == [product.id]
    assert product.title in client.get(reverse("core:wishlist")).content.decode()
    client.post(reverse("core:wishlist_toggle", args=[product.id]), HTTP_HX_REQUEST="true")
    assert client.session["wishlist"] == []


# --- Живой поиск ---

def test_suggest(client, product):
    r = client.get(reverse("catalog:suggest"), {"q": "Trek"})
    assert product.title in r.content.decode()
    assert product.title not in client.get(reverse("catalog:suggest"), {"q": "z"}).content.decode()


# --- Уведомление о поступлении ---

def test_stock_notify(client, product):
    r = client.post(reverse("catalog:stock_notify", args=[product.id]), {"email": "a@b.ru"}, HTTP_HX_REQUEST="true")
    assert r.status_code == 200
    assert StockNotification.objects.filter(product=product, email="a@b.ru").exists()


# --- Промокоды ---

def test_coupon_check(client, product):
    Coupon.objects.create(code="VELO10", discount_type=Coupon.TYPE_PERCENT, amount=10)
    _add(client, product)
    assert "применён" in client.post(reverse("orders:coupon_check"), {"promo": "VELO10"}).content.decode().lower()
    assert "не найден" in client.post(reverse("orders:coupon_check"), {"promo": "NOPE"}).content.decode().lower()


def test_checkout_applies_coupon(client, product, store):
    Coupon.objects.create(code="VELO10", discount_type=Coupon.TYPE_PERCENT, amount=10)
    _add(client, product)
    client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "+79990001122", "delivery_method": "pickup",
        "store": store.id, "payment_method": "cash", "promo": "VELO10",
    })
    order = Order.objects.latest("id")
    assert order.coupon.code == "VELO10"
    assert order.discount == (product.price / 10).quantize(Decimal("1"))
    assert order.payable == order.total - order.discount


def test_coupon_min_sum_rejected(client, product, store):
    Coupon.objects.create(code="BIG", discount_type=Coupon.TYPE_FIXED, amount=1000, min_order_sum=Decimal("1000000"))
    _add(client, product)
    client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "1", "delivery_method": "pickup",
        "store": store.id, "payment_method": "cash", "promo": "BIG",
    })
    order = Order.objects.latest("id")
    assert order.coupon is None and order.discount == 0


# --- Бонусы ---

def test_checkout_uses_and_earns_bonus(auth_client, user, product, store):
    user.bonus_points = 5000
    user.save()
    _add(auth_client, product)
    auth_client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "1", "delivery_method": "pickup",
        "store": store.id, "payment_method": "cash", "use_bonus": 2000,
    })
    order = Order.objects.latest("id")
    assert order.bonus_used == 2000
    earned = int((order.total - 2000) * Decimal("0.03"))
    assert order.bonus_earned == earned
    user.refresh_from_db()
    assert user.bonus_points == 5000 - 2000 + earned


# --- Отслеживание заказа ---

def test_track_order(client, product, store):
    _add(client, product)
    client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "+79990001122", "delivery_method": "pickup",
        "store": store.id, "payment_method": "cash",
    })
    order = Order.objects.latest("id")
    r = client.get(reverse("orders:track"), {"number": order.number, "phone": "1122"})
    assert order.number in r.content.decode()
    r2 = client.get(reverse("orders:track"), {"number": "VP-00000000", "phone": "0000"})
    assert "не найден" in r2.content.decode().lower()


# --- Недавно просмотренные ---

def test_recently_viewed(client, product, category, brand):
    other = Product.objects.create(category=category, brand=brand, title="Other Bike", sku="O1", price=50000, stock_qty=1)
    Bike.objects.create(product=other)
    client.get(product.get_absolute_url())
    r = client.get(other.get_absolute_url())
    assert product.title in r.content.decode()


# --- SEO ---

def test_sitemap_and_robots(client, product):
    assert client.get("/sitemap.xml").status_code == 200
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert "Sitemap:" in r.content.decode()
