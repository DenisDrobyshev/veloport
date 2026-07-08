from decimal import Decimal

from django.conf import settings

from apps.catalog.models import Product, ProductVariant


class Cart:
    """Корзина на основе сессии."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    @staticmethod
    def _key(product_id, variant_id=None) -> str:
        return f"{product_id}:{variant_id or ''}"

    def add(self, product, qty=1, variant=None, update=False):
        key = self._key(product.id, variant.id if variant else None)
        if key not in self.cart:
            price = variant.price if variant else product.price
            self.cart[key] = {
                "product_id": product.id,
                "variant_id": variant.id if variant else None,
                "qty": 0,
                "price": str(price),
            }
        if update:
            self.cart[key]["qty"] = qty
        else:
            self.cart[key]["qty"] += qty
        if self.cart[key]["qty"] < 1:
            del self.cart[key]
        self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.cart = self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self):
        product_ids = [v["product_id"] for v in self.cart.values()]
        products = {
            p.id: p
            for p in Product.objects.filter(id__in=product_ids)
            .select_related("brand")
            .prefetch_related("images")
        }
        variant_ids = [v["variant_id"] for v in self.cart.values() if v["variant_id"]]
        variants = {v.id: v for v in ProductVariant.objects.filter(id__in=variant_ids)}
        for key, item in self.cart.items():
            product = products.get(item["product_id"])
            if not product:
                continue
            variant = variants.get(item["variant_id"]) if item["variant_id"] else None
            price = Decimal(item["price"])
            yield {
                "key": key,
                "product": product,
                "variant": variant,
                "qty": item["qty"],
                "price": price,
                "total": price * item["qty"],
            }

    def __len__(self):
        return sum(item["qty"] for item in self.cart.values())

    @property
    def total(self) -> Decimal:
        return sum(
            (Decimal(item["price"]) * item["qty"] for item in self.cart.values()),
            Decimal("0"),
        )

    @property
    def is_empty(self) -> bool:
        return len(self.cart) == 0

    @property
    def shipping(self) -> Decimal:
        if self.total >= settings.FREE_SHIPPING_THRESHOLD or self.is_empty:
            return Decimal("0")
        return Decimal("500")

    @property
    def grand_total(self) -> Decimal:
        return self.total + self.shipping
