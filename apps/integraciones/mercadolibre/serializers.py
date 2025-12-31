from rest_framework import serializers
from .models import MLCredential, MLPublication, MLSyncLog


class MLCredentialSerializer(serializers.ModelSerializer):
    """Serializer para mostrar estado de credenciales ML."""
    is_token_expired = serializers.BooleanField(read_only=True)
    needs_refresh = serializers.BooleanField(read_only=True)

    class Meta:
        model = MLCredential
        fields = [
            'id',
            'ml_user_id',
            'ml_nickname',
            'is_active',
            'is_token_expired',
            'needs_refresh',
            'expires_at',
            'scope',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class MLConnectionStatusSerializer(serializers.Serializer):
    """Serializer para el estado de conexion con ML."""
    connected = serializers.BooleanField()
    ml_user_id = serializers.CharField(allow_null=True)
    ml_nickname = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()
    token_expires_at = serializers.DateTimeField(allow_null=True)
    token_expired = serializers.BooleanField()
    needs_reauthorization = serializers.BooleanField()
    connected_at = serializers.DateTimeField(allow_null=True)


class MLAuthURLSerializer(serializers.Serializer):
    """Serializer para respuesta de URL de autorizacion."""
    auth_url = serializers.URLField()
    state = serializers.CharField()


class MLPublicationListSerializer(serializers.ModelSerializer):
    """Serializer para listado de publicaciones ML."""
    vehiculo_patente = serializers.CharField(source='vehiculo.patente', read_only=True, allow_null=True)
    vehiculo_titulo = serializers.CharField(source='vehiculo.titulo', read_only=True, allow_null=True)
    is_linked = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = MLPublication
        fields = [
            'id',
            'ml_item_id',
            'ml_title',
            'ml_status',
            'ml_price',
            'ml_currency',
            'ml_permalink',
            'ml_thumbnail',
            'patente_ml',
            'vehiculo',
            'vehiculo_patente',
            'vehiculo_titulo',
            'is_linked',
            'is_active',
            'last_synced',
            'created_from_system',
        ]


class MLPublicationDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de publicacion ML."""
    vehiculo_patente = serializers.CharField(source='vehiculo.patente', read_only=True, allow_null=True)
    vehiculo_titulo = serializers.CharField(source='vehiculo.titulo', read_only=True, allow_null=True)
    vehiculo_id = serializers.IntegerField(source='vehiculo.id', read_only=True, allow_null=True)
    is_linked = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = MLPublication
        fields = [
            'id',
            'ml_item_id',
            'ml_title',
            'ml_status',
            'ml_price',
            'ml_currency',
            'ml_permalink',
            'ml_thumbnail',
            'ml_category_id',
            'ml_listing_type',
            'patente_ml',
            'marca_ml',
            'modelo_ml',
            'anio_ml',
            'km_ml',
            'vehiculo',
            'vehiculo_id',
            'vehiculo_patente',
            'vehiculo_titulo',
            'is_linked',
            'is_active',
            'last_synced',
            'sync_error',
            'created_from_system',
            'created_at',
            'updated_at',
        ]


class MLPublicationLinkSerializer(serializers.Serializer):
    """Serializer para vincular publicacion a vehiculo."""
    vehiculo_id = serializers.IntegerField(required=True)


class MLPublicationStatusSerializer(serializers.Serializer):
    """Serializer para cambiar estado de publicacion."""
    status = serializers.ChoiceField(choices=['active', 'paused', 'closed'])


class MLSyncLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de sincronizacion."""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    publication_title = serializers.CharField(source='publication.ml_title', read_only=True, allow_null=True)
    vehiculo_patente = serializers.CharField(source='vehiculo.patente', read_only=True, allow_null=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)

    class Meta:
        model = MLSyncLog
        fields = [
            'id',
            'action',
            'action_display',
            'publication',
            'publication_title',
            'vehiculo',
            'vehiculo_patente',
            'user',
            'user_email',
            'success',
            'error_message',
            'created_at',
        ]


class MLSyncResultSerializer(serializers.Serializer):
    """Serializer para resultado de sincronizacion."""
    imported = serializers.IntegerField()
    updated = serializers.IntegerField()
    linked = serializers.IntegerField()
    total = serializers.IntegerField()


class MLStatisticsSerializer(serializers.Serializer):
    """Serializer para estadisticas de ML."""
    total_publications = serializers.IntegerField()
    active_publications = serializers.IntegerField()
    paused_publications = serializers.IntegerField()
    closed_publications = serializers.IntegerField()
    linked_publications = serializers.IntegerField()
    unlinked_publications = serializers.IntegerField()
    created_from_system = serializers.IntegerField()
    last_sync = serializers.DateTimeField(allow_null=True)
