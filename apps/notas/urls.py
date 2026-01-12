from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotaDiariaViewSet

app_name = 'notas'

router = DefaultRouter()
router.register('', NotaDiariaViewSet, basename='notas')

urlpatterns = [
    path('', include(router.urls)),
]
