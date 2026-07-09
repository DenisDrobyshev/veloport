import pytest
from django.urls import reverse

from apps.core.models import Subscriber
from apps.core.views import _recommend_size

pytestmark = pytest.mark.django_db


def test_recommend_size():
    assert _recommend_size(145) == "XS"
    assert _recommend_size(155) == "S"
    assert _recommend_size(165) == "S/M"
    assert _recommend_size(175) == "M"
    assert _recommend_size(184) == "L"
    assert _recommend_size(190) == "XL"
    assert _recommend_size(200) == "XXL"


def test_home_ok(client, product):
    assert client.get(reverse("core:home")).status_code == 200


def test_fit_finder_filters(client, product):
    r = client.get(reverse("core:fit_finder"),
                   {"height": 175, "style": "gornyy", "budget": "60000-120000"})
    assert r.status_code == 200
    assert product.title in r.content.decode()


def test_fit_finder_excludes_out_of_budget(client, product):
    r = client.get(reverse("core:fit_finder"),
                   {"height": 175, "style": "gornyy", "budget": "0-30000"})
    assert product.title not in r.content.decode()


def test_compare_add_remove(client, product):
    client.post(reverse("core:compare_add", args=[product.id]), HTTP_HX_REQUEST="true")
    assert client.session["compare"] == [product.id]
    assert product.title in client.get(reverse("core:compare")).content.decode()
    client.post(reverse("core:compare_remove", args=[product.id]))
    assert client.session["compare"] == []


def test_subscribe(client):
    client.post(reverse("core:subscribe"), {"email": "a@b.ru"}, HTTP_HX_REQUEST="true")
    assert Subscriber.objects.filter(email="a@b.ru").exists()
