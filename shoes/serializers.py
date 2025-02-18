from rest_framework import serializers
from .models import *
from django.db import transaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="image.url", required=False)

    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "is_main"]


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ["size", "quantity"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(
        many=True,
    )
    sizes = ProductSizeSerializer(
        many=True,
    )
    category = serializers.CharField(
        source="category.name",
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "design_type",
            "description",
            "price",
            "category",
            "images",
            "sizes",
        ]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        sizes_data = validated_data.pop("sizes", [])
        category_data = validated_data.pop("category")
        category_name = category_data.get("name")

        try:
            with transaction.atomic():
                category, _ = Category.objects.get_or_create(name=category_name)

                product = Product.objects.create(category=category, **validated_data)

                for image_data in images_data:
                    ProductImage.objects.create(product=product, **image_data)

                for size_data in sizes_data:
                    ProductSize.objects.create(product=product, **size_data)

            return product

        except serializers.ValidationError as ve:
            raise ve

        except Exception as e:
            raise serializers.ValidationError(
                {"error": "Product creation failed", "details": str(e)}
            )
