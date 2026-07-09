"""Загрузка реальных фотографий товаров из открытых источников.

Берёт фото со свободной лицензией (Openverse, фильтр commercial; фолбэк —
Wikimedia Commons) по ТИПУ товара и назначает их товарам категории.
Точные фото конкретных моделей можно заменить вручную в админке.

    python manage.py fetch_photos            # все категории
    python manage.py fetch_photos --per 10   # не более 10 фото на категорию
"""

import time

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product, ProductImage

UA = {"User-Agent": "veloport-demo/1.0 (educational project)"}

# slug категории -> поисковый запрос
QUERIES = {
    "gornye": "mountain bike bicycle",
    "shosseynye": "road racing bicycle",
    "gorodskie": "city commuter bicycle",
    "gravel": "gravel bike bicycle",
    "detskie": "kids children bicycle",
    "electro": "electric bicycle ebike",
    "fatbike": "fat bike bicycle",
    "bmx": "bmx bike",
    "folding": "folding bicycle",
    "hybrid": "hybrid trekking bicycle",
    "shlemy": "bicycle helmet",
    "zamki": "bicycle lock",
    "nasosy": "bicycle pump",
    "fary": "bicycle light lamp",
    "flyagi": "cycling water bottle",
    "ekipirovka": "cycling jersey clothing",
}


def openverse_urls(query, n):
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "license_type": "commercial", "page_size": n, "mature": "false"},
            headers=UA, timeout=30,
        )
        r.raise_for_status()
        return [i["url"] for i in r.json().get("results", []) if i.get("url")]
    except Exception:
        return []


def wikimedia_urls(query, n):
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "generator": "search", "gsrsearch": query,
                "gsrlimit": n, "gsrnamespace": 6, "prop": "imageinfo",
                "iiprop": "url", "iiurlwidth": 800, "format": "json",
            },
            headers=UA, timeout=30,
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        return [p["imageinfo"][0]["thumburl"] for p in pages.values() if p.get("imageinfo")]
    except Exception:
        return []


def download(url):
    try:
        resp = requests.get(url, headers=UA, timeout=30)
        ctype = resp.headers.get("Content-Type", "")
        if resp.status_code == 200 and ctype.startswith("image") and 3000 < len(resp.content) < 8_000_000:
            ext = "png" if "png" in ctype else "jpg"
            return resp.content, ext
    except Exception:
        pass
    return None, None


class Command(BaseCommand):
    help = "Загружает реальные фото товаров по типу (Openverse/Wikimedia)"

    def add_arguments(self, parser):
        parser.add_argument("--per", type=int, default=14, help="Максимум фото на категорию")

    def handle(self, *args, **options):
        per = options["per"]
        total = 0
        for slug, query in QUERIES.items():
            cat = Category.objects.filter(slug=slug).first()
            if not cat:
                continue
            products = list(Product.objects.filter(category=cat))
            if not products:
                continue
            need = min(len(products), per)

            urls = openverse_urls(query, need + 6) or wikimedia_urls(query, need + 6)
            pool = []
            for u in urls:
                content, ext = download(u)
                if content:
                    pool.append((content, ext))
                if len(pool) >= need:
                    break

            if not pool:
                self.stdout.write(self.style.WARNING(f"[{slug}] фото не найдено, пропуск"))
                continue

            for i, product in enumerate(products):
                content, ext = pool[i % len(pool)]
                product.images.all().delete()
                img = ProductImage(product=product, is_main=True, alt=product.title)
                img.image.save(f"{product.slug}.{ext}", ContentFile(content), save=True)
                total += 1
            self.stdout.write(self.style.SUCCESS(f"[{slug}] {query!r}: {len(pool)} фото → {len(products)} товаров"))
            time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS(f"Готово. Обновлено товаров: {total}"))
