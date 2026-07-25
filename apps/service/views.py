from django.contrib import messages
from django.shortcuts import redirect, render

from apps.stores.models import Store

from .forms import ServiceBookingForm, TradeInForm
from .models import ServiceType


def service_index(request):
    if request.method == "POST":
        form = ServiceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            from apps.core.emails import send_service_booking
            send_service_booking(booking)
            messages.success(
                request, f"Записали! Номер заявки {booking.number}. Перезвоним для подтверждения."
            )
            return redirect("service:index")
    else:
        form = ServiceBookingForm()
    return render(
        request,
        "service/index.html",
        {
            "form": form,
            "services": ServiceType.objects.filter(is_active=True),
            "stores": Store.objects.filter(is_active=True, has_service=True),
        },
    )


def tradein(request):
    if request.method == "POST":
        form = TradeInForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save()
            messages.success(
                request, f"Заявка {req.number} принята. Оценим и свяжемся с вами."
            )
            return redirect("service:tradein")
    else:
        form = TradeInForm()
    return render(request, "service/tradein.html", {"form": form})
