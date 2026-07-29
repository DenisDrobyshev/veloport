import pytest
from django.urls import reverse

from apps.accounts.models import Address
from apps.catalog.models import Bike, Product
from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


def _add(client, product, qty=1):
    client.post(reverse("cart:add", args=[product.id]), {"qty": qty}, HTTP_HX_REQUEST="true")


# --- Сравнение с подсветкой отличий ---

def test_compare_highlight(client, product, category, brand):
    other = Product.objects.create(category=category, brand=brand, title="Giant Talon", sku="G1", price=64990, stock_qty=1)
    Bike.objects.create(product=other, wheel_size="27.5", frame_material="alu", frame_size="M")
    client.post(reverse("core:compare_add", args=[product.id]), HTTP_HX_REQUEST="true")
    client.post(reverse("core:compare_add", args=[other.id]), HTTP_HX_REQUEST="true")
    r = client.get(reverse("core:compare"))
    assert r.status_code == 200
    assert "только отличия" in r.content.decode()


# --- Пагинация и сортировка отзывов ---

def test_product_reviews_pagination_and_sort(client, product):
    for i in range(7):
        Review.objects.create(product=product, name=f"U{i}", rating=(i % 5) + 1, text="t")
    r = client.get(reverse("catalog:product_reviews", args=[product.slug]))
    assert r.status_code == 200
    assert "Показать ещё" in r.content.decode()
    r2 = client.get(reverse("catalog:product_reviews", args=[product.slug]), {"rpage": 2})
    assert r2.status_code == 200
    assert client.get(reverse("catalog:product_reviews", args=[product.slug]), {"rsort": "helpful"}).status_code == 200


# --- Кабинет: адреса ---

def test_profile_shows_sections(auth_client):
    r = auth_client.get(reverse("accounts:profile"))
    assert r.status_code == 200
    assert "Адреса доставки" in r.content.decode()
    assert "Баланс бонусов" in r.content.decode()


def test_address_add_and_delete(auth_client, user):
    auth_client.post(reverse("accounts:address_add"), {
        "city": "Москва", "street": "Тверская", "house": "1", "is_default": "on",
    })
    assert user.addresses.count() == 1
    addr = user.addresses.first()
    auth_client.post(reverse("accounts:address_delete", args=[addr.id]))
    assert user.addresses.count() == 0


def test_checkout_saves_address(auth_client, user, product):
    _add(auth_client, product)
    auth_client.post(reverse("orders:checkout"), {
        "first_name": "A", "phone": "1", "delivery_method": "courier",
        "city": "Москва", "street": "Ленина", "house": "5",
        "payment_method": "cash", "save_address": "1",
    })
    assert Address.objects.filter(user=user, city="Москва", street="Ленина").exists()


# --- Дашборд ---

def test_dashboard_staff_only(client, auth_client, django_user_model):
    # аноним — редирект
    assert client.get(reverse("core:dashboard")).status_code == 302
    # обычный пользователь — редирект
    assert auth_client.get(reverse("core:dashboard")).status_code == 302
    # сотрудник — 200
    staff = django_user_model.objects.create_user(username="mgr", password="x", is_staff=True)
    client.force_login(staff)
    assert client.get(reverse("core:dashboard")).status_code == 200
