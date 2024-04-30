import django_filters
from .models import Producto, Marca, Cliente, Compra
from django.utils.translation import gettext_lazy as _


class ProductoPorMarcaFilter(django_filters.FilterSet):
    marca = django_filters.ChoiceFilter(choices=Marca.objects.values_list("id", "nombre"), empty_label=_("filter_all"))

    class Meta:
        model = Producto
        fields = ['marca']


class ComprasPorClienteFilter(django_filters.FilterSet):
    cliente = django_filters.ChoiceFilter(choices=Cliente.objects.values_list("id", "user__username"),
                                          empty_label=_("filter_all"))

    class Meta:
        model = Compra
        fields = ['cliente']


class TiendaListFilter(django_filters.FilterSet):
    marca = django_filters.ChoiceFilter(choices=Marca.objects.values_list("id", "nombre"), empty_label=_("filter_all"), label=_("filter_brand"))
    nombre = django_filters.CharFilter(lookup_expr="icontains", label=_("filter_name"))

    class Meta:
        model = Producto
        fields = ['marca', 'nombre']
