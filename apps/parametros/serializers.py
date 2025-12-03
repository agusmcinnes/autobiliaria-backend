from rest_framework import serializers

from .models import (
    Caja, Combustible, Condicion, Estado, Iva,
    Localidad, Moneda, Segmento, Marca, Modelo
)


class ParametroBaseSerializer(serializers.ModelSerializer):
    """Serializer base para parámetros simples"""

    class Meta:
        fields = ['id', 'nombre', 'activo', 'orden', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CajaSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Caja


class CombustibleSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Combustible


class CondicionSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Condicion


class EstadoSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Estado


class IvaSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Iva


class LocalidadSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Localidad


class MonedaSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Moneda


class SegmentoSerializer(ParametroBaseSerializer):
    class Meta(ParametroBaseSerializer.Meta):
        model = Segmento


class ModeloSerializer(ParametroBaseSerializer):
    """Serializer para Modelo con marca anidada"""
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)

    class Meta(ParametroBaseSerializer.Meta):
        model = Modelo
        fields = ['id', 'nombre', 'marca', 'marca_nombre', 'activo', 'orden', 'created_at', 'updated_at']


class ModeloSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple de Modelo para anidar en Marca"""

    class Meta:
        model = Modelo
        fields = ['id', 'nombre', 'activo', 'orden']


class MarcaSerializer(ParametroBaseSerializer):
    """Serializer para Marca"""

    class Meta(ParametroBaseSerializer.Meta):
        model = Marca


class MarcaConModelosSerializer(ParametroBaseSerializer):
    """Serializer para Marca con modelos anidados (detalle)"""
    modelos = ModeloSimpleSerializer(many=True, read_only=True)

    class Meta(ParametroBaseSerializer.Meta):
        model = Marca
        fields = ['id', 'nombre', 'activo', 'orden', 'modelos', 'created_at', 'updated_at']
