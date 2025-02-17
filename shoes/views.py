from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework import status
from .models import Product, ProductImage, ProductSize
from .serializers import ProductSerializer
from .permissions import IsAdminOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .pagination import ProductPagination


class ProductListCreateView(generics.ListCreateAPIView):
    """
    API view to list all products and create a new product.
    """

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "sizes", "images"
        )

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    pagination_class = ProductPagination
    search_fields = [
        "name",
        "description",
        "category__name",
    ]


class ProductDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a specific product.
    """

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "sizes", "images"
        )

    serializer_class = ProductSerializer
