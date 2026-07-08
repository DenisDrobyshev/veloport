import json

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.cart.cart import Cart
from apps.stores.models import Store

from . import payments
from .forms import CheckoutForm
from .models import Order, OrderItem


def checkout(request):
    cart = Cart(request)
    if cart.is_empty:
        messages.info(request, "Корзина пуста")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in cart:
                title = item["product"].title
                if item["variant"]:
                    title += f" ({item['variant'].group}: {item['variant'].value})"
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    variant=item["variant"],
                    title=title,
                    price=item["price"],
                    qty=item["qty"],
                )
            order.recalc_total()
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
