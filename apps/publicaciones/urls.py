from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PublicacionViewSet, TiposVehiculoView

app_name = 'publicaciones'

router = DefaultRouter()
router.register(r'', PublicacionViewSet, basename='publicacion')

urlpatterns = [
    path('tipos-vehiculo/', TiposVehiculoView.as_view({'get': 'list'}), name='tipos-vehiculo'),
    path('', include(router.urls)),
]
