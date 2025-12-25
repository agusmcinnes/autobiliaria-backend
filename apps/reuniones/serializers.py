from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Reunion


class ReunionListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para listados.
    """
    ubicacion_display = serializers.CharField(
        source='get_ubicacion_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    coordinador_nombre = serializers.SerializerMethodField()
    vendedor_display = serializers.CharField(read_only=True)
    vehiculo_display = serializers.CharField(read_only=True)
    vehiculo_titulo = serializers.CharField(
        source='vehiculo.titulo',
        read_only=True
    )
    vehiculo_patente = serializers.CharField(
        source='vehiculo.patente',
        read_only=True
    )

    class Meta:
        model = Reunion
        fields = [
            'id',
            'fecha',
            'hora',
            'ubicacion',
            'ubicacion_display',
            'estado',
            'estado_display',
            'coordinador',
            'coordinador_nombre',
            'comprador_nombre',
            'vendedor',
            'vendedor_texto',
            'vendedor_display',
            'vehiculo',
            'vehiculo_display',
            'vehiculo_titulo',
            'vehiculo_patente',
            'created_at',
        ]

    def get_coordinador_nombre(self, obj):
        return obj.coordinador.get_full_name()


class ReunionSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle, creacion y actualizacion.
    """
    ubicacion_display = serializers.CharField(
        source='get_ubicacion_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    coordinador_nombre = serializers.SerializerMethodField()
    vendedor_display = serializers.CharField(read_only=True)
    vendedor_nombre = serializers.SerializerMethodField()
    vehiculo_display = serializers.CharField(read_only=True)
    vehiculo_titulo = serializers.CharField(
        source='vehiculo.titulo',
        read_only=True
    )
    vehiculo_patente = serializers.CharField(
        source='vehiculo.patente',
        read_only=True
    )
    creada_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Reunion
        fields = [
            'id',
            'fecha',
            'hora',
            'ubicacion',
            'ubicacion_display',
            'estado',
            'estado_display',
            'coordinador',
            'coordinador_nombre',
            'comprador_nombre',
            'vendedor',
            'vendedor_nombre',
            'vendedor_texto',
            'vendedor_display',
            'vehiculo',
            'vehiculo_display',
            'vehiculo_titulo',
            'vehiculo_patente',
            'notas',
            'creada_por',
            'creada_por_nombre',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'creada_por',
            'created_at',
            'updated_at',
        ]

    def get_coordinador_nombre(self, obj):
        return obj.coordinador.get_full_name()

    def get_vendedor_nombre(self, obj):
        if obj.vendedor:
            return f"{obj.vendedor.nombre} {obj.vendedor.apellido}"
        return None

    def get_creada_por_nombre(self, obj):
        return obj.creada_por.get_full_name()

    def validate(self, attrs):
        """Validaciones de negocio."""
        vendedor = attrs.get('vendedor')
        vendedor_texto = attrs.get('vendedor_texto', '')

        # Si no hay vendedor FK ni texto, es valido (sin vendedor asignado)
        # Si hay ambos, priorizar el FK

        return attrs


class ReunionCreateSerializer(ReunionSerializer):
    """
    Serializer para creacion con usuario actual.
    """

    class Meta(ReunionSerializer.Meta):
        pass

    def create(self, validated_data):
        # Asignar el usuario que crea la reunion
        validated_data['creada_por'] = self.context['request'].user
        return super().create(validated_data)


class ReunionEstadisticasSerializer(serializers.Serializer):
    """
    Serializer para las estadisticas de reuniones.
    """
    hoy = serializers.IntegerField()
    manana = serializers.IntegerField()
    semana = serializers.IntegerField()
    mes = serializers.IntegerField()
