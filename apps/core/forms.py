from django import forms

from .models import Subscriber

STYLE_CHOICES = [
    ("gorod", "🏙 Город и прогулки"),
    ("gornyy", "⛰ Горы и бездорожье"),
    ("shosse", "🏁 Шоссе и скорость"),
    ("gravel", "🌾 Гравий и микс"),
    ("detskiy", "🧒 Ребёнку"),
    ("electro", "⚡ Электро"),
]

BUDGET_CHOICES = [
    ("0-30000", "до 30 000 ₽"),
    ("30000-60000", "30 000 – 60 000 ₽"),
    ("60000-120000", "60 000 – 120 000 ₽"),
    ("120000-0", "от 120 000 ₽"),
]

# style value -> slug категории (см. seed_demo)
STYLE_TO_CATEGORY = {
    "gorod": "gorodskie",
    "gornyy": "gornye",
    "shosse": "shosseynye",
    "gravel": "gravel",
    "detskiy": "detskie",
    "electro": "electro",
}


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email"]


class FitFinderForm(forms.Form):
    height = forms.IntegerField(label="Ваш рост, см", min_value=90, max_value=220)
    style = forms.ChoiceField(label="Стиль катания", choices=STYLE_CHOICES)
    budget = forms.ChoiceField(label="Бюджет", choices=BUDGET_CHOICES)
