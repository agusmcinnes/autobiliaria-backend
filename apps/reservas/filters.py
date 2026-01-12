import django_filters
from django.db import models

from .models import Reserva, TipoOperacion, EstadoReserva


class ReservaFilter(django_filters.FilterSet):
    """Filtros avanzados para reservas."""

    # Por tipo de operacion
    tipo_operacion = django_filters.ChoiceFilter(choices=TipoOperacion.choices)

    # Por estado
    estado = django_filters.ChoiceFilter(choices=EstadoReserva.choices)

    # Por vehiculo
    vehiculo = django_filters.NumberFilter(field_name='vehiculo_id')

    # Por cliente
    cliente = django_filters.NumberFilter(field_name='cliente_id')

    # Por vendedor (busca en vendedor_1 o vendedor_2)
    vendedor = django_filters.NumberFilter(method='filter_vendedor')

    # Por cliente DNI
    cliente_dni = django_filters.CharFilter(
        field_name='cliente__dni_cuit',
        lookup_expr='icontains'
    )

    # Por fechas de creacion
    fecha_desde = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte'
    )
    fecha_hasta = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte'
    )

    # Por fechas de entrega (filtro principal para reportes)
    mes_entrega = django_filters.NumberFilter(
        field_name='fecha_entrega_pactada',
        lookup_expr='month'
    )
    anio_entrega = django_filters.NumberFilter(
        field_name='fecha_entrega_pactada',
        lookup_expr='year'
    )
    fecha_entrega_desde = django_filters.DateFilter(
        field_name='fecha_entrega_pactada',
        lookup_expr='gte'
    )
    fecha_entrega_hasta = django_filters.DateFilter(
        field_name='fecha_entrega_pactada',
        lookup_expr='lte'
    )

    # Por monto
    monto_min = django_filters.NumberFilter(
        field_name='precio_venta',
        lookup_expr='gte'
    )
    monto_max = django_filters.NumberFilter(
        field_name='precio_venta',
        lookup_expr='lte'
    )

    # Booleanos
    entregado = django_filters.BooleanFilter()
    transferido = django_filters.BooleanFilter()
    a_reestructurar = django_filters.BooleanFilter()

    # Filtros especiales
    pendientes = django_filters.BooleanFilter(method='filter_pendientes')
    activas = django_filters.BooleanFilter(method='filter_activas')

    class Meta:
        model = Reserva
        fields = []

    def filter_vendedor(self, queryset, name, value):
        """Filtra por vendedor_1 o vendedor_2."""
        return queryset.filter(
            models.Q(vendedor_1_id=value) | models.Q(vendedor_2_id=value)
        )

    def filter_pendientes(self, queryset, name, value):
        """Filtra reservas pendientes de entrega."""
        if value:
            return queryset.filter(estado=EstadoReserva.PENDING)
        return queryset

    def filter_activas(self, queryset, name, value):
        """Filtra reservas activas (no canceladas ni reestructurando)."""
        if value:
            return queryset.exclude(
                estado__in=[
                    EstadoReserva.CANCELLED,
                    EstadoReserva.CANCELLED_LOST_DEPOSIT,
                    EstadoReserva.RESTRUCTURING,
                ]
            )
        return queryset
