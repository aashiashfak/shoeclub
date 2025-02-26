from rest_framework import viewsets, status, generics
from shoes.models import Category, Product
from shoes.serializers import *
from shoes.permissions import IsAdminOrReadOnly
from rest_framework.response import Response
from django.db import transaction
from cloudinary.uploader import destroy
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


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

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "sizes", "images"
        )
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductSizeListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating of a product productsize instances.
    """

    serializer_class = ProductSizeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return ProductSize.objects.filter(product=product_id)

    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs["product_id"])
        size = serializer.validated_data.get("size")  # Extract size from validated data

        # **Check if the size already exists before saving**
        if ProductSize.objects.filter(product=product, size=size).exists():
            raise ValidationError({"size": "This size already exists for the product."})

        serializer.save(product=product)


class ProductSizeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific ProductSize instance.
    """

    queryset = ProductSize.objects.all()
    serializer_class = ProductSizeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_update(self, serializer):
        product_size = self.get_object()
        product = product_size.product
        new_size = serializer.validated_data.get("size", product_size.size)

        if (
            ProductSize.objects.filter(product=product, size=new_size)
            .exclude(id=product_size.id)
            .exists()
        ):
            raise ValidationError({"size": "This size already exists for the product."})

        serializer.save()


class ProductImageListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating ProductImage instances for a specific product.
    """

    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Return images for a specific product.
        """
        return ProductImage.objects.filter(product=self.kwargs["product_id"])

    def perform_create(self, serializer):
        """
        Ensure only one 'is_main=True' per product when creating a new image.
        """
        product = get_object_or_404(Product, id=self.kwargs["product_id"])
        is_main = serializer.validated_data.get("is_main", False)

        with transaction.atomic():
            if is_main:
                ProductImage.objects.filter(product=product, is_main=True).update(
                    is_main=False
                )

            serializer.save(product=product)  


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific ProductImage instance.
    """

    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def perform_update(self, serializer):
        """
        Handle Cloudinary image updates and ensure only one 'is_main=True' per product.
        """
        instance = self.get_object()
        new_image = self.request.data.get("image", None)
        new_is_main = self.request.data.get("is_main", None)

        with transaction.atomic():
            if new_image and instance.image:
                destroy(instance.image.public_id)

            if new_is_main and new_is_main.lower() == "true":
                ProductImage.objects.filter(
                    product=instance.product, is_main=True
                ).update(is_main=False)

            serializer.save()

        def perform_destroy(self, instance):
            """
            Delete the image from Cloudinary before deleting the instance.
            """
            with transaction.atomic():
                if instance.image:
                    destroy(instance.image.public_id)
                instance.delete()
