from django.urls import path
from .views import *

urlpatterns = [
    path("list-create/", ProductListCreateView.as_view(), name="product-list-create"),
    path("details/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]
