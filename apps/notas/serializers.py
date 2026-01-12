from rest_framework import serializers
from .models import NotaDiaria


class NotaDiariaSerializer(serializers.ModelSerializer):
    """Serializer para listar notas diarias."""

    autor_nombre = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()
    puede_eliminar = serializers.SerializerMethodField()

    class Meta:
        model = NotaDiaria
        fields = [
            'id',
            'contenido',
            'autor',
            'autor_nombre',
            'fecha',
            'created_at',
            'hora',
            'puede_eliminar',
        ]
        read_only_fields = ['id', 'autor', 'created_at']

    def get_autor_nombre(self, obj):
        return f"{obj.autor.first_name} {obj.autor.last_name}".strip() or obj.autor.email

    def get_hora(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%H:%M')
        return ''

    def get_puede_eliminar(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.autor_id == request.user.id
        return False


class NotaDiariaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notas diarias."""

    class Meta:
        model = NotaDiaria
        fields = ['contenido', 'fecha']

    def create(self, validated_data):
        validated_data['autor'] = self.context['request'].user
        return super().create(validated_data)
