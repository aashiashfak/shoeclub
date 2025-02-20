from rest_framework import viewsets, status
from shoes.models import Category, Product
from shoes.serializers import *
from shoes.permissions import IsAdminOrReadOnly
from rest_framework.response import Response


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing category CRUD operations.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        print("entered in destroy method")
        category = self.get_object()
        associated_products = Product.objects.filter(category=category)

        if associated_products.exists():
            product_names = list(associated_products.values_list("name", flat=True))
            return Response(
                {
                    "error": "Category can't be deleted.",
                    "message": "There are products associated with this category.",
                    "products": product_names,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ProductSize CRUD operations.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductSizeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ProductSize CRUD operations.
    """

    queryset = ProductSize.objects.all()
    serializer_class = ProductSizeSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ProductImage CRUD operations.
    """

    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
