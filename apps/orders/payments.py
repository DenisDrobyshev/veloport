"""Интеграция оплаты через ЮKassa.

Если ключи заданы (settings.PAYMENTS_ENABLED) — создаём реальный платёж и
редиректим на страницу оплаты ЮKassa. Иначе используется demo-режим
(имитация оплаты) — удобно для локальной разработки.
"""

import uuid

from django.conf import settings


def is_configured() -> bool:
    return settings.PAYMENTS_ENABLED


def create_payment(order, return_url: str):
    """Создаёт платёж в ЮKassa и возвращает объект платежа."""
    from yookassa import Configuration, Payment

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    method = "sbp" if order.payment_method == order.PAYMENT_SBP else "bank_card"
    payment = Payment.create(
        {
            "amount": {"value": f"{order.total:.2f}", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": f"Заказ {order.number} в Veloport",
            "payment_method_data": {"type": method},
            "metadata": {"order_number": order.number},
        },
        uuid.uuid4(),
    )
    return payment
