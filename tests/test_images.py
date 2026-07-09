import pytest

from apps.catalog.images import attach_image, generate_svg

pytestmark = pytest.mark.django_db


def test_generate_svg_contains_title(product):
    svg = generate_svg(product)
    assert svg.startswith("<svg")
    assert "TREK" in svg  # бренд в верхнем регистре


def test_attach_image(product, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    img = attach_image(product)
    assert img is not None
    assert product.images.filter(is_main=True).exists()
    assert product.main_image is not None


def test_attach_image_skips_existing(product, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    attach_image(product)
    assert attach_image(product) is None  # уже есть картинка
