from rest_framework import serializers

from .models import Vehiculo, ImagenVehiculo
from apps.parametros.serializers import (
    MarcaSerializer, ModeloSerializer, SegmentoSerializer,
    CombustibleSerializer, CajaSerializer, EstadoSerializer,
    CondicionSerializer, MonedaSerializer
)
from apps.vendedores.serializers import VendedorListSerializer


class ImagenVehiculoSerializer(serializers.ModelSerializer):
    """Serializer para imagenes de vehiculos."""
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenVehiculo
        fields = ['id', 'imagen', 'imagen_url', 'orden', 'es_principal', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class VehiculoListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para listados de vehiculos.
    Optimizado para rendimiento con datos esenciales.
    """
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    moneda_nombre = serializers.CharField(source='moneda.nombre', read_only=True)
    vendedor_nombre = serializers.CharField(source='vendedor_dueno.get_full_name', read_only=True)
    titulo = serializers.CharField(read_only=True)
    disponible = serializers.BooleanField(read_only=True)
    imagen_principal = serializers.SerializerMethodField()
    cant_imagenes = serializers.SerializerMethodField()

    class Meta:
        model = Vehiculo
        fields = [
            'id',
            'titulo',
            'patente',
            'marca',
            'marca_nombre',
            'modelo',
            'modelo_nombre',
            'version',
            'anio',
            'km',
            'color',
            'precio',
            'moneda',
            'moneda_nombre',
            'estado',
            'estado_nombre',
            'vendedor_dueno',
            'vendedor_nombre',
            'reservado',
            'vendido',
            'disponible',
            'mostrar_en_web',
            'destacar_en_web',
            'oportunidad',
            'publicado_en_ml',
            'ml_item_id',
            'imagen_principal',
            'cant_imagenes',
            'created_at',
        ]

    def get_imagen_principal(self, obj):
        imagen = obj.imagenes.filter(es_principal=True).first()
        if not imagen:
            imagen = obj.imagenes.first()
        if imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(imagen.imagen.url)
        return None

    def get_cant_imagenes(self, obj):
        return obj.imagenes.count()


class VehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle, creacion y actualizacion.
    Incluye validaciones de negocio.
    """
    # Campos de solo lectura expandidos
    marca_detail = MarcaSerializer(source='marca', read_only=True)
    modelo_detail = ModeloSerializer(source='modelo', read_only=True)
    segmento1_detail = SegmentoSerializer(source='segmento1', read_only=True)
    segmento2_detail = SegmentoSerializer(source='segmento2', read_only=True)
    combustible_detail = CombustibleSerializer(source='combustible', read_only=True)
    caja_detail = CajaSerializer(source='caja', read_only=True)
    estado_detail = EstadoSerializer(source='estado', read_only=True)
    condicion_detail = CondicionSerializer(source='condicion', read_only=True)
    moneda_detail = MonedaSerializer(source='moneda', read_only=True)
    vendedor_detail = VendedorListSerializer(source='vendedor_dueno', read_only=True)
    cargado_por_nombre = serializers.CharField(source='cargado_por.get_full_name', read_only=True)

    # Campos calculados
    titulo = serializers.CharField(read_only=True)
    precio_financiado = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    disponible = serializers.BooleanField(read_only=True)

    # Imagenes anidadas
    imagenes = ImagenVehiculoSerializer(many=True, read_only=True)

    class Meta:
        model = Vehiculo
        fields = [
            'id',
            # Titulo calculado
            'titulo',
            # Relaciones - IDs para escritura
            'marca',
            'modelo',
            'segmento1',
            'segmento2',
            'combustible',
            'caja',
            'estado',
            'condicion',
            'moneda',
            'vendedor_dueno',
            'cargado_por',
            # Relaciones - Objetos expandidos (solo lectura)
            'marca_detail',
            'modelo_detail',
            'segmento1_detail',
            'segmento2_detail',
            'combustible_detail',
            'caja_detail',
            'estado_detail',
            'condicion_detail',
            'moneda_detail',
            'vendedor_detail',
            'cargado_por_nombre',
            # Campos generales
            'version',
            'patente',
            'anio',
            'km',
            'color',
            'precio',
            'precio_financiado',
            'porcentaje_financiacion',
            'cant_duenos',
            # Booleans estado
            'vtv',
            'plan_ahorro',
            'reservado',
            'vendido',
            'disponible',
            # Booleans web
            'mostrar_en_web',
            'destacar_en_web',
            'oportunidad',
            'oportunidad_grupo',
            'reventa',
            # MercadoLibre
            'publicado_en_ml',
            'ml_item_id',
            'ml_estado',
            'ml_fecha_sync',
            'ml_error',
            'ml_permalink',
            # Otros
            'comentario_carga',
            'imagenes',
            # Auditoria
            'created_at',
            'updated_at',
            'deleted_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'deleted_at',
            'ml_item_id',
            'ml_estado',
            'ml_fecha_sync',
            'ml_error',
            'ml_permalink',
        ]

    def validate(self, data):
        """
        Valida coherencia entre marca y modelo.
        El modelo debe pertenecer a la marca seleccionada.
        """
        marca = data.get('marca') or (self.instance.marca if self.instance else None)
        modelo = data.get('modelo') or (self.instance.modelo if self.instance else None)

        if marca and modelo:
            if modelo.marca_id != marca.id:
                raise serializers.ValidationError({
                    'modelo': f'El modelo "{modelo.nombre}" no pertenece a la marca "{marca.nombre}".'
                })

        # Validar que segmento1 y segmento2 sean diferentes si ambos estan presentes
        segmento1 = data.get('segmento1')
        segmento2 = data.get('segmento2')
        if segmento1 and segmento2 and segmento1 == segmento2:
            raise serializers.ValidationError({
                'segmento2': 'El segmento secundario debe ser diferente al principal.'
            })

        return data

    def validate_patente(self, value):
        """Normaliza patente a mayusculas sin espacios."""
        return value.upper().replace(' ', '').replace('-', '')


class VehiculoCreateSerializer(VehiculoSerializer):
    """
    Serializer para creacion de vehiculos.
    Asigna automaticamente el usuario que crea.
    """
    cargado_por = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
