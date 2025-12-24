from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import Reunion
from .serializers import (
    ReunionSerializer,
    ReunionListSerializer,
    ReunionCreateSerializer,
    ReunionEstadisticasSerializer,
)
from .filters import ReunionFilter


class ReunionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reuniones.

    Endpoints:
    - GET /api/reuniones/ - Listar reuniones
    - POST /api/reuniones/ - Crear reunion
    - GET /api/reuniones/{id}/ - Detalle reunion
    - PUT /api/reuniones/{id}/ - Actualizar reunion
    - PATCH /api/reuniones/{id}/ - Actualizar parcial
    - DELETE /api/reuniones/{id}/ - Eliminar reunion

    Acciones extra:
    - GET /api/reuniones/estadisticas/ - Conteo de reuniones
    - GET /api/reuniones/por-fecha/{fecha}/ - Reuniones de un dia
    - PATCH /api/reuniones/{id}/marcar-completada/ - Marcar como completada
    - PATCH /api/reuniones/{id}/marcar-cancelada/ - Marcar como cancelada

    Filtros:
    - ?fecha=2024-12-24
    - ?fecha_desde=X&fecha_hasta=Y
    - ?ubicacion=falucho|playa_grande
    - ?estado=pendiente|completada|cancelada
    - ?coordinador=1
    - ?vendedor=3
    - ?vehiculo=5
    - ?hoy=true
    - ?pendientes=true
    - ?search=texto
    - ?ordering=fecha,hora
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReunionFilter
    search_fields = ['comprador_nombre', 'vendedor_texto', 'notas']
    ordering_fields = ['fecha', 'hora', 'created_at', 'ubicacion', 'estado']
    ordering = ['fecha', 'hora']

    def get_queryset(self):
        """
        Retorna queryset optimizado con select_related.
        """
        return Reunion.objects.select_related(
            'coordinador',
            'vendedor',
            'vehiculo',
            'vehiculo__marca',
            'vehiculo__modelo',
            'creada_por',
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return ReunionCreateSerializer
        if self.action == 'list':
            return ReunionListSerializer
        if self.action == 'estadisticas':
            return ReunionEstadisticasSerializer
        return ReunionSerializer

    # =========================================================================
    # ACCIONES EXTRA
    # =========================================================================

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Retorna el conteo de reuniones para hoy, manana, semana y mes.
        Solo cuenta reuniones pendientes.
        """
        hoy = timezone.localdate()
        manana = hoy + timedelta(days=1)

        # Inicio de la semana (lunes)
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)

        # Inicio y fin del mes
        inicio_mes = hoy.replace(day=1)
        if hoy.month == 12:
            fin_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fin_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)

        queryset = self.get_queryset()

        stats = {
            'hoy': queryset.filter(
                fecha=hoy,
                estado=Reunion.Estado.PENDIENTE
            ).count(),
            'manana': queryset.filter(
                fecha=manana,
                estado=Reunion.Estado.PENDIENTE
            ).count(),
            'semana': queryset.filter(
                fecha__gte=inicio_semana,
                fecha__lte=fin_semana,
                estado=Reunion.Estado.PENDIENTE
            ).count(),
            'mes': queryset.filter(
                fecha__gte=inicio_mes,
                fecha__lte=fin_mes,
                estado=Reunion.Estado.PENDIENTE
            ).count(),
        }

        serializer = ReunionEstadisticasSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='por-fecha/(?P<fecha>[0-9]{4}-[0-9]{2}-[0-9]{2})')
    def por_fecha(self, request, fecha=None):
        """
        Retorna todas las reuniones de una fecha especifica.
        """
        queryset = self.get_queryset().filter(fecha=fecha).order_by('hora')
        serializer = ReunionListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-completada')
    def marcar_completada(self, request, pk=None):
        """Marca la reunion como completada."""
        reunion = self.get_object()
        reunion.marcar_completada()
        serializer = ReunionSerializer(reunion, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-cancelada')
    def marcar_cancelada(self, request, pk=None):
        """Marca la reunion como cancelada."""
        reunion = self.get_object()
        reunion.marcar_cancelada()
        serializer = ReunionSerializer(reunion, context={'request': request})
        return Response(serializer.data)
