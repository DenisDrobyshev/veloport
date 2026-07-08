from django.urls import path

from . import views

app_name = "stores"

urlpatterns = [
    path("", views.store_list, name="list"),
    path("reserve/<int:product_id>/", views.reserve, name="reserve"),
    path("<slug:slug>/", views.store_detail, name="detail"),
]
