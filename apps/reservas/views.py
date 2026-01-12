from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.utils import timezone

from .models import (
    Reserva, FormaPago, GastoAdministrativo, NotaReserva,
    TipoOperacion, EstadoReserva
)
from .serializers import (
    ReservaSerializer,
    ReservaListSerializer,
    ReservaCreateSerializer,
    FormaPagoSerializer,
    GastoAdministrativoSerializer,
    NotaReservaSerializer,
)
from .filters import ReservaFilter


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reservas/operaciones.

    Endpoints:
    - GET /api/reservas/ - Listar reservas
    - POST /api/reservas/ - Crear reserva
    - GET /api/reservas/{id}/ - Detalle reserva
    - PUT /api/reservas/{id}/ - Actualizar reserva
    - PATCH /api/reservas/{id}/ - Actualizar parcial
    - DELETE /api/reservas/{id}/ - Eliminar reserva

    Acciones extra:
    - GET /api/reservas/estadisticas/ - Dashboard de estadisticas
    - POST /api/reservas/{id}/formas-pago/ - Agregar forma de pago
    - DELETE /api/reservas/{id}/formas-pago/{fp_id}/ - Eliminar forma de pago
    - POST /api/reservas/{id}/gastos/ - Agregar gasto (EXTERNAL)
    - DELETE /api/reservas/{id}/gastos/{g_id}/ - Eliminar gasto
    - POST /api/reservas/{id}/notas/ - Agregar nota de seguimiento
    - PATCH /api/reservas/{id}/cambiar-estado/ - Cambiar estado
    - PATCH /api/reservas/{id}/marcar-entregado/ - Marcar como entregado
    - PATCH /api/reservas/{id}/marcar-transferido/ - Marcar transferencia realizada

    Filtros:
    - ?tipo_operacion=used|new|external
    - ?estado=pending|delivered|cancelled|cancelled_lost_deposit|restructuring
    - ?vehiculo=5
    - ?cliente=3
    - ?vendedor=3 (busca en vendedor_1 y vendedor_2)
    - ?cliente_dni=20123456
    - ?fecha_desde=2024-01-01&fecha_hasta=2024-12-31
    - ?mes_entrega=1&anio_entrega=2024
    - ?monto_min=10000&monto_max=50000
    - ?entregado=true|false
    - ?transferido=true|false
    - ?pendientes=true
    - ?activas=true
    - ?search=texto
    - ?ordering=-created_at,precio_venta
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReservaFilter
    search_fields = [
        'numero_reserva',
        'cliente__nombre',
        'cliente__apellido',
        'cliente__dni_cuit',
        'vehiculo__patente',
        'vehiculo__marca__nombre',
        'vehiculo__modelo__nombre',
        'dominio',
    ]
    ordering_fields = [
        'created_at', 'fecha_entrega_pactada', 'precio_venta',
        'numero_reserva', 'estado',
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        """Retorna queryset optimizado."""
        return Reserva.objects.select_related(
            'vehiculo',
            'vehiculo__marca',
            'vehiculo__modelo',
            'cliente',
            'propietario_anterior',
            'vendedor_1',
            'vendedor_2',
            'gestor_supervisor',
            'creada_por',
            'moneda',
        ).prefetch_related(
            'formas_pago',
            'formas_pago__sena_recibida_por',
            'gastos_administrativos',
            'notas__autor',
            'vehiculo__imagenes',
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        if self.action == 'create':
            return ReservaCreateSerializer
        return ReservaSerializer

    # =========================================================================
    # ESTADISTICAS
    # =========================================================================

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Retorna estadisticas del dashboard."""
        hoy = timezone.localdate()

        queryset = self.filter_queryset(self.get_queryset())

        # Totales por estado
        por_estado = {}
        for estado in EstadoReserva.values:
            por_estado[estado] = queryset.filter(estado=estado).count()

        # Totales por tipo
        por_tipo = {}
        for tipo in TipoOperacion.values:
            por_tipo[tipo] = queryset.filter(tipo_operacion=tipo).count()

        # Total general
        total = queryset.count()

        # Entregas para hoy
        entregas_hoy = queryset.filter(
            fecha_entrega_pactada=hoy,
            estado=EstadoReserva.PENDING
        ).count()

        # Total facturado (reservas activas)
        total_facturado = queryset.filter(
            estado__in=[EstadoReserva.PENDING, EstadoReserva.DELIVERED]
        ).aggregate(total=Sum('precio_venta'))['total'] or 0

        # Resumen de comisiones
        comisiones = queryset.filter(
            estado__in=[EstadoReserva.PENDING, EstadoReserva.DELIVERED]
        ).aggregate(
            comision_vendedor=Sum('comision_vendedor'),
            comision_comprador=Sum('comision_comprador'),
        )

        return Response({
            'total': total,
            'por_estado': por_estado,
            'por_tipo': por_tipo,
            'entregas_hoy': entregas_hoy,
            'total_facturado': str(total_facturado),
            'comisiones': {
                'vendedor': str(comisiones['comision_vendedor'] or 0),
                'comprador': str(comisiones['comision_comprador'] or 0),
            }
        })

    # =========================================================================
    # FORMAS DE PAGO
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='formas-pago')
    def agregar_forma_pago(self, request, pk=None):
        """Agrega una forma de pago a la reserva."""
        reserva = self.get_object()
        serializer = FormaPagoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(reserva=reserva)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['delete'],
        url_path='formas-pago/(?P<fp_id>[^/.]+)'
    )
    def eliminar_forma_pago(self, request, pk=None, fp_id=None):
        """Elimina una forma de pago."""
        reserva = self.get_object()
        try:
            forma_pago = reserva.formas_pago.get(pk=fp_id)
            forma_pago.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FormaPago.DoesNotExist:
            return Response(
                {'error': 'Forma de pago no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    # =========================================================================
    # GASTOS ADMINISTRATIVOS (EXTERNAL)
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='gastos')
    def agregar_gasto(self, request, pk=None):
        """Agrega un gasto administrativo (solo para EXTERNAL)."""
        reserva = self.get_object()

        if reserva.tipo_operacion != TipoOperacion.EXTERNAL:
            return Response(
                {'error': 'Los gastos administrativos solo aplican a operaciones externas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = GastoAdministrativoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reserva=reserva)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['delete'],
        url_path='gastos/(?P<g_id>[^/.]+)'
    )
    def eliminar_gasto(self, request, pk=None, g_id=None):
        """Elimina un gasto administrativo."""
        reserva = self.get_object()
        try:
            gasto = reserva.gastos_administrativos.get(pk=g_id)
            gasto.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GastoAdministrativo.DoesNotExist:
            return Response(
                {'error': 'Gasto no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    # =========================================================================
    # NOTAS DE SEGUIMIENTO
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='notas')
    def agregar_nota(self, request, pk=None):
        """Agrega una nota de seguimiento."""
        reserva = self.get_object()
        serializer = NotaReservaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(reserva=reserva, autor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # =========================================================================
    # CAMBIOS DE ESTADO
    # =========================================================================

    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de la reserva."""
        reserva = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in EstadoReserva.values:
            return Response(
                {'error': f'Estado invalido. Opciones: {list(EstadoReserva.values)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reserva.estado = nuevo_estado
        reserva.save(update_fields=['estado', 'updated_at'])

        serializer = ReservaSerializer(reserva, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-entregado')
    def marcar_entregado(self, request, pk=None):
        """Marca la reserva como entregada."""
        reserva = self.get_object()
        reserva.entregado = True
        reserva.estado = EstadoReserva.DELIVERED

        # Actualizar fecha de entrega si no está establecida
        if not reserva.fecha_entrega_pactada:
            reserva.fecha_entrega_pactada = timezone.localdate()

        reserva.save(update_fields=['entregado', 'estado', 'fecha_entrega_pactada', 'updated_at'])

        # Si hay vehiculo, marcarlo como vendido
        if reserva.vehiculo:
            reserva.vehiculo.vendido = True
            reserva.vehiculo.reservado = False
            reserva.vehiculo.mostrar_en_web = False
            reserva.vehiculo.save(update_fields=[
                'vendido', 'reservado', 'mostrar_en_web', 'updated_at'
            ])

        serializer = ReservaSerializer(reserva, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='marcar-transferido')
    def marcar_transferido(self, request, pk=None):
        """Marca la transferencia como realizada."""
        reserva = self.get_object()
        reserva.transferido = True
        reserva.save(update_fields=['transferido', 'updated_at'])

        serializer = ReservaSerializer(reserva, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='anular')
    def anular(self, request, pk=None):
        """Anula la reserva."""
        reserva = self.get_object()
        perder_sena = request.data.get('perder_sena', False)

        if perder_sena:
            reserva.estado = EstadoReserva.CANCELLED_LOST_DEPOSIT
        else:
            reserva.estado = EstadoReserva.CANCELLED

        reserva.save(update_fields=['estado', 'updated_at'])

        # Si hay vehiculo, liberarlo
        if reserva.vehiculo:
            reserva.vehiculo.reservado = False
            reserva.vehiculo.save(update_fields=['reservado', 'updated_at'])

        serializer = ReservaSerializer(reserva, context={'request': request})
        return Response(serializer.data)
