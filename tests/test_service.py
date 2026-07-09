import pytest
from django.urls import reverse

from apps.service.models import ServiceBooking, TradeInRequest

pytestmark = pytest.mark.django_db


def test_service_booking(client, service_type, store):
    client.post(reverse("service:index"),
                {"service_type": service_type.id, "name": "Гость", "phone": "1", "bike_info": "Trek"})
    assert ServiceBooking.objects.count() == 1
    assert ServiceBooking.objects.first().number.startswith("SB-")


def test_tradein_request(client):
    client.post(reverse("service:tradein"),
                {"name": "Гость", "phone": "1", "brand": "Stels", "model": "Navigator", "condition": "good"})
    assert TradeInRequest.objects.count() == 1
    assert TradeInRequest.objects.first().number.startswith("TI-")
