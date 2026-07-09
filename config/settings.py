"""
Django settings for Veloport — интернет-магазин велосипедов и спортинвентаря.

Монолит на Django. Задел под вынос сервисов (поиск, оплата, медиа) через DRF.
"""

from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из .env (если есть)
load_dotenv(BASE_DIR / ".env")


def env_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in {"1", "true", "yes", "on"}


# --- Security ---
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-dev-only-5s%i8_6^z7-lm$05de!#azom^=gp&fi72wp4ro-daaoq$9u@)f",
)
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
CSRF_TRUSTED_ORIGINS = [
    o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o
]


# --- Applications ---
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "mptt",
    "django_htmx",
    "widget_tweaks",
    "django_cleanup.apps.CleanupConfig",  # должен идти последним из third-party
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.catalog",
    "apps.cart",
    "apps.orders",
    "apps.reviews",
    "apps.stores",
    "apps.service",
    "apps.content",
]

# jazzmin должен идти ПЕРЕД django.contrib.admin
INSTALLED_APPS = ["jazzmin"] + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.cart.context_processors.cart",
                "apps.core.context_processors.catalog_menu",
                "apps.core.context_processors.compare_count",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Database ---
# По умолчанию SQLite (dev); в проде — DATABASE_URL (Postgres).
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# --- Auth ---
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "core:home"


# --- I18N / L10N ---
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True


# --- Static & Media ---
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Cart ---
CART_SESSION_ID = "cart"
COMPARE_SESSION_ID = "compare"


# --- DRF (задел под API/сервисы) ---
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}


# --- Магазин: бизнес-константы ---
SHOP_NAME = "Veloport"
SHOP_PHONE = "8 800 555-35-35"
SHOP_EMAIL = "hello@veloport.ru"
FREE_SHIPPING_THRESHOLD = 5000  # бесплатная доставка от суммы, ₽


# --- Оплата (ЮKassa / YooKassa) ---
# Задайте ключи в .env, чтобы включить реальную оплату.
# Если ключей нет — работает demo-режим (имитация оплаты).
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY", "")
PAYMENTS_ENABLED = bool(YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY)


# --- Админка (Jazzmin) ---
JAZZMIN_SETTINGS = {
    "site_title": "Veloport Admin",
    "site_header": "Veloport",
    "site_brand": "VELOPORT",
    "welcome_sign": "Панель управления магазином Veloport",
    "copyright": "Veloport",
    "search_model": ["catalog.Product", "orders.Order"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Открыть сайт", "url": "/", "new_window": True},
        {"name": "Заказы", "model": "orders.order"},
        {"name": "Товары", "model": "catalog.product"},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.User": "fas fa-user",
        "accounts.Address": "fas fa-map-marker-alt",
        "catalog.Category": "fas fa-sitemap",
        "catalog.Brand": "fas fa-tag",
        "catalog.Product": "fas fa-bicycle",
        "orders.Order": "fas fa-shopping-cart",
        "reviews.Review": "fas fa-star",
        "reviews.Question": "fas fa-question-circle",
        "stores.Store": "fas fa-store",
        "stores.Stock": "fas fa-boxes",
        "stores.Reservation": "fas fa-bookmark",
        "service.ServiceType": "fas fa-cogs",
        "service.ServiceBooking": "fas fa-wrench",
        "service.TradeInRequest": "fas fa-recycle",
        "content.Article": "fas fa-newspaper",
        "content.Page": "fas fa-file-alt",
        "content.SizeChart": "fas fa-ruler-combined",
        "content.FAQ": "fas fa-question",
        "core.Banner": "fas fa-images",
        "core.Subscriber": "fas fa-envelope",
    },
    "order_with_respect_to": [
        "catalog", "orders", "stores", "service", "reviews", "content", "accounts", "core",
    ],
    "changeform_format": "horizontal_tabs",
    "related_modal_active": True,
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": None,
    "navbar": "navbar-dark",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "accent": "accent-danger",
    "button_classes": {
        "primary": "btn-outline-primary",
        "success": "btn-outline-success",
    },
}
