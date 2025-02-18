import django_filters 
from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    size = django_filters.CharFilter(field_name="sizes__size", lookup_expr="iexact")
    category = filters.CharFilter(method="filter_category")

    class Meta:
        model = Product  
        fields = ["category", "is_active"]

    def filter_category(self, queryset, name, value):
        categories = value.split(",")
        return queryset.filter(category__name__in=categories)
