from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("suggest/", views.suggest, name="suggest"),
    path("notify/<int:product_id>/", views.stock_notify, name="stock_notify"),
    path("brand/<slug:brand>/", views.brand_view, name="brand"),
    path("product/<slug:slug>/", views.product_detail, name="product"),
    path("<slug:category>/", views.category_view, name="category"),
]
