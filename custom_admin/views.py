from rest_framework import viewsets
from shoes.models import Category
from shoes.serializers import CategorySerializer
from shoes.permissions import IsAdminOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing category CRUD operations.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer 

    permission_classes = [IsAdminOrReadOnly]
