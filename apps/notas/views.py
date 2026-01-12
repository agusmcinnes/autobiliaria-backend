from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import NotaDiaria
from .serializers import NotaDiariaSerializer, NotaDiariaCreateSerializer


class NotaDiariaViewSet(viewsets.ModelViewSet):
    """ViewSet para notas diarias."""

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        queryset = NotaDiaria.objects.select_related('autor')
        fecha = self.request.query_params.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        return queryset.order_by('created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return NotaDiariaCreateSerializer
        return NotaDiariaSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.autor_id != request.user.id:
            raise PermissionDenied('Solo puedes eliminar tus propias notas.')
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
