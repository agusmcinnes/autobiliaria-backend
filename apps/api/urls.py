from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

app_name = 'api'


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Endpoint raiz de la API."""
    return Response({
        'status': 'ok',
        'endpoints': {
            'auth': {
                'login': '/api/auth/login/',
                'refresh': '/api/auth/refresh/',
                'logout': '/api/auth/logout/',
                'me': '/api/auth/me/',
            },
            'vendedores': {
                'list': '/api/vendedores/',
                'detail': '/api/vendedores/{id}/',
            },
            'parametros': {
                'cajas': '/api/parametros/cajas/',
                'combustibles': '/api/parametros/combustibles/',
                'condiciones': '/api/parametros/condiciones/',
                'estados': '/api/parametros/estados/',
                'ivas': '/api/parametros/ivas/',
                'localidades': '/api/parametros/localidades/',
                'marcas': '/api/parametros/marcas/',
                'modelos': '/api/parametros/modelos/',
                'monedas': '/api/parametros/monedas/',
                'segmentos': '/api/parametros/segmentos/',
            },
            'vehiculos': {
                'list': '/api/vehiculos/',
                'detail': '/api/vehiculos/{id}/',
                'imagenes': '/api/vehiculos/{id}/imagenes/',
                'restaurar': '/api/vehiculos/{id}/restaurar/',
                'marcar_vendido': '/api/vehiculos/{id}/marcar-vendido/',
                'marcar_reservado': '/api/vehiculos/{id}/marcar-reservado/',
            },
            'consultas': {
                'list': '/api/consultas/',
                'create': '/api/consultas/',
                'detail': '/api/consultas/{id}/',
                'marcar_leida': '/api/consultas/{id}/marcar-leida/',
                'marcar_atendida': '/api/consultas/{id}/marcar-atendida/',
            },
            'publicaciones': {
                'tipos_vehiculo': '/api/publicaciones/tipos-vehiculo/',
                'list': '/api/publicaciones/',
                'create': '/api/publicaciones/',
                'detail': '/api/publicaciones/{id}/',
                'marcar_vista': '/api/publicaciones/{id}/marcar-vista/',
                'marcar_eliminada': '/api/publicaciones/{id}/marcar-eliminada/',
            },
            'reuniones': {
                'list': '/api/reuniones/',
                'create': '/api/reuniones/',
                'detail': '/api/reuniones/{id}/',
                'estadisticas': '/api/reuniones/estadisticas/',
                'por_fecha': '/api/reuniones/por-fecha/{fecha}/',
                'marcar_completada': '/api/reuniones/{id}/marcar-completada/',
                'marcar_cancelada': '/api/reuniones/{id}/marcar-cancelada/',
            }
        }
    })


urlpatterns = [
    path('', api_root, name='root'),
    path('auth/', include('apps.usuarios.urls', namespace='auth')),
    path('vendedores/', include('apps.vendedores.urls', namespace='vendedores')),
    path('parametros/', include('apps.parametros.urls', namespace='parametros')),
    path('vehiculos/', include('apps.vehiculos.urls', namespace='vehiculos')),
    path('consultas/', include('apps.consultas.urls', namespace='consultas')),
    path('publicaciones/', include('apps.publicaciones.urls', namespace='publicaciones')),
    path('reuniones/', include('apps.reuniones.urls', namespace='reuniones')),
]
