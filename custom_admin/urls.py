from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
     
]


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"sizes", ProductSizeViewSet, basename="size")
router.register(r"images", ProductImageViewSet, basename="image")

urlpatterns += router.urls
