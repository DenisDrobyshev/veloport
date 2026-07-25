"""Сигналы каталога: авто-уведомление о поступлении товара."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.emails import send_restock

from .models import Product


@receiver(post_save, sender=Product)
def notify_restock(sender, instance, **kwargs):
    """Когда у товара появился остаток — уведомляем подписчиков."""
    if instance.stock_qty <= 0:
        return
    pending = list(instance.stock_notifications.filter(is_notified=False))
    if not pending:
        return
    for note in pending:
        send_restock(instance, note.email)
    instance.stock_notifications.filter(id__in=[n.id for n in pending]).update(is_notified=True)
