from django.urls import path

from . import views

app_name = "service"

urlpatterns = [
    path("", views.service_index, name="index"),
    path("trade-in/", views.tradein, name="tradein"),
]
