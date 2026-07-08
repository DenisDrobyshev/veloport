from django.urls import path

from . import api

app_name = "catalog_api"

urlpatterns = [
    path("products/", api.ProductListAPI.as_view(), name="products"),
    path("products/<slug:slug>/", api.ProductDetailAPI.as_view(), name="product"),
    path("categories/", api.CategoryListAPI.as_view(), name="categories"),
]
