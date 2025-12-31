from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MLConnectionStatusView,
    MLAuthURLView,
    MLAuthCallbackView,
    MLDisconnectView,
    MLPublicationViewSet,
    MLSyncView,
    MLStatisticsView,
    MLSyncLogViewSet,
)

app_name = 'mercadolibre'

router = DefaultRouter()
router.register(r'publications', MLPublicationViewSet, basename='ml-publications')
router.register(r'logs', MLSyncLogViewSet, basename='ml-logs')

urlpatterns = [
    # Estado de conexion
    path('status/', MLConnectionStatusView.as_view(), name='ml-status'),

    # OAuth2
    path('auth/url/', MLAuthURLView.as_view(), name='ml-auth-url'),
    path('auth/callback/', MLAuthCallbackView.as_view(), name='ml-auth-callback'),

    # Desconectar
    path('disconnect/', MLDisconnectView.as_view(), name='ml-disconnect'),

    # Sincronizacion
    path('sync/', MLSyncView.as_view(), name='ml-sync'),

    # Estadisticas
    path('statistics/', MLStatisticsView.as_view(), name='ml-statistics'),

    # ViewSets (publications, logs)
    path('', include(router.urls)),
]
