from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VehiculoViewSet

app_name = 'vehiculos'

router = DefaultRouter()
router.register('', VehiculoViewSet, basename='vehiculo')

urlpatterns = [
    path('', include(router.urls)),
]
