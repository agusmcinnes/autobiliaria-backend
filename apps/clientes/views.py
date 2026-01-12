from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Cliente
from .serializers import ClienteSerializer, ClienteListSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar clientes.

    Endpoints:
    - GET /api/clientes/ - Listar clientes
    - POST /api/clientes/ - Crear cliente
    - GET /api/clientes/{id}/ - Detalle cliente
    - PUT /api/clientes/{id}/ - Actualizar cliente
    - PATCH /api/clientes/{id}/ - Actualizar parcial
    - DELETE /api/clientes/{id}/ - Eliminar cliente
    - GET /api/clientes/buscar/?dni=X - Buscar por DNI

    Filtros:
    - ?activo=true|false
    - ?search=texto (busca en nombre, apellido, dni_cuit, email)
    - ?ordering=apellido|-created_at
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'apellido', 'dni_cuit', 'email', 'telefono']
    ordering_fields = ['nombre', 'apellido', 'created_at', 'dni_cuit']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        return ClienteSerializer

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Buscar cliente por DNI/CUIT exacto.
        Util para autocompletar en formulario de reservas.

        GET /api/clientes/buscar/?dni=12345678
        """
        dni = request.query_params.get('dni', '').replace('.', '').replace('-', '').strip()

        if not dni:
            return Response(
                {'error': 'Debe proporcionar el parametro dni'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cliente = Cliente.objects.get(dni_cuit=dni)
            serializer = ClienteSerializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response(
                {'found': False, 'message': 'Cliente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
