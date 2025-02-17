from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import TimeStampedModel


class Category(TimeStampedModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(TimeStampedModel, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.PROTECT
    )

    def __str__(self):
        return self.name


class ProductSize(TimeStampedModel, models.Model):
    product = models.ForeignKey(Product, related_name="sizes", on_delete=models.CASCADE)
    size = models.CharField(max_length=8)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Size {self.size} - {self.quantity} in stock"

    class Meta:
        unique_together = ("product", "size")


class ProductImage(TimeStampedModel, models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = CloudinaryField("image", folder="shoe_images/")
    is_main = models.BooleanField(default=False)  

    @property
    def image_url(self):
        return self.image.url if self.image else "No image"

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "is_main"],
                condition=models.Q(is_main=True),
                name="unique_main_image",
            )
        ]
