from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Consulta
from .serializers import (
    ConsultaSerializer,
    ConsultaListSerializer,
    ConsultaCreateSerializer,
)
from .filters import ConsultaFilter


class ConsultaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar consultas de clientes.

    Endpoints:
    - GET /api/consultas/ - Listar consultas (staff)
    - POST /api/consultas/ - Crear consulta (publico)
    - GET /api/consultas/{id}/ - Detalle consulta (staff)
    - PUT /api/consultas/{id}/ - Actualizar consulta (staff)
    - PATCH /api/consultas/{id}/ - Actualizar parcial (staff)
    - DELETE /api/consultas/{id}/ - Eliminar consulta (staff)

    Acciones extra:
    - PATCH /api/consultas/{id}/marcar-leida/ - Marcar como leida
    - PATCH /api/consultas/{id}/marcar-atendida/ - Marcar como atendida

    Filtros:
    - ?tipo=consulta|reserva
    - ?vehiculo=1
    - ?leida=true|false
    - ?atendida=true|false
    - ?pendientes=true
    - ?search=texto (nombre, email)
    - ?ordering=-created_at
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConsultaFilter
    search_fields = ['nombre', 'email', 'telefono', 'vehiculo__patente']
    ordering_fields = ['created_at', 'tipo', 'leida', 'atendida']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        POST (create) es publico para que clientes envien consultas.
        El resto de acciones requieren autenticacion (staff).
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Retorna queryset optimizado con select_related.
        """
        return Consulta.objects.select_related(
            'vehiculo',
            'vehiculo__marca',
            'vehiculo__modelo',
            'atendida_por',
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return ConsultaCreateSerializer
        if self.action == 'list':
            return ConsultaListSerializer
        return ConsultaSerializer

    # =========================================================================
    # ACCIONES EXTRA
    # =========================================================================

    @action(detail=True, methods=['patch'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        """Marca la consulta como leida."""
        consulta = self.get_object()
        consulta.marcar_leida()
        serializer = ConsultaSerializer(consulta, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-atendida')
    def marcar_atendida(self, request, pk=None):
        """Marca la consulta como atendida por el usuario actual."""
        consulta = self.get_object()
        consulta.marcar_atendida(usuario=request.user)
        serializer = ConsultaSerializer(consulta, context={'request': request})
        return Response(serializer.data)
