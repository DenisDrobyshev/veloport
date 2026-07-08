from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name", "last_name", "phone", "email",
            "delivery_method", "store",
            "city", "street", "house", "apartment", "postal_code",
            "payment_method", "comment",
        ]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("delivery_method")
        if method == Order.DELIVERY_PICKUP and not cleaned.get("store"):
            self.add_error("store", "Выберите магазин для самовывоза")
        if method in {Order.DELIVERY_COURIER, Order.DELIVERY_CDEK, Order.DELIVERY_POST}:
            if not cleaned.get("city"):
                self.add_error("city", "Укажите город доставки")
            if not cleaned.get("street"):
                self.add_error("street", "Укажите улицу")
        return cleaned
