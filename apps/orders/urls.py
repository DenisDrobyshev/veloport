from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("success/<str:number>/", views.order_success, name="success"),
    path("pay/<str:number>/", views.pay, name="pay"),
    path("pay/<str:number>/confirm/", views.mock_confirm, name="mock_confirm"),
    path("webhook/yookassa/", views.yookassa_webhook, name="yookassa_webhook"),
]
