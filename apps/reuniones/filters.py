import django_filters
from django.utils import timezone
from datetime import timedelta

from .models import Reunion


class ReunionFilter(django_filters.FilterSet):
    """
    Filtros avanzados para reuniones.
    """
    # Filtro por fecha exacta
    fecha = django_filters.DateFilter(field_name='fecha')

    # Filtros por rango de fechas
    fecha_desde = django_filters.DateFilter(
        field_name='fecha',
        lookup_expr='gte'
    )
    fecha_hasta = django_filters.DateFilter(
        field_name='fecha',
        lookup_expr='lte'
    )

    # Filtros por ubicacion
    ubicacion = django_filters.ChoiceFilter(
        choices=Reunion.Ubicacion.choices
    )

    # Filtros por estado
    estado = django_filters.ChoiceFilter(
        choices=Reunion.Estado.choices
    )

    # Filtros por FK
    coordinador = django_filters.NumberFilter(field_name='coordinador')
    vendedor = django_filters.NumberFilter(field_name='vendedor')
    vehiculo = django_filters.NumberFilter(field_name='vehiculo')

    # Filtro personalizado: reuniones de hoy
    hoy = django_filters.BooleanFilter(method='filter_hoy')

    # Filtro personalizado: reuniones pendientes
    pendientes = django_filters.BooleanFilter(method='filter_pendientes')

    class Meta:
        model = Reunion
        fields = [
            'fecha',
            'fecha_desde',
            'fecha_hasta',
            'ubicacion',
            'estado',
            'coordinador',
            'vendedor',
            'vehiculo',
        ]

    def filter_hoy(self, queryset, name, value):
        """Filtrar reuniones de hoy."""
        if value:
            hoy = timezone.localdate()
            return queryset.filter(fecha=hoy)
        return queryset

    def filter_pendientes(self, queryset, name, value):
        """Filtrar reuniones pendientes."""
        if value:
            return queryset.filter(estado=Reunion.Estado.PENDIENTE)
        return queryset
