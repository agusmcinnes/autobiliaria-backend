from rest_framework import serializers

from .models import Vendedor


class VendedorSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Vendedor.
    Usado en detalle, creación y actualización.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Vendedor
        fields = [
            'id',
            'nombre',
            'apellido',
            'full_name',
            'email',
            'direccion',
            'celular',
            'dni',
            'tiene_cartel',
            'activo',
            'comentarios',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VendedorListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para listados.
    Excluye campos extensos como comentarios.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Vendedor
        fields = [
            'id',
            'nombre',
            'apellido',
            'full_name',
            'email',
            'celular',
            'dni',
            'tiene_cartel',
            'activo',
            'created_at',
        ]
