from rest_framework import generics

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductListAPI(generics.ListAPIView):
    """Список товаров (задел под будущий сервис/фронт)."""

    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.active().select_related("brand", "category")
        if category := self.request.query_params.get("category"):
            qs = qs.filter(category__slug=category)
        if q := self.request.query_params.get("q"):
            qs = qs.filter(title__icontains=q)
        return qs


class ProductDetailAPI(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = "slug"
    queryset = Product.objects.active()


class CategoryListAPI(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)
