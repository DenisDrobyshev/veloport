"""Отправка транзакционных писем (устойчиво к ошибкам SMTP)."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _send(subject, template, context, to):
    if not to:
        return
    try:
        body = render_to_string(template, context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=True)
    except Exception as exc:  # письма не должны ломать основной поток
        logger.warning("email send failed: %s", exc)


def send_order_confirmation(order):
    _send(
        f"Заказ {order.number} принят — Veloport",
        "emails/order_confirmation.txt",
        {"order": order},
        order.email,
    )


def send_restock(product, email):
    _send(
        f"«{product.title}» снова в наличии — Veloport",
        "emails/restock.txt",
        {"product": product},
        email,
    )


def send_service_booking(booking):
    _send(
        f"Запись в веломастерскую {booking.number} — Veloport",
        "emails/service_booking.txt",
        {"booking": booking},
        booking.email,
    )
