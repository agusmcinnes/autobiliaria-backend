from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Consulta


class ConsultaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creacion publica de consultas.
    Solo campos que el cliente puede enviar.
    """

    class Meta:
        model = Consulta
        fields = [
            'nombre',
            'email',
            'telefono',
            'mensaje',
            'tipo',
            'vehiculo',
        ]

    def validate_vehiculo(self, value):
        """Validar que el vehiculo este disponible."""
        if value.deleted_at is not None:
            raise serializers.ValidationError(
                _('El vehiculo no esta disponible.')
            )
        if value.vendido:
            raise serializers.ValidationError(
                _('El vehiculo ya fue vendido.')
            )
        return value


class ConsultaListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para listados (staff).
    """
    vehiculo_titulo = serializers.CharField(
        source='vehiculo.titulo',
        read_only=True
    )
    vehiculo_patente = serializers.CharField(
        source='vehiculo.patente',
        read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )

    class Meta:
        model = Consulta
        fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'tipo',
            'tipo_display',
            'vehiculo',
            'vehiculo_titulo',
            'vehiculo_patente',
            'leida',
            'atendida',
            'created_at',
        ]


class ConsultaSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle y actualizacion (staff).
    """
    vehiculo_titulo = serializers.CharField(
        source='vehiculo.titulo',
        read_only=True
    )
    vehiculo_patente = serializers.CharField(
        source='vehiculo.patente',
        read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )
    atendida_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'mensaje',
            'tipo',
            'tipo_display',
            'vehiculo',
            'vehiculo_titulo',
            'vehiculo_patente',
            'leida',
            'atendida',
            'notas_staff',
            'atendida_por',
            'atendida_por_nombre',
            'fecha_atendida',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'mensaje',
            'tipo',
            'vehiculo',
            'atendida_por',
            'fecha_atendida',
            'created_at',
            'updated_at',
        ]

    def get_atendida_por_nombre(self, obj):
        if obj.atendida_por:
            return obj.atendida_por.get_full_name()
        return None
