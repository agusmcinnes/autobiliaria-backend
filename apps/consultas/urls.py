from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ConsultaViewSet

app_name = 'consultas'

router = DefaultRouter()
router.register('', ConsultaViewSet, basename='consulta')

urlpatterns = [
    path('', include(router.urls)),
]
