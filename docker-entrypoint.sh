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

if [ "$SEED" = "1" ]; then
  echo "==> Загружаю демо-данные..."
  python manage.py seed_demo
fi

echo "==> Запуск: $*"
exec "$@"
