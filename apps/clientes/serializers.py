from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Cliente.
    Usado en detalle, creacion y actualizacion.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id',
            'nombre',
            'apellido',
            'full_name',
            'dni_cuit',
            'email',
            'telefono',
            'domicilio',
            'notas',
            'activo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_dni_cuit(self, value):
        """Normaliza el DNI/CUIT quitando puntos y guiones."""
        return value.replace('.', '').replace('-', '').strip()


class ClienteListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para listados.
    Excluye campos extensos como notas.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id',
            'nombre',
            'apellido',
            'full_name',
            'dni_cuit',
            'email',
            'telefono',
            'activo',
            'created_at',
        ]


class ClienteMinimalSerializer(serializers.ModelSerializer):
    """
    Serializer minimo para usar en relaciones.
    Solo campos esenciales para mostrar en reservas.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id',
            'full_name',
            'dni_cuit',
            'telefono',
        ]
