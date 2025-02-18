from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
     
]


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns += router.urls
