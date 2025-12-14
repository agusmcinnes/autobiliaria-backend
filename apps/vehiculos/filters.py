import django_filters
from django.db import models

from .models import Vehiculo, TipoVehiculo


class VehiculoFilter(django_filters.FilterSet):
    """Filtros avanzados para vehiculos."""

    # Tipo de vehiculo
    tipo_vehiculo = django_filters.ChoiceFilter(choices=TipoVehiculo.choices)

    # Rangos de precio
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')

    # Rangos de ano
    anio_min = django_filters.NumberFilter(field_name='anio', lookup_expr='gte')
    anio_max = django_filters.NumberFilter(field_name='anio', lookup_expr='lte')

    # Rangos de km
    km_min = django_filters.NumberFilter(field_name='km', lookup_expr='gte')
    km_max = django_filters.NumberFilter(field_name='km', lookup_expr='lte')

    # Filtros exactos por FK
    marca = django_filters.NumberFilter(field_name='marca_id')
    modelo = django_filters.NumberFilter(field_name='modelo_id')
    combustible = django_filters.NumberFilter(field_name='combustible_id')
    caja = django_filters.NumberFilter(field_name='caja_id')
    estado = django_filters.NumberFilter(field_name='estado_id')
    condicion = django_filters.NumberFilter(field_name='condicion_id')
    moneda = django_filters.NumberFilter(field_name='moneda_id')
    segmento = django_filters.NumberFilter(method='filter_segmento')
    vendedor = django_filters.NumberFilter(field_name='vendedor_dueno_id')

    # Filtros booleanos
    vendido = django_filters.BooleanFilter()
    reservado = django_filters.BooleanFilter()
    mostrar_en_web = django_filters.BooleanFilter()
    destacar_en_web = django_filters.BooleanFilter()
    oportunidad = django_filters.BooleanFilter()
    publicado_en_ml = django_filters.BooleanFilter()
    vtv = django_filters.BooleanFilter()

    # Filtro de disponibilidad
    disponible = django_filters.BooleanFilter(method='filter_disponible')

    class Meta:
        model = Vehiculo
        fields = []

    def filter_segmento(self, queryset, name, value):
        """Filtra por segmento1 o segmento2."""
        return queryset.filter(
            models.Q(segmento1_id=value) | models.Q(segmento2_id=value)
        )

    def filter_disponible(self, queryset, name, value):
        """Filtra vehiculos disponibles (no vendidos, no reservados, no eliminados)."""
        if value:
            return queryset.filter(
                vendido=False,
                reservado=False,
                deleted_at__isnull=True
            )
        return queryset
