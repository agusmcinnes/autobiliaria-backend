import django_filters

from .models import PublicacionVehiculo, EstadoPublicacion, TipoVehiculo


class PublicacionFilter(django_filters.FilterSet):
    """Filtros para publicaciones de vehiculos."""

    # Filtros por estado
    estado = django_filters.ChoiceFilter(choices=EstadoPublicacion.choices)
    pendientes = django_filters.BooleanFilter(method='filter_pendientes')

    # Filtros por tipo vehiculo
    tipo_vehiculo = django_filters.ChoiceFilter(choices=TipoVehiculo.choices)

    # Filtros por FK
    marca = django_filters.NumberFilter(field_name='marca_id')
    modelo = django_filters.NumberFilter(field_name='modelo_id')

    # Filtros por fecha
    fecha_desde = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    fecha_hasta = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = PublicacionVehiculo
        fields = []

    def filter_pendientes(self, queryset, name, value):
        """Filtra solo publicaciones pendientes."""
        if value:
            return queryset.filter(estado=EstadoPublicacion.PENDIENTE)
        return queryset
