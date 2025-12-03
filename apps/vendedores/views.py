from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Vendedor
from .serializers import VendedorSerializer, VendedorListSerializer


class VendedorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar vendedores.

    Endpoints:
    - GET /api/vendedores/ - Listar vendedores
    - POST /api/vendedores/ - Crear vendedor
    - GET /api/vendedores/{id}/ - Detalle vendedor
    - PUT /api/vendedores/{id}/ - Actualizar vendedor
    - PATCH /api/vendedores/{id}/ - Actualizar parcial
    - DELETE /api/vendedores/{id}/ - Eliminar vendedor

    Filtros:
    - ?activo=true|false
    - ?tiene_cartel=true|false
    - ?search=texto (busca en nombre, apellido, dni, email)
    - ?ordering=nombre|-created_at
    """
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo', 'tiene_cartel']
    search_fields = ['nombre', 'apellido', 'dni', 'email']
    ordering_fields = ['nombre', 'apellido', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return VendedorListSerializer
        return VendedorSerializer
