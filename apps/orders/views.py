import json
import re
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.cart.cart import Cart
from apps.stores.models import Store

from . import payments
from .forms import CheckoutForm
from .models import Coupon, Order, OrderItem


def checkout(request):
    cart = Cart(request)
    if cart.is_empty:
        messages.info(request, "Корзина пуста")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            user = request.user if request.user.is_authenticated else None
            if user:
                order.user = user

            goods = cart.total

            # Промокод
            discount = Decimal("0")
            coupon = None
            promo = request.POST.get("promo", "").strip().upper()
            if promo:
                coupon = Coupon.objects.filter(code=promo).first()
                if coupon:
                    ok, _ = coupon.validate_for(goods)
                    if ok:
                        discount = coupon.discount_for(goods)
                    else:
                        coupon = None

            # Бонусные баллы
            bonus_used = 0
            if user:
                try:
                    want = int(request.POST.get("use_bonus", 0) or 0)
                except ValueError:
                    want = 0
                cap = int(goods - discount)
                bonus_used = max(0, min(want, user.bonus_points, cap))

            order.coupon = coupon
            order.discount = discount
            order.bonus_used = bonus_used
            order.save()

            for item in cart:
                title = item["product"].title
                if item["variant"]:
                    title += f" ({item['variant'].group}: {item['variant'].value})"
                OrderItem.objects.create(
                    order=order, product=item["product"], variant=item["variant"],
                    title=title, price=item["price"], qty=item["qty"],
                )
            order.recalc_total()

            if coupon:
                Coupon.objects.filter(pk=coupon.pk).update(used_count=F("used_count") + 1)

            if user:
                earned = int(order.payable * Decimal(str(settings.BONUS_ACCRUAL_RATE)))
                order.bonus_earned = earned
                order.save(update_fields=["bonus_earned"])
                user.bonus_points = max(0, user.bonus_points - bonus_used + earned)
                user.save(update_fields=["bonus_points"])

            cart.clear()
            if order.is_online_payment:
                return redirect("orders:pay", number=order.number)
            return redirect("orders:success", number=order.number)
    else:
        initial = {}
        if request.user.is_authenticated:
            u = request.user
            initial = {
                "first_name": u.first_name,
                "last_name": u.last_name,
                "phone": u.phone,
                "email": u.email,
            }
        form = CheckoutForm(initial=initial)

    return render(
        request,
        "orders/checkout.html",
        {"form": form, "stores": Store.objects.filter(is_active=True)},
    )


def order_success(request, number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), number=number)
    return render(request, "orders/success.html", {"order": order})


def pay(request, number):
    """Инициирует оплату: реальную (ЮKassa) или demo."""
    order = get_object_or_404(Order, number=number)
    if not order.needs_payment:
        return redirect("orders:success", number=order.number)

    return_url = request.build_absolute_uri(reverse("orders:success", args=[order.number]))

    if payments.is_configured():
        payment = payments.create_payment(order, return_url)
        order.payment_id = payment.id
        order.save(update_fields=["payment_id"])
        return redirect(payment.confirmation.confirmation_url)

    # demo-режим
    return render(request, "orders/pay_mock.html", {"order": order})


@require_POST
def mock_confirm(request, number):
    """Подтверждение оплаты в demo-режиме."""
    order = get_object_or_404(Order, number=number)
    order.is_paid = True
    order.status = Order.STATUS_CONFIRMED
    order.save(update_fields=["is_paid", "status"])
    messages.success(request, "Оплата прошла успешно (demo-режим) ✅")
    return redirect("orders:success", number=order.number)


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    """Вебхук ЮKassa: помечает заказ оплаченным при payment.succeeded."""
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    if data.get("event") == "payment.succeeded":
        number = data.get("object", {}).get("metadata", {}).get("order_number")
        if number:
            Order.objects.filter(number=number).update(
                is_paid=True, status=Order.STATUS_CONFIRMED
            )
    return HttpResponse(status=200)


@require_POST
def coupon_check(request):
    """HTMX-проверка промокода на странице оформления."""
    code = request.POST.get("promo", "").strip().upper()
    cart = Cart(request)
    ctx = {"ok": False, "msg": "Введите промокод", "discount": 0}
    if code:
        coupon = Coupon.objects.filter(code=code).first()
        if not coupon:
            ctx["msg"] = "Промокод не найден"
        else:
            ok, msg = coupon.validate_for(cart.total)
            ctx = {"ok": ok, "msg": msg, "discount": coupon.discount_for(cart.total) if ok else 0}
    return render(request, "orders/_coupon_msg.html", ctx)


def track(request):
    """Публичное отслеживание заказа по номеру + телефону."""
    number = request.GET.get("number", "").strip()
    phone = request.GET.get("phone", "").strip()
    order = None
    searched = bool(number and phone)
    if searched:
        digits = re.sub(r"\D", "", phone)
        if digits:
            order = (
                Order.objects.filter(number__iexact=number)
                .filter(phone__endswith=digits)
                .prefetch_related("items")
                .first()
            )
    flow = [Order.STATUS_NEW, Order.STATUS_CONFIRMED, Order.STATUS_ASSEMBLING,
            Order.STATUS_SHIPPED, Order.STATUS_READY, Order.STATUS_DONE]
    labels = dict(Order.STATUSES)
    timeline = []
    if order and order.status in flow:
        idx = flow.index(order.status)
        timeline = [{"label": labels[s], "reached": i <= idx, "current": i == idx}
                    for i, s in enumerate(flow)]
    return render(request, "orders/track.html", {
        "order": order, "number": number, "phone": phone,
        "searched": searched, "timeline": timeline,
    })
