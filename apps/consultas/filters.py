import django_filters

from .models import Consulta


class ConsultaFilter(django_filters.FilterSet):
    """Filtros avanzados para consultas."""

    # Filtros exactos
    tipo = django_filters.CharFilter(field_name='tipo')
    vehiculo = django_filters.NumberFilter(field_name='vehiculo_id')

    # Filtros booleanos
    leida = django_filters.BooleanFilter()
    atendida = django_filters.BooleanFilter()

    # Filtro de rango de fechas
    fecha_desde = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    fecha_hasta = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    # Filtro combinado: pendientes (no atendidas)
    pendientes = django_filters.BooleanFilter(method='filter_pendientes')

    class Meta:
        model = Consulta
        fields = []

    def filter_pendientes(self, queryset, name, value):
        """Filtra consultas pendientes (no atendidas)."""
        if value:
            return queryset.filter(atendida=False)
        return queryset
