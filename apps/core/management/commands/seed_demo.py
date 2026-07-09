"""Наполнение БД демо-данными: python manage.py seed_demo"""

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.images import attach_image
from apps.catalog.models import Bike, Brand, Category, Product, Specification
from apps.content.models import FAQ, Article, Page, SizeChart
from apps.core.models import Banner
from apps.reviews.models import Answer, Question, Review
from apps.service.models import ServiceType
from apps.stores.models import Stock, Store

User = get_user_model()

HEIGHT_BY_SIZE = {
    "XS": (140, 158), "S": (158, 170), "M": (168, 180),
    "L": (178, 190), "XL": (188, 198), "XXL": (196, 210),
}

# (title, brand, cat, price, old, wheel, material, size, brake, susp, speeds, weight, electric)
BIKES = [
    # Горные
    ("Trek Marlin 7", "Trek", "gornye", 89990, 99990, "29", "alu", "M", "disc_hydraulic", "hardtail", 18, 13.5, False),
    ("Giant Talon 3", "Giant", "gornye", 64990, None, "27.5", "alu", "M", "disc_mech", "hardtail", 16, 14.2, False),
    ("Merida Big Nine 100", "Merida", "gornye", 79990, None, "29", "alu", "L", "disc_hydraulic", "hardtail", 20, 13.8, False),
    ("Cube Aim Pro", "Cube", "gornye", 72990, 82990, "29", "alu", "M", "disc_hydraulic", "hardtail", 16, 14.0, False),
    ("Scott Aspect 950", "Scott", "gornye", 69990, None, "29", "alu", "L", "disc_mech", "hardtail", 21, 14.5, False),
    ("Specialized Rockhopper", "Specialized", "gornye", 94990, None, "29", "alu", "M", "disc_hydraulic", "hardtail", 24, 13.2, False),
    ("Stels Navigator 620", "Stels", "gornye", 32990, 37990, "26", "alu", "S", "v_brake", "hardtail", 21, 15.5, False),
    ("Cube Stereo 140", "Cube", "gornye", 189990, None, "29", "alu", "L", "disc_hydraulic", "full", 12, 15.0, False),
    # Шоссейные
    ("Trek Domane AL 2", "Trek", "shosseynye", 99990, None, "700c", "alu", "M", "rim", "rigid", 16, 10.2, False),
    ("Giant Contend 3", "Giant", "shosseynye", 84990, 94990, "700c", "alu", "M", "rim", "rigid", 16, 10.5, False),
    ("Merida Scultura 400", "Merida", "shosseynye", 149990, None, "700c", "carbon", "L", "disc_hydraulic", "rigid", 22, 8.6, False),
    ("Specialized Allez", "Specialized", "shosseynye", 119990, None, "700c", "alu", "M", "disc_mech", "rigid", 18, 9.4, False),
    # Гравийные
    ("Cube Nuroad", "Cube", "gravel", 129990, None, "700c", "alu", "L", "disc_hydraulic", "rigid", 20, 10.8, False),
    ("Merida Silex 300", "Merida", "gravel", 139990, 154990, "700c", "alu", "M", "disc_hydraulic", "rigid", 22, 10.5, False),
    ("Trek Checkpoint ALR", "Trek", "gravel", 179990, None, "700c", "alu", "L", "disc_hydraulic", "rigid", 22, 10.0, False),
    # Городские
    ("Giant Escape 3", "Giant", "gorodskie", 54990, None, "700c", "alu", "M", "v_brake", "rigid", 21, 12.5, False),
    ("Cube Hyde", "Cube", "gorodskie", 79990, None, "700c", "alu", "M", "disc_hydraulic", "rigid", 8, 13.0, False),
    ("Stels Cross 150", "Stels", "gorodskie", 27990, 31990, "28", "steel", "M", "v_brake", "rigid", 7, 15.0, False),
    ("Format 3342", "Format", "gorodskie", 39990, None, "700c", "alu", "M", "v_brake", "rigid", 18, 13.5, False),
    # Детские
    ("Stels Pilot 170", "Stels", "detskie", 14990, None, "20", "steel", "XS", "v_brake", "rigid", 1, 11.0, False),
    ("Author Stylo 20", "Author", "detskie", 21990, 24990, "20", "alu", "XS", "v_brake", "rigid", 6, 10.5, False),
    ("Merida Matts J16", "Merida", "detskie", 24990, None, "16", "alu", "XS", "v_brake", "rigid", 1, 9.0, False),
    # Электро
    ("Cube Reaction Hybrid Pro", "Cube", "electro", 329990, None, "29", "alu", "L", "disc_hydraulic", "hardtail", 12, 22.0, True),
    ("Format E-Bike 1", "Format", "electro", 149990, 169990, "27.5", "alu", "M", "disc_hydraulic", "hardtail", 9, 24.0, True),
    ("Eltreco XT 800 New", "Eltreco", "electro", 89990, None, "26", "alu", "M", "disc_mech", "hardtail", 21, 28.0, True),
    # Горные (доп.)
    ("Cannondale Trail 6", "Cannondale", "gornye", 84990, None, "29", "alu", "M", "disc_hydraulic", "hardtail", 18, 14.0, False),
    ("GT Aggressor Expert", "GT", "gornye", 59990, 69990, "27.5", "alu", "M", "disc_mech", "hardtail", 21, 15.0, False),
    ("Focus Whistler 3.7", "Focus", "gornye", 99990, None, "29", "alu", "L", "disc_hydraulic", "hardtail", 20, 13.5, False),
    ("Marin Bobcat Trail 3", "Marin", "gornye", 89990, None, "29", "alu", "M", "disc_hydraulic", "hardtail", 16, 14.2, False),
    ("Norco Storm 3", "Norco", "gornye", 74990, None, "27.5", "alu", "S", "disc_hydraulic", "hardtail", 16, 14.5, False),
    ("Polygon Cascade 3", "Polygon", "gornye", 64990, None, "29", "alu", "M", "disc_mech", "hardtail", 18, 14.8, False),
    ("Merida One-Forty 400", "Merida", "gornye", 229990, None, "29", "alu", "L", "disc_hydraulic", "full", 12, 15.5, False),
    ("Scott Scale 970", "Scott", "gornye", 119990, 134990, "29", "alu", "L", "disc_hydraulic", "hardtail", 24, 12.8, False),
    ("Forward Sporting 29", "Forward", "gornye", 29990, None, "29", "alu", "M", "disc_mech", "hardtail", 21, 15.8, False),
    ("Stels Navigator 720 MD", "Stels", "gornye", 39990, None, "27.5", "alu", "M", "disc_mech", "hardtail", 24, 15.0, False),
    # Шоссейные (доп.)
    ("Cannondale CAAD13 105", "Cannondale", "shosseynye", 219990, None, "700c", "alu", "M", "disc_hydraulic", "rigid", 22, 8.9, False),
    ("GT GTR Comp", "GT", "shosseynye", 74990, None, "700c", "alu", "M", "rim", "rigid", 16, 10.6, False),
    ("Focus Izalco Race", "Focus", "shosseynye", 259990, None, "700c", "carbon", "L", "disc_hydraulic", "rigid", 22, 8.2, False),
    ("Bianchi Via Nirone 7", "Bianchi", "shosseynye", 139990, None, "700c", "alu", "M", "rim", "rigid", 18, 9.6, False),
    ("Cervelo Caledonia 105", "Cervelo", "shosseynye", 329990, None, "700c", "carbon", "L", "disc_hydraulic", "rigid", 22, 8.4, False),
    # Гравийные (доп.)
    ("Cannondale Topstone 3", "Cannondale", "gravel", 149990, None, "700c", "alu", "M", "disc_hydraulic", "rigid", 18, 11.0, False),
    ("Focus Atlas 6.7", "Focus", "gravel", 169990, None, "700c", "alu", "L", "disc_hydraulic", "rigid", 20, 10.6, False),
    ("Marin Nicasio", "Marin", "gravel", 99990, None, "700c", "steel", "M", "disc_mech", "rigid", 16, 11.5, False),
    # Городские (доп.)
    ("Cannondale Quick 5", "Cannondale", "gorodskie", 74990, None, "700c", "alu", "M", "v_brake", "rigid", 21, 12.0, False),
    ("Marin Presidio 1", "Marin", "gorodskie", 69990, None, "700c", "alu", "M", "disc_mech", "rigid", 8, 12.2, False),
    ("Shulz Roadkiller", "Shulz", "gorodskie", 44990, None, "700c", "alu", "M", "v_brake", "rigid", 7, 12.8, False),
    ("Welt London", "Welt", "gorodskie", 34990, 39990, "28", "alu", "M", "v_brake", "rigid", 7, 13.5, False),
    # Детские (доп.)
    ("Forward Cosmo 12", "Forward", "detskie", 9990, None, "12", "steel", "XS", "v_brake", "rigid", 1, 8.5, False),
    ("Shulz Bubble 16", "Shulz", "detskie", 18990, None, "16", "alu", "XS", "v_brake", "rigid", 1, 8.8, False),
    ("GT Siren 24", "GT", "detskie", 34990, None, "24", "alu", "XS", "disc_mech", "hardtail", 8, 12.0, False),
    ("Welt Peak 20", "Welt", "detskie", 19990, 22990, "20", "steel", "XS", "v_brake", "rigid", 6, 11.0, False),
    # Электро (доп.)
    ("Cube Reaction Hybrid One 500", "Cube", "electro", 279990, None, "29", "alu", "M", "disc_hydraulic", "hardtail", 10, 23.0, True),
    ("Haibike Trekking 4", "Haibike", "electro", 249990, None, "28", "alu", "L", "disc_hydraulic", "rigid", 10, 25.0, True),
    ("Eltreco Ultra Max", "Eltreco", "electro", 119990, 139990, "26", "alu", "M", "disc_mech", "hardtail", 21, 30.0, True),
    ("Forward Cyclone 27", "Forward", "electro", 99990, None, "27.5", "alu", "M", "disc_mech", "hardtail", 7, 26.0, True),
    # Фэтбайки
    ("Stels Aggressor Fat", "Stels", "fatbike", 54990, None, "26", "alu", "M", "disc_mech", "hardtail", 7, 18.5, False),
    ("Welt Bighorn Fat", "Welt", "fatbike", 64990, None, "26", "alu", "L", "disc_hydraulic", "hardtail", 9, 18.0, False),
    # BMX
    ("Haro Downtown 20", "Haro", "bmx", 34990, None, "20", "chromoly", "S", "v_brake", "rigid", 1, 11.5, False),
    ("Mongoose Legion L60", "Mongoose", "bmx", 29990, 34990, "20", "chromoly", "S", "v_brake", "rigid", 1, 11.8, False),
    # Складные
    ("Shulz Krabi V", "Shulz", "folding", 39990, None, "20", "alu", "M", "v_brake", "rigid", 7, 13.0, False),
    ("Forward Enigma 20", "Forward", "folding", 27990, None, "20", "alu", "M", "v_brake", "rigid", 6, 13.5, False),
    # Гибриды
    ("Cube Nature Pro", "Cube", "hybrid", 89990, None, "700c", "alu", "L", "disc_hydraulic", "rigid", 20, 12.5, False),
    ("Marin Fairfax 2", "Marin", "hybrid", 64990, None, "700c", "alu", "M", "disc_mech", "rigid", 16, 12.8, False),
]

# (title, brand, cat, price, old, ptype, emoji_type)
GEAR = [
    ("Шлем Giro Fixture", "Giro", "shlemy", 5990, None, Product.TYPE_PROTECTION),
    ("Шлем Cube Pathos", "Cube", "shlemy", 4490, 5490, Product.TYPE_PROTECTION),
    ("Наколенники Fox Launch", "Fox", "shlemy", 4990, None, Product.TYPE_PROTECTION),
    ("Замок Kryptonite Evolution", "Kryptonite", "zamki", 6990, None, Product.TYPE_ACCESSORY),
    ("Насос Topeak JoeBlow Sport", "Topeak", "nasosy", 3990, 4590, Product.TYPE_ACCESSORY),
    ("Фара Cateye Volt 400", "Cateye", "fary", 4590, None, Product.TYPE_ACCESSORY),
    ("Фляга Zefal + держатель", "Zefal", "flyagi", 990, None, Product.TYPE_ACCESSORY),
    ("Велоперчатки Fox Ranger", "Fox", "ekipirovka", 2490, None, Product.TYPE_APPAREL),
    ("Веломайка Craft Essence", "Craft", "ekipirovka", 3990, 4990, Product.TYPE_APPAREL),
    ("Велорюкзак Deuter Race", "Deuter", "ekipirovka", 7990, None, Product.TYPE_ACCESSORY),
    ("Шлем Bell Tracker", "Bell", "shlemy", 6990, None, Product.TYPE_PROTECTION),
    ("Перчатки Giro DND", "Giro", "ekipirovka", 2990, None, Product.TYPE_APPAREL),
    ("Насос напольный BBB AirBoost", "BBB", "nasosy", 4990, None, Product.TYPE_ACCESSORY),
    ("Велозамок ABUS Bordo", "ABUS", "zamki", 8990, None, Product.TYPE_ACCESSORY),
    ("Фонарь задний Cateye Rapid", "Cateye", "fary", 1990, None, Product.TYPE_ACCESSORY),
    ("Фляга Camelbak Podium", "Camelbak", "flyagi", 1490, None, Product.TYPE_ACCESSORY),
    ("Веломайка Craft Pro", "Craft", "ekipirovka", 4990, 5990, Product.TYPE_APPAREL),
]

CATEGORIES = [
    # (name, slug, icon, parent_slug)
    ("Велосипеды", "velosipedy", "🚲", None),
    ("Горные (MTB)", "gornye", "⛰", "velosipedy"),
    ("Шоссейные", "shosseynye", "🏁", "velosipedy"),
    ("Городские", "gorodskie", "🏙", "velosipedy"),
    ("Гравийные", "gravel", "🌾", "velosipedy"),
    ("Детские", "detskie", "🧒", "velosipedy"),
    ("Электровелосипеды", "electro", "⚡", "velosipedy"),
    ("Фэтбайки", "fatbike", "🏔", "velosipedy"),
    ("BMX", "bmx", "🛞", "velosipedy"),
    ("Складные", "folding", "🧳", "velosipedy"),
    ("Гибриды", "hybrid", "🔀", "velosipedy"),
    ("Аксессуары", "accessories", "🧰", None),
    ("Шлемы и защита", "shlemy", "🪖", "accessories"),
    ("Замки", "zamki", "🔒", "accessories"),
    ("Насосы", "nasosy", "💨", "accessories"),
    ("Фары и свет", "fary", "🔦", "accessories"),
    ("Фляги", "flyagi", "🍶", "accessories"),
    ("Экипировка", "ekipirovka", "👕", None),
]

BRANDS = [
    ("Trek", "США"), ("Giant", "Тайвань"), ("Merida", "Тайвань"), ("Cube", "Германия"),
    ("Scott", "Швейцария"), ("Specialized", "США"), ("Stels", "Россия"), ("Format", "Россия"),
    ("Author", "Чехия"), ("Eltreco", "Россия"), ("Giro", "США"), ("Kryptonite", "США"),
    ("Topeak", "Тайвань"), ("Cateye", "Япония"), ("Zefal", "Франция"), ("Fox", "США"),
    ("Craft", "Швеция"), ("Deuter", "Германия"),
    ("Cannondale", "США"), ("GT", "США"), ("Focus", "Германия"), ("Marin", "США"),
    ("Norco", "Канада"), ("Polygon", "Индонезия"), ("Forward", "Россия"), ("Shulz", "Россия"),
    ("Welt", "Россия"), ("Haibike", "Германия"), ("Bianchi", "Италия"), ("Cervelo", "Канада"),
    ("Haro", "США"), ("Mongoose", "США"), ("Bell", "США"), ("BBB", "Нидерланды"),
    ("ABUS", "Германия"), ("Camelbak", "США"),
]

FEATURED_BRANDS = {
    "Trek", "Giant", "Merida", "Cube", "Scott", "Specialized",
    "Cannondale", "GT", "Focus", "Marin",
}

REVIEW_SNIPPETS = [
    ("Отличный велосипед!", "Лёгкий, накатистый", "Педали простоватые", 5),
    ("Доволен покупкой", "Качество сборки, тормоза", "", 5),
    ("Хорош за свои деньги", "Цена/качество", "Тяжеловат", 4),
    ("Нормально", "Едет и едет", "Ожидал большего от навески", 4),
    ("Супер для города", "Манёвренный, лёгкий", "", 5),
]


class Command(BaseCommand):
    help = "Наполняет БД демонстрационными данными"

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write("Очистка старых демо-данных…")
        for model in (Stock, Review, Question, Specification, Bike, Product, Store,
                      Article, Page, SizeChart, FAQ, ServiceType, Banner):
            model.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        # Категории
        cats = {}
        for name, slug, icon, parent_slug in CATEGORIES:
            cats[slug] = Category.objects.create(
                name=name, slug=slug, icon=icon,
                parent=cats.get(parent_slug), show_in_menu=(parent_slug is None or slug in {"gornye", "shosseynye", "gorodskie", "electro"}),
            )
        self.stdout.write(f"Категорий: {Category.objects.count()}")

        # Бренды
        brands = {}
        for name, country in BRANDS:
            brands[name] = Brand.objects.create(
                name=name, country=country, is_featured=name in FEATURED_BRANDS,
            )
        self.stdout.write(f"Брендов: {Brand.objects.count()}")

        # Велосипеды
        idx = 0
        products = []
        for (title, brand, cat, price, old, wheel, material, size,
             brake, susp, speeds, weight, electric) in BIKES:
            idx += 1
            ptype = Product.TYPE_EBIKE if electric else Product.TYPE_BIKE
            p = Product.objects.create(
                category=cats[cat], brand=brands[brand], title=title,
                sku=f"BK-{idx:04d}", product_type=ptype,
                short_description=f"{title} — {cats[cat].name.lower()} велосипед {brand}",
                description=(f"{title} — надёжный велосипед для {cats[cat].name.lower()} катания. "
                             f"Рама из {dict(Bike.FRAME_MATERIALS).get(material)}, "
                             f"колёса {wheel}\", {speeds} скоростей. "
                             "Предпродажная подготовка и настройка входят в стоимость."),
                price=price, old_price=old, stock_qty=random.randint(0, 12),
                is_new=(idx % 5 == 0), is_bestseller=(idx % 4 == 0),
                is_featured=(idx % 3 == 0), warranty_months=random.choice([12, 24, 24, 36]),
            )
            h_min, h_max = HEIGHT_BY_SIZE.get(size, (160, 185))
            Bike.objects.create(
                product=p, model_year=random.choice([2024, 2025, 2025]),
                gender="kids" if cat == "detskie" else random.choice(["unisex", "unisex", "male"]),
                wheel_size=wheel, frame_material=material, frame_size=size,
                brake_type=brake, suspension=susp, speeds=speeds,
                fork_travel=(100 if susp != "rigid" else None), is_electric=electric,
                weight_kg=weight, max_rider_weight=random.choice([110, 120, 130]),
                rider_height_min=h_min, rider_height_max=h_max,
            )
            Specification.objects.bulk_create([
                Specification(product=p, group="Трансмиссия", name="Кол-во скоростей", value=str(speeds), order=1),
                Specification(product=p, group="Трансмиссия", name="Переключатели", value=random.choice(["Shimano Altus", "Shimano Deore", "microSHIFT"]), order=2),
                Specification(product=p, group="Тормоза", name="Тип", value=dict(Bike.BRAKE_TYPES).get(brake), order=1),
                Specification(product=p, group="Колёса", name="Размер", value=f'{wheel}"', order=1),
                Specification(product=p, group="Рама", name="Материал", value=dict(Bike.FRAME_MATERIALS).get(material), order=1),
            ])
            products.append(p)

        # Аксессуары/экипировка
        for title, brand, cat, price, old, ptype in GEAR:
            idx += 1
            p = Product.objects.create(
                category=cats[cat], brand=brands[brand], title=title,
                sku=f"AC-{idx:04d}", product_type=ptype,
                short_description=f"{title} — {brand}",
                description=f"{title}. Официальная гарантия, оригинальный товар {brand}.",
                price=price, old_price=old, stock_qty=random.randint(3, 40),
                is_new=(idx % 6 == 0), is_bestseller=(idx % 5 == 0), is_featured=(idx % 4 == 0),
            )
            Specification.objects.create(product=p, group="Общие", name="Бренд", value=brand)
            products.append(p)

        self.stdout.write(f"Товаров: {Product.objects.count()}")

        # Изображения товаров (генерируем SVG)
        img_count = sum(1 for p in products if attach_image(p))
        self.stdout.write(f"Изображений: {img_count}")

        # Отзывы
        for p in products:
            if random.random() < 0.6:
                for _ in range(random.randint(1, 3)):
                    title, pros, cons, rating = random.choice(REVIEW_SNIPPETS)
                    Review.objects.create(
                        product=p, name=random.choice(["Алексей", "Мария", "Дмитрий", "Иван", "Ольга", "Сергей"]),
                        rating=rating, pros=pros, cons=cons, text=title,
                    )
        q = Question.objects.create(product=products[0], name="Никита", text="Подойдёт ли этот велосипед при росте 182 см?")
        Answer.objects.create(question=q, text="Да, ростовка M/L отлично подойдёт для роста 178–188 см.")
        self.stdout.write(f"Отзывов: {Review.objects.count()}")

        # Магазины + остатки
        stores_data = [
            ("Veloport Центр", "Москва", "ул. Тверская, 15", "8 495 111-22-33"),
            ("Veloport Юг", "Москва", "Каширское ш., 61", "8 495 111-22-34"),
            ("Veloport СПб", "Санкт-Петербург", "Невский пр., 100", "8 812 111-22-35"),
        ]
        stores = [Store.objects.create(name=n, city=c, address=a, phone=ph) for n, c, a, ph in stores_data]
        for store in stores:
            for p in random.sample(products, k=int(len(products) * 0.6)):
                Stock.objects.create(store=store, product=p, qty=random.randint(1, 6))
        self.stdout.write(f"Магазинов: {len(stores)}, остатков: {Stock.objects.count()}")

        # Услуги мастерской
        services = [
            ("ТО базовое", "Проверка и настройка узлов, смазка цепи", 1500, 60, "🔧"),
            ("ТО расширенное", "Полная переборка, чистка трансмиссии", 3500, 120, "🛠"),
            ("Сборка велосипеда из коробки", "Профессиональная сборка и настройка", 2000, 60, "📦"),
            ("Настройка переключателей", "Регулировка переднего и заднего", 900, 30, "⚙️"),
            ("Прокачка гидравлических тормозов", "Замена жидкости, прокачка", 1200, 45, "🩸"),
            ("Обслуживание вилки", "ТО амортизационной вилки", 2500, 90, "🔩"),
        ]
        for i, (n, d, price, dur, icon) in enumerate(services):
            ServiceType.objects.create(name=n, description=d, price_from=price, duration_min=dur, icon=icon, order=i)
        self.stdout.write(f"Услуг: {ServiceType.objects.count()}")

        # Контент
        Banner.objects.create(title="Сезон открыт!", subtitle="Скидки до 30% на горные велосипеды", button_text="Смотреть")
        articles = [
            ("Как выбрать первый велосипед: полный гайд", "guide",
             "Разбираем типы велосипедов, ростовки и на что смотреть новичку."),
            ("Горный или шоссейный: что выбрать", "guide",
             "Сравниваем MTB и road: где, как и зачем на них катаются."),
            ("Гид по ростовкам рам под ваш рост", "howto",
             "Таблицы соответствия роста и размера рамы для разных типов."),
            ("Обзор Trek Marlin 7 2025", "review",
             "Тестируем популярный хардтейл: плюсы, минусы и кому подойдёт."),
            ("5 аксессуаров, без которых не стоит выезжать", "howto",
             "Шлем, замок, свет, насос и фляга — базовый набор велосипедиста."),
        ]
        for title, cat, excerpt in articles:
            Article.objects.create(
                title=title, category=cat, excerpt=excerpt, reading_time=random.randint(4, 9),
                body=(excerpt + "\n\n" + "Это демонстрационная статья контент-хаба Veloport. "
                      "Здесь будет подробный разбор темы с примерами, таблицами и фото. "
                      "Контент-маркетинг помогает покупателю принять решение и повышает доверие к магазину."),
            )
        self.stdout.write(f"Статей: {Article.objects.count()}")

        SizeChart.objects.create(
            title="Ростовка горного велосипеда по росту",
            intro="Подберите размер рамы MTB под свой рост.",
            body="<table><thead><tr><th>Рост, см</th><th>Ростовка</th></tr></thead><tbody>"
                 "<tr><td>150–160</td><td>XS (13–14\")</td></tr>"
                 "<tr><td>160–170</td><td>S (15–16\")</td></tr>"
                 "<tr><td>170–180</td><td>M (17–18\")</td></tr>"
                 "<tr><td>180–190</td><td>L (19–20\")</td></tr>"
                 "<tr><td>190+</td><td>XL (21–22\")</td></tr></tbody></table>",
        )
        faqs = [
            ("Собираете ли вы велосипед перед выдачей?", "Да, предпродажная сборка и настройка входят в стоимость."),
            ("Есть ли доставка велосипедов?", "Да, курьером по городу и СДЭК по России. Крупногабарит доставляем в собранном виде."),
            ("Можно ли вернуть велосипед?", "Да, в течение 14 дней при сохранении товарного вида."),
            ("Действует ли гарантия на раму?", "На рамы большинства брендов действует расширенная гарантия до 5 лет."),
        ]
        for i, (q_, a_) in enumerate(faqs):
            FAQ.objects.create(question=q_, answer=a_, order=i)

        Page.objects.create(title="Доставка и оплата", body="Курьер по Москве — от 1 дня. СДЭК по России. Оплата картой онлайн, СБП или при получении.")
        Page.objects.create(title="Гарантия и возврат", body="Гарантия производителя. Возврат в течение 14 дней. Сервисное обслуживание в наших мастерских.")

        # Админ
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@veloport.ru", "admin")
            self.stdout.write(self.style.WARNING("Создан суперпользователь admin / admin"))

        self.stdout.write(self.style.SUCCESS("Готово! Демо-данные загружены. 🚴"))
