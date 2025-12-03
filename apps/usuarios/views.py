import logging

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    UsuarioSerializer,
)

logger = logging.getLogger(__name__)


class LoginThrottle(ScopedRateThrottle):
    """Throttle especifico para login."""
    scope = 'login'


class LoginView(GenericAPIView):
    """
    POST /api/auth/login/

    Autentica un usuario y retorna tokens JWT.

    Request body:
        - email: string (required)
        - password: string (required)

    Response:
        - access: string (JWT access token)
        - refresh: string (JWT refresh token)
        - user: object (datos del usuario)
    """

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.warning(
                f"Intento de login fallido para email: {request.data.get('email', 'N/A')}"
            )
            raise

        logger.info(f"Login exitoso: {serializer.validated_data['user']['email']}")
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshTokenView(TokenRefreshView):
    """
    POST /api/auth/refresh/

    Refresca el access token usando el refresh token.

    Request body:
        - refresh: string (JWT refresh token)

    Response:
        - access: string (nuevo JWT access token)
        - refresh: string (nuevo JWT refresh token, por rotacion)
    """
    pass


class LogoutView(GenericAPIView):
    """
    POST /api/auth/logout/

    Invalida el refresh token (lo agrega a blacklist).
    Requiere autenticacion.

    Request body:
        - refresh: string (JWT refresh token a invalidar)

    Response:
        - detail: string (mensaje de confirmacion)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            logger.info(f"Logout exitoso: {request.user.email}")
            return Response(
                {'detail': 'Sesion cerrada correctamente.'},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'detail': 'Token invalido o ya invalidado.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(APIView):
    """
    GET /api/auth/me/

    Retorna los datos del usuario autenticado.
    Requiere autenticacion.

    Response:
        - user object con todos los campos del usuario
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
