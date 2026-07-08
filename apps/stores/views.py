from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .models import Reservation, Store


def store_list(request):
    stores = Store.objects.filter(is_active=True)
    return render(request, "stores/list.html", {"stores": stores})


def store_detail(request, slug):
    store = get_object_or_404(Store, slug=slug, is_active=True)
    stocks = store.stocks.filter(qty__gt=0).select_related("product", "product__brand")
    return render(request, "stores/detail.html", {"store": store, "stocks": stocks})


@require_POST
def reserve(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    store = get_object_or_404(Store, id=request.POST.get("store"))
    reservation = Reservation.objects.create(
        product=product,
        store=store,
        name=request.POST.get("name", "").strip() or "Гость",
        phone=request.POST.get("phone", "").strip(),
        qty=max(1, int(request.POST.get("qty", 1) or 1)),
        comment=request.POST.get("comment", "").strip(),
    )
    if request.htmx:
        return render(request, "stores/_reserve_ok.html", {"reservation": reservation})
    messages.success(request, f"Товар зарезервирован. Номер брони {reservation.number}")
    return redirect(product.get_absolute_url())
