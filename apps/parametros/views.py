from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Caja, Combustible, Condicion, Estado, Iva,
    Localidad, Moneda, Segmento, Marca, Modelo
)
from .serializers import (
    CajaSerializer, CombustibleSerializer, CondicionSerializer,
    EstadoSerializer, IvaSerializer, LocalidadSerializer,
    MonedaSerializer, SegmentoSerializer, MarcaSerializer,
    MarcaConModelosSerializer, ModeloSerializer
)


class ParametroBaseViewSet(viewsets.ModelViewSet):
    """ViewSet base para parámetros con CRUD completo"""
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'orden', 'created_at']
    ordering = ['orden', 'nombre']


class CajaViewSet(ParametroBaseViewSet):
    queryset = Caja.objects.all()
    serializer_class = CajaSerializer


class CombustibleViewSet(ParametroBaseViewSet):
    queryset = Combustible.objects.all()
    serializer_class = CombustibleSerializer


class CondicionViewSet(ParametroBaseViewSet):
    queryset = Condicion.objects.all()
    serializer_class = CondicionSerializer


class EstadoViewSet(ParametroBaseViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer


class IvaViewSet(ParametroBaseViewSet):
    queryset = Iva.objects.all()
    serializer_class = IvaSerializer


class LocalidadViewSet(ParametroBaseViewSet):
    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer


class MonedaViewSet(ParametroBaseViewSet):
    queryset = Moneda.objects.all()
    serializer_class = MonedaSerializer


class SegmentoViewSet(ParametroBaseViewSet):
    queryset = Segmento.objects.all()
    serializer_class = SegmentoSerializer


class MarcaViewSet(ParametroBaseViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MarcaConModelosSerializer
        return MarcaSerializer


class ModeloViewSet(ParametroBaseViewSet):
    queryset = Modelo.objects.select_related('marca').all()
    serializer_class = ModeloSerializer
    filterset_fields = ['activo', 'marca']
    search_fields = ['nombre', 'marca__nombre']
