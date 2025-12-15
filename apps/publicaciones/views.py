from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import PublicacionVehiculo, EstadoPublicacion, TipoVehiculo
from .serializers import (
    PublicacionCreateSerializer,
    PublicacionListSerializer,
    PublicacionDetailSerializer,
    PublicacionUpdateSerializer,
)
from .filters import PublicacionFilter


class TiposVehiculoView(viewsets.ViewSet):
    """
    Vista para obtener los tipos de vehiculo disponibles.
    Publico para los filtros del frontend.
    """
    permission_classes = [AllowAny]

    def list(self, request):
        tipos = [
            {'value': choice[0], 'label': choice[1]}
            for choice in TipoVehiculo.choices
        ]
        return Response(tipos)


class PublicacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar publicaciones de vehiculos.

    - POST (create): Publico - clientes pueden enviar publicaciones
    - GET/PUT/PATCH/DELETE: Requieren autenticacion (staff)
    """
    queryset = PublicacionVehiculo.objects.select_related(
        'marca', 'modelo', 'revisada_por'
    ).prefetch_related('imagenes').all()

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PublicacionFilter
    search_fields = ['nombre', 'email', 'telefono', 'marca__nombre', 'modelo__nombre']
    ordering_fields = ['created_at', 'estado', 'nombre']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        """POST (create) es publico, el resto requiere autenticacion."""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return PublicacionCreateSerializer
        if self.action == 'list':
            return PublicacionListSerializer
        if self.action in ['update', 'partial_update']:
            return PublicacionUpdateSerializer
        return PublicacionDetailSerializer

    @action(detail=True, methods=['patch'], url_path='marcar-vista')
    def marcar_vista(self, request, pk=None):
        """Marca una publicacion como vista."""
        publicacion = self.get_object()

        publicacion.estado = EstadoPublicacion.VISTA
        publicacion.revisada_por = request.user
        publicacion.fecha_revision = timezone.now()
        publicacion.save()

        serializer = PublicacionDetailSerializer(publicacion, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-eliminada')
    def marcar_eliminada(self, request, pk=None):
        """Marca una publicacion como eliminada (soft delete)."""
        publicacion = self.get_object()

        publicacion.estado = EstadoPublicacion.ELIMINADA
        publicacion.revisada_por = request.user
        publicacion.fecha_revision = timezone.now()

        # Guardar nota si viene en el request
        notas = request.data.get('notas_staff', '')
        if notas:
            publicacion.notas_staff = notas

        publicacion.save()

        serializer = PublicacionDetailSerializer(publicacion, context={'request': request})
        return Response(serializer.data)
