import pytest
from django.urls import reverse

from apps.content.models import Article, Page

pytestmark = pytest.mark.django_db


def test_blog_and_article(client):
    a = Article.objects.create(title="Как выбрать велосипед", body="Текст статьи")
    assert client.get(reverse("content:blog")).status_code == 200
    r = client.get(a.get_absolute_url())
    assert r.status_code == 200
    a.refresh_from_db()
    assert a.views == 1


def test_page_view(client):
    p = Page.objects.create(title="Доставка и оплата", body="Условия")
    assert client.get(p.get_absolute_url()).status_code == 200


def test_guides(client):
    assert client.get(reverse("content:guides")).status_code == 200
