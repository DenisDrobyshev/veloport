from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Address, User


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["city", "street", "house", "apartment", "postal_code", "is_default"]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "birth_date", "height_cm"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }
