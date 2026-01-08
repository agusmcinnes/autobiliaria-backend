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

    @action(detail=True, methods=['patch'], url_path='reordenar-imagenes')
    def reordenar_imagenes(self, request, pk=None):
        """
        Reordena las imágenes del vehículo.
        Espera: { "orden": [{ "id": 1, "orden": 0 }, { "id": 2, "orden": 1 }, ...] }
        """
        vehiculo = self.get_object()
        orden_data = request.data.get('orden', [])

        if not orden_data:
            return Response(
                {'error': 'Se requiere el campo "orden" con lista de {id, orden}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar que todas las imágenes pertenezcan al vehículo
        imagen_ids = [item['id'] for item in orden_data]
        imagenes = vehiculo.imagenes.filter(id__in=imagen_ids)

        if imagenes.count() != len(imagen_ids):
            return Response(
                {'error': 'Algunas imágenes no pertenecen a este vehículo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar orden de cada imagen
        for item in orden_data:
            vehiculo.imagenes.filter(id=item['id']).update(orden=item['orden'])

        # Retornar imágenes actualizadas
        imagenes_actualizadas = vehiculo.imagenes.order_by('orden', 'created_at')
        serializer = ImagenVehiculoSerializer(
            imagenes_actualizadas,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['patch'],
        url_path='imagenes/(?P<imagen_id>[^/.]+)/principal'
    )
    def marcar_principal(self, request, pk=None, imagen_id=None):
        """Marca una imagen como principal (quita el flag de las demás)."""
        vehiculo = self.get_object()

        try:
            imagen = vehiculo.imagenes.get(pk=imagen_id)
        except ImagenVehiculo.DoesNotExist:
            return Response(
                {'error': 'Imagen no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Quitar es_principal de todas las imágenes del vehículo
        vehiculo.imagenes.update(es_principal=False)

        # Marcar esta como principal
        imagen.es_principal = True
        imagen.save(update_fields=['es_principal'])

        # Retornar imágenes actualizadas
        imagenes_actualizadas = vehiculo.imagenes.order_by('orden', 'created_at')
        serializer = ImagenVehiculoSerializer(
            imagenes_actualizadas,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    # =========================================================================
    # ACCIONES MERCADO LIBRE
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='publicar-ml')
    def publicar_ml(self, request, pk=None):
        """
        Publica el vehiculo en Mercado Libre.
        Requiere cuenta de ML conectada.

        Body opcional:
            - title: Titulo personalizado para la publicacion
        """
        from apps.integraciones.mercadolibre.models import MLCredential
        from apps.integraciones.mercadolibre.services import MLSyncService, MLAPIError

        vehiculo = self.get_object()

        # Obtener titulo personalizado del request (opcional)
        custom_title = request.data.get('title', None)

        # Verificar que no este ya publicado
        if vehiculo.ml_item_id:
            return Response(
                {'detail': f'El vehiculo ya tiene una publicacion activa: {vehiculo.ml_item_id}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            credential = MLCredential.objects.get(is_active=True)
        except MLCredential.DoesNotExist:
            return Response(
                {'detail': 'No hay cuenta de Mercado Libre conectada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sync_service = MLSyncService(credential)
            publication = sync_service.publish_vehicle(
                vehiculo,
                user=request.user,
                custom_title=custom_title
            )

            return Response({
                'detail': 'Vehiculo publicado exitosamente en Mercado Libre.',
                'ml_item_id': publication.ml_item_id,
                'ml_permalink': publication.ml_permalink,
            })

        except MLAPIError as e:
            return Response(
                {'detail': str(e), 'ml_error': e.response_data},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], url_path='ml-status')
    def ml_status(self, request, pk=None):
        """
        Cambia el estado de la publicacion en ML (pausar/activar).
        Espera: { "status": "active" | "paused" }
        """
        from apps.integraciones.mercadolibre.models import MLCredential, MLPublication
        from apps.integraciones.mercadolibre.services import MLSyncService, MLAPIError

        vehiculo = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['active', 'paused']:
            return Response(
                {'detail': 'El estado debe ser "active" o "paused".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not vehiculo.ml_item_id:
            return Response(
                {'detail': 'El vehiculo no tiene publicacion en Mercado Libre.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            credential = MLCredential.objects.get(is_active=True)
        except MLCredential.DoesNotExist:
            return Response(
                {'detail': 'No hay cuenta de Mercado Libre conectada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            publication = MLPublication.objects.get(ml_item_id=vehiculo.ml_item_id)
            sync_service = MLSyncService(credential)
            sync_service.update_publication_status(publication, new_status, user=request.user)

            action_msg = 'activada' if new_status == 'active' else 'pausada'
            return Response({
                'detail': f'Publicacion {action_msg} exitosamente.',
                'ml_status': new_status,
            })

        except MLPublication.DoesNotExist:
            return Response(
                {'detail': 'No se encontro la publicacion en el sistema.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except MLAPIError as e:
            return Response(
                {'detail': str(e), 'ml_error': e.response_data},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'], url_path='cerrar-ml')
    def cerrar_ml(self, request, pk=None):
        """Cierra definitivamente la publicacion en Mercado Libre."""
        from apps.integraciones.mercadolibre.models import MLCredential, MLPublication
        from apps.integraciones.mercadolibre.services import MLSyncService, MLAPIError

        vehiculo = self.get_object()

        if not vehiculo.ml_item_id:
            return Response(
                {'detail': 'El vehiculo no tiene publicacion en Mercado Libre.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            credential = MLCredential.objects.get(is_active=True)
        except MLCredential.DoesNotExist:
            return Response(
                {'detail': 'No hay cuenta de Mercado Libre conectada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            publication = MLPublication.objects.get(ml_item_id=vehiculo.ml_item_id)
            sync_service = MLSyncService(credential)
            sync_service.update_publication_status(publication, 'closed', user=request.user)

            return Response({
                'detail': 'Publicacion cerrada exitosamente.',
            })

        except MLPublication.DoesNotExist:
            return Response(
                {'detail': 'No se encontro la publicacion en el sistema.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except MLAPIError as e:
            return Response(
                {'detail': str(e), 'ml_error': e.response_data},
                status=status.HTTP_400_BAD_REQUEST
            )
