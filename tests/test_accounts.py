import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_register_creates_and_logs_in(client):
    r = client.post(reverse("accounts:register"), {
        "username": "newu", "email": "n@t.ru", "phone": "1",
        "password1": "SuperPass123!", "password2": "SuperPass123!",
    })
    assert r.status_code == 302
    assert get_user_model().objects.filter(username="newu").exists()


def test_profile_requires_login(client):
    r = client.get(reverse("accounts:profile"))
    assert r.status_code == 302
    assert "/account/login" in r.url


def test_profile_authed(auth_client):
    assert auth_client.get(reverse("accounts:profile")).status_code == 200


def test_login_page(client):
    assert client.get(reverse("accounts:login")).status_code == 200
