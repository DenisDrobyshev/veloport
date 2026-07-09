"""Общие фикстуры для тестов Veloport."""

from decimal import Decimal

import pytest

from apps.catalog.models import Bike, Brand, Category, Product, ProductVariant
from apps.service.models import ServiceType
from apps.stores.models import Stock, Store


@pytest.fixture(autouse=True)
def _allow_testserver(settings):
    if "testserver" not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ["testserver"]


@pytest.fixture
def root_category(db):
    return Category.objects.create(name="Велосипеды", slug="velosipedy")


@pytest.fixture
def category(db, root_category):
    return Category.objects.create(name="Горные", slug="gornye", parent=root_category)


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="Trek", country="США", is_featured=True)


@pytest.fixture
def product(db, category, brand):
    p = Product.objects.create(
        category=category, brand=brand, title="Trek Marlin 7", sku="BK-0001",
        product_type=Product.TYPE_BIKE, price=Decimal("89990"), old_price=Decimal("99990"),
        stock_qty=5, is_bestseller=True,
    )
    Bike.objects.create(
        product=p, wheel_size="29", frame_material="alu", frame_size="M",
        brake_type="disc_hydraulic", suspension="hardtail", speeds=18,
        rider_height_min=168, rider_height_max=180,
    )
    return p


@pytest.fixture
def variant(db, product):
    return ProductVariant.objects.create(product=product, group="Ростовка", value="M (18\")", stock_qty=3)


@pytest.fixture
def store(db, product):
    s = Store.objects.create(name="Veloport Центр", city="Москва", address="Тверская, 15", phone="88001112233")
    Stock.objects.create(store=s, product=product, qty=4)
    return s


@pytest.fixture
def service_type(db):
    return ServiceType.objects.create(name="ТО базовое", price_from=Decimal("1500"), duration_min=60)


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(username="denis", password="Pass12345!", email="d@t.ru")


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client
