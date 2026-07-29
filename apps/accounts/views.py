from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import StockNotification

from .forms import AddressForm, ProfileForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Добро пожаловать в Veloport!")
            return redirect("accounts:profile")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    user = request.user
    orders = user.orders.prefetch_related("items").all()
    subscriptions = (
        StockNotification.objects.filter(email=user.email).select_related("product")
        if user.email else StockNotification.objects.none()
    )
    return render(request, "accounts/profile.html", {
        "orders": orders,
        "addresses": user.addresses.all(),
        "subscriptions": subscriptions,
        "bonus_earned": sum(o.bonus_earned for o in orders),
        "bonus_spent": sum(o.bonus_used for o in orders),
    })


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def address_add(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                request.user.addresses.update(is_default=False)
            address.save()
            messages.success(request, "Адрес сохранён")
            return redirect("accounts:profile")
    else:
        form = AddressForm()
    return render(request, "accounts/address_form.html", {"form": form})


@login_required
@require_POST
def address_delete(request, pk):
    request.user.addresses.filter(pk=pk).delete()
    messages.info(request, "Адрес удалён")
    return redirect("accounts:profile")
