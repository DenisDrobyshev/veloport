import pytest
from django.urls import reverse

from apps.stores.models import Reservation

pytestmark = pytest.mark.django_db


def test_store_list_and_detail(client, store):
    assert client.get(reverse("stores:list")).status_code == 200
    assert client.get(reverse("stores:detail", args=[store.slug])).status_code == 200


def test_reserve_creates_reservation(client, product, store):
    r = client.post(reverse("stores:reserve", args=[product.id]),
                    {"store": store.id, "name": "Гость", "phone": "+79990001122", "qty": 1},
                    HTTP_HX_REQUEST="true")
    assert r.status_code == 200
    assert Reservation.objects.count() == 1
    res = Reservation.objects.first()
    assert res.number.startswith("RS-")
