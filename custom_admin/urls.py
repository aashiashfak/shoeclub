from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

urlpatterns = [
    path("sizes/<int:product_id>/", ProductSizeListCreateView.as_view(), name="product-size-list"),
    path("size/<int:pk>/", ProductSizeDetailView.as_view(), name="product-size-detail"),
    path("images/<int:product_id>/", ProductImageListCreateView.as_view(), name="product-image-list"),
    path("image/<int:pk>/", ProductImageDetailView.as_view(), name="product-image-detail"),
     
]


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns += router.urls
