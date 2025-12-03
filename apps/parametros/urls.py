from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CajaViewSet, CombustibleViewSet, CondicionViewSet,
    EstadoViewSet, IvaViewSet, LocalidadViewSet,
    MonedaViewSet, SegmentoViewSet, MarcaViewSet, ModeloViewSet
)

app_name = 'parametros'

router = DefaultRouter()
router.register('cajas', CajaViewSet, basename='caja')
router.register('combustibles', CombustibleViewSet, basename='combustible')
router.register('condiciones', CondicionViewSet, basename='condicion')
router.register('estados', EstadoViewSet, basename='estado')
router.register('ivas', IvaViewSet, basename='iva')
router.register('localidades', LocalidadViewSet, basename='localidad')
router.register('monedas', MonedaViewSet, basename='moneda')
router.register('segmentos', SegmentoViewSet, basename='segmento')
router.register('marcas', MarcaViewSet, basename='marca')
router.register('modelos', ModeloViewSet, basename='modelo')

urlpatterns = [
    path('', include(router.urls)),
]
