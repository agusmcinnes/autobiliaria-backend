from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """
    Serializer personalizado para obtener tokens JWT.
    Incluye informacion adicional del usuario en la respuesta.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    {'detail': 'Credenciales invalidas.'},
                    code='authentication'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    {'detail': 'Usuario desactivado.'},
                    code='authentication'
                )
        else:
            raise serializers.ValidationError(
                {'detail': 'Email y password son requeridos.'},
                code='authentication'
            )

        # Generar tokens
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UsuarioSerializer(user).data,
        }


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario.
    Solo lectura, para respuestas de la API.
    """

    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Usuario
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'rol',
            'is_active',
            'is_admin',
            'created_at',
            'updated_at',
            'last_login',
        )
        read_only_fields = fields


class LogoutSerializer(serializers.Serializer):
    """
    Serializer para logout (invalidar refresh token).
    """

    refresh = serializers.CharField(required=True)

    def validate_refresh(self, value):
        """Valida que el token sea valido."""
        try:
            RefreshToken(value)
        except Exception:
            raise serializers.ValidationError('Token invalido o expirado.')
        return value
