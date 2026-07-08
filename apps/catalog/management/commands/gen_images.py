"""Генерация SVG-изображений для товаров: python manage.py gen_images [--force]"""

from django.core.management.base import BaseCommand

from apps.catalog.images import attach_image
from apps.catalog.models import Product


class Command(BaseCommand):
    help = "Генерирует изображения товаров (SVG на фирменном градиенте)"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Перегенерировать даже если фото уже есть")

    def handle(self, *args, **options):
        force = options["force"]
        count = 0
        for product in Product.objects.all():
            if attach_image(product, force=force):
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Сгенерировано изображений: {count}"))
