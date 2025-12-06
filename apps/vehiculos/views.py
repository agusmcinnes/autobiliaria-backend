from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch

from .models import Vehiculo, ImagenVehiculo
from .serializers import (
    VehiculoSerializer,
    VehiculoListSerializer,
    VehiculoCreateSerializer,
    ImagenVehiculoSerializer,
)
from .filters import VehiculoFilter


class VehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar vehiculos.

    Endpoints:
    - GET /api/vehiculos/ - Listar vehiculos
    - POST /api/vehiculos/ - Crear vehiculo
    - GET /api/vehiculos/{id}/ - Detalle vehiculo
    - PUT /api/vehiculos/{id}/ - Actualizar vehiculo
    - PATCH /api/vehiculos/{id}/ - Actualizar parcial
    - DELETE /api/vehiculos/{id}/ - Soft delete vehiculo

    Acciones extra:
    - POST /api/vehiculos/{id}/imagenes/ - Subir imagen
    - DELETE /api/vehiculos/{id}/imagenes/{imagen_id}/ - Eliminar imagen
    - POST /api/vehiculos/{id}/restaurar/ - Restaurar vehiculo eliminado
    - PATCH /api/vehiculos/{id}/marcar-vendido/ - Marcar como vendido
    - PATCH /api/vehiculos/{id}/marcar-reservado/ - Marcar como reservado
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VehiculoFilter
    search_fields = ['patente', 'marca__nombre', 'modelo__nombre', 'version', 'color']
    ordering_fields = ['precio', 'anio', 'km', 'created_at', 'marca__nombre']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        GET (list y retrieve) son públicos para que la web muestre los vehículos.
        El resto de acciones requieren autenticación.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Retorna queryset optimizado con select_related y prefetch_related.
        Por defecto excluye vehiculos soft-deleted.
        """
        queryset = Vehiculo.objects.select_related(
            'marca',
            'modelo',
            'segmento1',
            'segmento2',
            'combustible',
            'caja',
            'estado',
            'condicion',
            'moneda',
            'vendedor_dueno',
            'cargado_por',
        ).prefetch_related(
            Prefetch(
                'imagenes',
                queryset=ImagenVehiculo.objects.order_by('orden', 'created_at')
            )
        )

        # Por defecto excluir eliminados, a menos que se pida explicitamente
        include_deleted = self.request.query_params.get('include_deleted', 'false')
        if include_deleted.lower() != 'true':
            queryset = queryset.filter(deleted_at__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return VehiculoListSerializer
        if self.action == 'create':
            return VehiculoCreateSerializer
        return VehiculoSerializer

    def perform_destroy(self, instance):
        """Soft delete en lugar de eliminar."""
        instance.soft_delete()

    # =========================================================================
    # ACCIONES EXTRA
    # =========================================================================

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def imagenes(self, request, pk=None):
        """
        Sube una nueva imagen al vehiculo.
        Maximo 15 imagenes por vehiculo.
        """
        vehiculo = self.get_object()

        # Validar limite de imagenes
        if vehiculo.imagenes.count() >= 15:
            return Response(
                {'error': 'El vehiculo ya tiene el maximo de 15 imagenes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ImagenVehiculoSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(vehiculo=vehiculo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['delete'],
        url_path='imagenes/(?P<imagen_id>[^/.]+)'
    )
    def eliminar_imagen(self, request, pk=None, imagen_id=None):
        """Elimina una imagen del vehiculo."""
        vehiculo = self.get_object()
        try:
            imagen = vehiculo.imagenes.get(pk=imagen_id)
            imagen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ImagenVehiculo.DoesNotExist:
            return Response(
                {'error': 'Imagen no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        """Restaura un vehiculo soft-deleted."""
        # Obtener incluyendo eliminados
        try:
            vehiculo = Vehiculo.objects.get(pk=pk)
        except Vehiculo.DoesNotExist:
            return Response(
                {'error': 'Vehiculo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not vehiculo.is_deleted:
            return Response(
                {'error': 'El vehiculo no esta eliminado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        vehiculo.restore()
        serializer = VehiculoSerializer(vehiculo, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-vendido')
    def marcar_vendido(self, request, pk=None):
        """Marca el vehiculo como vendido."""
        vehiculo = self.get_object()
        vehiculo.vendido = True
        vehiculo.reservado = False
        vehiculo.mostrar_en_web = False
        vehiculo.save(update_fields=['vendido', 'reservado', 'mostrar_en_web', 'updated_at'])
        serializer = VehiculoSerializer(vehiculo, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-reservado')
    def marcar_reservado(self, request, pk=None):
        """Marca/desmarca el vehiculo como reservado."""
        vehiculo = self.get_object()
        vehiculo.reservado = not vehiculo.reservado
        vehiculo.save(update_fields=['reservado', 'updated_at'])
        serializer = VehiculoSerializer(vehiculo, context={'request': request})
        return Response(serializer.data)
