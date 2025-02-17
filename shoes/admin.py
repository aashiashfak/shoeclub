from django.contrib import admin
from .models import Category, Product, ProductSize, ProductImage


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "price",
        "category",
    )
    search_fields = (
        "name",
        "description",
    )
    list_filter = ("category",)  #


class ProductSizeAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "quantity",
    )
    search_fields = ("product__name", "size")
    list_filter = ("product",)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "image_url",
        "is_main",
    )
    search_fields = ("product__name",)
    list_filter = ("is_main",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
