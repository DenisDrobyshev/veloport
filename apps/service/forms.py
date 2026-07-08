from django import forms

from .models import ServiceBooking, TradeInRequest


class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = [
            "service_type", "store", "name", "phone", "email",
            "bike_info", "preferred_date", "preferred_time", "comment",
        ]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class TradeInForm(forms.ModelForm):
    class Meta:
        model = TradeInRequest
        fields = [
            "name", "phone", "email", "brand", "model", "year",
            "condition", "description", "photo", "desired_product",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
