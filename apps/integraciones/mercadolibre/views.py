"""
Views para la API de Mercado Libre.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from .models import MLCredential, MLPublication, MLSyncLog


from .serializers import (
    MLConnectionStatusSerializer,
    MLAuthURLSerializer,
    MLPublicationListSerializer,
    MLPublicationDetailSerializer,
    MLPublicationLinkSerializer,
    MLPublicationStatusSerializer,
    MLSyncLogSerializer,
    MLSyncResultSerializer,
    MLStatisticsSerializer,
)
from .services import (
    MLClient,
    MLSyncService,
    MLAPIError,
    get_ml_auth_url,
    exchange_code_for_token,
)

logger = logging.getLogger(__name__)


class MLPublicationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MLConnectionStatusView(APIView):
    """
    GET /api/mercadolibre/status/
    Retorna el estado de conexion con Mercado Libre.
    Renueva el token automaticamente si esta por expirar.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            credential = MLCredential.objects.get(is_active=True)

            # Renovar token automáticamente si es necesario
            if credential.needs_refresh and not credential.is_token_expired:
                try:
                    client = MLClient(credential)
                    # El cliente ya renueva en __init__ si needs_refresh
                    credential.refresh_from_db()
                    logger.info(f"Token renovado automáticamente para {credential.ml_nickname}")
                except Exception as e:
                    logger.warning(f"No se pudo renovar token automáticamente: {e}")

            data = {
                'connected': True,
                'ml_user_id': credential.ml_user_id,
                'ml_nickname': credential.ml_nickname,
                'is_active': credential.is_active,
                'token_expires_at': credential.expires_at,
                'token_expired': credential.is_token_expired,
                'needs_reauthorization': not credential.is_active or credential.is_token_expired,
                'connected_at': credential.created_at,
            }
        except MLCredential.DoesNotExist:
            data = {
                'connected': False,
                'ml_user_id': None,
                'ml_nickname': None,
                'is_active': False,
                'token_expires_at': None,
                'token_expired': True,
                'needs_reauthorization': True,
                'connected_at': None,
            }

        serializer = MLConnectionStatusSerializer(data)
        return Response(serializer.data)


class MLAuthURLView(APIView):
    """
    POST /api/mercadolibre/auth/url/
    Genera la URL de autorizacion OAuth2.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_url, state = get_ml_auth_url()

        # Guardar state en sesion para validar callback
        request.session['ml_oauth_state'] = state
        request.session['ml_oauth_user_id'] = request.user.id

        serializer = MLAuthURLSerializer({
            'auth_url': auth_url,
            'state': state,
        })
        return Response(serializer.data)


class MLAuthCallbackView(APIView):
    """
    GET /api/mercadolibre/auth/callback/
    Callback de OAuth2 de Mercado Libre.
    Recibe el codigo de autorizacion y lo intercambia por tokens.
    """
    permission_classes = [AllowAny]  # ML redirige sin auth

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        # URL de redireccion al frontend
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        success_url = f"{frontend_url}/admin/mercadolibre?connected=true"
        error_url = f"{frontend_url}/admin/mercadolibre?error="

        if error:
            logger.error(f"Error en OAuth ML: {error}")
            return redirect(f"{error_url}authorization_denied")

        if not code:
            return redirect(f"{error_url}no_code")

        # Validar state (opcional pero recomendado)
        # saved_state = request.session.get('ml_oauth_state')
        # if state != saved_state:
        #     return redirect(f"{error_url}invalid_state")

        try:
            # Intercambiar codigo por tokens
            token_data = exchange_code_for_token(code)

            # Obtener info del usuario de ML
            access_token = token_data['access_token']
            ml_user_id = str(token_data['user_id'])

            # Obtener nickname del usuario
            import requests
            user_response = requests.get(
                f"https://api.mercadolibre.com/users/{ml_user_id}",
                headers={'Authorization': f'Bearer {access_token}'}
            )
            ml_nickname = ''
            if user_response.status_code == 200:
                ml_nickname = user_response.json().get('nickname', '')

            # Obtener usuario del sistema (usar el primero activo si no hay sesion)
            from apps.usuarios.models import Usuario
            user_id = request.session.get('ml_oauth_user_id')
            logger.info(f"ML OAuth callback - session user_id: {user_id}")

            if user_id:
                try:
                    user = Usuario.objects.get(id=user_id)
                except Usuario.DoesNotExist:
                    logger.error(f"Usuario con id {user_id} no existe")
                    user = None
            else:
                user = Usuario.objects.filter(is_active=True).first()
                logger.info(f"Usando primer usuario activo: {user}")

            if not user:
                logger.error("No hay usuarios activos en el sistema para vincular la cuenta ML")
                return redirect(f"{error_url}no_user_available")

            # Desactivar otras credenciales activas (de otros usuarios)
            MLCredential.objects.filter(is_active=True).exclude(user=user).update(is_active=False)

            # Crear o actualizar credencial del usuario
            credential, created = MLCredential.objects.update_or_create(
                user=user,
                defaults={
                    'ml_user_id': ml_user_id,
                    'ml_nickname': ml_nickname,
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data['refresh_token'],
                    'expires_at': timezone.now() + timedelta(seconds=token_data['expires_in']),
                    'scope': token_data.get('scope', ''),
                    'is_active': True,
                }
            )

            # Log
            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.REFRESH_TOKEN,
                user=user,
                success=True,
                response_data={'message': 'Cuenta conectada exitosamente'}
            )

            logger.info(f"Cuenta ML conectada: {ml_nickname} ({ml_user_id})")
            return redirect(success_url)

        except MLAPIError as e:
            logger.error(f"Error intercambiando codigo ML: {e}")
            return redirect(f"{error_url}token_exchange_failed")
        except Exception as e:
            logger.exception(f"Error inesperado en callback ML: {e}")
            return redirect(f"{error_url}unexpected_error")


class MLDisconnectView(APIView):
    """
    DELETE /api/mercadolibre/disconnect/
    Desconecta la cuenta de Mercado Libre.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        count = MLCredential.objects.filter(is_active=True).update(is_active=False)

        if count > 0:
            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.REFRESH_TOKEN,
                user=request.user,
                success=True,
                response_data={'message': 'Cuenta desconectada'}
            )
            return Response({'detail': 'Cuenta de Mercado Libre desconectada.'})

        return Response(
            {'detail': 'No hay cuenta conectada.'},
            status=status.HTTP_404_NOT_FOUND
        )


class MLPublicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar publicaciones de Mercado Libre.

    list:   GET    /api/mercadolibre/publications/
    create: POST   /api/mercadolibre/publications/ (no implementado, usar sync)
    retrieve: GET  /api/mercadolibre/publications/{id}/
    update: PUT    /api/mercadolibre/publications/{id}/ (no implementado)
    destroy: DELETE /api/mercadolibre/publications/{id}/ (solo elimina del sistema)
    """
    permission_classes = [IsAuthenticated]
    pagination_class = MLPublicationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ml_status', 'vehiculo', 'created_from_system']
    search_fields = ['ml_title', 'ml_item_id', 'patente_ml', 'marca_ml', 'modelo_ml']
    ordering_fields = ['ml_price', 'last_synced', 'created_at', 'ml_status']
    ordering = ['-last_synced']

    def get_queryset(self):
        queryset = MLPublication.objects.select_related('vehiculo').all()

        # Filtro personalizado: linked/unlinked
        linked = self.request.query_params.get('linked')
        if linked == 'true':
            queryset = queryset.filter(vehiculo__isnull=False)
        elif linked == 'false':
            queryset = queryset.filter(vehiculo__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return MLPublicationListSerializer
        return MLPublicationDetailSerializer

    @action(detail=True, methods=['post'])
    def link(self, request, pk=None):
        """
        POST /api/mercadolibre/publications/{id}/link/
        Vincula una publicacion a un vehiculo.
        """
        from apps.vehiculos.models import Vehiculo

        publication = self.get_object()
        serializer = MLPublicationLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehiculo_id = serializer.validated_data['vehiculo_id']

        try:
            vehiculo = Vehiculo.objects.get(id=vehiculo_id, deleted_at__isnull=True)
        except Vehiculo.DoesNotExist:
            return Response(
                {'detail': 'Vehiculo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar que el vehiculo no tenga otra publicacion vinculada
        if MLPublication.objects.filter(vehiculo=vehiculo).exclude(pk=publication.pk).exists():
            return Response(
                {'detail': 'El vehiculo ya tiene una publicacion vinculada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        publication.vehiculo = vehiculo
        publication.save()

        # Actualizar datos de ML en el vehiculo
        vehiculo.publicado_en_ml = True
        vehiculo.ml_item_id = publication.ml_item_id
        vehiculo.ml_estado = publication.ml_status
        vehiculo.ml_permalink = publication.ml_permalink
        vehiculo.ml_fecha_sync = publication.last_synced
        vehiculo.save()

        return Response(MLPublicationDetailSerializer(publication).data)

    @action(detail=True, methods=['post'])
    def unlink(self, request, pk=None):
        """
        POST /api/mercadolibre/publications/{id}/unlink/
        Desvincula una publicacion de su vehiculo.
        """
        publication = self.get_object()

        if not publication.vehiculo:
            return Response(
                {'detail': 'La publicacion no esta vinculada a ningun vehiculo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehiculo = publication.vehiculo

        # Limpiar datos de ML en el vehiculo
        vehiculo.publicado_en_ml = False
        vehiculo.ml_item_id = None
        vehiculo.ml_estado = ''
        vehiculo.ml_permalink = ''
        vehiculo.ml_error = ''
        vehiculo.save()

        publication.vehiculo = None
        publication.save()

        return Response(MLPublicationDetailSerializer(publication).data)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        """
        PATCH /api/mercadolibre/publications/{id}/status/
        Cambia el estado de una publicacion (pausar, activar, cerrar).
        """
        publication = self.get_object()
        serializer = MLPublicationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']

        try:
            credential = MLCredential.objects.get(is_active=True)
            sync_service = MLSyncService(credential)
            publication = sync_service.update_publication_status(
                publication,
                new_status,
                user=request.user
            )
            return Response(MLPublicationDetailSerializer(publication).data)

        except MLCredential.DoesNotExist:
            return Response(
                {'detail': 'No hay cuenta de Mercado Libre conectada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except MLAPIError as e:
            return Response(
                {'detail': str(e), 'ml_error': e.response_data},
                status=status.HTTP_400_BAD_REQUEST
            )


class MLSyncView(APIView):
    """
    POST /api/mercadolibre/sync/
    Sincroniza publicaciones desde Mercado Libre.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            credential = MLCredential.objects.get(is_active=True)
        except MLCredential.DoesNotExist:
            return Response(
                {'detail': 'No hay cuenta de Mercado Libre conectada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sync_service = MLSyncService(credential)
            imported, updated, linked = sync_service.sync_publications(user=request.user)

            serializer = MLSyncResultSerializer({
                'imported': imported,
                'updated': updated,
                'linked': linked,
                'total': imported + updated,
            })
            return Response(serializer.data)

        except MLAPIError as e:
            return Response(
                {'detail': str(e), 'ml_error': e.response_data},
                status=status.HTTP_400_BAD_REQUEST
            )


class MLStatisticsView(APIView):
    """
    GET /api/mercadolibre/statistics/
    Retorna estadisticas de publicaciones ML.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = MLPublication.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(ml_status='active')),
            paused=Count('id', filter=Q(ml_status='paused')),
            closed=Count('id', filter=Q(ml_status='closed')),
            linked=Count('id', filter=Q(vehiculo__isnull=False)),
            unlinked=Count('id', filter=Q(vehiculo__isnull=True)),
            from_system=Count('id', filter=Q(created_from_system=True)),
        )

        # Ultima sincronizacion
        last_sync = MLPublication.objects.order_by('-last_synced').first()

        data = {
            'total_publications': stats['total'],
            'active_publications': stats['active'],
            'paused_publications': stats['paused'],
            'closed_publications': stats['closed'],
            'linked_publications': stats['linked'],
            'unlinked_publications': stats['unlinked'],
            'created_from_system': stats['from_system'],
            'last_sync': last_sync.last_synced if last_sync else None,
        }

        serializer = MLStatisticsSerializer(data)
        return Response(serializer.data)


class MLQuotaView(APIView):
    """
    GET /api/mercadolibre/quota/
    Retorna el quota de publicaciones disponible en la cuenta de ML.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            credential = MLCredential.objects.get(is_active=True)
        except MLCredential.DoesNotExist:
            return Response(
                {'detail': 'No hay cuenta de Mercado Libre conectada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sync_service = MLSyncService(credential)
            quota_info = sync_service.get_quota(site_id='MLA')
            return Response(quota_info)

        except MLAPIError as e:
            return Response(
                {'detail': str(e), 'ml_error': e.response_data},
                status=status.HTTP_400_BAD_REQUEST
            )


class MLSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para logs de sincronizacion.
    GET /api/mercadolibre/logs/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MLSyncLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action', 'success']
    ordering = ['-created_at']

    def get_queryset(self):
        return MLSyncLog.objects.select_related(
            'publication', 'vehiculo', 'user'
        ).all()[:100]  # Limitar a ultimos 100
