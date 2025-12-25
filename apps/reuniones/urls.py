from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ReunionViewSet

router = DefaultRouter()
router.register(r'', ReunionViewSet, basename='reunion')

urlpatterns = [
    path('', include(router.urls)),
]
