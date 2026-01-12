from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import (
    Reserva, FormaPago, GastoAdministrativo, NotaReserva,
    TipoOperacion, TipoFormaPago
)
from apps.clientes.serializers import ClienteMinimalSerializer


class NotaReservaSerializer(serializers.ModelSerializer):
    """Serializer para notas de seguimiento."""
    autor_nombre = serializers.SerializerMethodField()

    class Meta:
        model = NotaReserva
        fields = ['id', 'contenido', 'autor', 'autor_nombre', 'created_at']
        read_only_fields = ['id', 'autor', 'created_at']

    def get_autor_nombre(self, obj):
        return obj.autor.get_full_name()


class FormaPagoSerializer(serializers.ModelSerializer):
    """Serializer completo para formas de pago."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    sena_recibida_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = FormaPago
        fields = [
            'id', 'tipo', 'tipo_display', 'monto',
            # Cheque
            'cheque_numero', 'cheque_banco', 'cheque_fecha_vencimiento',
            # Credito
            'credito_banco', 'credito_cuotas', 'credito_valor_cuota', 'credito_valor_acreditado',
            # Permuta
            'permuta_marca', 'permuta_modelo', 'permuta_anio', 'permuta_km',
            'permuta_patente', 'permuta_es_stock', 'permuta_vehiculo',
            # Sena
            'sena_fecha', 'sena_recibida_por', 'sena_recibida_por_nombre',
            # General
            'notas', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_sena_recibida_por_nombre(self, obj):
        if obj.sena_recibida_por:
            return obj.sena_recibida_por.get_full_name()
        return None

    def validate(self, data):
        """Validar campos requeridos segun tipo de pago."""
        tipo = data.get('tipo')

        if tipo == TipoFormaPago.CHECK:
            if not data.get('cheque_banco'):
                raise serializers.ValidationError({
                    'cheque_banco': 'El banco es requerido para pagos con cheque.'
                })

        if tipo == TipoFormaPago.CREDIT:
            if not data.get('credito_banco'):
                raise serializers.ValidationError({
                    'credito_banco': 'El banco es requerido para creditos.'
                })

        if tipo == TipoFormaPago.TRADE_IN:
            if not (data.get('permuta_patente') or data.get('permuta_vehiculo')):
                raise serializers.ValidationError({
                    'permuta_patente': 'Debe indicar la patente o vincular un vehiculo existente.'
                })

        return data


class GastoAdministrativoSerializer(serializers.ModelSerializer):
    """Serializer para gastos administrativos."""
    tipo_cuenta_display = serializers.CharField(source='get_tipo_cuenta_display', read_only=True)

    class Meta:
        model = GastoAdministrativo
        fields = [
            'id', 'concepto', 'monto', 'tipo_cuenta', 'tipo_cuenta_display',
            'fecha', 'metodo_pago', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReservaListSerializer(serializers.ModelSerializer):
    """Serializer reducido para listados."""
    tipo_operacion_display = serializers.CharField(source='get_tipo_operacion_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    color_operacion = serializers.CharField(read_only=True)
    vehiculo_titulo = serializers.SerializerMethodField()
    vehiculo_patente = serializers.SerializerMethodField()
    cliente_nombre = serializers.SerializerMethodField()
    cliente_dni = serializers.SerializerMethodField()
    vendedor_1_nombre = serializers.SerializerMethodField()
    moneda_nombre = serializers.SerializerMethodField()
    total_operacion = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_pagado = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'numero_reserva',
            'tipo_operacion', 'tipo_operacion_display', 'color_operacion',
            'estado', 'estado_display',
            'vehiculo', 'vehiculo_titulo', 'vehiculo_patente',
            'cliente', 'cliente_nombre', 'cliente_dni',
            'precio_venta', 'moneda', 'moneda_nombre',
            'total_operacion', 'total_pagado', 'saldo_pendiente',
            'vendedor_1', 'vendedor_1_nombre',
            'fecha_entrega_pactada',
            'entregado', 'transferido',
            'created_at',
        ]

    def get_vehiculo_titulo(self, obj):
        return obj.vehiculo.titulo if obj.vehiculo else None

    def get_vehiculo_patente(self, obj):
        return obj.vehiculo.patente if obj.vehiculo else obj.dominio

    def get_cliente_nombre(self, obj):
        return obj.cliente.get_full_name()

    def get_cliente_dni(self, obj):
        return obj.cliente.dni_cuit

    def get_vendedor_1_nombre(self, obj):
        return obj.vendedor_1.get_full_name()

    def get_moneda_nombre(self, obj):
        return obj.moneda.nombre if obj.moneda else None


class ReservaSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle, creacion y actualizacion."""
    # Campos de solo lectura expandidos
    tipo_operacion_display = serializers.CharField(source='get_tipo_operacion_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    color_operacion = serializers.CharField(read_only=True)
    total_operacion = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_pagado = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    porcentaje_pagado = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    # Relaciones expandidas
    vehiculo_detail = serializers.SerializerMethodField()
    cliente_detail = ClienteMinimalSerializer(source='cliente', read_only=True)
    propietario_anterior_nombre = serializers.SerializerMethodField()
    vendedor_1_nombre = serializers.SerializerMethodField()
    vendedor_2_nombre = serializers.SerializerMethodField()
    gestor_supervisor_nombre = serializers.SerializerMethodField()
    creada_por_nombre = serializers.SerializerMethodField()
    moneda_nombre = serializers.SerializerMethodField()

    # Relaciones anidadas
    formas_pago = FormaPagoSerializer(many=True, read_only=True)
    gastos_administrativos = GastoAdministrativoSerializer(many=True, read_only=True)
    notas = NotaReservaSerializer(many=True, read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'numero_reserva',
            # Tipo y estado
            'tipo_operacion', 'tipo_operacion_display', 'color_operacion',
            'estado', 'estado_display',
            # Vehiculo
            'vehiculo', 'vehiculo_detail',
            # Cliente
            'cliente', 'cliente_detail',
            # Usados
            'dominio', 'propietario_anterior', 'propietario_anterior_nombre',
            # 0KM
            'numero_chasis', 'proveedor', 'costo_patentamiento', 'costo_flete',
            # Costos
            'precio_venta', 'moneda', 'moneda_nombre',
            'comision_vendedor', 'comision_comprador',
            'gestion_credito', 'gastos_transferencia', 'impuestos',
            'otros_gastos', 'descripcion_otros_gastos', 'observaciones_costos',
            'total_operacion', 'total_pagado', 'saldo_pendiente', 'porcentaje_pagado',
            # Administrativo
            'fecha_entrega_pactada',
            'vendedor_1', 'vendedor_1_nombre',
            'vendedor_2', 'vendedor_2_nombre',
            'gestor_supervisor', 'gestor_supervisor_nombre',
            # Checkboxes
            'entregado', 'transferido', 'a_reestructurar',
            # Relaciones
            'formas_pago', 'gastos_administrativos', 'notas',
            # Auditoria
            'creada_por', 'creada_por_nombre', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'numero_reserva', 'creada_por', 'created_at', 'updated_at'
        ]

    def get_vehiculo_detail(self, obj):
        if obj.vehiculo:
            return {
                'id': obj.vehiculo.id,
                'titulo': obj.vehiculo.titulo,
                'patente': obj.vehiculo.patente,
                'precio': str(obj.vehiculo.precio),
                'imagen_principal': obj.vehiculo.imagenes.filter(es_principal=True).first().imagen.url if obj.vehiculo.imagenes.filter(es_principal=True).exists() else None,
            }
        return None

    def get_propietario_anterior_nombre(self, obj):
        if obj.propietario_anterior:
            return obj.propietario_anterior.get_full_name()
        return None

    def get_vendedor_1_nombre(self, obj):
        return obj.vendedor_1.get_full_name()

    def get_vendedor_2_nombre(self, obj):
        if obj.vendedor_2:
            return obj.vendedor_2.get_full_name()
        return None

    def get_gestor_supervisor_nombre(self, obj):
        if obj.gestor_supervisor:
            return obj.gestor_supervisor.get_full_name()
        return None

    def get_creada_por_nombre(self, obj):
        return obj.creada_por.get_full_name()

    def get_moneda_nombre(self, obj):
        return obj.moneda.nombre if obj.moneda else None

    def validate(self, data):
        """Validaciones de negocio segun tipo de operacion."""
        tipo = data.get('tipo_operacion') or (self.instance.tipo_operacion if self.instance else None)

        if tipo == TipoOperacion.USED:
            # Usados requieren vehiculo y dominio
            vehiculo = data.get('vehiculo') or (self.instance.vehiculo if self.instance else None)
            dominio = data.get('dominio') or (self.instance.dominio if self.instance else None)

            if not vehiculo:
                raise serializers.ValidationError({
                    'vehiculo': 'El vehiculo es requerido para reservas de usados.'
                })
            if not dominio:
                raise serializers.ValidationError({
                    'dominio': 'El dominio es requerido para reservas de usados.'
                })

        elif tipo == TipoOperacion.NEW:
            # 0KM requieren vehiculo y numero de chasis
            vehiculo = data.get('vehiculo') or (self.instance.vehiculo if self.instance else None)
            numero_chasis = data.get('numero_chasis') or (self.instance.numero_chasis if self.instance else None)

            if not vehiculo:
                raise serializers.ValidationError({
                    'vehiculo': 'El vehiculo es requerido para reservas de 0km.'
                })
            if not numero_chasis:
                raise serializers.ValidationError({
                    'numero_chasis': 'El numero de chasis es requerido para 0km.'
                })

        # EXTERNAL no tiene validaciones especiales de vehiculo

        return data


class ReservaCreateSerializer(ReservaSerializer):
    """Serializer para creacion con usuario actual."""

    class Meta(ReservaSerializer.Meta):
        pass

    def create(self, validated_data):
        validated_data['creada_por'] = self.context['request'].user
        return super().create(validated_data)
