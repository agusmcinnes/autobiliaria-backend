from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ReservaViewSet

app_name = 'reservas'

router = DefaultRouter()
router.register('', ReservaViewSet, basename='reserva')

urlpatterns = [
    path('', include(router.urls)),
]
