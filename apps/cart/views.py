from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product, ProductVariant

from .cart import Cart


def cart_detail(request):
    return render(request, "cart/detail.html", {})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    qty = max(1, int(request.POST.get("qty", 1) or 1))
    variant = None
    if variant_id := request.POST.get("variant"):
        variant = ProductVariant.objects.filter(id=variant_id, product=product).first()
    cart.add(product, qty=qty, variant=variant)
    if request.htmx:
        return render(request, "cart/_badge.html", {"added": product})
    return redirect("cart:detail")


def _parse_key(key):
    pid, _, vid = key.partition(":")
    return pid, (vid or None)


@require_POST
def cart_update(request, key):
    cart = Cart(request)
    pid, vid = _parse_key(key)
    product = get_object_or_404(Product, id=pid)
    variant = ProductVariant.objects.filter(id=vid).first() if vid else None
    qty = max(1, int(request.POST.get("qty", 1) or 1))
    cart.add(product, qty=qty, variant=variant, update=True)
    if request.htmx:
        return render(request, "cart/_content.html", {})
    return redirect("cart:detail")


@require_POST
def cart_remove(request, key):
    cart = Cart(request)
    cart.remove(key)
    if request.htmx:
        return render(request, "cart/_content.html", {})
    return redirect("cart:detail")


@require_POST
def cart_clear(request):
    Cart(request).clear()
    return redirect("cart:detail")
