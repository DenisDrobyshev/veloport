#!/bin/sh
set -e

echo "==> Применяю миграции..."
n=0
until python manage.py migrate --noinput; do
  n=$((n + 1))
  if [ "$n" -ge 10 ]; then
    echo "База данных недоступна, выхожу."
    exit 1
  fi
  echo "База не готова, повтор ($n)..."
  sleep 3
done

echo "==> Собираю статику..."
python manage.py collectstatic --noinput

# Первичное наполнение (только если товаров ещё нет)
if [ "$SEED" = "1" ]; then
  COUNT=$(python -c "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings');django.setup();from apps.catalog.models import Product;print(Product.objects.count())" 2>/dev/null || echo 0)
  if [ "$COUNT" = "0" ]; then
    echo "==> Загружаю демо-данные..."
    python manage.py seed_demo
    if [ "$FETCH_PHOTOS" = "1" ]; then
      echo "==> Загружаю фото товаров..."
      python manage.py fetch_photos || true
    fi
  else
    echo "==> Данные уже есть ($COUNT товаров), пропускаю seed."
  fi
fi

echo "==> Запуск: $*"
exec "$@"
